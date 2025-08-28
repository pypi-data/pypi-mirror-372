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
import mds_util as utils


def translate_path(path):
    path = path.replace("${", ":")
    return path.replace("}", "")


def get_package(class_name, class_data):
    if "package" in class_data:
        return class_data["package"]
    else:
        return class_name


def get_data_by_class(class_name, class_data):
    properties = []
    index = 1
    datas = []
    for intf in class_data["interfaces"]:
        intfs = intf.split(".")
        properties.append(
            {
                "name": intfs[-1],
                "type": intfs[-1],
                "options": {"interface": intf},
                "id": index,
                "repeated": False,
            }
        )
        index = index + 1
    datas.append(
        {
            "package": get_package(class_name, class_data),
            "name": class_name,
            "options": {"path": translate_path(class_data["path"])},
            "type": "Message",
            "properties": properties,
            "nested_type": [],
        }
    )
    return datas, get_package(class_name, class_data)


def generate(if_name, of_name):
    load_f = utils.open_file(if_name)

    load_dict = json.load(load_f)
    classes = []

    for class_name, class_data in load_dict.items():
        classes, package = get_data_by_class(class_name, class_data)

    data = {
        "imports": [
            "google/protobuf/descriptor.proto",
            "ipmi_types.proto",
            "types.proto",
        ],
        "dependency": ["types.proto"],
        "data": classes,
        "service": [],
        "package": package,
        "options": {},
    }

    utils.save_proto_json(of_name, data)

    load_f.close()


def usage():
    logging.info("gen_mdb_json.py -i <inputfile> -o <outfile>")


def main(argv):
    m_input = ""
    output = ""
    try:
        opts, _ = getopt.getopt(argv, "hi:o:d:", ["help", "input=", "out="])
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
        else:
            raise RuntimeError("不支持的选项: {}".format(opt))
    if not m_input or not output:
        usage()
        return
    generate(m_input, output)


if __name__ == "__main__":
    main(sys.argv[1:])
