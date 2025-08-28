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
import mds_util as utils
from utils import Utils


PROPERTY_FLAGS = {
    'emitsChangedSignal': {
        'true': 'EMIT_CHANGE',
        'const': 'CONST',
        'invalidates': 'EMIT_NO_VALUE',
        'false': ''
    },
    'explicit': {
        True: 'EXPLICIT',
        False: ''
    },
    'deprecated': {
        True: 'DEPRECATED',
        False: ''
    },
    'volatile': {
        True: 'VOLATILE',
        False: ''
    }
}
OPTIONS = 'options'


def is_struct(prop_data):
    if 'baseType' not in prop_data:
        return True
    elif prop_data['baseType'] == "Enum":
        return False
    elif prop_data['baseType'] == "Array" and 'baseType' in prop_data["items"] and \
        prop_data["items"]['baseType'] == "Enum":
        return False
    else:
        return True


def get_message(msg_name, msg_data, msg_pack, imports):
    has_struct = False
    depends = []
    message = {}
    message_type = utils.get_message_type(msg_data)
    if message_type == 'struct':
        message = utils.get_struct_message(msg_pack, msg_name, msg_data)
    elif message_type == 'enum':
        message = utils.get_enum_message(msg_pack, msg_name, msg_data)
        return message, depends
    else:
        message = utils.get_dict_message(msg_pack, msg_name, msg_data)

    imports[msg_pack] = imports.get(msg_pack, set())
    for prop in message.get("properties", []):
        if prop["type"] in utils.ALLOW_BASIC_TYPES.values():
            continue
        if prop["type"].startswith("def_types."):
            imports[msg_pack].add("def_types.proto")
            prop["type"] = prop["type"].replace("defs_", "")
        elif ".defs_" in prop["type"]:
            imports[msg_pack].add(f'../json_types/{prop["type"].split(".")[0]}.proto')
            prop["type"] = prop["type"].replace("defs_", "")
        else:
            prop["type"] = prop["type"].replace("defs.", msg_pack + ".")
        depends.append(prop["type"])
        if message_type == 'dict':
            prop["is_struct"] = True
        has_struct = is_struct(msg_data[prop['original_name']])
    if "options" in message:
        message["options"]["has_struct"] = has_struct

    return message, depends


def save_model_msg(intfs, out_dir, extra_imports):
    for pkg_name, pkg_data in intfs.items():
        if "defs" == pkg_name:
            continue
        file_name = pkg_name[1:] + ".proto"
        imports = [
            "google/protobuf/descriptor.proto",
            "ipmi_types.proto",
            "types.proto"
        ]
        dependency = ["types.proto"]
        if pkg_name in extra_imports:
            imports.extend(extra_imports[pkg_name])
            dependency.extend(extra_imports[pkg_name])
        datas = {
            "imports": imports,
            "dependency": dependency,
            "data": pkg_data["messages"],
            "package": pkg_name,
            "options": {},
            "filename": file_name,
            "require_path": "class.types." + pkg_name[1:]
        }
        utils.save_proto_json(out_dir + "/" + pkg_name[1:] + ".proto.json", datas)


def save_types_msg(intfs, out_dir, extra_imports):
    for pkg_name, pkg_data in intfs.items():
        if "defs" == pkg_name:
            continue
        file_name = pkg_name + ".proto"
        imports = [
            "google/protobuf/descriptor.proto",
            "ipmi_types.proto",
            "types.proto"
        ]
        dependency = ["types.proto"]
        if pkg_name in extra_imports:
            imports.extend(extra_imports[pkg_name])
            dependency.extend(extra_imports[pkg_name])
        datas = {
            "imports": imports,
            "dependency": dependency,
            "data": pkg_data["messages"],
            "package": pkg_name,
            "options": {},
            "filename": file_name,
            "require_path": "class.types.types"
        }
        utils.save_proto_json(out_dir + "/" + pkg_name + ".proto.json", datas)


def save_msg(intfs, out_dir, project_name):
    for pkg_name, pkg_data in intfs.items():
        if "defs" == pkg_name:
            continue
        file_name = pkg_name + ".proto"
        imports = ["types.proto"]
        require_dir = "device_types" if ("intf" in pkg_data and 
            pkg_data["intf"].startswith('bmc.dev.')) else "json_types"
        new_out_dir = os.path.join(out_dir, '../device_types') if ("intf" in pkg_data
            and pkg_data["intf"].startswith('bmc.dev.')) else out_dir
        if not os.path.exists(new_out_dir):
            os.mkdir(new_out_dir)

        datas = {
            "imports": [
                "google/protobuf/descriptor.proto",
                "ipmi_types.proto",
                "types.proto"
            ],
            "dependency": imports,
            "data": pkg_data["messages"],
            "package": pkg_name,
            "options": {},
            "filename": file_name,
            "require_path": f"{project_name}.{require_dir}.{pkg_name}",
            "intf": pkg_data["data"] if "data" in pkg_data else {},
        }
        utils.save_proto_json(f"{new_out_dir}/{file_name}.json", datas)


