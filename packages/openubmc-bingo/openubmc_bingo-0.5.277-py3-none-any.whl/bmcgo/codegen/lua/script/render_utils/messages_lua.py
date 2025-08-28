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

from utils import Utils
from dto.options import Options
from bmcgo.codegen.lua.script.base import Base
from bmcgo.codegen.lua.script.factory import Factory


class MessagesLuaUtils(Base, Utils):
    LOG_MAP = {
        "OK": "log.INFO",
        "Warning": "log.WARN",
        "Critical": "log.ERROR"
    }

    def __init__(self, data: dict, options: Options):
        super().__init__(data, options=options)

    @staticmethod
    def match_placeholders(msg):
        return sorted(set(int(v) for v in re.findall(r"%(\d+)", msg)))

    @staticmethod
    def format_hex(data):
        return "0x%02X" % data

    @staticmethod
    def format(msg):
        return re.sub(r"%(\d+)", r"%s", re.sub(r'%\D', lambda x: '%%' + x.group(0)[1:], msg))

    @staticmethod
    def get_app_name(code):
        name = code.split(".")
        if name == -1:
            return code
        return name[1]

    @staticmethod
    def get_http_response(root, err):
        ret = -1
        if 'HttpStatusCode' in err:
            ret = err['HttpStatusCode']
        elif 'HttpStatusCode' in root:
            ret = root['HttpStatusCode']
        if ret == -1: # 没有配置则返回nil
            return 'nil'
        return str(ret)

    @staticmethod
    def get_redfish_response(root, err):
        if 'RedfishResponse' in err and len(err['RedfishResponse']) > 0:
            return "\"{}\"".format(err['RedfishResponse'])
        if 'RedfishResponse' in root and len(root['RedfishResponse']) > 0:
            return "\"{}\"".format(root['RedfishResponse'])
        return 'nil'

    @staticmethod
    def ret_check_ipmi(res):
        generic_completion_codes = [
            0x00,
            0xC0,
            0xC1,
            0xC2,
            0xC3,
            0xC4,
            0xC5,
            0xC6,
            0xC7,
            0xC8,
            0xC9,
            0xCA,
            0xCB,
            0xCC,
            0xCD,
            0xCE,
            0xCF,
            0xD0,
            0xD1,
            0xD2,
            0xD3,
            0xD4,
            0xD5,
            0xD6,
            0xFF,
        ]
        device_specific_codes = range(0x01, 0x7E + 1)
        command_specific_codes = range(0x80, 0xBE + 1)
        if res == -1:  # 没有配置则返回nil
            return "nil"
        valid = res in generic_completion_codes or res in device_specific_codes \
                or res in command_specific_codes
        if not valid:  # 不在规定的返回码范围中则抛错
            raise Exception("无效的 ipmi 响应: 0x%02X" % res)
        return "0x%02X" % res

    @staticmethod
    def get_ipmi_response(err):
        res = 0
        if "IpmiCompletionCode" in err:
            res = int(err["IpmiCompletionCode"], 16)

        return MessagesLuaUtils.ret_check_ipmi(res)

    @staticmethod
    def get_backtrace_level(root, err):
        ret = 0
        if "TraceDepth" in err:
            ret = err["TraceDepth"]
        elif "TraceDepth" in root:
            ret = root["TraceDepth"]
        if ret > 5:  # 层级不超过5层
            return 5
        return ret

    @staticmethod
    def get_severity_err(err):
        if "Severity" in err and err["Severity"] in MessagesLuaUtils.LOG_MAP:
            return MessagesLuaUtils.LOG_MAP.get(err["Severity"])
        return "log.DEBUG"  # 不在log_map映射表中则默认返回debug

    @staticmethod
    def get_severity(root, err):
        if 'Severity' in err and err['Severity'] in MessagesLuaUtils.LOG_MAP:
            return MessagesLuaUtils.LOG_MAP.get(err['Severity'])
        if 'Severity' in root and root['Severity'] in MessagesLuaUtils.LOG_MAP:
            return MessagesLuaUtils.LOG_MAP.get(root['Severity'])
        return 'log.DEBUG' # 不在log_map映射表中则默认返回debug

    def error_params(self, err):
        params = self.params(err["Message"])
        if len(params) == 0:
            return ""
        return f", {params}"

    def params(self, msg):
        placeholders = self.match_placeholders(msg)
        if len(placeholders) == 0:
            return ""
        elif len(placeholders) != placeholders[len(placeholders) - 1]:
            raise RuntimeError("无效错误信息: `{}`, 无法匹配到占位符".format(msg))
        return ", ".join(["val" + str(v) for v in placeholders])


Factory().register("messages.lua.mako", MessagesLuaUtils)
