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
import re
import mds_util as utils
from utils import Utils
from bmcgo.utils.tools import Tools

PROP_PRIORITY = "priority"
PROP_LOCAL = "LocalPer"

PROP_REMOTE = "RemotePer"
CLASS_PRIVATE = "private_class"
INTERFACES = "interfaces"
METHODS = "methods"
SIGNALS = "signals"
NEED_MEM_DB = "need_mem_db"
KLASS = "class"
PATH = "path"
PATHS = "paths"
DEFS = "defs"
ITEMS = ["dep_properties", "dep_methods", "dep_signals"]
DEPRECATED = "deprecated"

tool = Tools()
log = tool.log


class InterfaceDep:
    def __init__(self, required: dict):
        self.name = required.get("interface", "")
        self.optional = required.get("optional", False)
        self.stage = required.get("stage", "running")
        self.dep_properties = ["*"]
        self.dep_methods = ["*"]
        self.dep_signals = ["*"]
        if "properties" in required:
            self.dep_properties = []
            for prop, prop_config in required["properties"].items():
                if "subscribe" in prop_config:
                    self.dep_properties.append(prop)
        
        if "methods" in required:
            self.dep_methods = list(required["methods"].keys())

        if "signals" in required:
            self.dep_signals = list(required["signals"].keys())

        if "paths" in required:
            self.paths = required[PATHS]


def save_service(service, intf_imports, paths, of_name, path_level):
    service_json_path, ipmi_json_path = paths.get('service_json_path', ''), paths.get('ipmi_json_path', '')
    load_f = utils.open_file(service_json_path)
    load_dict = json.load(load_f)
    imports = [
        "google/protobuf/descriptor.proto",
        "types.proto",
        "google/protobuf/empty.proto",
    ]
    opt = {}
    if PROP_LOCAL in intf_imports:
        for local_per_type in intf_imports[PROP_LOCAL]:
            opt["has_local_" + local_per_type.lower()[:-3]] = True
    if intf_imports.get(PROP_REMOTE):
        opt["has_remote_per"] = True
    class_require = intf_imports[KLASS]
    handled_intf_imports = {}
    for k, v in intf_imports["intf"].items():
        if v['interface'].startswith('bmc.dev.'):
            handled_intf_imports[os.path.join('../device_types/' + k)] = v
        else:
            handled_intf_imports[k] = v

    has_ipmi_cmd = False
    if os.path.exists(ipmi_json_path):
        with open(ipmi_json_path, "r", encoding="utf-8") as fd:
            ipmi_data = json.load(fd)
            if ipmi_data.get('cmds', {}):
                has_ipmi_cmd = True

    intf_imports_old = handled_intf_imports.keys()
    intf_imports_tmp = list(map(lambda x: x + ".proto", intf_imports_old))
    depends = ["types.proto", "google/protobuf/empty.proto"]
    datas = {
        "imports": imports + intf_imports_tmp,
        "dependency": depends,
        "intf_imports": intf_imports["intf"],
        "class_require": class_require,
        "private_class_require": intf_imports.get(CLASS_PRIVATE, {}),
        "data": [],
        INTERFACES: service[INTERFACES],
        METHODS: service[METHODS],
        SIGNALS: service[SIGNALS],
        "has_ipmi_cmd": has_ipmi_cmd,
        "package": load_dict['name'],
        "options": opt,
        NEED_MEM_DB: service.get(NEED_MEM_DB, False)
    }

    ## 匹配APP下的service_json_path目录，如果是扩展组件，层级为3
    if path_level != 0:
        datas['path_level'] = path_level

    utils.save_proto_json(of_name, datas)


def check_duplicate(services, method_name):
    for method in services:
        if method["name"] == method_name:
            return True
    return False


def get_require_by_path(path, class_name):
    if path == "*":
        return path
    path = utils.cut_ids(path)
    path = os.path.realpath(path)
    return "mdb" + path.replace("/", ".") + "." + class_name


def get_intf_impl(intf_data):
    return "" if "implement" not in intf_data else intf_data["implement"]


def fill_imports(imports, intf_data, intf, class_path, class_name):
    intf_class = Utils.get_unique_intf_name(intf)
    imports["intf"][intf_class] = {
        "interface": intf,
        "default": get_intf_impl(intf_data),
        "data": {intf: intf_data},
    }
    if class_path != "*":
        imports[KLASS][class_name] = {
            PATH: class_path.replace("${", ":").replace("}", ""),
            PROP_PRIORITY: 0 if PROP_PRIORITY not in intf_data else intf_data[PROP_PRIORITY],
        }


