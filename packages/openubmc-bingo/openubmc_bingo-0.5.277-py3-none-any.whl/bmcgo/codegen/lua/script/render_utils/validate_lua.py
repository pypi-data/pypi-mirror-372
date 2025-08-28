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


class ValidateLua(Utils):
    readonly_fields = {
        "odata_context",
        "odata_etag",
        "odata_id",
        "odata_type",
        "Actions",
        "Links",
    }
    validate_need_readonly = {"Required", "Optional", "RequiredArray", "OptionalArray"}
    type_default = {
        "uint8" : "0",
        "int8" : "0",
        "int16" : "0",
        "uint16" : "0",
        "int32" : "0",
        "uint32" : "0",
        "uint64" : "0",
        "int64" : "0",
        "string" : "''",
        "bytes" : "''",
        "float" : "0",
        "double" : "0",
        "bool" : "false"
    }

    @staticmethod
    def is_required(prop):
        options = prop["options"]
        return ("allow_null" not in options) or not options["allow_null"]

    @staticmethod
    def format_param(vv):
        result = []
        for p in vv[1]:
            if isinstance(p, str):
                if vv[0] == "regex":
                    result.append('[=[{}]=]'.format(p))
                else:
                    result.append('"{}"'.format(p))
            else:
                result.append("nil" if p is None else str(p))

        if vv[0] == "enum":
            return "Enum", ["'', {" + ", ".join(result) + "}"]
        return vv[0], result

    @staticmethod
    def proper_name(name, prefix):
        if not prefix:
            return name
        return prefix + name

    @staticmethod
    def validate_name(name, prefix):
        if not prefix:
            return f"'{name}'"
        return f"{prefix} .. '{name}'"

    def get_struct_require(self, prop):
        prop_type = prop["type"]
        if not Utils(self.data, self.options).is_base_type(prop_type) and prop_type != 'Enum':
            return {"type": prop_type, "repeated": prop["repeated"]}
        return {}

    def get_no_struct_require(self, prop):
        prop_type = prop["type"]
        params = [f'"{prop_type}"']
        if not Utils(self.data, self.options).is_base_type(prop_type) and prop_type != 'Enum':
            return []

        if self.is_required(prop):
            val = "RequiredArray" if prop["repeated"] else "Required"
        else:
            val = "OptionalArray" if prop["repeated"] else "Optional"
        return [[val, params]]

    def get_struct_requires(self, msg):
        result = {}
        if "properties" not in msg:
            return result

        for prop in msg["properties"]:
            prop_type = prop["type"]
            if not Utils(self.data, self.options).is_base_type(prop_type) and prop_type != 'Enum':
                result[prop["name"]] = {"type": prop_type, "repeated": prop["repeated"]}
        return result

    def get_no_struct_requires(self, msg):
        if "properties" not in msg:
            return []

        result = []
        for prop in msg["properties"]:
            prop_type = prop["type"]
            params = [f'"{prop_type}"']
            if not Utils(self.data, self.options).is_base_type(prop_type) and prop_type != 'Enum':
                continue

            if self.is_required(prop):
                val = "RequiredArray" if prop["repeated"] else "Required"
            else:
                val = "OptionalArray" if prop["repeated"] else "Optional"
            result.append((prop, [[val, params]]))

        return result

    def params1(self, var, msg):
        if msg["type"] == "Dictionary":
            return var

        paras = []
        if "properties" in msg:
            for p in msg["properties"]:
                paras.append(var + "." + p["name"])
        return ", ".join(paras)

    def get_requires(self, msg):
        if "properties" not in msg:
            return []

        result = []
        for prop in msg["properties"]:
            prop_type = prop["type"]
            params = [f'"{prop_type}"']

            if self.is_required(prop):
                val = "RequiredArray" if prop["repeated"] else "Required"
            else:
                val = "OptionalArray" if prop["repeated"] else "Optional"
            result.append((prop, [[val, params]]))

        return result

    def get_descriptions(self, msg, intf_name):
        pattern = r'^bmc\..*\.(Debug|Release)\..*$'
        if not re.match(pattern, intf_name):
            return ''

        if "properties" not in msg:
            return ''

        count = 0
        has_description = False
        name = msg['name']
        result = f'T{name}.descriptions = {{'
        for prop in msg["properties"]:
            if count != 0:
                result += ", "
            count += 1
            if "description" in prop:
                has_description = True
                result += '[=[' + prop["description"] + ']=]'
            else:
                result += "nil"

        return (result + '}') if has_description else ''

    def get_default(self, required, type_str):
        type_str = type_str.replace('"', '')
        match_obj = re.search("(.+?)\[\]", type_str)
        if match_obj is not None:
            type_str = match_obj.group(1)
        if type_str in self.type_default:
            type_default = self.type_default[type_str]
            return ("{}") if "Array" in required else type_default
        return ("{}") if "Array" in required else (type_str + '.default')

    def is_array(self, required):
        return "true" if "Array" in required else "false"

    def get_struct(self, type_str):
        type_str = type_str.replace('"', '')
        match_obj = re.search("(.+?)\[\]", type_str)
        if match_obj is not None:
            type_str = match_obj.group(1)
        if type_str in self.type_default:
            return "nil"
        return type_str + ".struct"

    def get_validates(self, msg):
        if "properties" not in msg:
            return []

        result = []
        for prop in msg["properties"]:
            if "validate" not in prop["options"]:
                continue

            opt_validate = Utils(self.data, self.options).get_validate(
                prop["options"]["validate"]
            )

            prop_result = [self.format_param(v) for v in opt_validate]
            result.append((prop, prop_result))
        return result

    def readonly(self, validate_type, field, types, options):
        if validate_type not in self.validate_need_readonly:
            return ""
        if field in self.readonly_fields or "Resource." in types:
            return ", true"
        if "readonly" in options:
            return ", true"
        return ", false"
