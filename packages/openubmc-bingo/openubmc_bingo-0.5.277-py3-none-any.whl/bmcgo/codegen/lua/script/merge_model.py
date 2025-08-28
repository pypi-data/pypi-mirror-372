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
from collections import OrderedDict
import mds_util as utils
from utils import Utils
from bmcgo.utils.tools import Tools


tool = Tools()
log = tool.log
OPTIONS_SETTING = ["explicit", "volatile"]
CHECK_PROPS_SETTINGS = ["usage", "alias", "primaryKey", "uniqueKey", "privilege", "default", "featureTag", "critical",
        "notAllowNull", "refInterface", "displayDescription", "sensitive"]
DEPRECATED = "deprecated"


def save_file(of_name, model_new):
    if os.path.exists(of_name):
        with os.fdopen(os.open(of_name, os.O_RDONLY, stat.S_IRUSR), "r") as load_f:
            if json.load(load_f) == model_new:
                logging.info("schema 未发生更改")
                return

    with os.fdopen(
        os.open(
            of_name, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IWUSR | stat.S_IRUSR
        ),
        "w", encoding="utf-8"
    ) as load_f:
        json.dump(model_new, load_f, ensure_ascii=False, indent=4)
        logging.info("schema 已经更改")


def fill_req_optional(intf_info, prop, properties, prop_data):
    if "req" not in properties[prop] or "req" not in prop_data:
        return
    
    class_name, intf_name = intf_info["class_name"], intf_info["intf_name"]
    has_optional = False
    for req_param, req_param_data in prop_data["req"].items():
        op = properties[prop]["req"].get(req_param, {}).get('optional', False)
        if not op:
            if has_optional:
                raise RuntimeError(f"model.json中{class_name}类{intf_name}接口的{prop}方法不满足所有可选参数在入参列表的末尾")
            continue

        has_optional = True
        default = properties[prop]["req"].get(req_param, {}).get('default')
        if default is None:
            raise RuntimeError(f"model.json中{class_name}类{intf_name}接口的{prop}方法的可选入参{req_param}未配置default字段")
        req_param_data["optional"] = op
        req_param_data["default"] = default


def fill_req_displaydescription(intf_info, prop, properties, prop_data):
    if "req" not in properties[prop] or "req" not in prop_data:
        return

    class_name, intf_name = intf_info["class_name"], intf_info["intf_name"]
    for req_param, req_param_data in prop_data["req"].items():
        display_des = properties[prop]["req"].get(req_param, {}).get('displayDescription', False)
        if not display_des:
            continue
        
        req_param_data["displayDescription"] = display_des


def get_options_from_mds(prop, properties, prop_data):
    if "options" not in properties[prop]:
        return
    for option in OPTIONS_SETTING:
        if option in properties[prop]["options"]:
            prop_data["options"] = prop_data.get("options", {})
            prop_data["options"][option] = properties[prop]["options"].get(option)


def merge_props_and_data(intf_info, prop, properties, prop_data, check_props):
    if prop not in properties:
        properties[prop] = {}
    else:
        if Utils.get_lua_codegen_version() >= 16:
            fill_req_optional(intf_info, prop, properties, prop_data)
            fill_req_displaydescription(intf_info, prop, properties, prop_data)

        if Utils.get_lua_codegen_version() >= 18:
            get_options_from_mds(prop, properties, prop_data)

        for check_prop in check_props:
            if properties[prop].get(check_prop, False):
                prop_data[check_prop] = properties[prop].get(check_prop)
    properties[prop] = prop_data


def merge_when_intf_exist(model, intf, item, class_name, intf_name):
    check_props = CHECK_PROPS_SETTINGS

    if Utils.get_lua_codegen_version() >= 16:
        check_props.append("cmdName")
        check_props.append("displayDescription")

    if item not in intf:
        if item in model:
            model.pop(item)
        return

    if item not in model:
        model[item] = {}

    properties = model[item]
    for prop in list(properties):
        label = "方法" if item == "methods" else "信号"
        if prop in intf[item]:
            if intf[item][prop].get(DEPRECATED, False):
                log.warning(f"model.json中类{class_name}接口{intf_name}的{label}{prop}已废弃")
            continue
        raise RuntimeError(f"model.json中类{class_name}接口{intf_name}的{label}{prop}在mdb_interface中没有被定义")

    intf_info = {"class_name": class_name, "intf_name": intf_name}
    for prop, prop_data in intf[item].items():
        merge_props_and_data(intf_info, prop, properties, prop_data, check_props)


