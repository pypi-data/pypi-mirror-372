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


def get_message(msg_name, msg_data, package):

    properties = []
    index = 1
    for arg, arg_data in msg_data.items():
        properties.append(utils.get_property(arg, arg_data, index))
        index = index + 1

    return {
        "package": package,
        "name": msg_name,
        "options": {},
        "type": "Message",
        "properties": properties,
        "nested_type": [],
    }


def get_depends(message):
    depends = []

    if 'properties' not in message:
        return depends

    for prop in message['properties']:
        if prop["type"] not in utils.ALLOW_BASIC_TYPES.values():
            depends.append(prop["type"])

    return depends


def get_depend_message_pos(depend, old_messages):
    index = 1
    for var in old_messages:
        if (var["package"] + "." + var["name"]) == depend:
            return index
        index = index + 1

    return -1


# 由于当前模板的限制，依赖必须是顺序的，因此要计算插入的位置
def update_messages(messages, message):
    depends = get_depends(message)
    last_pos = 0
    for depend in depends:
        pos = get_depend_message_pos(depend, messages)
        if pos != -1:
            last_pos = max(last_pos, pos)

    messages.insert(last_pos, message)


def get_signals(intf, intf_data):
    datas = []
    if "signals" not in intf_data:
        return datas

    for signal, signal_data in intf_data["signals"].items():
        index = 1
        properties = []
        for prop, prop_data in signal_data.items():
            properties.append(utils.get_property(prop, prop_data, index))
            index = index + 1

        datas.append(
            {
                "package": utils.get_intf_package_name(intf),
                "name": signal,
                "options": {},
                "type": "Message",
                "properties": properties,
                "nested_type": [],
            }
        )
    return datas


def get_services(intf, intf_data, messages):
    if "methods" not in intf_data:
        return []
    services = []
    for method_name, method_data in intf_data["methods"].items():
        msg_package = utils.get_intf_package_name(intf)
        service = {
            "method_options": {},
            "options": {"service_interface": intf},
            "name": method_name,
            "req": ".google.protobuf.Empty",
            "rsp": ".google.protobuf.Empty",
        }

        if "req" in method_data:
            req_name = method_name + "Req"
            service["req"] = "." + req_name
            update_messages(messages, get_message(req_name, method_data["req"], msg_package))
        if "rsp" in method_data:
            rsp_name = method_name + "Rsp"
            service["rsp"] = "." + rsp_name
            update_messages(messages, get_message(rsp_name, method_data["rsp"], msg_package))
        services.append(service)

    return services


def gen_virtual_data(intf_data, index, intf_properties):

    if "virtual" not in intf_data:
        return
    data = {
        "name": "priority",
        "type": "uint8",
        "options": {"readonly": True},
        "id": index,
        "repeated": False,
    }
    index = index + 1
    intf_properties.append(data)


def get_properties(intf, intf_data):
    datas = []
    index = 1
    intf_properties = []

    intfs = intf.split(".")
    if "properties" not in intf_data:
        return [
            {
                "package": intfs[-1],
                "name": intfs[-1],
                "options": {"interface": intf},
                "type": "Message",
                "properties": {},
                "nested_type": [],
            }
        ], intfs[-1]
    for prop, prop_data in intf_data["properties"].items():
        intf_properties.append(utils.get_property(prop, prop_data, index))
        index = index + 1
    gen_virtual_data(intf_data, index, intf_properties)
    datas.append(
        {
            "package": intfs[-1],
            "name": intfs[-1],
            "options": {"interface": intf},
            "type": "Message",
            "properties": intf_properties,
            "nested_type": get_signals(intf, intf_data),
        }
    )

    return datas, intfs[-1]


def gen_defs(defs, messages):
    for struct_name, struct_data in defs.items():
        message = {}
        message_type = utils.get_message_type(struct_data)
        if message_type == 'struct':
            message = utils.get_struct_message("defs", struct_name, struct_data)
        elif message_type == 'enum':
            message = utils.get_enum_message("defs", struct_name, struct_data)
        else:
            message = utils.get_dict_message("defs", struct_name, struct_data)
        update_messages(messages, message)


def generate(if_name, of_name, mdb_path):
    load_f = os.fdopen(os.open(if_name, os.O_RDONLY, stat.S_IRUSR), "r")

    load_dict = json.load(load_f)
    intfs = []
    messages = []
    services = []

    load_dict = utils.generate_default(load_dict, mdb_path)

    for intf_name, intf_data in load_dict.items():
        intf = []
        signals = []
        if intf_name == "defs":
            gen_defs(intf_data, messages)
        else:
            intf, package = get_properties(intf_name, intf_data)
            service = get_services(intf_name, intf_data, messages)
            services = services + service
        intfs = intfs + intf 

    intfs = intfs + messages
    data = {
        "imports": [
            "google/protobuf/descriptor.proto",
            "ipmi_types.proto",
            "types.proto",
        ],
        "dependency": ["types.proto"],
        "data": intfs,
        "service": services,
        "package": package,
        "options": {},
    }

    utils.save_proto_json(of_name, data)
    load_f.close()


def usage():
    logging.info("gen_mdb_json.py -i <inputfile> -d <mdb_root> -o <outfile>")


def main(argv):
    m_input = ""
    output = ""
    mdb_path = ""
    try:
        opts, _ = getopt.getopt(argv, "hi:o:d:", ["help", "input=", "out=", "root"])
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
        elif opt in ("-d", "--root"):
            mdb_path = arg
        else:
            raise RuntimeError("不支持的选项: {}".format(opt))
    if not m_input or not output:
        usage()
        return
    generate(m_input, output, mdb_path)


if __name__ == "__main__":
    main(sys.argv[1:])
