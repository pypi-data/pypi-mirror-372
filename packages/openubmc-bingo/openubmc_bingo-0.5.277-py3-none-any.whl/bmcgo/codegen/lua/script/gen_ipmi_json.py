#!/usr/bin/env python3
# coding=utf-8
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.


import re

import json
import logging
import getopt
import sys
import os
import stat
import mds_util as utils
from utils import Utils


MAX = "Max"
DEFAULT = "Default"
USER = "User"
OPERATOR = "Operator"
CALLBACK = "Callback"
UNSPECIFIED = "Unspecified"
BASETYPE = ["U8", "U16", "U32", "U64", "S8", "S16", "S32", "S64", "U8[]", "String"]
PRIORITY = ["Default", "OEM", "ODM", "OBM", "EndUser"]
ROLE = ["User", "Administrator", "Operator", "Unspecified", "Callback", "OEM"]
PRIVILEGE = ["UserMgmt", "BasicSetting", "KVMMgmt", "VMMMgmt", "SecurityMgmt",
            "PowerMgmt", "DiagnoseMgmt", "ReadOnly", "ConfigureSelf"]


# 请求/响应体参数校验
def check_message(message_index, message_data, message_len, command_name):
    name = message_data["data"]
    
    if message_data.get("baseType") is None:
        raise Exception(f"{command_name}命令请求/响应体中{name}缺少base_type字段配置")
    base_type = message_data["baseType"]
    if base_type not in BASETYPE:
        raise Exception(f"{command_name}命令请求/响应体中{name}配置的baseType参数{base_type}超出取值范围")

    length = message_data["len"]
    len_num = length[:-1]
    base_type_num = base_type[1:]
    if len_num.lstrip('-').isdigit() and int(len_num) <= 0:
        raise Exception(f"{command_name}命令请求/响应体中{name}配置的len参数{length}有误（须为大于0的整数）")
    if base_type in ["U8", "U16", "U32", "U64", "S8", "S16", "S32", "S64"]:
        if length[-1] == 'B' and int(len_num) * 8 > int(base_type_num):
            raise Exception(f"{command_name}命令请求/响应体中{name}配置的len参数{length}与basetype参数{base_type}不匹配")
        elif length[-1] == 'b' and int(len_num) > int(base_type_num):
            raise Exception(f"{command_name}命令请求/响应体中{name}配置的len参数{length}与basetype参数{base_type}不匹配")
    elif base_type in ["String", "U8[]"]:
        if length == "*" and message_index != message_len - 1:
            raise Exception(f"{command_name}命令请求/响应体中{name}配置的len参数{length}有误（仅当配置参数为请求/响应体中最后一个参数，len才可配置为*）")


def make_properties(package, message, imports, command_name):
    properties = []
    name_check = set()
    length = len(message)
    has_manufacture = False
    manufacturer_index = -1
    for index, prop_data in enumerate(message):
        check_message(index, prop_data, length, command_name)

        name = prop_data["data"]
        if len(name) > 64:
            raise Exception(f"{command_name}命令中请求/响应体配置的data参数{name}过长")
        if name in name_check:
            raise Exception(f"{command_name}命令中请求/响应体配置的data参数存在重复配置{name}")
        name_check.add(name)

        manufacturer = False
        if prop_data.get("customizedRule", "") == "Manufacturer":
            if has_manufacture:
                raise Exception(f"{command_name}命令的请求/响应中只允许一个参数配置Manufacturer")
            has_manufacture = True
            manufacturer = True
            manufacturer_index = index

        if "value" in prop_data:
            int_len = int(prop_data["len"][0])
            value = prop_data["value"]
            if prop_data["len"][-1] == 'B' and \
            re.match('^0x[0-9A-Fa-f]{' + str(int_len * 2) + '}$', value, re.IGNORECASE) is None:
                raise Exception(f"{command_name}命令中参数{name}的value配置值{value}有误（须为16进制且长度与配置的len一致）")
            elif prop_data["len"][-1] == 'b' and len(bin(int(value, 16))) - 2 > int_len:
                raise Exception(f"{command_name}命令中参数{name}的value配置值{value}有误（须为16进制且长度与配置的len一致）")
            if manufacturer:
                raise Exception(f"{command_name}命令中配置了value字段的参数{name}不允许配置Manufacturer")
            continue

        t_property = utils.get_property(name, prop_data, 0)
        t_property["options"]["manufacturer"] = manufacturer
        if "type" in t_property and t_property["type"] not in utils.ALLOW_BASIC_TYPES.values():
            t_property["type"] = t_property["type"].replace("defs_", "")
            if t_property["type"].startswith("def_types."):
                imports.add("model_types/def_types.proto")
            elif not t_property["type"].startswith("defs."):
                imports.add("server/" + t_property.get("interface", "") + ".proto")
            else:
                t_property["type"] = t_property["type"].replace("defs.", package + ".")
        properties.append(t_property)

    return properties, manufacturer_index


