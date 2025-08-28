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
import logging
import getopt
import sys
import os
import stat
import re
from collections import defaultdict
from utils import Utils
from bmcgo.utils.tools import Tools

tool = Tools()
log = tool.log
MDS_REF = "$ref"
MDS_DEFS = "defs"
MDS_REF_INTERFACE = "refInterface"
MDS_PATH = "path"
MDS_PARENT = "parent"
MDS_STRUCT = "structs"


def no_need_filter(k):
    filter_list = ["usage", "notAllowNull", "readOnly", "default", "primaryKey", "critical"]
    return k not in filter_list


def is_excluded_intf(intf):
    return intf == "bmc.kepler.Object.Properties"


def is_usage_csr(property_data):
    return "usage" in property_data and "CSR" in property_data["usage"]


def update_type(property_data):
    new_property_data = {}
    if not isinstance(property_data, dict):
        return new_property_data
    if "description" in property_data and Utils.get_lua_codegen_version() >= 13:
        property_data.pop("description", "")
    if "baseType" in property_data:
        base_type = property_data.pop("baseType", "")
        if base_type == "Array":
            new_property_data = property_data.copy()
            new_property_data["type"] = "array"
            try:
                new_property_data["items"][MDS_REF] = new_property_data["items"][MDS_REF].replace(MDS_DEFS, MDS_STRUCT)
            except Exception as e:
                log.error(f"任务状态错误: {e}")
                raise Exception(f"未找到{MDS_REF}") from e
            return new_property_data

        if MDS_REF_INTERFACE in property_data:
            new_property_data[MDS_REF_INTERFACE] = property_data.pop(MDS_REF_INTERFACE, "")
        types = []
        types.append({MDS_REF: "base.json#/" + base_type})
        if property_data:
            types.append(property_data.copy())
        new_property_data["allOf"] = types.copy()
    if MDS_REF in property_data:
        new_property_data[MDS_REF] = property_data[MDS_REF].replace(MDS_DEFS, MDS_STRUCT)

    return new_property_data


def read_properties(properties, out_properties, is_intf_props):
    # properties only mark usage as C should deploy to csr schema
    props = list(p for p, v in properties.items() if is_intf_props or is_usage_csr(v))
    for index, prop in enumerate(props):
        # filter properties which no need for csr
        prop_alias = prop
        if not is_usage_csr(properties[prop]):
            prop_alias = properties[prop].pop("alias", prop)
            props[index] = prop_alias
            continue
        # if prop have alias, use alias name replace prop name
        if "alias" in properties[prop] and Utils.get_lua_codegen_version() >= 13:
            prop_alias = properties[prop].pop("alias", "")
            properties[prop]["title"] = prop
        out_properties[prop_alias] = {
            k: v
            for k, v in properties[prop].items()
            if no_need_filter(k)
        }
        if prop_alias != prop and Utils.get_lua_codegen_version() >= 13:
            out_properties[prop_alias] = update_type(out_properties[prop_alias])
            props[index] = prop_alias
        else:
            out_properties[prop] = update_type(out_properties[prop])
    return props


def read_defs(structs, data):
    for struct_name, struct_data in data[MDS_DEFS].items():
        properties = {k: v for k, v in struct_data.items()}
        for prop, prop_data in properties.items():
            properties[prop] = update_type(prop_data).copy()
        structs[struct_name] = {"type": "object", "properties": properties}


def get_duplicated_props(class_name, class_props):
    props_by_name = defaultdict(list)
    for props, intf_name in class_props:
        for prop_name, prop_data in props.items():
            if intf_name is None or not is_usage_csr(prop_data):
                continue
            props_by_name[prop_name].append(intf_name)
    duplicated_props = list()
    for prop_name, intf_names in props_by_name.items():
        if len(intf_names) > 1:
            duplicated_props.append(prop_name)
            log.error("类%s下不同接口%s配置了同名属性%s并且都配置了CSR，不生成到schema.json中",
                      class_name, ', '.join(intf_names), prop_name)
    return duplicated_props


def remove_duplicate_props(class_name, class_data):
    class_props = [(class_data.get("properties", {}), None)] # 元组第2个元素表示资源树接口，None为私有属性
    for intf_name, intf_data in class_data.get("interfaces", {}).items():
        if is_excluded_intf(intf_name):
            continue
        class_props.append((intf_data.get("properties", {}), intf_name))

    duplicated_props = get_duplicated_props(class_name, class_props)
    for props, _ in class_props:
        for prop_name in duplicated_props:
            if prop_name in props:
                del props[prop_name]


def read_interfaces(interfaces, out_properties, structs):
    intfs = {}
    for intf_name, intf in interfaces.items():
        # no properties also need interface name , because may be reference Object by other property for Devkit check
        intfs[intf_name] = {}
        if "properties" in intf:
            props = read_properties(intf["properties"], out_properties, not is_excluded_intf(intf_name))
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
        "w",
    ) as load_f:
        json.dump(csr_schema, load_f, indent=4)
        logging.info("schema 已经发生改变")


csr_schema_template = {
    MDS_DEFS: {},
    "id": "bmc",
    "type": "object",
    "patternProperties": {},
    "$schema": "https://json-schema.org/draft/2019-09/schema#",
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


def create_schema_class(interfaces, properties, class_data):
    class_def = {"properties": properties, "type": "object", "interfaces": interfaces}
    if MDS_PATH in class_data:
        class_def[MDS_PATH] = replace_colon(class_data[MDS_PATH])
    if MDS_PARENT in class_data:
        class_def[MDS_PARENT] = class_data[MDS_PARENT]
    class_def["additionalProperties"] = False
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
        if Utils.get_lua_codegen_version() < 13:
            remove_duplicate_props(class_name, class_data)
        properties = {}
        interfaces = {}
        if "interfaces" in class_data:
            interfaces = read_interfaces(
                class_data["interfaces"], properties, csr_schema[MDS_STRUCT]
            )
        if "properties" in class_data:
            _ = read_properties(class_data["properties"], properties, False)
        if MDS_DEFS in class_data:
            read_defs(csr_schema[MDS_STRUCT], class_data)
        # no properties means no properties mark usage C ,no need generic csr schema class
        if properties:
            csr_schema[MDS_DEFS][class_name] = create_schema_class(
                interfaces, properties, class_data
            )
            csr_schema["patternProperties"]["^" + class_name + "_"] = {
                MDS_REF: "#/defs/" + class_name
            }
    if MDS_DEFS in load_dict:
        read_defs(csr_schema[MDS_STRUCT], load_dict)


def generate(if_name, of_name, project_name):   
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

    csr_schema = csr_schema_template.copy()
    csr_schema[MDS_STRUCT] = {}
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith('_model.json'):
                file_path = os.path.join(root, file)
                load_f = os.fdopen(os.open(file_path, os.O_RDONLY, stat.S_IRUSR), "r")
                if_name = os.path.realpath(if_name)
                load_dict = json.load(load_f)

                filling_material(load_dict, csr_schema)
                load_f.close()

    save_csr_schema(of_name, csr_schema)



def usage():
    logging.info("gen_schema.py -i <inputfile> -o <outfile> -n <project_name>")


def main(argv):
    m_input = ""
    output = ""
    try:
        opts, _ = getopt.getopt(argv, "hi:o:n:", ["help", "input=", "out=", "project_name="])
    except getopt.GetoptError:
        help()
        return
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            return
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
    generate(m_input, output, project_name)


if __name__ == "__main__":
    main(sys.argv[1:])
