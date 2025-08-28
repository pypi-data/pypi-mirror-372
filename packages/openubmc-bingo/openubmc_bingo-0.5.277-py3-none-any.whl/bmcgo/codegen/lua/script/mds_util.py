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
import stat
from collections import OrderedDict
from utils import Utils

USAGE = "usage"


def get_real_path(path):
    if path == "*":
        return path

    path = cut_ids(path)
    return os.path.realpath(path)


def convert_path_params(path: str):
    return re.sub(r":[\w\.]*", "*", re.sub(r"\$\{[\w\.]*\}", "*", path))


def get_intf(interface, mdb_path):
    real_path = ("/").join(
        [mdb_path, "intf", "mdb", interface.replace(".", "/") + ".json"]
    )
    with os.fdopen(os.open(real_path, os.O_RDONLY, stat.S_IRUSR), "r") as intf_file:
        return OrderedDict(json.load(intf_file))


def get_path(class_name, mdb_path, path):
    real_path = ("/").join([mdb_path, "path",
                            "mdb", path, class_name + ".json"])

    with os.fdopen(os.open(real_path, os.O_RDONLY, stat.S_IRUSR), "r") as obj_file:
        return OrderedDict(json.load(obj_file))


def get_path_by_interface(mdb_path: str, interface, path):
    real_path = os.path.join(mdb_path, "path", "mdb", get_real_path(path).lstrip("/"))
    expected_path = convert_path_params(path)
    for obj_file in os.scandir(real_path):
        if not obj_file.is_file():
            continue
        with os.fdopen(os.open(obj_file, os.O_RDONLY, stat.S_IRUSR), "r") as obj_fp:
            obj_dict = OrderedDict(json.load(obj_fp))
        for class_name, class_data in obj_dict.items():
            converted_path = convert_path_params(class_data.get("path"))
            if converted_path == expected_path and interface in class_data["interfaces"]:
                return class_name, obj_dict
    error_msg = f"service.json中配置的接口{interface}和路径{path}在mdb_interface中没有匹配的定义\n"\
    f"mdb_interface路径匹配目录为: {real_path}"
    raise RuntimeError(error_msg)


def save_proto_json(of_name, data):
    with os.fdopen(
        os.open(
            of_name, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IWUSR | stat.S_IRUSR
        ),
        "w",
    ) as load_f:
        json.dump(data, load_f, indent=4)


def open_file(file):
    return os.fdopen(os.open(file, os.O_RDONLY, stat.S_IRUSR), "r")


ALLOW_BASIC_TYPES = {
    "Boolean": "bool",
    "String": "string",
    "S32": "int32",
    "U32": "uint32",
    "S64": "int64",
    "U64": "uint64",
    "Double": "double",
    "U8": "uint8",
    "S8": "int8",
    "U16": "uint16",
    "S16": "int16",
    "Array": "message",
    "Binary": "string"
}


def get_base_type(base_type, is_array):
    if is_array:
        return base_type[0:-2]
    return base_type


def get_ref_type(referenced_type):
    if referenced_type.startswith("types.json"):
        return referenced_type.replace(
                    "types.json#/defs/", "def_types.defs_").replace("/", ".")
    elif referenced_type.startswith("mdb://"):
        slices = referenced_type.split(".json#")
        return (Utils.get_unique_intf_name(slices[0].replace("/", ".")) + slices[1]) \
            .replace("/defs/", ".defs_").replace("/", ".")
    else:
        return referenced_type.replace("#/", "").replace("/", ".")


def get_types(prop_name, prop_data):
    if "baseType" in prop_data:
        if prop_data["baseType"] == "Struct" or prop_data["baseType"] == "Enum" \
            or prop_data["baseType"] == "Dictionary":
            return False, get_ref_type(prop_data["$ref"])
        elif prop_data["baseType"] == "Array":
            return True, get_ref_type(prop_data["items"]["$ref"])
        elif prop_data["baseType"].endswith("[]"):
            return True, ALLOW_BASIC_TYPES[prop_data["baseType"][0:-2]]
        else:
            return False, ALLOW_BASIC_TYPES[prop_data["baseType"]]
    if "$ref" not in prop_data:
        raise RuntimeError(f"属性 {prop_name} 没有基类定义或找不到引用")
    return False, get_ref_type(prop_data["$ref"])


def get_validate_option(prop_data):
    validate_opt = ''
    if "maximum" in prop_data or "minimum" in prop_data:
        validate_opt += "ranges({}, {}),".format(
            prop_data["minimum"] if "minimum" in prop_data else None,
            prop_data["maximum"] if "maximum" in prop_data else None
        )
    if "maxLength" in prop_data or "minLength" in prop_data:
        validate_opt += "lens({}, {}),".format(
            prop_data["minLength"] if "minLength" in prop_data else None,
            prop_data["maxLength"] if "maxLength" in prop_data else None
        )
    if "enum" in prop_data:
        validate_opt += "enum({}),".format(prop_data["enum"])
    if "pattern" in prop_data:
        validate_opt += 'regex("{}"),'.format(prop_data["pattern"])
    return validate_opt


def get_options(prop_name, prop_data):
    options = {}
    if "readOnly" in prop_data and prop_data["readOnly"]:
        options["readonly"] = True
    if "default" in prop_data:
        options["default"] = prop_data["default"]
    if "deprecated" in prop_data:
        options["deprecated"] = prop_data["deprecated"]

    options["validate"] = get_validate_option(prop_data)
    options["allow_null"] = not prop_data.get("notAllowNull", False)

    if "primaryKey" in prop_data and prop_data["primaryKey"]:
        options["primary_key"] = prop_data["primaryKey"]
        if not prop_data.get("notAllowNull", True):
            raise RuntimeError(f"属性{prop_name}冲突: primaryKey 为真, 同时 notAllowNull 又为假")
        options["allow_null"] = False

    if "uniqueKey" in prop_data and prop_data["uniqueKey"]:
        options["unique"] = prop_data["uniqueKey"]

    if USAGE in prop_data:
        options[USAGE] = prop_data[USAGE]

    options["critical"] = prop_data.get("critical", False)
    return options


