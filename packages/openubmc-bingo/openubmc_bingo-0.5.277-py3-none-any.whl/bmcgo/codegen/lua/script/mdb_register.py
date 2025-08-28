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


class MdbRegister:
    JSON_TYPE_TO_LUA = {
        "S8": "integer",
        "U8": "integer",
        "S16": "integer",
        "U16": "integer",
        "S32": "integer",
        "U32": "integer",
        "S64": "integer",
        "U64": "integer",
        "Double": "number",
        "String": "string",
        "Boolean": "boolean",
        "Array": "message",
        "Binary": "string"
    }

    JSON_TYPE_TO_DBUS = {
        "S8": "y",
        "U8": "y",
        "S16": "n",
        "U16": "q",
        "S32": "i",
        "U32": "u",
        "S64": "x",
        "U64": "t",
        "Double": "d",
        "String": "s",
        "Boolean": "b",
        "Binary": "ay"
    }

    @staticmethod
    def transform_types(prop_data, trans_map):
        if isinstance(prop_data, int):
            return False, 'i'
        elif isinstance(prop_data, str):
            return False, 's'
        if "baseType" in prop_data:
            if prop_data["baseType"] == "Struct" or prop_data["baseType"] == "Enum" \
                or prop_data["baseType"] == "Dictionary":
                return False, prop_data["$ref"].replace("#/defs/", "")
            elif prop_data["baseType"] == "Array":
                return True, prop_data["items"]["$ref"].replace("#/defs/", "")
            elif prop_data["baseType"].endswith("[]"):
                return True, trans_map[prop_data["baseType"][0:-2]]
            else:
                return False, trans_map[prop_data["baseType"]]
        return False, prop_data["$ref"].replace("#/defs/", "")

    @staticmethod
    def readonly_json(prop_data):
        return str(prop_data.get("readOnly", False)).lower()

    @staticmethod
    def get_name(intf):
        intfs = intf.split(".")
        if intfs[-1] == "Default":
            return intfs[-2] + intfs[-1]
        return intfs[-1]

    @staticmethod
    def force_to_colon(path):
        return path.replace("${", ":").replace("}", "")

    @staticmethod
    def get_method_description(intf_name, method_data):
        pattern = r'^bmc\..*\.(Debug|Release)\..*$'
        if not re.match(pattern, intf_name):
            return ""
        if "displayDescription" in method_data:
            return ', [=[' + method_data["displayDescription"] + ']=]'
        return ""

    def recover_path(self, class_name, class_require):
        class_data = class_require[class_name]
        path = self.force_to_colon(class_data['path'])
        if 'parent' not in class_data['data']:
            return path
        return path.replace(':parent/', self.recover_path(class_data['data']['parent'], class_require) + ':parent/')

    def get_path(self, class_name, class_require):
        path = self.recover_path(class_name, class_require)
        return Utils.deduplicate_path(self, path)

    def is_dbus_base_type(self, name):
        return name in self.JSON_TYPE_TO_DBUS.values()

    def get_types_in_defs(self, defs, struct):
        is_dict = False
        if "key" in defs[struct] and "value" in defs[struct]:
            is_dict = True
        dbus_types = "a{" if is_dict else "("
        for prop in defs[struct].values():
            if isinstance(prop, int):
                return 'i'
            elif isinstance(prop, str):
                return 's'
            repeated, dbus_type = self.transform_types(
                prop, self.JSON_TYPE_TO_DBUS)
            dbus_types += "a" if repeated else ""
            dbus_types += (
                dbus_type
                if self.is_dbus_base_type(dbus_type)
                else self.get_types_in_defs(defs, dbus_type)
            )

        return dbus_types + ("}" if is_dict else ")")

    def do_type_to_lua_json(self, prop_data):
        repeated, lua_type = self.transform_types(
            prop_data, self.JSON_TYPE_TO_LUA)
        return lua_type + "[]" if repeated else lua_type

    def do_type_to_dbus_json(self, root, prop):
        dbus_types = ""
        repeated, dbus_type = self.transform_types(
            prop, self.JSON_TYPE_TO_DBUS)
        dbus_types += "a" if repeated else ""
        dbus_types += (
            dbus_type
            if self.is_dbus_base_type(dbus_type)
            else self.get_types_in_defs(root["defs"], dbus_type)
        )
        return dbus_types

    def do_types_to_dbus_json(self, root, struct_data, name):
        dbus_types = ""
        if name not in struct_data:
            return dbus_types

        for prop in struct_data[name].values():
            repeated, dbus_type = self.transform_types(
                prop, self.JSON_TYPE_TO_DBUS)
            dbus_types += "a" if repeated else ""
            dbus_types += (
                dbus_type
                if self.is_dbus_base_type(dbus_type)
                else self.get_types_in_defs(root["defs"], dbus_type)
            )
        return dbus_types

    def convert_dict_to_lua_table(self, msg, ):
        string = '{\n'
        i = 1
        for (prop, value) in msg.items():
            if prop == "pattern":
                string += "['" + prop + "'] = [=[" + value + "]=],\n"
            elif prop == "validator":
                string += "['" + prop + "'] = " + value + ",\n"
            else:
                string += "['" + prop + "'] = " + \
                    self.convert_to_lua(value) + ",\n"
            i += 1
        return string + '}'

    def convert_to_lua(self, value):
        if isinstance(value, str):
            return "'" + value + "'"
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, int) or isinstance(value, float):
            return str(value)
        elif isinstance(value, dict):
            return self.convert_dict_to_lua_table(value)
        elif isinstance(value, list):
            string = "{"
            for val in value:
                string += self.convert_to_lua(val) + ","
            string += "}"
            return string
        raise Exception("值类型无效")

    def default_json(self, prop_data):
        if 'default' not in prop_data:
            return 'nil'

        default_val = prop_data['default']

        if 'baseType' not in prop_data:
            return self.convert_to_lua(default_val)

        if prop_data['baseType'] == 'Enum':
            return 'utils.unpack_enum(true, E' + prop_data['$ref'].replace('#/defs/', '') + "." + default_val + ")"

        if prop_data['baseType'] == 'Array' and \
            'baseType' in prop_data['items'] and prop_data['items']['baseType'] == 'Enum':
            result = []
            for default in default_val:
                result.append('utils.unpack_enum(true, E' +
                              prop_data['items']['$ref'].replace('#/defs/', '') + "." + default + ")")
            return '{' + ",".join(result) + '}'

        return self.convert_to_lua(default_val)

    def options_json(self, prop_data):
        if 'options' not in prop_data:
            return 'nil'
        return self.convert_to_lua(prop_data['options'])
