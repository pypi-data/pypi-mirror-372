#!/usr/bin/env python3
# coding=utf-8
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
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
from bmcgo.codegen.lua.script.dto.options import Options
from bmcgo.codegen.lua.script.base import Base
from bmcgo.codegen.lua.script.factory import Factory


BASE_TYPE = "baseType"
ITEMS = "items"
NON_CONVERT_ITEMS = ["validator", "req_type", "rsp_type", "feature", "default_value", "read", "write"]
FILTERED_ITEMS = ["description", "$ref", "default", "items", "req", "rsp", "featureTag", "privilege"]
PERSIST_TYPES = {
    "PermanentPer", "PoweroffPer", "ResetPer", "TemporaryPer", "PoweroffPerRetain",
    "ResetPerRetain", "TemporaryPerRetain", "Memory"
}
OBJECT_PROPERTIES_INTERFACE = "bmc.kepler.Object.Properties"


class ConsistencyModelLuaUtils(Base, Utils):

    def __init__(self, data: dict, options: Options):
        super().__init__(data, options=options)

    @staticmethod
    def has_path(msg):
        return 'path' in msg

    @staticmethod
    def has_properties(msg):
        return 'properties' in msg

    @staticmethod
    def has_interfaces(msg):
        return 'interfaces' in msg

    @staticmethod
    def has_methods(msg):
        return 'methods' in msg

    @staticmethod
    def has_signals(msg):
        return 'signals' in msg

    @staticmethod
    def has_table_name(msg):
        return 'tableName' in msg

    @staticmethod
    def has_parent(msg):
        return 'parent' in msg

    @staticmethod
    def is_enum_array(prop_config):
        return prop_config[BASE_TYPE] == 'Array' and ITEMS in prop_config and BASE_TYPE in prop_config[ITEMS] \
            and prop_config[ITEMS][BASE_TYPE] == 'Enum'

    @staticmethod
    def combine_privileges(privileges):
        prefix = "privilege."
        return prefix + (" | " + prefix).join(sorted(privileges))
    
    @staticmethod
    def prop_contains_persist_type(prop_config: dict):
        return bool(set(prop_config.get("usage", [])) & PERSIST_TYPES)

    def class_has_block_io(self, msg):
        if self.has_path(msg):
            for (interface, _) in msg['interfaces'].items():
                if interface == 'bmc.kepler.Chip.BlockIO':
                    return True
        return False

    def has_block_io(self, root):
        for (_, msg) in root.items():
            if self.class_has_block_io(msg):
                return True
        return False

    def convert_dict_to_lua_table(self, msg):
        string = '{\n'
        i = 1
        for (prop, value) in msg.items():
            if prop in FILTERED_ITEMS:
                continue
            if prop == "pattern":
                string += f"['{prop}'] = [=[{value}]=],\n"
            elif prop == "privilege_value" and isinstance(value, str):
                string += f"['{prop}'] = {value},\n"
            elif prop in NON_CONVERT_ITEMS:
                string += f"['{prop}'] = {value},\n"
            else:
                string += f"['{prop}'] = " + self.convert_to_lua(value) + ",\n"
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
        raise Exception("无效值类型")

    def get_enum_value(self, ref, enum_type):
        if ref.startswith("types.json"):
            return "types." + ref.replace("types.json#/defs/", "") + "." + enum_type
        elif ref.startswith("mdb://"):
            spices = ref.split(".json#")
            return self.get_intf_type(Utils.get_unique_intf_name(spices[0].replace("/", "."))) + "." + \
                spices[1].replace("/defs/", "") + "." + enum_type
        raise Exception("枚举引用定义错误")

    def get_prop_default_value(self, class_name, prop, prop_config):
        if 'default' not in prop_config:
            if BASE_TYPE in prop_config and prop_config[BASE_TYPE] == 'Enum':
                return self.get_class_type(class_name) + "." + prop + ".default[1]:value()"
            else:
                return self.get_class_type(class_name) + "." + prop + ".default[1]"

        default = prop_config['default']
        if 'baseType' not in prop_config:
            return self.convert_to_lua(default)

        if prop_config[BASE_TYPE] == 'Enum':
            return self.get_enum_value(prop_config["$ref"], default) + ":value()"
        elif self.is_enum_array(prop_config):
            result = "{"
            for enum_type in default:
                result += self.get_enum_value(prop_config[ITEMS]["$ref"], enum_type) + ":value(),"
            return result + "}"

        return self.convert_to_lua(default)

    def get_mdb_prop_default_value(self, intf_name, prop, prop_config):
        pkg_name = self.get_intf_type(intf_name) + "."
        if 'default' not in prop_config:
            if BASE_TYPE in prop_config and prop_config[BASE_TYPE] == 'Enum':
                return pkg_name + prop + ".default[1]:value()"
            else:
                return pkg_name + prop + ".default[1]"

        default = prop_config['default']
        if 'baseType' not in prop_config:
            return self.convert_to_lua(default)

        if prop_config[BASE_TYPE] == 'Enum':
            return pkg_name + \
                prop_config["$ref"].replace("#/defs/", "") + "." + default + ":value()"
        elif self.is_enum_array(prop_config):
            result = "{"
            for enum_type in default:
                result += pkg_name + prop_config[ITEMS]["$ref"].replace("#/defs/", "") + "." + enum_type + ":value(),"
            return result + "}"

        return self.convert_to_lua(default)

    def get_path(self, root, msg):
        if not self.has_path(msg):
            return ''
        if not self.has_parent(msg):
            return msg['path']
        return msg['path'].replace(':parent/', self.get_path(root, root[msg['parent']]) + ':parent/')

    def is_enable_orm(self, msg):
        if "tableName" not in msg:
            return False

        if "tableLocation" in msg and msg["tableLocation"] == "Local":
            return False

        if "tableType" in msg:
            return True

        for _, prop_config in msg.get('properties', {}).items():
            if self.prop_contains_persist_type(prop_config):
                return True

        for intf_data in msg.get('interfaces', {}).values():
            for _, prop_config in intf_data.get('properties', {}).items():
                if self.prop_contains_persist_type(prop_config):
                    return True

        return False

    def convert_dynamic_params(self, msg):
        match_obj = re.search("\$\{(.+?)\}", msg)
        if match_obj is None:
            return msg

        return self.convert_dynamic_params(re.sub('\$\{(.+?)\}', ':' + match_obj.group(1), msg, 1))

    def get_primary_key(self, msg):
        if self.has_properties(msg):
            for (prop, prop_config) in msg['properties'].items():
                if "primaryKey" in prop_config:
                    return self.convert_to_lua({"field": prop, BASE_TYPE: prop_config.get('baseType')})

        if 'interfaces' not in msg:
            return {}

        for (_, intf_msg) in msg['interfaces'].items():
            if not self.has_properties(intf_msg):
                continue
            for (prop, prop_config) in intf_msg['properties'].items():
                if "primaryKey" not in prop_config:
                    continue
                result = {"field": prop_config.get("alias", prop), BASE_TYPE: prop_config.get('baseType')}
                return self.convert_to_lua(result)

        return {}

    def has_prop_configs(self, msg):
        return self.has_properties(msg)

    def get_prop_configs(self, class_name, msg):
        for (prop, prop_config) in msg['properties'].items():
            prop_config["default_value"] = self.get_prop_default_value(class_name, prop, prop_config)
            prop_config["validator"] = self.get_class_type(class_name) + "." + prop
        return self.convert_to_lua(msg['properties'])

    def get_default_props(self, class_name, msg):
        string = '{'
        for (prop, prop_config) in msg['properties'].items():
            string += "['" + str(prop) + "'] = " + \
                str(self.get_prop_default_value(class_name, prop, prop_config)) + ","

        return string + '}'

    def has_mdb_prop_configs(self, msg):
        if not self.has_path(msg):
            return False

        for (_, intf_msg) in msg['interfaces'].items():
            if self.has_properties(intf_msg):
                return True

        return False

    def get_mdb_prop_configs(self, msg):
        string = '{'
        path_privilege = msg.get("privilege", [])
        for (interface, intf_msg) in msg['interfaces'].items():
            if not self.has_properties(intf_msg):
                continue
            interface_privilege = intf_msg.get("privilege", [])
            intf_name = self.get_intf_name(interface, intf_msg)
            for (prop, prop_config) in intf_msg['properties'].items():
                prop_config["default_value"] = self.get_mdb_prop_default_value(intf_name, prop, prop_config)
                prop_config["validator"] = f"{self.get_intf_type(intf_name)}.{prop}"
                property_read_privilege = prop_config.get("privilege", {}).get("read", [])
                property_write_privilege = prop_config.get("privilege", {}).get("write", [])
                r = list(set(path_privilege + interface_privilege + property_read_privilege))
                w = list(set(path_privilege + interface_privilege + property_write_privilege))
                if r or w:
                    prop_config["privilege_value"] = {"read": self.combine_privileges(r),
                                                      "write": self.combine_privileges(w)}
            string += f"['{interface}'] = {self.convert_to_lua(intf_msg['properties'])},"

        return string + '}'

    def convert_methods(self, methods):
        result = {}
        for (method, method_config) in methods.items():
            result[method] = {}
            for (body, params) in method_config.items():
                if body != 'req' and body != 'rsp':
                    result[method][body] = params
                    continue
                result[method][body] = []
                for (param, param_config) in params.items():
                    param_config["param"] = param
                    result[method][body].append(param_config)
        return result

    def convert_signals(self, signals):
        result = {}
        for (signal, signal_config) in signals.items():
            result[signal] = []
            for (param, param_config) in signal_config.items():
                param_config["param"] = param
                result[signal].append(param_config)
        return result

    def has_mdb_method_configs(self, msg):
        if not self.has_path(msg):
            return False

        for (intf_name, intf_msg) in msg['interfaces'].items():
            if intf_name == OBJECT_PROPERTIES_INTERFACE:
                continue
            if self.has_methods(intf_msg):
                return True

        return False

    def has_private_method_configs(self, msg):
        return self.has_methods(msg)

    def fill_method_validator(self, msg_type, methods, privileges):
        for method, method_config in methods.items():
            method_privilege = method_config.get("privilege", [])
            p = list(set(privileges + method_privilege))
            if p:
                method_config["privilege_value"] = self.combine_privileges(p)
            if "featureTag" in method_config:
                method_config["feature"] = method_config["featureTag"]
            method_config["req_type"] = msg_type + "." + method + "Req"
            method_config["rsp_type"] = msg_type + "." + method + "Rsp"

    def get_mdb_method_configs(self, msg):
        string = '{'
        path_privilege = msg.get("privilege", [])
        for (interface, intf_msg) in msg['interfaces'].items():
            if interface == OBJECT_PROPERTIES_INTERFACE:
                continue
            interface_privilege = intf_msg.get("privilege", [])
            if self.has_methods(intf_msg):
                intf_name = self.get_intf_name(interface, intf_msg)
                self.fill_method_validator(self.get_intf_type(intf_name), intf_msg["methods"],
                                            list(set(path_privilege + interface_privilege)))
                methods = self.convert_methods(intf_msg['methods'])
                string += "['" + str(interface) + "'] = " + self.convert_to_lua(methods) + ","
        return string + '}'

    def get_private_method_configs(self, class_name, msg):
        self.fill_method_validator(self.get_class_type(class_name), msg['methods'], [])
        methods = self.convert_methods(msg["methods"])
        return self.convert_to_lua(methods)

    def has_mdb_signal_configs(self, msg):
        if not self.has_path(msg):
            return False

        for (intf_name, intf_msg) in msg['interfaces'].items():
            if intf_name == OBJECT_PROPERTIES_INTERFACE:
                continue
            if self.has_signals(intf_msg):
                return True

        return False

    def get_mdb_signal_configs(self, msg):
        string = '{'
        for (interface, intf_msg) in msg['interfaces'].items():
            if self.has_signals(intf_msg):
                signals = self.convert_signals(intf_msg['signals'])
                string += "['" + str(interface) + "'] = " + self.convert_to_lua(signals) + ","

        return string + '}'

    def has_alias(self, msg):    
        if not self.has_path(msg):
            return False

        for (_, intf_msg) in msg['interfaces'].items():
            if not self.has_properties(intf_msg):
                continue

            for (_, prop_config) in intf_msg['properties'].items():
                if 'alias' in prop_config:
                    return True

        return False

    def get_alias_map(self, msg):
        result = {}
        for (interface, intf_msg) in msg['interfaces'].items():
            if not self.has_properties(intf_msg):
                continue

            for (prop, prop_config) in intf_msg['properties'].items():
                if 'alias' in prop_config:
                    result[prop_config['alias']] = {"original_name": prop, "interface": interface}

        return self.convert_to_lua(result)

    def get_full_path(self, root, msg):
        return self.convert_to_lua(self.deduplicate_path(self.convert_dynamic_params(self.get_path(root, msg))))

    def get_interface_types(self, msg):
        string = "{"
        for (interface, intf_msg) in msg["interfaces"].items():
            intf_name = self.get_intf_name(interface, intf_msg)
            string += f"['{interface}'] = {self.get_intf_type(intf_name)},"
        return string + "}"

    def get_intf_name(self, interface, intf_msg):
        slices = interface.split(".")
        if "implement" in intf_msg:
            return slices[-2] + slices[-1]
        return Utils.get_unique_intf_name(interface)

    def get_property_privilege(self, config):
        result = {}
        if 'privilege' not in config:
            return result

        for item, privileges in config['privilege'].items():
            privilege = []
            for priv in privileges:
                privilege.append('privilege.' + priv)

            result[item] = " | ".join(privilege)

        return result

    def get_class_type(self, class_name):
        return Utils.camel_to_snake(class_name) + '_class_types'

    def get_class_types(self, project_name, root):
        types = {}
        for (class_name, msg) in root.items():
            if not msg.get('properties', {}) and not msg.get('methods', {}):
                continue

            if msg.get('properties', {}):
                if any(('default' in prop_config and prop_config.get(BASE_TYPE, {}) == 'Enum' and \
                    prop_config["$ref"].startswith("types.json")) for prop_config in msg['properties'].values()):
                    type_json_type = 'types'
                    types[type_json_type] = f"local {type_json_type} = require 'class.types.types'\n"

            c_type = self.get_class_type(class_name)
            if project_name != 'dft' and project_name != 'debug':
                types[c_type] = f"local {c_type} = require 'class.types.{class_name}'\n"
            else:
                types[c_type] = f"local {c_type} = require '{project_name}.class.types.{class_name}'\n"
        return types

    def get_intf_type(self, intf_name):
        return Utils.camel_to_snake(intf_name) + '_intf_types'

    def get_intf_types(self, project_name, root):
        types = {}
        for (_, msg) in root.items():
            for (interface, intf_msg) in msg.get('interfaces', {}).items():
                intf_name = self.get_intf_name(interface, intf_msg)
                intf_type = self.get_intf_type(intf_name)
                types[intf_type] = f"local {intf_type} = require '{project_name}.json_types.{intf_name}'\n"
        return types

    def render_types(self, project_name, root):
        types = {}
        types.update(self.get_class_types(project_name, root))
        types.update(self.get_intf_types(project_name, root))

        string = ''
        for _, value in types.items():
            string += value
        return string

    def collect_features(self, intf_msg, features):
        for method_config in intf_msg.get('methods', {}).values():
            if "featureTag" in method_config:
                features.add(method_config["featureTag"])

    def get_features(self, root):
        features = set()
        if "private" in root:
            self.collect_features(root["private"], features)
        for msg in root.values():
            for intf_msg in msg.get('interfaces', {}).values():
                self.collect_features(intf_msg, features)
        return sorted(list(features))

Factory().register("v1/templates/apps/model.lua.mako", ConsistencyModelLuaUtils)
