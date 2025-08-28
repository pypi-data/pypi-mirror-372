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


class UtilsMessageLua(Utils):

    @staticmethod
    def params(msg):
        return ", ".join([p.get('original_name', p['name']) for p in msg['properties']])

    @staticmethod
    def get_group_names(names):
        return ', '.join([f"'{name}'" for name in names])

    @staticmethod
    def get_group_names_for_set(names):
        return ', '.join([f"{name}" for name in names])

    @staticmethod
    def get_group_names_for_join(names):
        return ', '.join([f"body.{name}" for name in names])

    @staticmethod
    def construct_rename(prop, option_name):
        return prop.get('original_name', prop['name']), prop['options'][option_name]

    @staticmethod
    def construct_group(prop, groups):
        group_id = prop['options']['group']
        if group_id in groups:
            groups[group_id].append(prop['name'])
        else:
            groups[group_id] = [prop['name']]

    def json_to_lua_value(self, val):
        if isinstance(val, str):
            return f'[=[{val}]=]'
        if isinstance(val, bool):
            return 'true' if val else 'false'
        if isinstance(val, list):
            result = '{'
            for value in val:
                result += f"{self.json_to_lua_value(value)},"
            return result + '}'
        if isinstance(val, int) or isinstance(val, float):
            return str(val)
        if isinstance(val, dict):
            return self.convert_dict_to_lua_table(val)
        return val

    def with_default(self, p):
        if 'options' in p and 'default' in p['options']:
            default = p['options']['default']
            if "is_enum" not in p or not p["is_enum"]:
                if p['type'] == 'bool' and default:
                    return f"{p.get('original_name', p['name'])} == nil and true or \
                        obj.{p.get('original_name', p['name'])}"
                else:
                    return f"{p.get('original_name', p['name'])} or {self.json_to_lua_value(default)}"

            if p["repeated"]:
                result = f"{p.get('original_name', p['name'])} or {{"
                for default_var in default:
                    result += f"{p['type']}.{default_var},"
                return result + "}"
            else:
                return f"{p.get('original_name', p['name'])} or {p['type']}.{default}"
        else:
            return p.get('original_name', p['name'])

    def obj_construct(self, msg):
        return "\n  ".join([f"self.{p.get('original_name', p['name'])} = \
            obj.{self.with_default(p)}" for p in msg['properties']])

    def remove_props_construct(self, msg):
        return "\n  ".join(
            [f"if errs.{p['name']} then obj.{self.with_default(p)} = nil end" for p in msg['properties']])

    def unpack_prop_name(self, p):
        if Utils(self.data, self.options).check_is_enum(p['type']):
            return f"{p.get('original_name', p['name'])}"
        elif Utils(self.data, self.options).check_is_message(self.data, p['type']):
            if 'repeated' in p and p['repeated']:
                return f"utils.unpack(raw, self.{p.get('original_name', p['name'])}, true)"
            else:
                return f"utils.unpack(raw, self.{p.get('original_name', p['name'])})"
        return f"self.{p.get('original_name', p['name'])}"

    def unpack(self, msg):
        return ", ".join([self.unpack_prop_name(p) for p in msg['properties']])

    def get_enums(self, msg, ):
        return [p for p in msg['properties'] if Utils(self.data, self.options).check_is_enum(p['type'])]

    def get_sub_type(self, msg):
        return [p for p in msg['properties'] if Utils(self.data, self.options).check_is_message(self.data, p['type'])]

    def get_rename_fields(self, msg):
        return [self.construct_rename(prop, 'rename')
                for prop in msg['properties']
                if 'options' in prop and 'rename' in prop['options']]

    def get_group_fields(self, msg):
        groups = {}
        [self.construct_group(prop, groups)
         for prop in msg['properties']
         if 'options' in prop and 'group' in prop['options']]
        return groups

    def get_groups(self, msg):
        return ',\n    '.join(['{' + self.get_group_names(v) + "}" for v in self.get_group_fields(msg).values()])

    def is_routes(self, file):
        return file.find("routes/") != -1