def copy_when_exist(model, intf, prop):
    if prop in intf:
        model[prop] = intf[prop]


def merge_model_intf(intf_data, model_intf, class_name, intf_name):
    mdb_props = intf_data.get("properties", {})
    if "properties" not in model_intf:
        model_intf["properties"] = {}
    model_props = model_intf["properties"]
    for prop in model_props.keys():
        if prop not in mdb_props:
            raise RuntimeError(f"model.json中类{class_name}接口{intf_name}的属性{prop}在mdb_interface中没有被定义")
        if mdb_props[prop].get(DEPRECATED, False):
            log.warning(f"model.json中类{class_name}接口{intf_name}的属性{prop}已废弃")
    if mdb_props and "virtual" in intf_data:
        model_props["priority"] = {
            "baseType": "U8",
            "default": 0
            if "priority" not in model_intf
            else model_intf["priority"],
        }
    intf_info = {"class_name": class_name, "intf_name": intf_name}
    for prop, prop_data in mdb_props.items():
        merge_props_and_data(intf_info, prop, model_props, prop_data, CHECK_PROPS_SETTINGS)

    merge_when_intf_exist(model_intf, intf_data, "methods", class_name, intf_name)
    merge_when_intf_exist(model_intf, intf_data, "signals", class_name, intf_name)
    copy_when_exist(model_intf, intf_data, "package")
    copy_when_exist(model_intf, intf_data, "virtual")
    copy_when_exist(model_intf, intf_data, "default")


def append_object_prop_intf(mds_data, mdb_data):
    object_prop_intf = "bmc.kepler.Object.Properties"
    if object_prop_intf not in mds_data:
        mds_data[object_prop_intf] = {}
    if object_prop_intf not in mdb_data:
        mdb_data.append(object_prop_intf)


def merge_model_class(class_name, mds_class, mdb_obj, mdb_path):
    if "package" in mdb_obj[class_name]:
        mds_class["package"] = mdb_obj[class_name]["package"]
    append_object_prop_intf(mds_class["interfaces"], mdb_obj[class_name]["interfaces"])
    for intf_name in mdb_obj[class_name]["interfaces"]:
        if intf_name not in mds_class["interfaces"]:
            raise RuntimeError(f"model.json中类{class_name}未配置资源树接口{intf_name}")
        if mds_class["interfaces"][intf_name].get(DEPRECATED, False):
            log.warning(f"model.json中类{class_name}配置了已废弃的资源数接口{intf_name}")
        for item in mds_class["interfaces"][intf_name]:
            if item not in ["properties", "methods", "signals", "privilege"]:
                raise RuntimeError(f"model.json中类{class_name}接口{intf_name}的字段{item}超出取值范围")

        intf_json = utils.get_intf(intf_name, mdb_path)
        if "implement" in intf_json[intf_name]:
            mds_class["interfaces"][intf_name] = utils.generate_default(
                intf_json, mdb_path
            )[intf_name]
        if "defs" in intf_json:
            mds_class["interfaces"][intf_name]["defs"] = intf_json["defs"]

        merge_model_intf(intf_json[intf_name], mds_class["interfaces"][intf_name], class_name, intf_name)
    mds_class["interfaces"]["bmc.kepler.Object.Properties"].pop("methods", None)
    defs = mds_class["interfaces"]["bmc.kepler.Object.Properties"].get("defs", None)
    if defs is not None:
        defs.pop("Options", None)


def get_class_name(path):
    return list(filter(None, path.split("/")))[-1]


def get_parent_path(origin_model, class_data):
    if "parent" in class_data and class_data["parent"] in origin_model and \
                "path" in origin_model[class_data["parent"]]:
        return get_parent_path(origin_model, origin_model[class_data["parent"]]) \
            + "/" + utils.cut_ids(class_data["path"])
    else:
        return utils.cut_ids(class_data["path"])


