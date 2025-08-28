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

import json
from utils import Utils
from dto.options import Options
from bmcgo.codegen.lua.script.base import Base
from bmcgo.codegen.lua.script.factory import Factory


class DbLuaUtils(Base, Utils):
    TYPE_TO_DB_MAP = {
        "int8": 'IntegerField',
        'uint8': 'IntegerField',
        'int16': 'IntegerField',
        'uint16': 'IntegerField',
        'int32': 'IntegerField',
        'uint32': 'IntegerField',
        'int64': 'IntegerField',
        'uint64': 'IntegerField',
        'double': 'RealField',
        'float': 'RealField',
        'bytes': 'BolbField',
        'string': 'TextField',
        'bool': 'BooleandField',
    }

    per_type_map = {
        'PoweroffPer': 'protect_power_off',
        'ResetPer': 'protect_reset',
        'PermanentPer': 'protect_permanent',
        'TemporaryPer': 'protect_temporary',
        'PoweroffPerRetain': 'protect_power_off_retain',
        'ResetPerRetain': 'protect_reset_retain',
        'TemporaryPerRetain': 'protect_temporary_retain'
    }

    def __init__(self, data: dict, options: Options):
        super().__init__(data, options=options)

    @staticmethod
    def table_name(msg):
        if msg['type'] != 'Message' or not msg['options'] or not msg['options']['table_name']:
            return False

        return msg['options']['table_name']

    @staticmethod
    def table_max_rows(msg):
        return msg.get('type') == 'Message' and msg.get('options', {}).get('table_max_rows', False)

    @staticmethod
    def all_persistence(msg):
        if msg['type'] != 'Message' or not msg['options']:
            return 'nil'

        if 'persistence' in msg['options']:
            return msg['options']['persistence']

        if 'table_type' in msg['options']:
            if msg['options']['table_type'] in DbLuaUtils.per_type_map:
                return DbLuaUtils.per_type_map[msg['options']['table_type']]
        return 'nil'

    @staticmethod
    def check_local_per_type(root):
        per_map = {
            "PoweroffPer": False,
            "ResetPer": False,
            "TemporaryPer": False
        }
        for msg in root["data"]:
            table_type = msg["options"].get("table_type", "PoweroffPer")
            if table_type not in per_map:
                continue
            per_map[table_type] = True
        return per_map.values()

    @staticmethod
    def check_local_per_poweroff(msg):
        if "options" not in msg or "table_type" not in msg["options"]:
            return True
        return "options" in msg and "table_type" in msg["options"] and msg["options"]["table_type"] == "PoweroffPer"

    @staticmethod
    def check_local_per_reset(msg):
        return "options" in msg and "table_type" in msg["options"] and msg["options"]["table_type"] == "ResetPer"

    @staticmethod
    def check_local_per_temporary(msg):
        return "options" in msg and "table_type" in msg["options"] and msg["options"]["table_type"] == "TemporaryPer"

    @staticmethod
    def column_max_len(prop):
        if prop['repeated']:
            return 0
        type_name = prop['type']
        if type_name == "int8" or type_name == 'uint8':
            return 8
        if type_name == "int16" or type_name == 'uint16':
            return 16
        if type_name == "int32" or type_name == 'uint32':
            return 32
        if type_name == "int64" or type_name == 'uint64':
            return 64
        if 'max_len' in prop['options']:
            return prop['options']['max_len']
        return 0

    @staticmethod
    def unique(prop):
        if 'unique' not in prop['options']:
            return ''
        return f':unique()'

    @staticmethod
    def primary_key(prop):
        if 'primary_key' not in prop['options']:
            return ''
        return f':primary_key()'

    @staticmethod
    def persistence_key(prop):
        if 'persistence_ex' in prop['options']:
            val = prop['options']['persistence_ex']
            return f':persistence_key("{val}")'

        if 'usage' not in prop['options']:
            return ''
        val = ''
        for use_type in prop['options']['usage']:
            if use_type in DbLuaUtils.per_type_map:
                val = DbLuaUtils.per_type_map[use_type]
                break
        if val == '':
            return ''

        return f':persistence_key("{val}")'

    @staticmethod
    def allow_null(prop):
        if prop['options'].get('allow_null', False):
            return ':null()'
        return ''

    @staticmethod
    def extend_field(prop):
        if prop['options'].get('extend_field', False):
            return ':extend_field()'
        return ''

    @staticmethod
    def deprecated(prop):
        if prop['options'].get('deprecated', False):
            return ':deprecated()'
        return ''

    @staticmethod
    def critical(prop):
        if prop['options'].get('critical', False):
            return ':critical()'
        return ''

    def column_type(self, prop):
        type_name = prop['type']
        if type_name in self.TYPE_TO_DB_MAP:
            if prop['repeated']:
                return "JsonField()"
            else:
                return self.TYPE_TO_DB_MAP[type_name] + "()"
        types = Utils(self.data, self.options).load_types(type_name)
        if types and ('type' in types) and types['type'] == 'Enum':
            return f'EnumField({types["package"]}.{types["name"]})'
        return "JsonField()"

    def max_len(self, prop):
        num = self.column_max_len(prop)
        if num == 0:
            return ''
        return f':max_length({num})'

    def default(self, class_name, prop):
        if 'default' not in prop['options']:
            return ''
        return f':default({self._convert_default_value(class_name, prop)})'

    def _convert_default_value(self, class_name, prop):
        d_val = prop['options']['default']
        type_name = prop['type']
        types = Utils(self.data, self.options).load_types(type_name)
        if types and ('type' in types) and types['type'] == 'Enum':
            if isinstance(d_val, list):
                result = "{"
                for val in d_val:
                    enum_type = Utils(self.data, self.options).enum_value_name(types["name"], val)
                    result += f'{types["package"]}.{types["name"]}.{enum_type},'
                return result + "}"
            value_name = Utils(self.data, self.options).enum_value_name(types["name"], d_val)
            return f'{types["package"]}.{types["name"]}.{value_name}'
        if Utils.get_lua_codegen_version() >= 10:
            if prop.get('repeated') and not isinstance(d_val, list):
                raise RuntimeError(f"model.json中类{class_name}的属性{prop['name']}默认值{d_val}类型与属性类型不一致")
            if isinstance(d_val, list) or isinstance(d_val, dict):
                json_str = json.dumps(d_val).replace("'", "''")
                return f"[['{json_str}']]"
        if type_name == "string" or type_name == 'bytes':
            return f'"\'{d_val}\'"'
        if type_name == "bool":
            return str(bool(d_val)).lower()
        return d_val


Factory().register("db.lua.mako", DbLuaUtils)
Factory().register("local_db.lua.mako", DbLuaUtils)
Factory().register("orm_classes.lua.mako", DbLuaUtils)
