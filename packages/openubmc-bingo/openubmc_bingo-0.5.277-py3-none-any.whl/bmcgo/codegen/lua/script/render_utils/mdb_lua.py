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
from render_utils.utils_message_lua import UtilsMessageLua
from render_utils.validate_lua import ValidateLua
from bmcgo.codegen.lua.script.base import Base
from bmcgo.codegen.lua.script.factory import Factory


class MdbLuaUtils(Base, ValidateLua, UtilsMessageLua):
    flag_names = ['const', 'emit_change', 'emit_no_value', 'explicit']

    def __init__(self, data: dict, options: Options):
        super().__init__(data, options=options)

    @staticmethod
    def message_type(msg_type):
        if msg_type == ".google.protobuf.Empty":
            return 'nil'
        return msg_type[1:] if msg_type.startswith('.') else msg_type

    @staticmethod
    def filename(name):
        if name.endswith("/index.proto"):
            return name[:-len("/index.proto")]
        elif name.endswith(".proto"):
            return name[:-len(".proto")]
        return name

    @staticmethod
    def count(params, name):
        c = 0
        for n in params:
            if n == name:
                c += 1
        return c

    @staticmethod
    def has_path(msg):
        return 'options' in msg and 'path' in msg['options']

    @staticmethod
    def has_interface(msg):
        return 'options' in msg and 'interface' in msg['options']

    @staticmethod
    def make_methods(root, interface):
        methods = []
        if 'service' not in root:
            return methods
        for method in root['service']:
            if 'options' in method and 'service_interface' in method['options'] and \
                    method['options']['service_interface'] == interface:
                methods.append(method)
        return methods

    @staticmethod
    def has_signals(msg):
        return 'nested_type' in msg and len(msg['nested_type']) > 0

    @staticmethod
    def make_interface(msg):
        return msg['options']['interface'] if 'options' in msg and 'interface' in msg['options'] else 'bmc.mdb.object'

    @staticmethod
    def realtime(prop):
        return 'true' if 'realtime' in prop['options'] and prop['options']['realtime'] else 'false'

    @staticmethod
    def readonly_flag(prop):
        return 'true' if 'readonly' in prop['options'] and prop['options']['readonly'] else 'false'

    @staticmethod
    def get_req(msg):
        return 'nil' if msg['req'] == '.google.protobuf.Empty' else msg['req'][1:]

    @staticmethod
    def get_rsp(msg):
        return 'nil' if msg['rsp'] == '.google.protobuf.Empty' else msg['rsp'][1:]

    @staticmethod
    def get_json_req(msg):
        return 'nil' if msg['req'] == '.google.protobuf.Empty' else ('msg' + msg['req'])

    @staticmethod
    def get_json_rsp(msg):
        return 'nil' if msg['rsp'] == '.google.protobuf.Empty' else ('msg' + msg['rsp'])

    def err_module(self):
        return "apps." + Utils(self.data, self.options).camel_to_snake(self.data['package']) + ".error"

    def sig(self, msg_type):
        msg = Utils(self.data, self.options).make_get_message(msg_type)
        return "".join(
            [Utils(self.data, self.options).do_type_to_dbus(p['type'], p['repeated']) for p in msg.get('properties')])

    def cb_name(self, rpc):
        return Utils(self.data, self.options).camel_to_snake('__on' + rpc['name'])

    def rsp_message(self, rpc):
        return self.message_type(rpc['rsp'])

    def req_message(self, rpc):
        return self.message_type(rpc['req'])

    def props(self, msg_type):
        msg = Utils(self.data, self.options).make_get_message(msg_type)
        return msg.get('properties')

    def get_flags(self, prop):
        if 'options' not in prop:
            return '0'
        options = prop['options']
        result = [f"'{name.upper()}'" for name in self.flag_names if name in options and options[name]]
        if len(result) == 0:
            return 'nil'
        return f"{{{','.join(result)}}}"

    def check_duplicate(self, params):
        for name in params:
            if self.count(params, name) > 1:
                raise RuntimeError(f"重复的参数: {name}")

    def make_path(self, msg):
        path = msg['options']['path']
        params = Utils.get_path_params(self, path)
        if len(params) == 0:
            return f"'{path}'"
        result = []
        for name in params:
            s = path.partition(f':{name}')
            result.append(f"'{s[0]}'")
            result.append(name)
            path = s[2]

        return (f"{' .. '.join(result)}") if path == '' else (f"{' .. '.join(result)} .. '{path}'")

    def default(self, prop):
        if 'default' not in prop['options']:
            return 'nil'
        default_val = prop['options']['default']
        type_name = prop['type']
        if type_name == "string" or type_name == 'bytes':
            default_val = f'"{default_val}"'
        t = Utils(self.data, self.options).load_types(type_name)
        if t and ('type' in t) and t['type'] == 'Enum':
            default_val = f'{t["package"]}.{t["name"]}.' \
                          f'{Utils(self.data, self.options).enum_value_name(t["name"], default_val)}'
        return default_val

    def dependency(self, root):
        if 'dependency' in root:
            return [(pkg, self.filename(data['filename'])) for (pkg, data) in root['dependency'].items()]
        return []

    def has_msg(self, root):
        for msg in root['data']:
            if self.has_path(msg):
                return True
        return False


Factory().register("mdb.lua.mako", MdbLuaUtils)
Factory().register("mdb_interface.lua.mako", MdbLuaUtils)
