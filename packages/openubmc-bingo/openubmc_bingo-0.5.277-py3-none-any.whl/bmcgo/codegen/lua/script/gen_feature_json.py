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
from utils import Utils


def insert_into_nested_dict(nested_dict, keys, value):
    if len(keys) == 1:
        nested_dict[keys[0]] = value
    elif len(keys) >= 2:
        if keys[0] not in nested_dict:
            nested_dict[keys[0]] = {}
        insert_into_nested_dict(nested_dict[keys[0]], keys[1:], value)


def make_public(class_name, class_data, datas):
    intfs = {}
    for intf_name, intf_data in class_data.items():
        name = Utils.get_unique_intf_name(intf_name)
        intfs[name] = intf_data
    sorted_intfs = {key: intfs.get(key) for key in sorted(intfs.keys())}

    datas[class_name] = sorted_intfs


def make_publics(public_feature, datas):
    for class_name, class_data in public_feature.items():
        datas[class_name] = {}
        make_public(class_name, class_data, datas)


def save_feature_json(feature, feature_data, out_dir):
    imports = [
        "google/protobuf/descriptor.proto",
        "ipmi_types.proto",
        "types.proto"
    ]
    dependency = ["types.proto"]
    datas = {
        "imports": imports,
        "dependency": dependency,
        "options": {},
        "feature": feature,
        "public": {},
        "private": {}
    }

    if "public" in feature_data:
        make_publics(feature_data["public"], datas["public"])
    if "private" in feature_data:
        datas["private"] = feature_data["private"]

    utils.save_proto_json(out_dir + "/" + feature + ".proto.json", datas)


def save_feature_jsons(features, out_dir):
    for feature, feature_data in features.items():
        save_feature_json(feature, feature_data, out_dir)


def collect_private_features(class_data, features):
    for method_name, method_data in class_data.get("methods", {}).items():
        if "featureTag" in method_data:
            insert_into_nested_dict(features, [method_data["featureTag"], "private", method_name], True)


def collect_public_features(class_name, class_data, features):
    for intf_name, intf_data in class_data.get("interfaces", {}).items():
        for method_name, method_data in intf_data.get("methods", {}).items():
            if "featureTag" not in method_data:
                continue
            insert_into_nested_dict(features, [method_data["featureTag"], "public", class_name, intf_name,
                method_name], True)


def sort_public_features(feature_data, class_data):
    for _, class_data in feature_data.items():
        for intf_name, intf_data in class_data.items():
            class_data[intf_name] = sorted(intf_data.keys())


def gen_features(model_path, out_dir):
    load_f = utils.open_file(model_path)
    load_dict = json.load(load_f)

    features = {}
    for class_name, class_data in load_dict.items():
        if class_name == "private":
            collect_private_features(class_data, features)
        else:
            collect_public_features(class_name, class_data, features)

    for _, feature_data in features.items():
        if "private" in feature_data:
            feature_data["private"] = sorted(feature_data["private"].keys())
        if "public" in feature_data:
            sort_public_features(feature_data["public"], class_data)

    save_feature_jsons(features, out_dir)


def usage():
    logging.info(
        "gen_plugin_json.py -i <inputfile> -o <outputfile> -n <project_name> -f"
    )


def main(argv):
    m_input = ""
    output = ""
    project_name = ""
    try:
        opts, _ = getopt.getopt(
            argv,
            "hi:o:n:f",
            ["help", "input=", "out=", "project_name="],
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
        elif opt in ("-n", "--project_name"):
            project_name = arg
        elif opt in ("-f", "--feature"):
            gen_features(m_input, output)
            return
        else:
            raise RuntimeError("不支持的选项: {}".format(opt))
    if not m_input or not output:
        usage()
        return


if __name__ == "__main__":
    main(sys.argv[1:])
