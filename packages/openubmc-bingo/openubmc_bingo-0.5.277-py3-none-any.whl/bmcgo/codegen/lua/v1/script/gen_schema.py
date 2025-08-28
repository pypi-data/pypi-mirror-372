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

import json
import logging
import getopt
import sys
import os
import stat
import re
from collections import OrderedDict
from bmcgo.codegen.lua.script.utils import Utils
from bmcgo.utils.tools import Tools

tool = Tools()
log = tool.log
MDS_REF = "$ref"
MDS_DEFS = "defs"
MDS_REF_INTERFACE = "refInterface"
MDS_PATH = "path"
MDS_PARENT = "parent"
MDS_DEFINITIONS = "definitions"
BASIC_TYPES = ["U8", "U16", "U32", "U64", "S16", "S32", "S64", "String", "Double", "Boolean"]
RETAIN_ITEMS = ["description", "enum", "minimum", "maximum", "minLength", "maxLength", "pattern", "x-originalName",
                "x-interface"]


def no_need_filter(k):
    filter_list = ["usage", "notAllowNull", "readOnly", "default", "primaryKey", "critical"]
    return k not in filter_list


def is_excluded_intf(intf):
    return intf == "bmc.kepler.Object.Properties"


def is_usage_csr(property_data):
    return "usage" in property_data and "CSR" in property_data["usage"]


def update_dictionary_type(key_data, value_data):
    new_property_data = {}
    if key_data["baseType"] == 'String':
        new_property_data["^.*$"] = update_type(value_data)
        return {"type": "object", "patternProperties": new_property_data}
    else:
        return {"type": "array", "items": {"$ref": "base.json#/definitions/S32"}}


def update_array_type(property_data, base_type):
    new_property_data = property_data.copy()
    new_property_data["type"] = "array"
    if base_type == "Array":
        try:
            new_property_data["items"][MDS_REF] = new_property_data["items"][MDS_REF] \
                .replace(MDS_DEFS, MDS_DEFINITIONS).replace("types.json", "")
        except Exception as e:
            log.error(f"任务状态错误: {e}")
            raise Exception(f"未找到{MDS_REF}") from e
        return new_property_data

    if "refInterface" in new_property_data:
        ref_interface = new_property_data.pop("refInterface")
        new_property_data["x-refInterface"] = ref_interface
    new_property_data["items"] = {MDS_REF: "base.json#/definitions/" + base_type[:-2]}
    return new_property_data


def update_type(property_data):
    new_property_data = {}
    if not isinstance(property_data, dict):
        return new_property_data

    if "baseType" in property_data or "$ref" in property_data:
        base_type = property_data.pop("baseType", "")
        match = re.fullmatch(r'^(.+)(\[\])$', base_type)
        if base_type == "Array" or (match and match.group(1) in BASIC_TYPES):
            return update_array_type(property_data, base_type)

        if MDS_REF_INTERFACE in property_data:
            new_property_data[MDS_REF_INTERFACE] = property_data.pop(MDS_REF_INTERFACE, "")
        
        if base_type in BASIC_TYPES:
            new_property_data[MDS_REF] = "base.json#/definitions/" + base_type
        elif MDS_REF in property_data:
            new_property_data[MDS_REF] = property_data[MDS_REF].replace(MDS_DEFS, MDS_DEFINITIONS) \
                .replace("types.json", "")

        for item in RETAIN_ITEMS:
            if item in property_data:
                new_property_data[item] = property_data[item]

    return new_property_data


def read_properties(intf_name, properties, out_properties, is_intf_props, usage_csr):
    # properties only mark usage as C should deploy to csr schema
    props = list(p for p, v in properties.items() if is_intf_props or is_usage_csr(v))
    for index, prop in enumerate(props):
        # filter properties which no need for csr
        if is_usage_csr(properties[prop]) != usage_csr:
            continue
        prop_alias = prop
        # if prop have alias, use alias name replace prop name
        if "alias" in properties[prop]:
            prop_alias = properties[prop].pop("alias", "")
            properties[prop]["x-originalName"] = prop
        if intf_name:
            properties[prop]["x-interface"] = intf_name
        out_properties[prop_alias] = {
            k: v
            for k, v in properties[prop].items()
            if no_need_filter(k)
        }

        if prop_alias != prop:
            out_properties[prop_alias] = update_type(out_properties[prop_alias])
            props[index] = prop_alias
        else:
            out_properties[prop] = update_type(out_properties[prop])

    return props


def read_defs(structs, data):
    for struct_name, struct_data in data[MDS_DEFS].items():
        if struct_name in structs:
            continue
        properties = {k: v for k, v in struct_data.items()}
        first_value = next(iter(struct_data.values()), None)
        if isinstance(first_value, str) or isinstance(first_value, int):
            structs[struct_name] = {"type": "string" if isinstance(first_value, str) else "integer",
                                    "enum": list(struct_data.values())}
            continue
        if "key" in properties:
            structs[struct_name] = update_dictionary_type(properties["key"], properties["value"])
            continue
        items = []
        for _, prop_data in properties.items():
            items.append(update_type(prop_data))
        structs[struct_name] = {"type": "array", "items": items}


def read_interfaces(interfaces, out_properties, structs, usage_csr):
    intfs = {}
    for intf_name, intf in interfaces.items():
        # no properties also need interface name , because may be reference Object by other property for Devkit check
        intfs[intf_name] = {}
        if "properties" in intf:
            props = read_properties(intf_name, intf["properties"], out_properties, not is_excluded_intf(intf_name),
                                    usage_csr)
            intfs[intf_name] = props
        if MDS_DEFS in intf:
            read_defs(structs, intf)
    return intfs


