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
from render_utils.utils_message_lua import UtilsMessageLua
from render_utils.validate_lua import ValidateLua
from bmcgo.codegen.lua.script.base import Base
from bmcgo.codegen.lua.script.factory import Factory


class ControllerLuaUtils(Base, ValidateLua, UtilsMessageLua):
    methods = ['get', 'post', 'patch', 'delete']

    def __init__(self, data: dict, options: Options):
        super().__init__(data, options)

    @staticmethod
    def get_property(properties, prop_name):
        for prop in properties:
            if prop["name"].lower() == prop_name.lower():
                return prop
        return False

    @staticmethod
    def get_lower_case_name(name):
        lst = []
        for index, char in enumerate(name):
            if char.isupper() and index != 0:
                lst.append("_")
            lst.append(char)
        return "".join(lst).lower()

    @staticmethod
    def get_auth(msg):
        if 'auth' in msg["options"]:
            return ', self.auth(ctx)'
        return ''

    def get_response(self, msg):
        return self.get_property(msg["properties"], "response")

    def get_body(self, msg):
        return self.get_property(msg["properties"], "body")

    def get_formdata_body(self, msg):
        return self.get_property(msg["properties"], "formdatabody")


    def get_header(self, msg):
        return self.get_property(msg["properties"], "header")

    def get_controller_methods(self, msg):
        result = {}
        for method in self.methods:
            method_prop = self.get_property(msg['nested_type'], method)
            if not method_prop:
                continue
            result[method] = method_prop
        return result


Factory().register("controller.lua.mako", ControllerLuaUtils)