def get_override(intf_data, method_name):
    override = True
    if "non_overrides" in intf_data:
        override = method_name not in intf_data["non_overrides"]

    return override


def get_intf_default(intf_data):
    return (
        ""
        if "default" not in intf_data
        else utils.get_intf_package_name(intf_data["default"])
    )


def check_interface_duplicate(interfaces, interface, intf_name, intf_data):
    for intf in interfaces:
        if intf["name"] == interface and PATHS not in intf_data and PATHS not in intf:
            return True

        if intf["interface"] == intf_name and PATHS in intf_data and PATHS in intf:
            return True
    return False


def generate_interface(class_name, intf_data, interfaces, intf, class_path):
    intf_class = Utils.get_unique_intf_name(intf)
    interface = class_name + intf_class
    if check_interface_duplicate(interfaces, interface, intf, intf_data):
        return
    if intf_data.get(DEPRECATED, False):
        log.warning(f"在service.json中配置了已废弃的依赖项, interface: {intf}")

    for item in ITEMS:
        values = intf_data.get(item, [])
        if values == ["*"]:
            continue
        if values and set(values) == set(intf_data.get(item[4:], {}).keys()):
            intf_data[item] = ["*"]
            continue
        for value in values:
            if not intf_data.get(item[4:], {}).get(value, {}):
                raise Exception(f"在service.json中配置了不存在的依赖项, interface: {intf}, item: {value}")
            if intf_data.get(item[4:], {}).get(value, {}).get(DEPRECATED, False):
                log.warning(f"在service.json中配置了已废弃的依赖项, interface: {intf}, item: {value}")

    
    interface_data = {
        "name": interface,
        KLASS: class_name,
        PATH: utils.get_real_path(class_path),
        "interface": intf,
        "intf_class": intf_class,
        "virtual": "virtual" in intf_data,
        "implement": get_intf_impl(intf_data),
        "default": get_intf_default(intf_data),
        "full_path": class_path,
        "retry": intf_data.get("retry", False),
        "dep_properties": intf_data.get("dep_properties", ["*"]),
        "dep_methods": intf_data.get("dep_methods", ["*"]),
        "dep_signals": intf_data.get("dep_signals", ["*"])
    }

    if PATHS in intf_data:
        interface_data[PATHS] = intf_data[PATHS]

    interfaces.append(interface_data)


def generate_method(class_name, intf_data, methods, intf, class_path):
    if not intf_data.get(METHODS, {}):
        return

    intf_class = Utils.get_unique_intf_name(intf)
    for method_name in intf_data[METHODS].keys():
        dep_methods = intf_data.get("dep_methods", ["*"])
        if dep_methods != ["*"] and method_name not in intf_data.get("dep_methods", []):
            continue
        method = "".join([class_name, intf_class, method_name])
        if check_duplicate(methods, method):
            continue
        req_name = method_name + "Req"
        rsp_name = method_name + "Rsp"

        method_data = {
            "name": method,
            "func_name": method_name,
            KLASS: class_name,
            "req": "." + intf_class + "." + req_name,
            "rsp": "." + intf_class + "." + rsp_name,
            PATH: utils.get_real_path(class_path),
            "interface": intf,
            "intf_class": intf_class,
            "virtual": "virtual" in intf_data,
            "implement": get_intf_impl(intf_data),
            "default": get_intf_default(intf_data),
            "override": get_override(intf_data, method_name),
            "full_path": class_path,
            "retry": intf_data.get("retry", False)
        }

        if PATHS in intf_data:
            method_data[PATHS] = intf_data[PATHS]
            
        methods.append(method_data)


def generate_signal(class_name, intf_data, signals, intf, class_path):
    if SIGNALS not in intf_data or len(intf_data[SIGNALS]) == 0:
        return

    intf_class = Utils.get_unique_intf_name(intf)
    for signal_name in intf_data[SIGNALS].keys():
        dep_signals = intf_data.get("dep_signals", ["*"])
        if dep_signals != ["*"] and signal_name not in intf_data.get("dep_signals", []):
            continue
        signal = class_name + intf_class + signal_name
        if check_duplicate(signals, signal):
            continue
        sig_name = signal_name + "Signature"
        signals.append(
            {
                "name": signal,
                "signal_name": signal_name,
                KLASS: class_name,
                "signature": "." + intf_class + "." + sig_name,
                PATH: class_path,
                "interface": intf,
                "intf_class": intf_class,
            }
        )