def check_duplicate_msg(messages, method_name):
    for method in messages:
        if method["name"] == method_name:
            return True
    return False


def get_req(method_data):
    if "req" in method_data:
        return method_data["req"]
    if "arg_in" in method_data:
        return method_data["arg_in"]
    return {}


def get_rsp(method_data):
    if "rsp" in method_data:
        return method_data["rsp"]
    if "arg_out" in method_data:
        return method_data["arg_out"]
    return {}


def get_depend_message_pos(depend, old_messages):
    index = 1
    for var in old_messages:
        if (var["package"] + "." + var["name"]) == depend:
            return index
        index = index + 1

    return -1


# 由于当前模板的限制，依赖必须是顺序的，因此要计算插入的位置
def update_package(package, msg_name, struct_data, msg_package, imports):
    new_message, depends = get_message(
        msg_name, struct_data, msg_package, imports)
    last_pos = 0
    for depend in depends:
        pos = get_depend_message_pos(depend, package["messages"])
        if pos != -1:
            last_pos = max(last_pos, pos)

    package["messages"].insert(last_pos, new_message)


# 为结构体生成message
def gen_defs(defs, msg_package, packages, imports=None):
    if imports is None:
        imports = {}

    if msg_package not in packages:
        packages[msg_package] = {"messages": []}

    package = packages[msg_package]
    for struct_name, struct_data in defs.items():
        msg_name = struct_name
        if not check_duplicate_msg(package["messages"], msg_name):
            update_package(package, msg_name, struct_data, msg_package, imports)


def validate_property_options(intf, property_name: str, key, value):
    values_map = PROPERTY_FLAGS.get(key)
    if values_map is None:
        return False, f'mdb_interface中接口{intf}属性{property_name}配置了无效的options字段{key}。'\
            f'可选字段为{", ".join(PROPERTY_FLAGS.keys())}。'
    flag = values_map.get(value)
    if flag is not None:
        return True, flag
    expected_type = "布尔类型"
    expected_values = map(lambda v: str(v).lower(), values_map.keys())
    if key == "emitsChangedSignal":
        expected_type = "字符串类型"
        expected_values = map(lambda v: f'"{v}"', expected_values)
    error_msg = f'mdb_interface中接口{intf}属性{property_name}配置了无效的options值"{key}": {json.dumps(value)}。'\
    f'\"{key}\"字段取值类型必须是{expected_type}，取值范围是{", ".join(expected_values)}。'
    return False, error_msg


def convert_property_options(intf, property_name: str, options_data: dict):
    flags = []
    for k, v in options_data.items():
        ok, result = validate_property_options(intf, property_name, k, v)
        if not ok:
            raise RuntimeError(result)
        if result:
            flags.append(result)
    # emitsChangedSignal默认为true
    if "emitsChangedSignal" not in options_data:
        flags.append(PROPERTY_FLAGS.get("emitsChangedSignal").get("true"))
    return flags


def generate_message(intf_data, intf, packages, imports):
    msg_package = Utils.get_unique_intf_name(intf)

    if msg_package not in packages:
        packages[msg_package] = {"messages": [], "depends": [], "data": {}, "intf": intf}
    package = packages[msg_package]
    package["data"] = {"name": intf, "data": intf_data}

    if "methods" in intf_data:
        for method_name, method_data in intf_data["methods"].items():
            req_name = method_name + "Req"
            rsp_name = method_name + "Rsp"
            if not check_duplicate_msg(package["messages"], req_name):
                update_package(package, req_name, get_req(
                    method_data), msg_package, imports)

            if not check_duplicate_msg(package["messages"], rsp_name):
                update_package(package, rsp_name, get_rsp(
                    method_data), msg_package, imports)

    if "signals" in intf_data:
        for signal_name, signal_data in intf_data["signals"].items():
            signature_name = signal_name + "Signature"
            if not check_duplicate_msg(package["messages"], signature_name):
                update_package(package, signature_name,
                               signal_data, msg_package, imports)

    if "properties" in intf_data:
        for property_name, property_data in intf_data["properties"].items():
            if not check_duplicate_msg(package["messages"], property_name):
                update_package(package, property_name,
                               {property_name: property_data}, msg_package, imports)
            if OPTIONS in property_data:
                property_data[OPTIONS] = convert_property_options(intf, property_name, property_data[OPTIONS])


def prepare_virutal(intf_data):
    if "virtual" in intf_data:
        intf_data["properties"]["priority"] = {
            "baseType": "U8",
        }


def prepare_intf_data(intf_data, intf):
    if "defs" in intf_data:
        intf_data[intf]["defs"] = intf_data["defs"]
    prepare_virutal(intf_data)


