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
import getopt
import sys
import os
import stat
from copy import deepcopy
import mds_util as utils
from utils import Utils
from bmcgo.utils.tools import Tools


tool = Tools()
log = tool.log
PERSIST_TYPES = {
    "PermanentPer", "PoweroffPer", "ResetPer", "TemporaryPer", "PoweroffPerRetain",
    "ResetPerRetain", "TemporaryPerRetain", "Memory"
}

BACKUP_PERSIST_TYPES = {
    "PoweroffPer", "PoweroffPerRetain"
}

NO_BACKUP_PERSIST_TYPES = {
    "PermanentPer",
    "ResetPer",
    "TemporaryPer",
    "ResetPerRetain",
    "TemporaryPerRetain"
}

EXTEND_FIELD = "extend_field"

# 主键检查白名单：对于白名单中的数据库表，在自动生成代码时不强制要求配置主键
# 主键检查白名单的修改需经过评审
PERSIST_WHITE_LIST = {
    "t_ddr5_mem_ce_diagnosed_record",
    "t_hbm_fault_diagnosed_record"
}


def check_duplicate_public_name(names, all_names, prop, prop_data, class_name):
    if "alias" in prop_data:
        if prop_data["alias"] in names:
            raise RuntimeError(f"model.json中类{class_name}具有重复的资源树属性别名: {prop_data['alias']}")
        names[prop_data["alias"]] = True
        all_names[prop] = True
        all_names[prop_data["alias"]] = True
        return

    if prop in names:
        raise RuntimeError(f"model.json中类{class_name}具有重复的资源树属性名称: {prop}")
    names[prop] = True
    all_names[prop] = True


def check_duplicate_private_name(all_names, prop, class_name):
    if prop in all_names:
        raise RuntimeError(f"model.json中类{class_name}具有重复的私有属性名称: {prop}")
    all_names[prop] = True


def check_if_local(class_data):
    return "tableLocation" in class_data and class_data["tableLocation"] == "Local"


def ignore_persistence_if_local(class_data, prop_data):
    if check_if_local(class_data):
        if 'usage' in prop_data:
            del prop_data['usage']
    return prop_data


def make_private_properties(class_info, properties, index, names, imports):
    class_name = class_info["class_name"]
    class_data = class_info["class_data"]
    if "properties" not in class_data:
        return properties, index
    for prop, prop_data in class_data["properties"].items():
        if prop == "priority":
            continue
        if "alias" in prop_data:
            raise RuntimeError(f"model.json中类{class_name}的私有属性{prop}具有别名")
        check_duplicate_private_name(names["all_names"], prop, class_name)

        prop_data = ignore_persistence_if_local(class_data, prop_data) # 判断是否忽略usage字段
        t_property = utils.get_property(prop, prop_data, index)
        if "type" in t_property and t_property["type"] not in utils.ALLOW_BASIC_TYPES.values():
            t_property["type"] = t_property["type"].replace("defs_", "")
            if t_property["type"].startswith("def_types."):
                imports.add("model_types/def_types.proto")
            else:
                imports.add(f"json_types/{t_property['type'].split('.')[0]}.proto")

        properties.append(t_property)
        index = index + 1
    return properties, index


def make_public_properties(class_info, properties, index, names, imports):
    class_name = class_info["class_name"]
    class_data = class_info["class_data"]
    if "interfaces" not in class_data:
        return properties, index
    is_local = check_if_local(class_data)
    for interface, props in class_data["interfaces"].items():
        if (is_local or Utils.get_lua_codegen_version() >= 14) and interface == "bmc.kepler.Object.Properties":
            continue
        if "properties" not in props:
            continue
        for prop, prop_data in props["properties"].items():
            if prop == "priority":
                continue
            check_duplicate_public_name(names["pub_names"], names["all_names"], prop, prop_data, class_name)

            t_property = utils.get_property(prop, prop_data, index)
            if "type" in t_property and t_property["type"] not in utils.ALLOW_BASIC_TYPES.values():
                unique_intf_name = Utils.get_unique_intf_name(interface)
                t_property["type"] = t_property["type"].replace(
                    "defs.", unique_intf_name + ".")
                imports.add(f"json_types/{unique_intf_name}.proto")
            properties.append(t_property)

            index = index + 1
    return properties, index


def class_contains_global_persist_type(class_data: dict):
    return class_data.get("tableType", "") in PERSIST_TYPES


def prop_contains_persist_type(prop_config: dict):
    return bool(set(prop_config.get("usage", [])) & PERSIST_TYPES)


def get_props_with_persist_type(class_data: dict):
    props = []
    for prop_name, prop_config in class_data.get('properties', {}).items():
        if prop_contains_persist_type(prop_config):
            props.append(prop_name)

    for intf_data in class_data.get('interfaces', {}).values():
        for prop_name, prop_config in intf_data.get('properties', {}).items():
            if prop_contains_persist_type(prop_config):
                props.append(prop_name)
    return props


def prop_contains_csr(prop_configs):
    for prop_config in prop_configs.values():
        for t_usage in prop_config.get("usage", []):
            if t_usage == "CSR":
                return True

    return False


