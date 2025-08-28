#!/usr/bin/python3
# coding: utf-8
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import json
import math
import os
import re
import subprocess
import stat
import inflection
from mako.lookup import TemplateLookup
from bmcgo.ipmigen.ctype_defination import CTypes, CTypeBase
from bmcgo.codegen.c.helper import Helper
from bmcgo.codegen.c.renderer import Renderer
from bmcgo.logger import Logger

log = Logger("ipmi_gen")
cwd = os.path.split(os.path.realpath(__file__))[0]
FILTER_SPLIT = "*,"
U8_POINT = "U8 *"


class MdsFormatError(OSError):
    """测试失败"""


def get_byte(obj, name, key):
    val = obj.get(key)
    if val is None:
        raise MdsFormatError("获取属性 %s.%s 失败", name, key)
    val = val.lower()
    if not val.startswith("0x"):
        raise MdsFormatError("无效的 16 进制字符串, 固定名: {}.{}}, 值: {}".format(name, key, val))
    return val


class IpmiCmdArg(object):
    def __init__(self, obj):
        self.data = obj.get("data")
        self.base_type = obj.get("baseType")
        self.manufacturer = obj.get("customizedRule") == "Manufacturer"
        if self.base_type is None:
            raise MdsFormatError("获取基础类型失败")
        self.base_type = self.base_type
        self.ctype: CTypeBase = None
        self.len = obj.get("len")
        self.value = obj.get("value", None)
        # 标记响应u8 *类型值的长度来自于请求
        self.len_from_req = False;
        if self.value is not None and self.value[0:2].lower() != "0x":
            raise MdsFormatError("过滤器参数 {} 格式错误, 必须以 '0x' 开头, 但实际值为 {}"
                                 .format(self.data, self.value))
        self.filter = ""
        # "*" 只适用于String，否则报错
        if self.base_type == "Double":
            if self.len != "8B":
                raise MdsFormatError("数据: {} 长度错误: 基础类型 `Double` 长度必须为 8B, 当前长度: {}"
                                     .format(self.data, self.len))
        elif self.len == "*":
            if self.base_type == "String":
                self.base_type = "String *"
            elif self.base_type == "U8[]":
                self.base_type = U8_POINT
            else:
                raise MdsFormatError("数据: {} 基础类型错误: 仅 `String` 和 `U8[]` 支持基础类型 '*'"
                                     .format(self.data))
        elif re.match('^[1-9][0-9]*B$', self.len):
            pass
        elif self.base_type == "U8[]" and not re.match('^[1-9][0-9]*B$', self.len):
            self.base_type = U8_POINT
        elif self.len == "0b" or self.len == "0B":
            raise MdsFormatError("数据: {} 长度错误: {}".format(self.data, self.len))
        self._ctype_parse()

    def _ctype_parse(self):
        # 获取C类型定义
        self.ctype = CTypes.types.get(self.base_type)
        if self.ctype is None:
            raise MdsFormatError("数据 {} 中有不支持的基础类型: {}".format(self.data, self.base_type))
        log.debug("数据: %s, 基础类型: %s, 基础类型: %d, 值:%s", self.data, self.base_type, self.len, self.value)
        if not self.base_type.endswith("[]") and not self.base_type.startswith("String") and self.base_type != U8_POINT:
            val_len = int(self.len[:-1], 10)
            if re.match('^[1-9][0-9]*B$', self.len) and val_len > self.ctype.c_len:
                raise MdsFormatError("数据: {} 长度错误: 长度必须小于或者等于 {}B, 当前长度为: {}B"
                                     .format(self.data, self.ctype.c_len, val_len))
            elif re.match('^[1-9][0-9]*b$', self.len) and val_len > (self.ctype.c_len * 8):
                max_len = self.ctype.c_len * 8
                raise MdsFormatError("数据: {} 长度错误: 长度必须小于或者等于 {}b, 当前长度为: {}b"
                                     .format(self.data, max_len, val_len))

        if re.match('^[1-9][0-9]*B$', self.len) is not None:
            # 如果是Byte，计算数组长度时需要除C元素大小并向上取整
            self.bit_len = int(self.len[:-1], 10) * 8
            self.type_len = math.ceil(self.bit_len / 8 / self.ctype.c_len)
            self.bit_field = ""
        elif re.match('^[1-9][0-9]*b$', self.len) is not None:
            # 如果是位域
            self.type_len = ""
            self.bit_len = int(self.len[:-1], 10)
            self.bit_field = ":" + str(self.bit_len)
        else:
            # 否则啥也不是
            self.type_len = ""
            self.bit_len = 0
            self.bit_field = ""

        self.c_declear_str = self.ctype.c_type.replace("<arg_name>", self.data)
        self.c_declear_str = self.c_declear_str.replace("<type_len>", str(self.type_len))
        self.c_declear_str = self.c_declear_str.replace("<bit_field>", self.bit_field)