def prepare_virutal(intf_data):
    if "virtual" in intf_data:
        intf_data["properties"][PROP_PRIORITY] = {
            "baseType": "U8",
        }


def prepare_intf_data(intf_data, intf_dep: InterfaceDep):
    intf = intf_dep.name
    if DEFS in intf_data:
        intf_data[intf][DEFS] = intf_data[DEFS]
    prepare_virutal(intf_data)
    intf_data[intf]["retry"] = not intf_dep.optional and intf_dep.stage == "running"
    for item in ITEMS:
        intf_data[intf][item] = getattr(intf_dep, item)
    if Utils.get_lua_codegen_version() >= 17:
        if hasattr(intf_dep, PATHS):
            intf_data[intf][PATHS] = getattr(intf_dep, PATHS)


def generate_path_interface(load_dict, service, imports, mdb_path, intf_dep: InterfaceDep):
    intf = intf_dep.name
    for class_name, class_data in load_dict.items():
        if INTERFACES in class_data:
            intf_data = utils.get_intf(intf, mdb_path)
            if "implement" in intf_data[intf]:
                intf_data = utils.generate_default(intf_data, mdb_path)
            prepare_intf_data(intf_data, intf_dep)
            generate_interface(
                class_name,
                intf_data[intf],
                service[INTERFACES],
                intf,
                class_data[PATH],
            )
            generate_method(
                class_name,
                intf_data[intf],
                service[METHODS],
                intf,
                class_data[PATH],
            )
            generate_signal(
                class_name,
                intf_data[intf],
                service[SIGNALS],
                intf,
                class_data[PATH],
            )
            fill_imports(imports, intf_data[intf],
                         intf, class_data[PATH], class_name)


def check_local_location(class_data, imports):
    if class_data.get("tableLocation", "") != "Local":
        return
    if PROP_LOCAL not in imports:
        imports[PROP_LOCAL] = {}
    imports[PROP_LOCAL][class_data.get("tableType", "PoweroffPer")] = True


def check_remote_per(class_data):
    if "tableName" not in class_data or class_data.get("tableLocation") == "Local":
        return False
    if "tableType" in class_data:
        return True
    class_props = list(class_data.get("properties", {}).values())
    for intf_data in class_data.get(INTERFACES, {}).values():
        class_props.extend(intf_data.get("properties", {}).values())

    for prop_data in class_props:
        for item in prop_data.get("usage", []):
            if "Per" in item:
                return True
    return False


def generate_service(model_merged_file, of_name, service_json_path, ipmi_json_path, path_level):
    load_f = utils.open_file(model_merged_file)
    load_dict = json.load(load_f)

    interfaces = []
    methods = []
    signals = []
    imports = {"intf": {}, KLASS: {}, CLASS_PRIVATE: {}}
    imports[PROP_REMOTE] = False
    for class_name, class_data in load_dict.items():
        imports[PROP_REMOTE] = imports[PROP_REMOTE] or check_remote_per(class_data)
        check_local_location(class_data, imports)
        if INTERFACES not in class_data:
            if CLASS_PRIVATE in imports:
                imports[CLASS_PRIVATE][class_name] = {"data": class_data}
            continue

        for intf_name, intf_data in class_data[INTERFACES].items():
            generate_interface(
                class_name,
                intf_data,
                interfaces,
                intf_name,
                class_data[PATH],
            )
            generate_method(
                class_name,
                intf_data,
                methods,
                intf_name,
                class_data[PATH],
            )
            generate_signal(
                class_name,
                intf_data,
                signals,
                intf_name,
                class_data[PATH],
            )
            fill_imports(imports, intf_data, intf_name,
                         class_data[PATH], class_name)
        if class_name not in imports[KLASS]:
            imports[KLASS][class_name] = {PATH: class_data[PATH]}
        imports[KLASS][class_name]["data"] = class_data

    service = {INTERFACES: interfaces, METHODS: methods, SIGNALS: signals}
    service[NEED_MEM_DB] = Utils.check_model_need_mem_db(load_dict)
    paths = {"service_json_path": service_json_path, "ipmi_json_path": ipmi_json_path}
    save_service(service, imports, paths, of_name, path_level)
    load_f.close()


def get_class_name(path):
    pos = -2 if path.endswith("/") else -1
    return path.split("/")[pos]