def save_csr_schema(of_name, csr_schema):
    if os.path.exists(of_name):
        with os.fdopen(os.open(of_name, os.O_RDONLY, stat.S_IRUSR), "r") as load_f:
            if json.load(load_f) == csr_schema:
                logging.info("schema 文件内容没有变更")
                return

    with os.fdopen(
        os.open(
            of_name, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IWUSR | stat.S_IRUSR
        ),
        "w", encoding="utf-8"
    ) as load_f:
        json.dump(csr_schema, load_f, ensure_ascii=False, indent=4)
        logging.info("schema 已经发生改变")


csr_schema_template = {
    "$id": "CSR",
    "$schema": "https://json-schema.org/draft/2019-09/schema#",
    "x-version": "1.0",
    "title": "CSR",
    "description": "支持对CSR对象配置进行检查和校验",
    "type": "object",
    "patternProperties": {}
}


def replace_colon(path):
    path = os.path.realpath(path) if (path[0:1] == "/") else path
    paths = path.split("/")
    maps = {}
    for var in paths:
        if var.startswith(":"):
            maps[var] = var.replace(":", "${") + "}"
    for old, new in maps.items():
        path = path.replace(old, new)
    return path


def create_schema_class(interfaces, properties, non_csr_properties, class_data):
    class_def = {"type": "object", "properties": properties, "x-publicProperties": non_csr_properties}
    if MDS_PATH in class_data:
        class_def["x-" + MDS_PATH] = replace_colon(class_data[MDS_PATH])
    if MDS_PARENT in class_data:
        class_def["x-" + MDS_PARENT] = class_data[MDS_PARENT]
    class_def["additionalProperties"] = True
    return class_def


def count_dir_level(path):
    level = 0
    while True:
        path = os.path.dirname(path)
        if path == '/':
            break
        level += 1
    return level


def filling_material(load_dict, csr_schema):
    for class_name, class_data in load_dict.items():
        properties = {}
        non_csr_properties = {}
        interfaces = {}
        if "interfaces" in class_data:
            interfaces = read_interfaces(
                class_data["interfaces"], properties, csr_schema[MDS_DEFINITIONS], True
            )
            _ = read_interfaces(
                class_data["interfaces"], non_csr_properties, csr_schema[MDS_DEFINITIONS], False
            )
        if "properties" in class_data:
            _ = read_properties(None, class_data["properties"], properties, False, True)
            _ = read_properties(None, class_data["properties"], non_csr_properties, False, False)
        if MDS_DEFS in class_data:
            read_defs(csr_schema[MDS_DEFINITIONS], class_data)
        # no properties means no properties mark usage C ,no need generic csr schema class
        if properties:
            csr_schema["patternProperties"]["^" + class_name + "_.+$"] = create_schema_class(
                interfaces, properties, non_csr_properties, class_data
            )
    if MDS_DEFS in load_dict:
        read_defs(csr_schema[MDS_DEFINITIONS], load_dict)


def generate_schema(types_path, root, file, csr_schema):
    file_path = os.path.join(root, file)
    load_f = os.fdopen(os.open(file_path, os.O_RDONLY, stat.S_IRUSR), "r")
    load_dict = json.load(load_f)
    if os.path.exists(types_path):
        load_f2 = os.fdopen(os.open(types_path, os.O_RDONLY, stat.S_IRUSR), "r")
        load_dict2 = json.load(load_f2)
        types_defs = {}
        read_defs(types_defs, load_dict2)
        csr_schema[MDS_DEFINITIONS].update(types_defs)

    filling_material(load_dict, csr_schema)
    load_f.close()


def generate(types_path, if_name, of_name, project_name):   
    if not os.path.exists(if_name):
        return

    # APP的目录层级是3，组件层级是4
    pattern = re.compile(f'.*(/[^/]+/temp/{project_name}/.*)')
    match = re.search(pattern, if_name)
    path_level = 0
    if match:
        temp_model_path = match.group(1)
        path_level = count_dir_level(temp_model_path)
    dir_path = os.path.dirname(if_name)

    if not (dir_path.endswith('test_gen_schema') or path_level == 3):
        return

    csr_schema = OrderedDict(csr_schema_template.copy())
    csr_schema[MDS_DEFINITIONS] = {}
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith('_model.json'):
                generate_schema(types_path, root, file, csr_schema)

    save_csr_schema(of_name, csr_schema)



def usage():
    logging.info("gen_schema.py -i <inputfile> -o <outfile> -n <project_name>")


def main(argv):
    m_input = ""
    output = ""
    try:
        opts, _ = getopt.getopt(argv, "ht:i:o:n:", ["help", "types_path=", "input=", "out=", "project_name="])
    except getopt.GetoptError:
        help()
        return
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            return
        elif opt in ("-t", "--types_path"):
            m_types_path = arg
        elif opt in ("-i", "--input"):
            m_input = arg
        elif opt in ("-o", "--out"):
            output = arg
        elif opt in ("-n", "--project_name"):
            project_name = arg
        else:
            raise RuntimeError("不支持的选项: {}".format(opt))
    if not m_input or not output:
        usage()
        return
    generate(m_types_path, m_input, output, project_name)


if __name__ == "__main__":
    main(sys.argv[1:])