def is_enum(prop_data):
    if 'baseType' not in prop_data:
        return False
    elif prop_data['baseType'] == "Enum":
        return True
    elif prop_data['baseType'] == "Array" and 'baseType' in prop_data["items"] \
        and prop_data["items"]['baseType'] == "Enum":
        return True
    else:
        return False


# only db.lua need index
def get_property(prop_name, prop_data, index):
    original_name = prop_name
    repeated, prop_type = get_types(prop_name, prop_data)

    if "alias" in prop_data:
        prop_name = prop_data["alias"]

    data = {
        "original_name": original_name,
        "name": prop_name,
        "type": prop_type,
        "options": get_options(prop_name, prop_data),
        "id": index,
        "repeated": repeated,
        "is_enum": is_enum(prop_data)
    }

    if "displayDescription" in prop_data:
        data["description"] = prop_data["displayDescription"]
    return data


def get_dict_item(prop_name, prop_data, index):
    repeated, prop_type = get_types(prop_name, prop_data)

    data = {
        "original_name": prop_name,
        "name": prop_name,
        "type": prop_type,
        "options": get_options(prop_name, prop_data),
        "id": index,
        "repeated": repeated,
        "is_enum": is_enum(prop_data)
    }

    if "displayDescription" in prop_data:
        data["description"] = prop_data["displayDescription"]
    return data


def get_enum(prop_name, prop_data, index):
    return {
        "name": prop_name,
        "value": prop_data,
        "id": index
    }


def get_message_type(struct_data):
    if 'key' in struct_data and 'value' in struct_data:
        return 'dict'

    dict_iter = iter(struct_data)
    first_key = next(dict_iter, None)
    if first_key is None or isinstance(struct_data[first_key], dict):
        return 'struct'

    return 'enum'


def get_struct_message(package, struct_name, struct_data):
    struct_properties = []
    index = 0
    for prop, prop_data in struct_data.items():
        struct_properties.append(get_property(prop, prop_data, index))
        index = index + 1

    return {
        "package": package,
        "name": struct_name,
        "options": {},
        "type": "Message",
        "properties": struct_properties,
        "nested_type": [],
    }


def get_enum_message(package, struct_name, struct_data):
    enum_type = str
    index = 0
    enum_values = []
    for prop, prop_data in struct_data.items():
        if not isinstance(prop_data, (int, str)):
            raise RuntimeError("确保枚举 {} 有正确的类型".format(prop))
        if index == 0:
            enum_type = type(prop_data)
        elif not isinstance(prop_data, enum_type):
            raise RuntimeError("确保枚举 {} 有正确的类型".format(prop))
        enum_values.append(get_enum(prop, prop_data, 0))
        index += 1

    return {
        "package": package,
        "name": struct_name,
        "options": {},
        "type": "Enum",
        "default": 2147483647 if enum_type == int else "''",
        "values": enum_values
    }


def get_dict_message(package, struct_name, struct_data):
    return {
        "package": package,
        "name": struct_name,
        "options": {},
        "type": "Dictionary",
        "properties": [
            get_dict_item('key', struct_data['key'], 0),
            get_dict_item('value', struct_data['value'], 1)
        ]
    }


def cut_ids_new(path):
    paths = []
    current = 0

    pos = path.find("${")
    while pos != -1:
        paths.append(path[current:pos])
        end = path.find("}", pos)
        if end != -1:
            path = path[end + 1:]
            pos = path.find("${")
        else:
            path = ""
            pos = -1
    paths.append(path)
    paths.append("/")
    return "".join(paths)


def cut_ids(path):
    path = path.replace(" ", "")
    paths = []
    current = 0
    path = cut_ids_new(path)
    pos = path.find(":")
    while pos != -1:
        paths.append(path[current:pos])
        end = path.find("/", pos)
        if end != -1:
            path = path[end:]
            pos = path.find(":")
        else:
            path = ""
            pos = -1
    paths.append(path)
    paths.append("/")
    return "".join(paths)


def get_intf_package_name(intf_name):
    intfs = intf_name.split(".")
    if intfs[-1] == "Default":
        return intfs[-2] + intfs[-1]
    return intfs[-1]


def get_default_intf(intf_data, origin_intf):
    if "properties" in origin_intf:
        intf_data["properties"] = origin_intf["properties"]

    if "signals" in origin_intf:
        intf_data["signals"] = origin_intf["signals"]

    if "methods" not in origin_intf:
        return
    intf_data["methods"] = {}
    default = intf_data["methods"]
    for method, method_intf in origin_intf["methods"].items():
        new_method = method
        default[new_method] = {}
        if "req" in method_intf:
            default[new_method]["req"] = {}
            default[new_method]["req"]["path"] = {"baseType": "String"}
            for arg, arg_data in method_intf["req"].items():
                default[new_method]["req"][arg] = arg_data.copy()
        if "rsp" in method_intf:
            default[new_method]["rsp"] = method_intf["rsp"].copy()


def generate_default(load_dict, mdb_path):
    for intf_data in load_dict.values():
        if "implement" in intf_data:
            if "properties" not in intf_data:
                intf_data["properties"] = {}
            default_intf = intf_data["implement"]
            intf = get_intf(default_intf, mdb_path)[default_intf]
            get_default_intf(intf_data, intf)

    return load_dict