class IpmiCmd(object):
    def __init__(self, name, obj):
        self.name = name
        log.info("ipmi 命令名称: %s === >>>", name)
        self.netfn = get_byte(obj, name, "netfn")
        self.cmd = get_byte(obj, name, "cmd")
        self.priority_str = obj.get("priority", "Default")
        priority_map = {
            "Default": 10, "Oem": 20, "OEM": 20, "Odm": 30, "ODM": 30, "OBM": 35, "EndUser": 40, "Max": 50
        }
        self.priority = priority_map.get(self.priority_str, None)
        if self.priority is None:
            raise MdsFormatError("{} 不支持的命令优先级 {}, 退出".format(name, self.priority_str))

        self.role_str = obj.get("role", "None")
        self.sensitive = obj.get("sensitive", False)

        privilege_map = {
            "OEM": 5, "Administrator": 4, "Operator": 3, "User": 2, "Callback": 1, "Unspecified": 0
        }
        self.role = privilege_map.get(self.role_str, 0)
        if self.role is None:
            raise MdsFormatError("命令 {} 不支持的规则 {}, 终止构建".format(name, self.role))
        self.privilege_str = obj.get("privilege", [])
        self.privilege = Helper.get_privilege(",".join(self.privilege_str))
        self.req_args: list[IpmiCmdArg] = []
        self.rsp_args: list[IpmiCmdArg] = []
        self._arg_parse(obj)

    @property
    def filter(self):
        filter_str = ""
        bit_pos = 0
        last_bit_type = None
        for arg in self.req_args:
            if re.match('^[1-9][0-9]*B$', arg.len):
                # 如果之前有位域未处理的，生成过滤符
                if bit_pos:
                    filter_str += FILTER_SPLIT.join("" for _ in range((bit_pos + 7) // 8 + 1))
                    bit_pos = 0
                # 如果需要过滤的
                if arg.value is not None:
                    hex_len = (arg.bit_len // 8) * 2
                    value = arg.value[2:].lower()
                    # 可能过长，需要截断
                    value = value[0:hex_len]
                    # 可能过短，需要补前零
                    value = value.rjust(hex_len, '0')
                    filter_str += ",".join(value[i - 2:i] for i in range(hex_len, 0, -2)) + ","
                else:
                    filter_str += FILTER_SPLIT.join("" for _ in range(arg.bit_len // 8 + 1))
            elif re.match('^[1-9][0-9]*b$', arg.len):
                cross_type = (bit_pos + arg.bit_len - 1) // (arg.ctype.c_len * 8) != bit_pos // (arg.ctype.c_len * 8)
                # 类型发生变更时重新计数或位域跨多个基础类型
                if bit_pos != 0 and last_bit_type != arg.base_type and cross_type:
                    filter_str += FILTER_SPLIT.join("" for _ in range((bit_pos + 7) // 8 + 1))
                    bit_pos = 0
                bit_pos += arg.bit_len
                last_bit_type = arg.base_type
            else:
                # 跳过大小不明确的内容
                break
        if bit_pos:
            filter_str += FILTER_SPLIT.join("" for _ in range((bit_pos + 7) // 8 + 1))
        while filter_str.endswith(",") or filter_str.endswith("*"):
            filter_str = filter_str[:-1]
        return filter_str

    def _req_arg_parse(self, obj):
        req_name = []
        last_dynamic_u8 = False
        for arg in obj.get("req", []):
            arg = IpmiCmdArg(arg)
            self.req_args.append(arg)
        # 检查类型为U8[]且长度为变量为*的场景
        index = 0
        req_manufacturer_index = -1
        for arg in self.req_args:
            if arg.manufacturer:
                if req_manufacturer_index != -1:
                    raise Exception(f"{self.name}的请求中只允许一个参数配置Manufacturer")
                req_manufacturer_index = index
            index = index + 1
            # 如果类型为U8[]且长度未在之前申明且不是最后一个参数的
            if arg.base_type == U8_POINT and arg.len not in req_name and index != len(self.req_args):
                raise MdsFormatError("数据 {}.{} 有无效长度".format(self.name, arg.data))
            req_name.append(arg.data)
        return req_name, req_manufacturer_index

    def _arg_parse(self, obj):
        req_name, req_manufacturer_index = self._req_arg_parse(obj)

        log.debug("ipmi 响应:")
        for arg in obj.get("rsp", []):
            self.rsp_args.append(IpmiCmdArg(arg))

        # 检查类型为U8[]且长度为变量为*的场景
        index = 0
        rsp_name = []
        rsp_manufacturer_index = -1
        for arg in self.rsp_args:
            if arg.manufacturer:
                if rsp_manufacturer_index != -1:
                    raise Exception(f"{self.name}的响应中只允许一个参数配置Manufacturer")
                rsp_manufacturer_index = index
            index = index + 1
            # 如果类型为U8[]且长度未在之前申明的（也就是说响应字段必须申明长度，否则不能正确构造响应体）
            if arg.base_type == U8_POINT:
                if arg.len not in rsp_name and arg.len not in req_name:
                    raise MdsFormatError("数据 {}.{} 有无效长度".format(self.name, arg.data))
                if arg.len in rsp_name:
                    pass
                # U8 *类型的响应值长度来自于请求体
                if arg.len in req_name:
                    arg.len_from_req = True
            rsp_name.append(arg.data)
        self.manufacturer = "{" + str(req_manufacturer_index) + ", " + str(rsp_manufacturer_index) + "}"
        self.need_free_rsp = False
        for arg in self.rsp_args:
            if arg.base_type == "String *" or arg.base_type == U8_POINT:
                self.need_free_rsp = True
                break
        if len(self.rsp_args) == 0:
            raise MdsFormatError("IPMI命令{}的响应缺少完成码".format(self.name))
        complete = self.rsp_args[0];
        if complete.data != "CompletionCode":
            log.warning(f"IPMI命令%s的响应第一个成员(%s)名称不是(CompletionCode)，为增加可读性，建议改名", self.name, complete.data)

        if complete.base_type != "U8":
            log.error(f"IPMI命令%s的响应第一个成员(%s)必须是U8类型", self.name, complete.data)


class IpmiCmds(Renderer):
    def __init__(self, lookup, ipmi_json, base_version):
        super(Renderer, self).__init__()
        self.base_version = base_version
        self.lookup = lookup
        with open(ipmi_json) as file_handler:
            ipmi_cmds = json.load(file_handler)
        self.package = ipmi_cmds.get("package")
        self.name = inflection.underscore(self.package)
        self.cmds: list[IpmiCmd] = []
        for cmd, data in ipmi_cmds.get("cmds", {}).items():
            self.cmds.append(IpmiCmd(cmd, data))

    def render_ipmi(self, template, out_file):
        file_handler = os.fdopen(os.open(out_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                         stat.S_IWUSR | stat.S_IRUSR), 'w')
        out = self.render(self.lookup, template, ipmi_cmds=self, version=self.base_version)
        file_handler.write(out)
        file_handler.close()
        pass

    def render_cmd(self, template, out_dir):
        for cmd in self.cmds:
            out_file = os.path.join(out_dir, "ipmi_cmd_" + inflection.underscore(cmd.name) + ".c")
            file_handler = os.fdopen(os.open(out_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                             stat.S_IWUSR | stat.S_IRUSR), 'w')
            out = self.render(self.lookup, template, package_name=self.package, cmd=cmd, version=self.base_version)
            file_handler.write(out)
            file_handler.close()


class IpmiGen(object):
    def __init__(self, base_version):
        self.base_version = base_version

    def format(self, out_file):
        try:
            Helper.run(["/usr/bin/clang-format", "--version"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except Exception:
            log.error("命令 clang-format 没找到, 跳过格式化 %s/%s", os.getcwd(), out_file)
            return
        if not os.path.isfile(".clang-format"):
            log.error("样式文件 .clang-format 不存在, 跳过格式化 %s/%s", os.getcwd(), out_file)
            return
        log.info("格式化源: %s/%s", os.getcwd(), out_file)
        Helper.run(["/usr/bin/clang-format", "--style=file", "-i", out_file])

    def gen(self, json_file, directory="."):
        os.makedirs(directory, exist_ok=True)
        lookup = TemplateLookup(directories=os.path.join(cwd, "template"))
        ipmi_cmds = IpmiCmds(lookup, json_file, self.base_version)
        out_file = os.path.join(directory, ipmi_cmds.name + ".h")
        ipmi_cmds.render_ipmi("ipmi.h.mako", out_file)
        out_file = os.path.join(directory, ipmi_cmds.name + ".c")
        ipmi_cmds.render_ipmi("ipmi.c.mako", out_file)
        ipmi_cmds.render_cmd("cmd.c.mako", directory)
        self.format(out_file)
        log.success("Generate code successfully, interface: %s", json_file)
