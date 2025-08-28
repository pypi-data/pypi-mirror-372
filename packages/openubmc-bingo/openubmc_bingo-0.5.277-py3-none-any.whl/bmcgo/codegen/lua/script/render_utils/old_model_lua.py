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
ALIAS = "alias"
PROPERTIES = "properties"
ENUM = "Enum"
DEFAULT = "default"


class OldModelLuaUtils(Base, Utils):
    TYPE_TO_DEFAULT_MAP = {
        "U8": 0,
        "U16": 0,
        "U32": 0,
        "U64": 0,
        "S8": 0,
        "S16": 0,
        "S32": 0,
        "S64": 0,
        "Double": 0,
        'String': "''",
        "Boolean": 'false'
    }

    def __init__(self, data: dict, options: Options):
        super().__init__(data, options=options)

    @staticmethod
    def has_path(msg):
        return 'path' in msg

    @staticmethod
    def has_properties(msg):
        return PROPERTIES in msg

    @staticmethod
    def make_class(classes):
        string = '{\n'
        for i in range(len(classes)):
            string += '    ' + list(classes)[i] + ' = ' + list(
                classes)[i] + ('\n' if (i == len(classes) - 1) else ',\n')
        return string + '}\n'

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
    def has_arg_in(msg):
        return 'req' in msg

    @staticmethod
    def get_arg_in_params(msg):
        result = []
        for (param, _) in msg.items():
            result.append(param)
        return result

    @staticmethod
    def get_intf_package_name(intf_name):
        intfs = intf_name.split(".")
        if intfs[-1] == "Default":
            return intfs[-2] + intfs[-1]
        return intfs[-1]

    @staticmethod
    def is_enum_array(prop_config):
        return prop_config[BASE_TYPE] == 'Array' and ITEMS in prop_config and BASE_TYPE in prop_config[ITEMS] \
            and prop_config[ITEMS][BASE_TYPE] == ENUM

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

    def get_enum_value(self, project_name, ref, enum_type):
        if ref.startswith("types.json"):
            return "require 'class.types.types'." + \
                ref.replace("types.json#/defs/", "") + "." + enum_type
        elif ref.startswith("mdb://"):
            spices = ref.split(".json#")
            return "require '" + project_name + ".json_types." + \
                Utils.get_unique_intf_name(spices[0].replace("/", ".")) + "'." + \
                spices[1].replace("/defs/", "") + "." + enum_type
        raise Exception("枚举引用定义错误")

    def get_prop_default_value(self, project_name, class_name, prop, prop_config):
        if project_name != 'dft' and project_name != 'debug':
            if DEFAULT not in prop_config:
                if BASE_TYPE in prop_config and prop_config[BASE_TYPE] == ENUM:
                    return f"require 'class.types.{class_name}'.{prop}.default[1]:value()"
                else:
                    return f"require 'class.types.{class_name}'.{prop}.default[1]"
        else:
            if DEFAULT not in prop_config:
                if BASE_TYPE in prop_config and prop_config[BASE_TYPE] == ENUM:
                    return f"require '{project_name}.class.types.{class_name}'.{prop}.default[1]:value()"
                else:
                    return f"require '{project_name}.class.types.{class_name}'.{prop}.default[1]"

        default = prop_config[DEFAULT]
        if BASE_TYPE not in prop_config:
            return self.convert_to_lua(default)

        if prop_config[BASE_TYPE] == ENUM:
            return self.get_enum_value(project_name, prop_config["$ref"], default) + ":value()"
        elif self.is_enum_array(prop_config):
            result = "{"
            for enum_type in default:
                result += self.get_enum_value(project_name, prop_config[ITEMS]["$ref"], enum_type) + ":value(),"
            return result + "}"

        return self.convert_to_lua(default)

    def get_mdb_prop_default_value(self, project_name, intf_name, prop, prop_config):
        pkg_name = "require '" + project_name + ".json_types." + intf_name + "'."
        if DEFAULT not in prop_config:
            if BASE_TYPE in prop_config and prop_config[BASE_TYPE] == ENUM:
                return pkg_name + prop + ".default[1]:value()"
            else:
                return pkg_name + prop + ".default[1]"

        default = prop_config[DEFAULT]
        if BASE_TYPE not in prop_config:
            return self.convert_to_lua(default)

        if prop_config[BASE_TYPE] == ENUM:
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
            for (prop, prop_config) in msg[PROPERTIES].items():
                if "primaryKey" in prop_config:
                    return self.convert_to_lua({"field": prop, BASE_TYPE: prop_config.get(BASE_TYPE)})

        if 'interfaces' not in msg:
            return {}

        for (_, intf_msg) in msg['interfaces'].items():
            if not self.has_properties(intf_msg):
                continue
            for (prop, prop_config) in intf_msg[PROPERTIES].items():
                if "primaryKey" not in prop_config:
                    continue
                result = {"field": prop_config.get(ALIAS, prop), BASE_TYPE: prop_config.get(BASE_TYPE)}
                return self.convert_to_lua(result)

        return {}

    def get_prop_configs(self, class_name, msg, project_name):
        if not self.has_properties(msg):
            return '{}'
        if project_name != 'dft' and project_name != 'debug':
            for (prop, prop_config) in msg[PROPERTIES].items():
                prop_config["validator"] = "require 'class.types." + class_name + "'." + prop
        else:
            for (prop, prop_config) in msg[PROPERTIES].items():
                prop_config["validator"] = "require '" + project_name + ".class.types." + class_name + "'." + prop
        return self.convert_to_lua(msg[PROPERTIES])

    def get_default_props(self, project_name, class_name, msg):
        if not self.has_properties(msg):
            return '{}'
        string = '{'
        for (prop, prop_config) in msg[PROPERTIES].items():
            string += "['" + str(prop) + "'] = " + \
                str(self.get_prop_default_value(project_name, class_name, prop, prop_config)) + ","

        return string + '}'

    def get_mdb_default_props(self, project_name, msg):
        if not self.has_path(msg):
            return '{}'
        string = '{'
        for (interface, intf_msg) in msg['interfaces'].items():
            if not self.has_properties(intf_msg):
                continue
            intf_name = self.get_intf_name(interface, intf_msg)
            for (prop, prop_config) in intf_msg[PROPERTIES].items():
                string += "['" + str(prop_config.get(ALIAS, prop)) + "'] = " + \
                str(self.get_mdb_prop_default_value(project_name, intf_name, prop, prop_config)) + ","

        return string + '}'

    def get_mdb_prop_configs(self, project_name, msg):
        if not self.has_path(msg):
            return '{}'
        string = '{'
        for (interface, intf_msg) in msg['interfaces'].items():
            if not self.has_properties(intf_msg):
                continue
            intf_name = self.get_intf_name(interface, intf_msg)
            for (prop, prop_config) in intf_msg[PROPERTIES].items():
                prop_config["validator"] = f"require '{project_name}.json_types.{intf_name}'.{prop}"
            string += f"['{interface}'] = {self.convert_to_lua(intf_msg[PROPERTIES])},"

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

    def get_mdb_method_configs(self, msg):
        if not self.has_path(msg):
            return '{}'
        string = '{'
        for (interface, intf_msg) in msg['interfaces'].items():
            if self.has_methods(intf_msg):
                methods = self.convert_methods(intf_msg['methods'])
                string += "['" + str(interface) + "'] = " + self.convert_to_lua(methods) + ","

        return string + '}'

    def get_mdb_signal_configs(self, msg):
        if not self.has_path(msg):
            return '{}'

        string = '{'
        for (interface, intf_msg) in msg['interfaces'].items():
            if self.has_signals(intf_msg):
                signals = self.convert_signals(intf_msg['signals'])
                string += "['" + str(interface) + "'] = " + self.convert_to_lua(signals) + ","

        return string + '}'

    def get_alias_map(self, msg):
        result = {}
        if self.has_properties(msg):
            for (prop, prop_config) in msg[PROPERTIES].items():
                if ALIAS in prop_config:
                    result[prop_config[ALIAS]] = {"original_name": prop}

        if not self.has_path(msg):
            return self.convert_to_lua(result)

        for (interface, intf_msg) in msg['interfaces'].items():
            if not self.has_properties(intf_msg):
                continue

            for (prop, prop_config) in intf_msg[PROPERTIES].items():
                if ALIAS in prop_config:
                    result[prop_config[ALIAS]] = {"original_name": prop, "interface": interface}

        return self.convert_to_lua(result)

    def get_mdb_classes(self, root, msg):
        if not self.has_path(msg):
            return '{}'

        return "mdb.get_class_obj('" + self.deduplicate_path(self.convert_dynamic_params(self.get_path(root, msg))) + \
            "')"

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
            if 'privilege' not in prop_config:
                continue
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

    def get_property_privileges(self, configs):
        privileges = {}
        for prop, prop_config in configs.items():
            if 'privilege' not in prop_config:
                continue
            privileges[prop] = self.get_property_privilege(prop_config)

        result = '{\n'
        for (prop, value) in privileges.items():
            priv = '{\n'
            for item, privilege in value.items():
                priv += "['" + item + "'] = " + privilege + ",\n"
            priv += '}'

            result += "['" + prop + "'] = " + priv + ",\n"
        return result + '}'

    def get_readonlys(self, configs):
        readonlys = {}
        for prop, prop_config in configs.items():
            if 'readOnly' not in prop_config:
                continue
            readonlys[prop] = prop_config['readOnly']
        return self.convert_to_lua(readonlys)


Factory().register("old_model.lua.mako", OldModelLuaUtils)