def check_class_property_name_conflict(class_name, class_data):
    prop_names = {}

    for prop_name, prop_config in class_data.get("properties", {}).items():
        name = prop_config.get('alias', prop_name)
        if name in prop_names:
            raise RuntimeError(f"在model.json文件{class_name}类中发现重名私有属性{prop_name}")
        else:
            prop_names[name] = True

    for interface, intf_data in class_data.get("interfaces", {}).items():
        for prop_name, prop_config in intf_data.get("properties", {}).items():
            name = prop_config.get('alias', prop_name)
            if name in prop_names:
                raise RuntimeError(f"在model.json文件{class_name}类的{interface}接口中发现重名资源树属性{prop_name}")
            else:
                prop_names[name] = True


def check_property_name_conflict(origin_model):
    for class_name, class_data in origin_model.items():
        check_class_property_name_conflict(class_name, class_data)


def merge_model(origin_model, mdb_path):
    for class_name, class_data in origin_model.items():
        if "path" in class_data and class_name != "defs":
            class_path = get_parent_path(origin_model, class_data)
            mdb_obj = utils.get_path(class_name, mdb_path, class_path)
            merge_model_class(class_name, class_data, mdb_obj, mdb_path)

    check_property_name_conflict(origin_model)


def save_merged_json(of_name, model):
    paths = of_name.split("/")
    paths.pop()
    merged_json_path = os.path.realpath(("/").join(paths))
    if not os.path.exists(merged_json_path):
        os.mkdir(merged_json_path)
    save_file(of_name, model)


def check_method_cmd_name(class_name, intf_name, method, method_data, cmds):
    if "cmdName" in method_data:
        cmd_name = method_data["cmdName"]
        if cmd_name in cmds:
            if intf_name != cmds[cmd_name][0] or method != cmds[cmd_name][1]:
                raise RuntimeError(f"model.json文件的{class_name}类的{intf_name}接口的{method}方法的cmdName {cmd_name}已被使用，请重新命名")
        else:
            cmds[cmd_name] = [intf_name, method]


def check_cmd_name(mds_class, cmd_file):
    cmds = {}
    if os.path.exists(cmd_file):
        load_f = os.fdopen(os.open(cmd_file, os.O_RDONLY, stat.S_IRUSR), "r")
        try:
            cmds = OrderedDict(json.load(load_f))
        except json.JSONDecodeError as e:
            log.debug(f"JSON 解析错误: {e}")
        load_f.close()

    for class_name, class_data in mds_class.items():
        for intf_name, intf_data in class_data.get("interfaces", {}).items():
            for method, method_data in intf_data.get("methods", {}).items():
                check_method_cmd_name(class_name, intf_name, method, method_data, cmds)

    save_file(cmd_file, cmds)


def generate(if_name, of_name, mdb_path, cmd_file):
    load_dict = {}
    if os.path.exists(if_name):
        load_f = os.fdopen(os.open(if_name, os.O_RDONLY, stat.S_IRUSR), "r")
        load_dict = OrderedDict(json.load(load_f))
        load_f.close()

    if Utils.get_lua_codegen_version() >= 16:
        check_cmd_name(load_dict, cmd_file)
    merge_model(load_dict, mdb_path)
    save_merged_json(of_name, load_dict)


def usage():
    logging.info("gen_schema.py -i <inputfile> -o <outfile>")


def main(argv):
    m_input = ""
    output = ""
    mdb_path = ""
    try:
        opts, _ = getopt.getopt(
            argv, "hi:o:d:c:", ["help", "input=", "out=", "mdb_interfac_path", "cmdfile="]
        )
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
        elif opt in ("-d", "--dir"):
            mdb_path = arg
        elif opt in ("-c", "--cmdfile"):
            cmd_file = arg
        else:
            raise RuntimeError("不支持的选项: {}".format(opt))
    if not m_input or not output:
        usage()
        return
    generate(m_input, output, mdb_path, cmd_file)


if __name__ == "__main__":
    main(sys.argv[1:])