def make_nested_types(data_value, package, imports, data_name):
    req_properties, req_manufacturer_index = make_properties(package, data_value["req"], imports, data_name)
    req = {
        "package": package,
        "name": "Req",
        "options": {},
        "type": "Message",
        "manufacturer": req_manufacturer_index,
        "properties": req_properties,
        "nested_type": [],
    }

    rsp_properties, rsp_manufacturer_index = make_properties(package, data_value["rsp"], imports, data_name)
    rsp = {
        "package": package,
        "name": "Rsp",
        "options": {},
        "type": "Message",
        "manufacturer": rsp_manufacturer_index,
        "properties": rsp_properties,
        "nested_type": [],
    }
    return [req, rsp]


def get_byte_count(data_len):
    if data_len.endswith("B"):
        return int(data_len.split("B")[0]), 0
    if data_len.endswith("b"):
        return 0, int(data_len.split("b")[0])
    return 0, 0


def get_hex_values(prop_data):
    values = []
    real_hex = prop_data["value"].replace("0x", "")
    if prop_data["len"].endswith("B"):
        str_len = int(prop_data["len"].split("B")[0]) * 2
        if len(real_hex) < str_len:
            real_hex = "0" * (str_len - len(real_hex)) + real_hex

    values = re.findall(r".{2}", real_hex)
    values.reverse()
    return values


def make_filters(message):
    filters = []
    temp_filters = []
    bit_count = 0
    for prop_data in message:
        if "value" in prop_data:
            temp_filters += get_hex_values(prop_data)
            filters = filters + temp_filters
            temp_filters = []
        else:
            byte_count, temp_bit_count = get_byte_count(prop_data["len"])
            bit_count += temp_bit_count
            if bit_count >= 8:
                byte_count += 1
                bit_count -= 8
            temp_filters += ["*"] * byte_count
    out = ",".join(filters)
    return out


def get_type(data_type, data_len, message):
    out_type = ""
    out_unit = "string"
    if data_len in message:
        out_type += ":" + data_len
    else:
        if data_len != "*":
            if not data_len[:-1].isdigit():
                raise Exception(f"命令请求/响应体中参数len配置值{data_len}有误（须为固定长度、'*'或前面出现的参数名称）")
            params = re.compile(r"([0-9]+)([Bb])").findall(data_len)
            out_type += ":" + params[0][0]
            types = {"B": "unit:8", "b": "unit:1"}
            out_unit = types.get(params[0][1], "")
    if data_type == "String":
        out_unit = "string"

    out_type += "/" + out_unit

    return out_type


def make_code(message, data_name):
    code = []
    var_list = []
    for prop_data in message:
        if prop_data.get("data") is None:
            raise Exception(f"{data_name}命令请求/响应体中存在参数缺少data字段配置")
        var_list.append(prop_data["data"])
        
        var_name = prop_data["value"] if "value" in prop_data else prop_data["data"]
        name = prop_data["data"]
        if prop_data.get("len") is None:
            raise Exception(f"{data_name}命令请求/响应体中{name}缺少len字段配置")
        code.append(
            var_name + get_type(prop_data["baseType"] if "baseType" in prop_data else None, prop_data["len"], var_list)
        )

    if len(code) == 0:
        return ""
    return "<<" + ", ".join(code) + ">>"