def contains_csr(class_data):
    if prop_contains_csr(class_data.get("properties", {})):
        return True

    for intf_data in class_data.get("interfaces", {}).values():
        if prop_contains_csr(intf_data.get("properties", {})):
            return True

    return False


def check_white_list(table_name):
    if table_name in PERSIST_WHITE_LIST:
        return True

    return False


def has_primary_key(class_data):
    for prop_config in class_data.get('properties', {}).values():
        if prop_config.get("primaryKey", False):
            return True

    for intf_data in class_data.get('interfaces', {}).values():
        for prop_config in intf_data.get('properties', {}).values():
            if prop_config.get("primaryKey", False):
                return True

    return False


def is_positive_integer(value):
    return isinstance(value, int) and value > 0


def gen_class_option(class_name, class_data):
    class_options = {"table_name": class_data["tableName"]}
    if "tableType" in class_data and class_data["tableType"]:
        class_options["table_type"] = class_data["tableType"]
    if "tableMaxRows" in class_data and Utils.get_lua_codegen_version() >= 11:
        if not is_positive_integer(class_data["tableMaxRows"]):
            raise RuntimeError(f"model.json中类{class_name}配置了'tableMaxRows字段', 但是类型不是正整数")
        class_options["table_max_rows"] = class_data["tableMaxRows"]
    return class_options


def need_gen_db(class_data, props_with_persist_type):
    if check_if_local(class_data):
        return True

    if class_data.get("tableType", "") in PERSIST_TYPES:
        return True
    
    return bool(props_with_persist_type)


def fill_table_type(backup_table_types, no_backup_table_types, table_type):
    if table_type in BACKUP_PERSIST_TYPES:
        backup_table_types.add(table_type)
    elif table_type in NO_BACKUP_PERSIST_TYPES:
        no_backup_table_types.add(table_type)


def fill_properties_table_type(global_type, properties, conflict_props, backup_table_types, no_backup_table_types):
    for prop_name, prop_config in properties.items():
        u = deepcopy(prop_config.get("usage", []))
        if not prop_contains_persist_type(prop_config):
            if global_type:
                u.append(global_type)

        if not bool(set(u) & BACKUP_PERSIST_TYPES):
            if prop_config.get("notAllowNull", False) and not prop_config.get("primaryKey", False) \
                and "default" not in prop_config:
                conflict_props.append(prop_config.get("alias", prop_name))

        for table_type in u:
            fill_table_type(backup_table_types, no_backup_table_types, table_type)


def check_table_type_consistency(class_name, class_data):
    backup_table_types = set()
    no_backup_table_types = set()
    conflict_props = []

    global_type = class_data.get("tableType", None)

    fill_properties_table_type(global_type, class_data.get('properties', {}), conflict_props, backup_table_types,
        no_backup_table_types)

    for intf_data in class_data.get('interfaces', {}).values():
        fill_properties_table_type(global_type, intf_data.get('properties', {}), conflict_props, backup_table_types,
            no_backup_table_types)

    if not contains_csr(class_data) and backup_table_types and conflict_props:
        raise RuntimeError(f"请为类{class_name}的属性{conflict_props}配置默认值或允许属性为null，否则可能出现恢复数据到内存数据库失败的问题")
    
    if backup_table_types and no_backup_table_types:
        log.warning(f"类{class_name}配置了多种持久化类型，支持备份机制的{backup_table_types}与不支持备份机制的{no_backup_table_types}混用，" + 
            "在主数据库文件丢失、从备份数据库恢复数据时，可能出现数据不一致的问题")

    if "PermanentPer" in no_backup_table_types and (len(no_backup_table_types) > 1 or len(backup_table_types) > 0):
        log.warning(f"类{class_name}同时配置了PermanentPer和其他持久化类型，掉电场景下可能出现数据不一致的问题")


def make_datas(load_dict, package, imports, is_local):
    datas = []

    for class_name, class_data in load_dict.items():
        props_with_persist_type = get_props_with_persist_type(class_data)
        data_need_persist = class_contains_global_persist_type(class_data) or bool(props_with_persist_type)
        if "tableName" not in class_data:
            if data_need_persist:
                raise RuntimeError(f"model.json中类{class_name}配置了持久化但是没有配置'tableName'")
            continue

        if Utils.get_lua_codegen_version() >= 14 and not need_gen_db(class_data, props_with_persist_type):
            continue

        table_name = class_data["tableName"]
        if table_name.startswith("_"):
            raise RuntimeError(f"model.json中类{class_name}配置的'tableName' {table_name}不能以保留字符'_'开头")

        if check_if_local(class_data) != is_local: # 与本地持久化标志不一致则跳过
            continue

        if Utils.get_lua_codegen_version() < 11:
            if data_need_persist and not is_local and not has_primary_key(class_data):
                raise RuntimeError(f"model.json中类{class_name}配置了远程持久化但是没有配置'primaryKey'")
        else:
            if data_need_persist and not has_primary_key(class_data) and not check_white_list(table_name):
                raise RuntimeError(f"model.json中类{class_name}配置了持久化但是没有配置'primaryKey'")

        if is_local and props_with_persist_type:
            log.warning("model.json中类%s配置了本地持久化，持久化类型以'tableType'字段值为准，其属性%s在usage中配置的持久化类型是无效的",
                            class_name, ', '.join(props_with_persist_type))
        elif Utils.get_lua_codegen_version() >= 14:
            check_table_type_consistency(class_name, class_data)

        names = {"pub_names": {}, "all_names": {}}
        class_options = {}
        index = 1
        properties = []

        class_options = gen_class_option(class_name, class_data)
        class_info = {
            "class_name": class_name,
            "class_data": class_data
            }
        properties, index = make_public_properties(class_info, properties, index, names, imports)
        properties, index = make_private_properties(class_info, properties, index, names, imports)

        if index > 1:
            datas.append(
                {
                    "package": package,
                    "name": class_name,
                    "options": class_options,
                    "type": "Message",
                    "properties": properties,
                    "nested_type": [],
                }
            )
    return datas


