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
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from bmcgo.codegen.lua.script.dto.options import Options
from bmcgo.codegen.lua.script.validate import all_validates
from bmcgo.codegen import __version__ as codegen_version


class Utils:
    TYPE_TO_DBUS_MAP = {
        'int8': 'y',
        'uint8': 'y',
        'int16': 'n',
        'uint16': 'q',
        'int32': 'i',
        'uint32': 'u',
        'int64': 'x',
        'uint64': 't',
        'double': 'd',
        'float': 'd',
        'bytes': 'ay',
        'string': 's',
        'bool': 'b'
    }

    TYPE_TO_LUA = {
        'int8': 'integer',
        'uint8': 'integer',
        'int16': 'integer',
        'uint16': 'integer',
        'int32': 'integer',
        'uint32': 'integer',
        'int64': 'integer',
        'uint64': 'integer',
        'double': 'number',
        'float': 'number',
        'bytes': 'string',
        'string': 'string',
        'bool': 'boolean'
    }

    INTEGER_TYPE = {
        'int8': 'integer',
        'uint8': 'integer',
        'int16': 'integer',
        'uint16': 'integer',
        'int32': 'integer',
        'uint32': 'integer',
        'int64': 'integer',
        'uint64': 'integer',
    }

    OPEN_PROJECTS = {
        'profile_schema',
        'mdb_interface',
        'hica',
        'rootfs_user',
        'webui',
        'rackmount',
        'rack_mgmt',
        'fructrl',
        'sensor',
        'frudata',
        'chassis',
        'power_mgmt',
        'thermal_mgmt',
        'network_adapter',
        'storage',
        'pcie_device', 
        'bios',
        'general_hardware',
        'lsw',
        'manufacture',
        'account'
    }

    def __init__(self, data: dict, options: Options):
        self.data = data
        self.options = options

    @staticmethod
    def enum_value_name(e, prop):
        if prop.startswith(e + '_'):
            if prop[len(e) + 1:].isdigit():
                return prop
            else:
                return prop[len(e) + 1:]
        return prop

    @staticmethod
    def camel_to_snake(name):
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    @staticmethod
    def convert_dictionary_to_lua_table(msg):
        string = '{\n'
        i = 1
        for (prop, value) in msg.items():
            string += f"['{prop}'] = " + Utils.to_lua_value(value) + ",\n"
            i += 1
        return string + '}'

    @staticmethod
    def to_lua_value(val):
        if isinstance(val, str):
            return f'[=[{val}]=]'
        if isinstance(val, bool):
            return 'true' if val else 'false'
        if isinstance(val, list):
            result = '{'
            for value in val:
                result += f"{Utils.to_lua_value(value)},"
            return result + '}'
        if isinstance(val, int) or isinstance(val, float):
            return str(val)
        if isinstance(val, dict):
            return Utils.convert_dictionary_to_lua_table(val)
        return val

    @staticmethod
    def get_msg_property(t, name):
        ret = None
        if 'properties' not in t:
            return ret
        for p in t['properties']:
            if p['name'] == name:
                ret = p
        return ret

    @staticmethod
    def add_types(types, root):
        if 'data' in root:
            for data in root['data']:
                package = data['package']
                name = data['name']
                types[f'{package}.{name}'] = data

    @staticmethod
    def get_create_date(target_file):
        if os.path.exists(target_file):
            file = open(target_file, "r")
            content = file.read()
            file.close()
            date = re.search(r"Create: (\d+)-(\d+)-(\d+)", content)
            if date:
                return date[1], date[2], date[3]
        now = datetime.now(tz=timezone.utc)
        return now.year, now.month, now.day

    @staticmethod
    def make_prefix(lang):
        prefix = ['-- ', '-- ', '', '--']  # lua style is default
        if lang in ['c', 'cpp', 'java', 'rust', 'proto']:
            prefix = ['/* ', ' * ', ' */\n', ' *']  # c style for C/C++/proto etc.
        elif lang in ['python', 'shell']:
            prefix = ['#\! ', ' # ', '', ' #']  # python style for shell/python
        return prefix

    @staticmethod
    def maybe_array_type_to_lua(r, is_array):
        return r if not is_array else f'{r}[]'

    @staticmethod
    def maybe_array_type_to_dbus(r: str, is_array):
        return r if not is_array else f'a{r}'

    @staticmethod
    def get_message_type(data_type):
        res = re.match(r'^\.?([^.]+)\.(.+)$', data_type)
        if res:
            return res.group(2), res.group(1)
        return data_type, False

    @staticmethod
    def get_validate(validate_str):
        if not validate_str:
            return []
        return eval('[{}]'.format(validate_str), all_validates())

    @staticmethod
    def oem_is_exist(source_name):
        path = os.path.join(os.getcwd(), "..", "..", "proto", "apps", "redfish", "resource", "oem", "hw",
                            source_name + '.proto')
        return os.path.exists(path)

    @staticmethod
    def get_lua_codegen_version():
        env_version = os.getenv('LUA_CODEGEN_VERSION')
        if env_version is None or env_version == "-1" or not env_version.isdigit():
            return codegen_version
        return int(env_version)

    @staticmethod
    def get_major_version():
        env_version = os.getenv('MAJOR_VERSION')
        if env_version is None or env_version == "-1" or not env_version.isdigit():
            return 1
        return int(env_version)

    @staticmethod
    def formatter(header, date, filename, lang, draft_info):
        if draft_info:
            author = '<change to your name>'
            create = '<模板自动生成初稿, 需要您进行编辑>'
            description = draft_info
        else:
            author = 'auto generate'
            create = date
            description = f'DO NOT EDIT; Code generated by "{filename}"'

        return header.format(date[:4], author, create, description,
                             Utils.make_prefix(
                                 lang)[1], Utils.make_prefix(lang)[0],
                             Utils.make_prefix(lang)[2], Utils.make_prefix(lang)[3])

    @staticmethod
    def make_header(tpl, target_file, draft_info=""):
        pattern = r'(.*)/gen/(.*)'
        gen_bak_file = re.sub(pattern, r'\1/gen_bak/\2', target_file)
        year, month, day = Utils.get_create_date(gen_bak_file)
        date = f'{year}-{month}-{day}'
        filename = os.path.basename(tpl)
        header = '''{5}Copyright (c) Huawei Technologies Co., Ltd. {0}. All rights reserved.
{7}
{4}this file licensed under the Mulan PSL v2.
{4}You can use this software according to the terms and conditions of the Mulan PSL v2.
{4}You may obtain a copy of Mulan PSL v2 at: http://license.coscl.org.cn/MulanPSL2
{7}
{4}THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
{4}IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
{4}PURPOSE.
{4}See the Mulan PSL v2 for more details.
{7}
{4}Author: {1}
{4}Create: {2}
{4}Description: {3}
{6}'''
        project_name = os.getenv('PROJECT_NAME')
        if Utils.get_lua_codegen_version() >= 8 and project_name in Utils.OPEN_PROJECTS:
            header = '''{5}Copyright (c) 2024 Huawei Technologies Co., Ltd.
{4}openUBMC is licensed under Mulan PSL v2.
{4}You can use this software according to the terms and conditions of the Mulan PSL v2.
{4}You may obtain a copy of Mulan PSL v2 at:
{4}         http://license.coscl.org.cn/MulanPSL2
{4}THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
{4}EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
{4}MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
{4}See the Mulan PSL v2 for more details.
{6}'''
        return lambda lang: Utils.formatter(header, date, filename, lang, draft_info)

    @staticmethod
    def force_to_colon(path):
        if isinstance(path, str):
            return path.replace("${", ":").replace("}", "")
        return [p.replace("${", ":").replace("}", "") for p in path]

    @staticmethod
    def check_db_open(name):
        return 'persist' not in Utils.camel_to_snake(name)

    @staticmethod
    def check_model_need_mem_db(model_json: dict):
        for class_data in model_json.values():
            if "tableName" in class_data and class_data.get("tableLocation") != "Local":
                return True
        return False
    
    @staticmethod
    def has_db(root: dict):
        return Utils.check_need_mem_db(root) or Utils.check_local_poweroff_db(root) or \
            Utils.check_local_reset_db(root) or Utils.check_local_temporary_db(root)
    
    @staticmethod
    def get_db_types(root: dict):
        db_types = '{'
        if Utils.check_need_mem_db(root):
            db_types += "'memory', "
        if Utils.check_local_poweroff_db(root):
            db_types += "'local_poweroff', "
        if Utils.check_local_reset_db(root):
            db_types += "'local_reset', "
        if Utils.check_local_temporary_db(root):
            db_types += "'local_temporary', "
        return db_types + '}'

    @staticmethod
    def check_need_mem_db(root: dict):
        if Utils.get_lua_codegen_version() < 7:
            return Utils.check_db_open(root['package'])
        return root.get('need_mem_db', False)

    @staticmethod
    def check_need_local_db(root: dict):
        return Utils.check_local_poweroff_db(root) or Utils.check_local_reset_db(root) \
        or Utils.check_local_reset_db(root)

    @staticmethod
    def check_remote_per(root):
        return root.get('options', {}).get('has_remote_per', False)

    @staticmethod
    def check_local_poweroff_db(root):
        return 'options' in root and 'has_local_poweroff' in root['options'] and root['options']['has_local_poweroff']

    @staticmethod
    def check_local_reset_db(root):
        return 'options' in root and 'has_local_reset' in root['options'] and root['options']['has_local_reset']

    @staticmethod
    def check_local_temporary_db(root):
        return 'options' in root and 'has_local_temporary' in root['options'] and root['options']['has_local_temporary']

    @staticmethod
    def remove_duplicate(params):
        result = []
        for name in params:
            if name not in result:
                result.append(name)
        return result

    @staticmethod
    def get_primal_path_params(path):
        params = re.compile(
            r':([a-zA-Z_][0-9a-zA-Z_]+)').findall(path)
        return params

    @staticmethod
    def get_type_name(prop_type):
        slices = prop_type.split(".")
        full_intf_name = ".".join(slices[:-1])
        return Utils.get_unique_intf_name(full_intf_name) + "." + slices[-1]

    @staticmethod
    def get_unique_intf_name(intf):
        check_intfs = Path(__file__).parent.parent.joinpath("temp").joinpath("check_intfs.json")
        with open(check_intfs, 'r') as check_intfs_fp:
            intf_map = json.load(check_intfs_fp)

        slices = intf.split('.')
        if slices[-1] == "Default":
            return slices[-2] + slices[-1]
        return intf_map.get(intf, slices[-1])

    @staticmethod
    def get_files(path):
        file_list = []
        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            if os.path.isdir(file_path):
                file_list.extend(Utils.get_files(file_path))
            else:
                file_list.append(file_path)
        return file_list

    @staticmethod
    def count(params, name):
        return params.count(name)

    @classmethod
    def get_dir_name(cls, path):
        path_list = path.split('/')
        return path_list[len(path_list) - 2]

    @classmethod
    def format_string_val(cls, val):
        if len(val) < 50:
            return f'[=[{val}]=]'
        chunks, chunk_size = len(val), 50
        lines = []
        for line in [val[i:i + chunk_size] for i in range(0, chunks, chunk_size)]:
            lines.append(f'[=[{line}]=]')
        return " .. ".join(lines)

    def make_get_message(self, data_type):
        return self.get_message(self.data, data_type)

    def default_in_message(self, msg):
        for prop in msg['properties']:
            if self.check_is_message(self.data, prop['type']):
                return self.default_in_message(self.make_get_message(prop['type']))
            elif 'options' in prop and 'default' in prop['options']:
                return 'true'
        return 'false'

    def with_default_new(self, p):
        if self.check_is_message(self.data, p['type']):
            if self.default_in_message(self.make_get_message(p['type'])) == 'true':
                return f"{p.get('original_name', p['name'])} or {p['type']}.new()"
            if 'options' in p and 'default' in p['options']:
                return f"{p.get('original_name', p['name'])} or {self.to_lua_value(p['options']['default'])}"
            else:
                return p.get('original_name', p['name'])
        elif 'options' in p and 'default' in p['options']:
            default = p['options']['default']
            if p["repeated"]:
                result = f"{p.get('original_name', p['name'])} or {{"
                for default_var in default:
                    result += f"{self.to_lua_value(default_var)},"
                return result + "}"
            else:
                if p['type'] == 'bool' and default:
                    return f"{p.get('original_name', p['name'])} == nil and true or {p.get('original_name', p['name'])}"
                else:
                    return f"{p.get('original_name', p['name'])} or {self.to_lua_value(default)}"
        return p.get('original_name', p['name'])

    def construct(self, msg):
        return ",\n    ".join([f"{p.get('original_name', p['name'])} = \
            {self.with_default_new(p)}" for p in msg['properties']])

    def format_value(self, val, prefix):
        if val is None:
            return 'nil'
        elif isinstance(val, str):
            return self.format_string_val(val)
        elif isinstance(val, bool):
            return 'true' if val else 'false'
        elif isinstance(val, list):
            result = []
            for v in val:
                result.append(self.format_value(v, prefix))
            return '{%s}' % (','.join(result))
        elif isinstance(val, dict):
            result = []
            for k, v in val.items():
                result.append(f'{k} = {self.format_value(v, prefix + "  ")}')
            return "{\n%s%s\n%s}" % (prefix, f',\n{prefix}'.join(result), prefix)
        else:
            return f'{val}'

    def load_types(self, name):
        types = {}
        self.add_types(types, self.data)

        if 'imports' in self.data:
            for (_, data) in self.data['imports'].items():
                self.add_types(types, data)

        return types.get(name)

    def is_map_type(self, t):
        if 'properties' not in t:
            return False
        return len(t['properties']) == 2 and self.get_msg_property(t, 'key') and self.get_msg_property(t, 'value')

    def try_get_map_type(self, t):
        ret = {}
        res = re.match(r'^(.+)\.([^.]+Entry)$', t)
        if not res:
            return ret
        msg_type = res.group(1)
        prop_type = res.group(2)
        msg = self.load_types(msg_type)
        if 'nested_type' not in msg:
            return ret
        ret = self.do_find_type(msg['nested_type'], prop_type)
        if not ret or not self.is_map_type(ret):
            return ret
        return ret

    def do_type_to_lua(self, t, is_array):
        if t.endswith('[]'):
            is_array = True
            t = t[:-2]
        if t in self.TYPE_TO_LUA:
            return self.maybe_array_type_to_lua(self.TYPE_TO_LUA[t], is_array)
        tt = self.load_types(t)
        if tt is None:
            map_type = self.try_get_map_type(t)
            if not map_type:
                return self.maybe_array_type_to_lua(t, is_array)
            key = self.get_msg_property(map_type, 'key')
            value = self.get_msg_property(map_type, 'value')
            key_type = self.do_type_to_lua(key['type'], key['repeated'])
            value_type = self.do_type_to_lua(value['type'], value['repeated'])
            return f'table<{key_type}, {value_type}>'
        else:
            return self.maybe_array_type_to_lua(f'{tt["package"]}.{tt["name"]}', is_array)

    def do_type_to_dbus(self, t: str, is_array):
        if t.endswith('[]'):
            is_array = True
            t = t[:-2]
        if t in self.TYPE_TO_DBUS_MAP:
            return self.maybe_array_type_to_dbus(self.TYPE_TO_DBUS_MAP[t], is_array)
        tt = self.load_types(t)
        if tt is None:
            map_type = self.try_get_map_type(t)
            if not map_type:
                return t
            key = self.get_msg_property(map_type, 'key')
            value = self.get_msg_property(map_type, 'value')
            key_type = self.do_type_to_dbus(key['type'], False)
            value_type = self.do_type_to_dbus(value['type'], False)
            return f'a{{{key_type}{value_type}}}'
        elif tt["type"] == "Enum":
            return self.maybe_array_type_to_dbus('i', is_array)
        elif tt["type"] == "Dictionary":
            map_config = tt.get("properties", [{}, {}])
            key_type = self.do_type_to_dbus(map_config[0].get('type'), map_config[0].get('repeated'))
            value_type = self.do_type_to_dbus(map_config[1].get('type'), map_config[1].get('repeated'))
            return f'a{{{key_type}{value_type}}}'
        elif tt['type'] == 'Message' and 'properties' in tt:
            result = []
            for p in tt['properties']:
                result.append(self.do_type_to_dbus(p['type'], p['repeated']))
            if 'options' in tt and 'flatten' in tt['options'] and tt['options']['flatten']:
                return self.maybe_array_type_to_dbus(f'{"".join(result)}', is_array)
            return self.maybe_array_type_to_dbus(f'({"".join(result)})', is_array)
        else:
            raise RuntimeError(f"类型 `{t}` 转换为 dbus 类型失败")

    def do_types_to_dbus(self, msg):
        types = ''
        for p in msg['properties']:
            types += self.do_type_to_dbus(p['type'], p['repeated'])
        return types

    def do_service_types_to_dbus(self, root, input_data_type):
        message = self.get_message(root, input_data_type)
        return self.do_types_to_dbus(message)

    def do_find_type(self, root, data_type) -> dict:
        ret = {}
        for data in root:
            if data['name'] == data_type:
                ret = data
            if 'nested_type' not in data.keys():
                continue
            nested_data = self.do_find_type(data['nested_type'], data_type)
            if nested_data:
                ret = nested_data
        return ret

    def is_oem_message(self, filename, data_type):
        return self.check_is_message(self.data['imports'][filename], data_type)

    def get_oem_message(self, filename, data_type):
        return self.get_message(self.data['imports'][filename], data_type)

    def get_message(self, root, input_data_type, level=0) -> dict:
        data_type, pkg = self.get_message_type(input_data_type)
        if not pkg:
            msg = self.do_find_type(root['data'], data_type)
            if msg:
                return msg
            else:
                pkg = 'def_types'

        if level > 0:
            msg = self.get_message(root, pkg, level + 1)
            if msg and 'nested_type' in msg:
                return self.get_message({'data': msg.get('nested_type')}, data_type, level + 1)
        elif pkg == root['package'] or pkg == 'defs':
            return self.get_message(root, data_type, level + 1)
        elif pkg in root['imports']:
            return self.get_message(root['imports'][pkg], data_type, level + 1)
        elif pkg == 'google':
            return {
                "package": "google",
                "name": input_data_type,
                "options": {},
                "type": "Message",
                "properties": [],
                "nested_type": []
            }
        raise RuntimeError("无效消息: {}".format(data_type))

    def get_root(self, root, input_data_type, level=0):
        data_type, pkg = self.get_message_type(input_data_type)
        if not pkg:
            msg = self.do_find_type(root['data'], data_type)
            if msg:
                return root
        elif level > 0:
            msg = self.get_root(root, pkg, level + 1)
            if msg and 'nested_type' in msg:
                return self.get_root({'data': msg.get('nested_type')}, data_type, level + 1)
        elif pkg == root['package']:
            return self.get_root(root, data_type, level + 1)
        elif pkg in root['imports']:
            return self.get_root(root['imports'][pkg], data_type, level + 1)
        elif pkg == 'google':
            return {
                "package": "google",
                "name": input_data_type,
                "options": {},
                "type": "Message",
                "properties": [],
                "nested_type": []
            }
        raise RuntimeError("无效消息: {}".format(data_type))

    def is_integer(self, i_type):
        return i_type in self.INTEGER_TYPE

    def check_is_enum(self, p):
        try:
            pp = self.get_message(self.data, p)
            return pp.get('type') == 'Enum'
        except RuntimeError:
            return False

    def check_is_message(self, root, p):
        try:
            pp = self.get_message(root, p)
            return pp.get('type') == 'Message' and not self.is_map_type(pp)
        except RuntimeError:
            return False

    def is_base_type(self, name):
        return name in self.TYPE_TO_LUA.keys()

    def resolve_duplicate(self, params):
        parent_count = self.count(params, 'parent')
        if parent_count == 0:
            return params

        group_list = [[] for _ in range(parent_count + 1)]

        num = 0
        for param in params:
            if param == 'parent':
                num += 1
                continue
            group_list[num].append(param)

        result = []
        duplicate_map = {}
        for i in range(parent_count + 1):
            set_flag = {}
            for item in group_list[i]:
                if self.count(params, item) > self.count(group_list[i], item):
                    duplicate_map[item] = duplicate_map.get(item, 0)
                    duplicate_map[item] += set_flag.get(item, 1)
                    set_flag[item] = 0
                    result.append(item + str(duplicate_map[item]))
                else:
                    result.append(item)
            if i < parent_count:
                result.append("parent")

        return result

    def get_all_params(self, path):
        params = re.compile(
            r':([a-zA-Z_][0-9a-zA-Z_]+)').findall(path)
        return self.resolve_duplicate(params)

    def get_path_params(self, path):
        path = self.force_to_colon(path)

        pattern = r':([a-zA-Z_][0-9a-zA-Z_]+)'
        if isinstance(path, str):
            params = re.compile(pattern).findall(path)
        else:
            params = []
            for p in path:
                params.extend(re.compile(pattern).findall(p))
                
        return self.remove_duplicate(params)

    def deduplicate_path(self, path):
        primal_params = self.get_primal_path_params(path)
        if len(primal_params) == 0:
            return path

        result = ''
        params = self.get_all_params(path)
        params_len = len(primal_params)
        for i in range(params_len):
            string = path.partition(f':{primal_params[i]}')
            result += string[0]
            if params[i] != 'parent':
                result += ':' + params[i]
            path = string[2]
        if path:
            result += path

        return result