def trans_priority_map(origin, version):
    if int(version) >= 5:
        priority_map = {
            DEFAULT: True,
            "OEM": True,
            "ODM": True,
            "OBM": True,
            "EndUser": True,
            MAX: True,
        }

        return origin if origin in priority_map else DEFAULT

    priority_map = {
        DEFAULT: "BmcBase",
        "OEM": "OemBase",
        "ODM": "OdmBase",
        "OBM": "OdmBase",
        "EndUser": "CustomBase",
        MAX: MAX,
    }
    if origin not in priority_map:
        origin = DEFAULT
    return priority_map[origin]


def get_sys_locked_policy(policy, name):
    if policy is None:
        return "Allowed"
    policies = {"Allowed", "Forbidden"}
    if policy not in policies:
        raise Exception(f"命令{name}的sysLockedPolicy配置值{policy}不在取值范围内")
    return policy


def trans_role_map(origin, version):
    if int(version) >= 5:
        role_map = {
            UNSPECIFIED: True,
            CALLBACK: True,
            USER: True,
            OPERATOR: True,
            "Administrator": True,
            "OEM": True,
        }

        return origin if origin in role_map else UNSPECIFIED

    role_map = {
        UNSPECIFIED: "None",
        CALLBACK: CALLBACK,
        USER: USER,
        OPERATOR: OPERATOR,
        "Administrator": "Admin",
        "OEM": "Oem",
    }
    if origin not in role_map:
        origin = UNSPECIFIED
    return role_map[origin]


def check_duplicate_msg(messages, method_name):
    for method in messages:
        if method["name"] == method_name:
            return True
    return False


# 为结构体生成message
def gen_defs(defs, msg_package, packages):
    if msg_package not in packages:
        packages[msg_package] = {"messages": []}

    package = packages[msg_package]
    for struct_name, struct_data in defs.items():
        msg_name = struct_name
        if not check_duplicate_msg(package["messages"], msg_name):
            update_package(package, msg_name, struct_data, msg_package)


def get_message(msg_name, msg_data, msg_pack):
    has_struct = False
    depends = []
    message = {}
    message_type = utils.get_message_type(msg_data)
    if message_type == 'struct':
        message = utils.get_struct_message(msg_pack, msg_name, msg_data)
        for prop in message.get("properties", []):
            if prop["type"] not in utils.ALLOW_BASIC_TYPES.values():
                prop["type"] = prop["type"].replace("defs.", msg_pack + ".")
                depends.append(prop["type"])
                has_struct = True
        if "options" in message:
            message["options"]["has_struct"] = has_struct
    elif message_type == 'enum':
        message = utils.get_enum_message(msg_pack, msg_name, msg_data)
    else:
        message = utils.get_dict_message(msg_pack, msg_name, msg_data)

    return message, depends


def get_depend_message_pos(depend, old_messages):
    index = 1
    for var in old_messages:
        if (var["package"] + "." + var["name"]) == depend:
            return index
        index = index + 1

    return -1


# 由于当前模板的限制，依赖必须是顺序的，因此要计算插入的位置
def update_package(package, msg_name, struct_data, msg_package):
    new_message, depends = get_message(msg_name, struct_data, msg_package)
    last_pos = 0
    for depend in depends:
        pos = get_depend_message_pos(depend, package["messages"])
        if pos != -1:
            last_pos = max(last_pos, pos)

    package["messages"].insert(last_pos, new_message)