def generate_default_message(default_intf_name, mdb_path, messages):
    intf_json = utils.get_intf(default_intf_name, mdb_path)
    imports = {}
    if "implement" in intf_json[default_intf_name]:
        intf_json = utils.generate_default(intf_json, mdb_path)
    generate_message(intf_json[default_intf_name],
                     default_intf_name, messages, imports)


def gen_dev_intf(intf, output, project_name):
    messages = {}
    intf_name = ''
    for key in intf.keys():
        if key != 'defs':
            intf_name = key
    gen_client_msg_intf(intf, intf_name, messages)
    save_msg(messages, output, project_name)


def gen_dev_intfs(mdb_path, output, project_name):
    file_list = Utils.get_files(os.path.join(mdb_path, "intf/mdb/bmc/dev"))
    for file in file_list:
        with os.fdopen(os.open(file, os.O_RDONLY, stat.S_IRUSR), "r") as intf_file:
            gen_dev_intf(json.load(intf_file), output, project_name)


def get_service_messages(mdb_path, classes, messages, imports):
    for _, class_data in classes.items():
        if "interfaces" not in class_data:
            continue
        for intf_name, intf_data in class_data["interfaces"].items():
            if "defs" in intf_data:
                gen_defs(
                    intf_data["defs"], Utils.get_unique_intf_name(
                        intf_name), messages
                )
            prepare_virutal(intf_data)
            generate_message(intf_data, intf_name, messages, imports)

            if "default" in intf_data:
                generate_default_message(
                    intf_data["default"], mdb_path, messages)


def gen_service_msg(model_merged_file, of_name, mdb_path, project_name):
    load_f = utils.open_file(model_merged_file)
    load_dict = json.load(load_f)

    messages = {}
    imports = {}
    get_service_messages(mdb_path, load_dict, messages, imports)
    save_msg(messages, of_name, project_name)
    load_f.close()

    if project_name == 'hwproxy':
        gen_dev_intfs(mdb_path, of_name, project_name)


def gen_model_msg(model_merged_file, of_name):
    load_f = utils.open_file(model_merged_file)
    load_dict = json.load(load_f)
    messages = {}
    imports = {}
    for class_name, class_data in load_dict.items():
        class_name = "M" + class_name
        if "defs" in class_data:
            gen_defs(class_data["defs"], class_name, messages)
        generate_message(class_data, class_name, messages, imports)

    save_model_msg(messages, of_name, imports)
    load_f.close()


def gen_client_msg_intf(intf_json, intf, messages):
    imports = {}
    for intf_name, intf_data in intf_json.items():
        if intf_name == "defs":
            gen_defs(intf_data, Utils.get_unique_intf_name(intf), messages)
        else:
            prepare_intf_data(intf_json, intf_name)
            prepare_virutal(intf_data)
            generate_message(intf_data, intf_name, messages, imports)


def gen_client_msg(service_file, output, mdb_path, project_name):
    load_f = utils.open_file(service_file)
    service_json = json.load(load_f)

    if "required" not in service_json:
        load_f.close()
        return

    messages = {}
    for required in service_json["required"]:
        intf = required["interface"]
        intf_json = utils.get_intf(intf, mdb_path)
        if "implement" in intf_json[intf]:
            intf_json = utils.generate_default(intf_json, mdb_path)
        gen_client_msg_intf(intf_json, intf, messages)

    save_msg(messages, output, project_name)
    load_f.close()


def gen_types_msg(types_file, of_name):
    load_f = utils.open_file(types_file)
    load_dict = json.load(load_f)
    messages = {}
    imports = {}
    if "defs" in load_dict:
        gen_defs(load_dict["defs"], "def_types", messages, imports)
        generate_message(load_dict, "def_types", messages, imports)

    save_types_msg(messages, of_name, imports)
    load_f.close()


def usage():
    logging.info(
        "gen_rpc_msg_json.py -i <inputfile> -d<mdb_path> -o<outputfile> -x <client_msg> -m<service_msg>"
    )


def main(argv):
    m_input = ""
    output = ""
    mdb_path = ""
    project_name = ""
    try:
        opts, _ = getopt.getopt(
            argv,
            "hi:o:d:n:mcxpt",
            ["help", "input=", "out=", "message", "project_name=",
                "client", "client_msg", "model_message", "types_message"],
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
        elif opt in ("-n", "--project_name"):
            project_name = arg
        elif opt in ("-m", "--message"):
            gen_service_msg(m_input, output, mdb_path, project_name)
            return
        elif opt in ("-p", "--model_message"):
            gen_model_msg(m_input, output)
            return
        elif opt in ("-x", "--client_message"):
            gen_client_msg(m_input, output, mdb_path, project_name)
            return
        elif opt in ("-t", "--types_message"):
            gen_types_msg(m_input, output)
            return
        else:
            raise RuntimeError("不支持的选项: {}".format(opt))
    if not m_input or not output:
        usage()
        return


if __name__ == "__main__":
    main(sys.argv[1:])
