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

from utils import Utils
from dto.options import Options
from bmcgo.codegen.lua.script.mdb_register import MdbRegister
from bmcgo.codegen.lua.script.base import Base
from bmcgo.codegen.lua.script.factory import Factory


class ClientLuaUtils(Base, Utils, MdbRegister):
    def __init__(self, data: dict, options: Options):
        super().__init__(data, options=options)

    @staticmethod
    def message_type(t):
        if t == ".google.protobuf.Empty":
            return 'nil'
        return t[1:] if t.startswith('.') else t

    def sig(self, msg_type):
        msg = Utils(self.data, self.options).make_get_message(msg_type)
        return "".join(
            [Utils(self.data, self.options).do_type_to_dbus(p['type'], p['repeated']) for p in msg.get('properties')])

    def props(self, msg_type):
        msg = Utils(self.data, self.options).make_get_message(msg_type)
        return msg.get('properties')

    def params(self, msg_type):
        return ", ".join([p['name'] for p in self.props(msg_type)])

    def cb_name(self, rpc):
        return Utils(self.data, self.options).camel_to_snake('__On' + rpc['name'])

    def rsp_message(self, rpc):
        return self.message_type(rpc['rsp'])

    def req_message(self, rpc):
        return self.message_type(rpc['req'])

    def make_path_with_params(self, path):
        path = self.force_to_colon(path)
        params = self.get_path_params(path)
        if not params:
            return f"'{path}'"
        result = []
        for name in params:
            parts = path.partition(f':{name}')
            result.append(f"'{parts[0]}'")
            result.append(f"path_params['{name}']")
            path = parts[2]
        ret = ' .. '.join(result)
        if path:
            ret += f" .. '{path}'"
        return ret

    def get_path_arg(self, path, with_comma=True):
        if not self.get_path_params(path):
            return ""
        if with_comma:
            return ", path_params"
        return "path_params"

    def get_dep_properties(self, properties):
        if properties == ["*"]:
            return ""

        return ', {"' + '", "'.join(properties) + '"}'

    def get_path_namespace(self, path):
        if not self.get_path_params(path):
            return f"'{path}'"
        path_with_params = self.make_path_with_params(path)
        if Utils.get_lua_codegen_version() >= 17:
            return f"path_params and ({path_with_params}) or '{path}'"
        prefix = path_with_params.split("/' ..")[0]
        return f"path_params and ({path_with_params}) or {prefix}'"

    def get_path_patterns(self, paths):
        return MdbRegister.convert_to_lua(self, paths)

    def get_object_path(self, path):
        if not self.get_path_params(path):
            return f"'{path}'"
        path_with_params = self.make_path_with_params(path)
        return f"path_params and ({path_with_params}) or '{path}'"

Factory().register("client.lua.mako", ClientLuaUtils)