def get_property(prop_name, properties):
    for item in properties:
        if item['name'] == prop_name:
            return item
    
    return None


def rectify_local_db(historical_local_db_file, out_dict):
    if not os.path.exists(historical_local_db_file):
        return

    load_f = os.fdopen(os.open(historical_local_db_file, os.O_RDONLY, stat.S_IRUSR), "r")
    load_dict = json.load(load_f)
    for table_info in out_dict["data"]:
        class_name = table_info["name"]
        properties = table_info["properties"]
        historical_table_info = load_dict.get(class_name, [])
        if not historical_table_info:
            continue

        historical_props = set()
        for item in historical_table_info:
            historical_props.add(item['name'])
        props = set()
        for item in properties:
            props.add(item['name'])
        
        deleted_props = historical_props - props
        if deleted_props:
            raise RuntimeError(f"使用deprecated关键字废弃{class_name}类中不再使用的属性{deleted_props},而不是直接删除属性")
        
        new_props = []
        for item in historical_table_info:
            prop = get_property(item['name'], properties)
            prop["options"][EXTEND_FIELD] = item[EXTEND_FIELD]
            new_props.append(prop)
            prop["id"] = len(new_props)
        
        added_props = sorted(list(props - historical_props))
        for prop_name in added_props:
            prop = get_property(prop_name, properties)
            prop["options"][EXTEND_FIELD] = True
            new_props.append(prop)
            prop["id"] = len(new_props)
        
        table_info["properties"] = new_props


def save_json_file(is_local, load_dict, historical_local_db_file, of_name, disable_gen=False):
    package = of_name.split("/")[-2]
    extra_imports = set()
    datas = make_datas(load_dict, package, extra_imports, is_local)
    extra_imports = sorted(extra_imports)

    imports = [
        "google/protobuf/descriptor.proto",
        "ipmi_types.proto",
        "types.proto"
    ]
    imports.extend(extra_imports)
    dependency = ["types.proto"]
    dependency.extend(extra_imports)

    out_dict = {
        "imports": imports,
        "dependency": dependency,
        "data": datas,
        "service": [],
        "filename": "database.proto",
        "package": package.capitalize() + "DB",
        "options": {},
        "disable_gen": disable_gen
    }
    if is_local:
        rectify_local_db(historical_local_db_file, out_dict)
        segs = of_name.split("/")
        segs[-1] = "local_" + segs[-1] # -1 表示以/为间隔符拆分的最后一段
        of_name = '/'.join(segs)
    utils.save_proto_json(of_name, out_dict)


def generate(if_name, historical_local_db_file, of_name):
    if not os.path.exists(if_name):
        return
    load_f = os.fdopen(os.open(if_name, os.O_RDONLY, stat.S_IRUSR), "r")
    load_dict = json.load(load_f)
    load_f.close()
    disable_mem_db_gen = Utils.get_lua_codegen_version() >= 7 and not Utils.check_model_need_mem_db(load_dict)
    save_json_file(False, load_dict, historical_local_db_file, of_name, disable_gen=disable_mem_db_gen) # 保存普通持久化的表
    save_json_file(True, load_dict, historical_local_db_file, of_name)  # 保存本地持久化的表


def usage():
    logging.info("gen_db_json.py -i <inputfile> -o <file>")


def main(argv):
    m_input = ""
    output = ""
    try:
        opts, _ = getopt.getopt(argv, "hi:m:o:d:", ["help", "input=", "history=", "out="])
    except getopt.GetoptError:
        help()
        return
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            return
        elif opt in ("-i", "--input"):
            m_input = arg
        elif opt in ("-m", "--history"):
            m_hisctory = arg
        elif opt in ("-o", "--out"):
            output = arg
        else:
            raise RuntimeError("不支持的选项: {}".format(opt))
    if not m_input or not output:
        usage()
        return
    generate(m_input, m_hisctory, output)


if __name__ == "__main__":
    main(sys.argv[1:])
