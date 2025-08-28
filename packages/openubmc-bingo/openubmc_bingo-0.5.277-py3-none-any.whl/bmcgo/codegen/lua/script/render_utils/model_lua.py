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


BASE_TYPE = "baseType"
ITEMS = "items"


class ModelLuaUtils(Base, Utils):

    def __init__(self, data: dict, options: Options):
        super().__init__(data, options=options)

    @staticmethod
    def has_path(msg):
        return 'path' in msg

    @staticmethod
    def has_properties(msg):
        return 'properties' in msg

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
            if prop == "pattern":
                string += f"['{prop}'] = [=[{value}]=],\n"
            elif prop == "validator":
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
        for (interface, intf_msg) in msg['interfaces'].items():
            if not self.has_properties(intf_msg):
                continue
            intf_name = self.get_intf_name(interface, intf_msg)
            for (prop, prop_config) in intf_msg['properties'].items():
                prop_config["validator"] = f"{self.get_intf_type(intf_name)}.{prop}"
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

        for (_, intf_msg) in msg['interfaces'].items():
            if self.has_methods(intf_msg):
                return True

        return False

    def get_mdb_method_configs(self, msg):
        string = '{'
        for (interface, intf_msg) in msg['interfaces'].items():
            if self.has_methods(intf_msg):
                methods = self.convert_methods(intf_msg['methods'])
                string += "['" + str(interface) + "'] = " + self.convert_to_lua(methods) + ","
        return string + '}'

    def has_mdb_signal_configs(self, msg):
        if not self.has_path(msg):
            return False

        for (_, intf_msg) in msg['interfaces'].items():
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

    def has_mdb_classes(self, msg):
        return self.has_path(msg)

    def get_mdb_classes(self, root, msg):
        return "mdb.get_class_obj('" + self.deduplicate_path(self.convert_dynamic_params(self.get_path(root, msg))) + \
            "')"

    def has_new_mdb_objects(self, msg):
        return self.has_path(msg)

    def has_privilege(self, msg, intf_msg):
        return ('privilege' in msg) or ('privilege' in intf_msg) or (self.has_property_privilege(intf_msg)) or \
                (self.has_method_privilege(intf_msg))

    def get_new_mdb_objects(self, msg):
        string = 'mdb.new_objects_builder({'
        for (interface, intf_msg) in msg['interfaces'].items():
            string += f"['{interface}'] = {{"
            intf_name = self.get_intf_name(interface, intf_msg)
            if self.has_properties(intf_msg):
                string += "['property_defaults'] = {"
                for (prop, prop_config) in intf_msg['properties'].items():
                    string += f"['{prop}'] = " + self.get_mdb_prop_default_value(intf_name, prop, prop_config) + ','
                string += '},'

            if self.has_privilege(msg, intf_msg):
                string += "['privileges'] = {"
                if 'privilege' in msg:
                    string += "['path'] = " + self.get_privilege(msg) + ','
                if 'privilege' in intf_msg:
                    string += "['interface'] = " + self.get_privilege(intf_msg) + ','
                if self.has_property_privilege(intf_msg):
                    string += "['props'] = " + self.get_property_privileges(intf_msg['properties']) + ','
                if self.has_method_privilege(intf_msg):
                    string += "['methods'] = " + self.get_privileges(intf_msg['methods']) + ','
                string += '},'

            string += f"['interface_types'] = {self.get_intf_type(intf_name)}}},"

        return string + "})"

    def get_intf_name(self, interface, intf_msg):
        slices = interface.split(".")
        if "implement" in intf_msg:
            return slices[-2] + slices[-1]
        return Utils.get_unique_intf_name(interface)

    def get_privilege(self, config):
        if 'privilege' not in config:
            return 'nil'
        privilege = []
        for priv in config['privilege']:
            privilege.append('privilege.' + priv)
        return " | ".join(privilege)

    def get_privileges(self, configs):
        privileges = {}
        for prop, prop_config in configs.items():
            if 'privilege' in prop_config:
                privileges[prop] = self.get_privilege(prop_config)

        string = '{\n'
        for (prop, value) in privileges.items():
            string += "['" + prop + "'] = " + value + ",\n"
        return string + '}'

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

    def has_property_privilege(self, intf_msg):
        if 'properties' not in intf_msg:
            return False

        for _, prop_config in intf_msg['properties'].items():
            if 'privilege' in prop_config:
                return True
        return False

    def has_method_privilege(self, intf_msg):
        if 'methods' not in intf_msg:
            return False

        for _, method_config in intf_msg['methods'].items():
            if 'privilege' in method_config:
                return True
        return False

    def get_property_privileges(self, configs):
        privileges = {}
        for prop, prop_config in configs.items():
            if 'privilege' in prop_config:
                privileges[prop] = self.get_property_privilege(prop_config)

        result = '{\n'
        for (prop, value) in privileges.items():
            priv = '{\n'
            for item, privilege in value.items():
                priv += "['" + item + "'] = " + privilege + ",\n"
            priv += '}'

            result += "['" + prop + "'] = " + priv + ",\n"
        return result + '}'

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
    
    def remove_description(self, input_dict):
        keys_to_delete = []
        for key, value in input_dict.items():
            if isinstance(value, dict):
                _ = self.remove_description(value)
            if key == 'description':
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del input_dict[key]
        return input_dict

Factory().register("model.lua.mako", ModelLuaUtils)
