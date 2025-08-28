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


class ErrorLuaUtils(Base, Utils):
    LOG_MAP = {
        "error": "log.ERROR",
        "warning": "log.WARN",
        "debug": "log.DEBUG",
        "trace": "log.TRACE",
    }

    def __init__(self, data: dict, options: Options):
        super().__init__(data, options=options)

    @staticmethod
    def get_error_name(code):
        err = code.split(".")
        if err == -1 or len(err) != 3:  # 不满足3段式格式则抛错
            raise Exception("无法满足 <xx.xx.xx> 的格式要求, %s" % code)
        idx = code.rfind(".")
        if idx == -1:
            return code
        return code[idx + 1:]

    @staticmethod
    def match_placeholders(msg):
        return sorted(set([int(v) for v in re.findall(r"{(\d+)}", msg)]))

    @staticmethod
    def format_hex(data):
        return "0x%02X" % data

    @staticmethod
    def format(msg):
        return re.sub(r"{(\d+)}", r"%s", msg)

    @staticmethod
    def get_app_name(code):
        name = code.split(".")
        if name == -1:
            return code
        return name[1]

    @staticmethod
    def get_http_response(root, err):
        ret = -1
        if 'http_response' in err:
            ret = err['http_response']
        elif 'http_response' in root:
            ret = root['http_response']
        http_check_list = [
            400, 401, 402, 403, 404, 405, 406, 408, 409, 410, 426,
            429, 444, 451, 500, 501, 502, 503, 504, 505, 507
        ]
        if ret == -1: # 没有配置则返回nil
            return 'nil'
        if ret not in http_check_list: # 不在规定的返回码列表中则抛错
            raise Exception("http 响应无效: %d" % ret)
        return str(ret)

    @staticmethod
    def get_redfish_response(root, err):
        if 'redfish_response' in err and len(err['redfish_response']) > 0:
            return "\"{}\"".format(err['redfish_response'])
        if 'redfish_response' in root and len(root['redfish_response']) > 0:
            return "\"{}\"".format(root['redfish_response'])
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
            raise Exception("ipmi 响应无效: 0x%02X" % res)
        return "0x%02X" % res

    @staticmethod
    def get_ipmi_response(root, err):
        res = 0
        if "ipmi_response" in err:
            res = err["ipmi_response"]
        elif "ipmi_response" in root:
            res = root["ipmi_response"]
        return ErrorLuaUtils.ret_check_ipmi(res)

    @staticmethod
    def get_ipmi_response_json(err):
        res = 0
        if "ipmi_response" in err:
            res = int(err["ipmi_response"], 16)

        return ErrorLuaUtils.ret_check_ipmi(res)

    @staticmethod
    def get_backtrace_level(root, err):
        ret = 0
        if "backtrace_level" in err:
            ret = err["backtrace_level"]
        elif "backtrace_level" in root:
            ret = root["backtrace_level"]
        if ret > 5:  # 层级不超过5层
            return 5
        return ret

    @staticmethod
    def get_severity_err(err):
        if "severity" in err and err["severity"] in ErrorLuaUtils.LOG_MAP:
            return ErrorLuaUtils.LOG_MAP.get(err["severity"])
        return "log.DEBUG"  # 不在log_map映射表中则默认返回debug

    @staticmethod
    def get_severity(root, err):
        if 'severity' in err and err['severity'] in ErrorLuaUtils.LOG_MAP:
            return ErrorLuaUtils.LOG_MAP.get(err['severity'])
        if 'severity' in root and root['severity'] in ErrorLuaUtils.LOG_MAP:
            return ErrorLuaUtils.LOG_MAP.get(root['severity'])
        return 'log.DEBUG' # 不在log_map映射表中则默认返回debug

    def error_params(self, err):
        s = self.params(err["message"])
        if len(s) == 0:
            return ""
        return f", {s}"

    def params(self, msg):
        placeholders = self.match_placeholders(msg)
        if len(placeholders) == 0:
            return ""
        elif len(placeholders) != placeholders[len(placeholders) - 1]:
            raise RuntimeError("无效错误信息: `{}`, 未匹配到占位符".format(msg))
        return ", ".join(["val" + str(v) for v in placeholders])

    def get_function_name(self, code):
        return Utils.camel_to_snake(self.get_error_name(code))


Factory().register("errors.lua.mako", ErrorLuaUtils)
