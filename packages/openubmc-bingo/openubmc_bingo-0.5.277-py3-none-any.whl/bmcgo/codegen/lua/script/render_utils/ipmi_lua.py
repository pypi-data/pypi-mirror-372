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

from dto.options import Options
from bmcgo.codegen.lua.script.base import Base
from bmcgo.codegen.lua.script.factory import Factory


class IpmiLuaUtils(Base):
    def __init__(self, data: dict, options: Options):
        super().__init__(data, options=options)

    @staticmethod
    def params(msg):
        return ", ".join([p["name"] for p in msg["properties"]])

    @staticmethod
    def params_array(msg):
        return (
            "{" + ", ".join([("'" + p["name"] + "'") for p in msg["properties"]]) + "}"
        )

    @staticmethod
    def is_req(t):
        return t["name"] == "Req"

    @staticmethod
    def is_rsp(t):
        return t["name"] == "Rsp"

    @staticmethod
    def get_option(ipmi, option):
        return (
            ipmi["options"][option]
            if option in ipmi["options"] and ipmi["options"][option]
            else ""
        )

    @staticmethod
    def format_hex(data):
        return "0x%02x" % data

    @staticmethod
    def wrap_json(msg):
        return (
            "{"
            + (", ".join([(p["name"] + " = " + p["name"]) for p in msg["properties"]]))
            + "}"
        )

    @staticmethod
    def get_privilege(ipmi):
        if len(ipmi['options']['privilege']) == 0:
            return 'nil'
        return " | ".join([("privilege." + p) for p in ipmi['options']['privilege']])

    def req(self, ipmi):
        result = None
        if "nested_type" not in ipmi:
            return result

        req_list = [p for p in ipmi["nested_type"] if self.is_req(p)]
        return req_list[0] if req_list else None

    def rsp(self, ipmi):
        result = None
        if "nested_type" not in ipmi:
            return result

        rsp_list = [p for p in ipmi["nested_type"] if self.is_rsp(p)]
        return rsp_list[0] if rsp_list else None

    def req_params(self, ipmi):
        req_info = self.req(ipmi)
        return self.params(req_info) if req_info else ""

    def req_properties(self, ipmi):
        req_info = self.req(ipmi)
        return req_info["properties"] if req_info else []

    def rsp_properties(self, ipmi):
        rsp_info = self.rsp(ipmi)
        return rsp_info["properties"] if rsp_info else []

    def req_json(self, ipmi):
        req_info = self.req(ipmi)
        return self.wrap_json(req_info) if req_info else ""

    def get_netfn(self, ipmi):
        if "net_fn" in ipmi["options"]:
            return ipmi["options"]["net_fn"]
        if "netfn" in ipmi["options"]:
            return ipmi["options"]["netfn"]
        return ""

    def get_priority(self, ipmi):
        if "prio" in ipmi["options"]:
            return ipmi["options"]["prio"]
        if "priority" in ipmi["options"]:
            return ipmi["options"]["priority"]
        return ""


    def get_sys_locked_policy(self, ipmi):
        if "sysLockedPolicy" in ipmi["options"]:
            return ipmi["options"]["sysLockedPolicy"]
        return "Allowed"

    def is_generate_service(self, ipmi):
        if "prio" in ipmi["options"] and ipmi["options"]["prio"]:
            return True
        if "priority" in ipmi["options"] and ipmi["options"]["priority"]:
            return True
        return False

    def has_generate_service(self):
        for ipmi in self.data["data"]:
            if self.is_generate_service(ipmi):
                return True

        return False

    def has_generate_client(self):
        for ipmi in self.data["data"]:
            if "prio" not in ipmi["options"] or not ipmi["options"]["prio"]:
                return True
            if "priority" not in ipmi["options"] or not ipmi["options"]["priority"]:
                return True

        return False

    def get_channel(self, ipmi):
        if "channel" in ipmi["options"] and ipmi["options"]["channel"]:
            return ipmi["options"]["channel"]
        else:
            return self.data["options"]["default_channel"]

    def get_restricted_channel(self, ipmi):
        if "restricted_channels" in ipmi["options"] and ipmi["options"]["restricted_channels"]:
            return '{' + ','.join([("'" + p + "'") for p in ipmi["options"]["restricted_channels"]]) + '}'
        else:
            return "{}"

    def get_manufacturer(self, ipmi):
        manufacturer = [-1, -1]
        for i in range(2):
            manufacturer[i] = ipmi["nested_type"][i]["manufacturer"]
        return manufacturer

Factory().register("ipmi.lua.mako", IpmiLuaUtils)