# cmds参数校验
def check_cmds_data(name, value):
    if len(name) > 64:
        raise Exception(f"命令{name}的名称过长")

    netfn = value["netfn"]
    if re.match('^0x[0-9A-Fa-f]{1,2}$', netfn, re.IGNORECASE) is None:
        raise Exception(f"命令{name}中netfn的配置值{netfn}不满足16进制、1字节的格式要求")

    cmd = value["cmd"]
    if re.match('^0x[0-9A-Fa-f]{1,2}$', cmd, re.IGNORECASE) is None:
        raise Exception(f"命令{name}中cmd的配置值{cmd}不满足16进制、1字节的格式要求")

    priority = value["priority"]
    if priority not in PRIORITY and Utils.get_lua_codegen_version() >= 5:
        raise Exception(f"命令{name}中priority的配置值{priority}不在取值范围内")

    role = value.get("role")
    if role is not None and role not in ROLE:
        raise Exception(f"命令{name}中role的配置值{role}不在取值范围内")

    privilege = value["privilege"] if isinstance(value["privilege"], list) else []
    for item in privilege:
        if item not in PRIVILEGE and Utils.get_lua_codegen_version() >= 5:
            raise Exception(f"命令{name}中privilege的配置值{item}不在取值范围内")
        
    sensitive = value.get("sensitive")
    if sensitive is not None and not isinstance(sensitive, bool):
        raise Exception(f"命令{name}中sensitive的配置值{sensitive}不在取值范围内（只可配置为true或false）")


def make_datas(load_dict, imports, version):
    datas = []
    if load_dict.get("package") is None:
        raise Exception(f"ipmi命令文件中缺少package字段配置")
    if load_dict.get("cmds") is None:
        raise Exception(f"ipmi命令文件中缺少cmds字段配置")

    for data_name, data_value in load_dict["cmds"].items():
        role = data_value.get("role", data_value["privilege"])
        privilege = data_value["privilege"] if isinstance(data_value["privilege"], list) else []

        check_cmds_data(data_name, data_value)

        datas.append(
            {
                "package": load_dict["package"],
                "name": data_name,
                "options": {
                    "netfn": int(data_value["netfn"], 16),
                    "cmd": int(data_value["cmd"], 16),
                    "priority": trans_priority_map(data_value["priority"], version),
                    "role": trans_role_map(role, version),
                    "privilege": privilege,
                    "sensitive": data_value.get("sensitive", False),
                    "restricted_channels": data_value.get("restricted_channels", []),
                    "decode": make_code(data_value["req"], data_name),
                    "encode": make_code(data_value["rsp"], data_name),
                    "filters": make_filters(data_value["req"]),
                    "sysLockedPolicy": get_sys_locked_policy(data_value.get("sysLockedPolicy", None), data_name)
                },
                "type": "Message",
                "properties": [],
                "nested_type": make_nested_types(data_value, load_dict["package"], imports, data_name),
            }
        )

    messages = {}
    if "defs" in load_dict:
        gen_defs(load_dict["defs"], load_dict["package"], messages)

    for pkg_data in messages.values():
        datas.extend(pkg_data["messages"])

    return datas


def generate(if_name, of_name, version):
    if not os.path.exists(if_name):
        return

    load_f = os.fdopen(os.open(if_name, os.O_RDONLY, stat.S_IRUSR), "r")

    load_dict = json.load(load_f)
    extra_imports = set()
    datas = make_datas(load_dict, extra_imports, version)
    imports = [
        "google/protobuf/descriptor.proto",
        "ipmi_types.proto",
        "types.proto"
    ]
    imports.extend(extra_imports)
    dependency = ["types.proto", "ipmi_types.proto"]
    dependency.extend(extra_imports)
    out_dict = {
        "imports": imports,
        "dependency": dependency,
        "data": datas,
        "service": [],
        "filename": "ipmi/ipmi.proto",
        "package": load_dict["package"],
        "options": {},
    }
    utils.save_proto_json(of_name, out_dict)
    load_f.close()


def usage():
    logging.info("gen_ipmi_json.py -i <inputfile> -o <file>")


def main(argv):
    m_input = ""
    output = ""
    try:
        opts, _ = getopt.getopt(argv, "hi:o:d:v:", ["help", "input=", "out=", "version="])
    except getopt.GetoptError:
        help()
        return
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            return
        elif opt in ("-i", "--input"):
            m_input = arg
        elif opt in ("-o", "--out"):
            output = arg
        elif opt in ("-v", "--version"):
            version = arg
        else:
            raise RuntimeError("不支持的选项: {}".format(opt))
    if not m_input or not output:
        usage()
        return
    generate(m_input, output, version)


if __name__ == "__main__":
    main(sys.argv[1:])