def generate_only_interface(intf_dep: InterfaceDep, service, imports, mdb_path):
    intf = intf_dep.name
    intf_data = utils.get_intf(intf, mdb_path)
    if "implement" in intf_data[intf]:
        intf_data = utils.generate_default(intf_data, mdb_path)

    prepare_intf_data(intf_data, intf_dep)
    generate_interface(
        "",
        intf_data[intf],
        service[INTERFACES],
        intf,
        "*",
    )
    generate_method(
        "",
        intf_data[intf],
        service[METHODS],
        intf,
        "*",
    )
    generate_signal(
        "",
        intf_data[intf],
        service[SIGNALS],
        intf,
        "*",
    )
    fill_imports(imports, intf_data[intf], intf, "*", "")


def fill_client_intf(service, imports, mdb_path, required, path):
    intf_dep = InterfaceDep(required)
    intf_seg = (intf_dep.name).split('.')
    if len(intf_seg) >= 3 and intf_seg[2] == 'Debug':
        raise Exception(f"在service.json中配置了调试版本的依赖项, interface: {intf_dep.name}")
    if path != "*":
        class_name, path_json = utils.get_path_by_interface(mdb_path, required["interface"], path)
        generate_path_interface(
            path_json, service, imports, mdb_path, intf_dep
        )

        if class_name not in imports[KLASS]:
            imports[KLASS][class_name] = {}
        imports[KLASS][class_name]["data"] = path_json[class_name]
    else:
        generate_only_interface(
            intf_dep, service, imports, mdb_path
        )


def check_multiple_paths(interfaces):
    intf_map = {}
    for intf in interfaces:
        intf_name = intf["interface"]
        if intf_name in intf_map and PATHS in intf:
            raise Exception(f"service.json中{intf_name}接口配置了多个paths依赖")
        if PATHS in intf:
            intf_map[intf_name] = True


def generate_client(service_file, output, mdb_path, mds_path, path_level):
    load_f = utils.open_file(service_file)
    service_dict = json.load(load_f)

    imports = {"intf": {}, KLASS: {}}
    if "required" not in service_dict:
        load_f.close()
        return

    if Utils.get_lua_codegen_version() >= 17:
        check_multiple_paths(service_dict["required"])

    interfaces = []
    methods = []
    signals = []
    service = {INTERFACES: interfaces, METHODS: methods, SIGNALS: signals}
    for required in service_dict["required"]:
        if PATH in required:
            fill_client_intf(service, imports, mdb_path, required, required[PATH])
            continue

        if Utils.get_lua_codegen_version() >= 17:
            if PATHS not in required:
                continue
            for path in required[PATHS]:
                fill_client_intf(service, imports, mdb_path, required, path)

    paths = {"service_json_path": mds_path}
    save_service(service, imports, paths, output, path_level)
    load_f.close()


def usage():
    logging.info(
        "gen_intf_rpc_json.py -i <inputfile> -d<mdb_path> -o<outputfile> -c<client> -s<service_json_path>"
    )


def count_dir_level(path):
    level = 0
    while True:
        path = os.path.dirname(path)
        if path == '/':
            break
        level += 1
    return level


## 匹配APP下的service_json_path目录，如果是扩展组件，层级为3
def match_level(service_json_path):
    path_level = 0
    match = re.search(r'.*(/[^/]+/mds/.*)', service_json_path)
    if match:
        mds_path = match.group(1)
        path_level = count_dir_level(mds_path)
    return path_level


def main(argv):
    m_input = ""
    output = ""
    mdb_path = ""
    service_json_path = ""
    try:
        opts, _ = getopt.getopt(
            argv,
            "hi:o:d:s:p:cx",
            ["help", "input=", "out=", "service_json_path=", "ipmi_json_path=", "client", "client_msg"],
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
        elif opt in ("-s", "--service_json_path"):
            service_json_path = arg
            path_level = match_level(service_json_path)
            if path_level != 2:
                parent_path = os.path.abspath(os.path.join(service_json_path, os.pardir, os.pardir))
                service_json_path = os.path.join(parent_path, "service.json")
        elif opt in ("-p", "--ipmi_json_path"):
            ipmi_json_path = arg
        elif opt in ("-c", "--client"):
            generate_client(m_input, output, mdb_path, service_json_path, path_level)
            return
        else:
            raise RuntimeError("不支持的选项: {}".format(opt))
    if not m_input or not output:
        usage()
        return
    generate_service(m_input, output, service_json_path, ipmi_json_path, path_level)


if __name__ == "__main__":
    main(sys.argv[1:])
