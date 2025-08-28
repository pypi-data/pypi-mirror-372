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
import time
from collections import defaultdict
from pathlib import Path


class IntfPool:
    def __init__(self, project_name, mdb_path, mds_dir):
        self.pool = defaultdict(set)
        self.dev_pool = defaultdict(set)
        self.output = dict()
        self.duplicates = []
        for root, _, files in os.walk(mds_dir):
            for file in files:
                if file == "service.json":
                    self.add_from_service(os.path.join(root, file))
                if file == "model.json":
                    self.add_from_model(os.path.join(root, file))

        if project_name == 'hwproxy':
            for root, _, files in os.walk(os.path.join(mdb_path, "intf/mdb/bmc/dev")):
                for file in files:
                    self.add_from_device_tree(os.path.join(root, file))
        self.resolve_duplicates()
        self.log_duplicates()

    @staticmethod
    def open_mds(mds_file):
        with os.fdopen(os.open(mds_file, os.O_RDONLY, stat.S_IRUSR), 'r') as mds_fp:
            ret = json.load(mds_fp)
        return ret

    def extend_alias(self, alias, interface):
        prefix_len = len(interface) - len(alias) - 1
        prefix = interface[:prefix_len]
        if prefix == "bmc":
            return alias
        dot_index = prefix.rfind('.')
        ret = interface[(dot_index + 1):]
        new_alias = ret.replace('.', '')
        self.duplicates.append((interface, alias, new_alias))
        return ret

    def log_duplicates(self):
        for interface, alias, new_alias in self.duplicates:
            logging.warning("接口 '%s' 末尾部分 '%s' 重复，已扩展为 '%s'", interface, alias, new_alias)
            logging.warning("手写代码中如有调用名字以 '%s' 拼接的自动生成函数，请同步修改", alias)
            time.sleep(3 / len(self.duplicates))

    def add_from_service(self, service_json):
        if not os.path.exists(service_json):
            return

        service_dict = self.open_mds(service_json)
        for item in service_dict.get("required", []):
            interface = item.get("interface")
            if interface:
                self.pool[interface.split('.')[-1]].add(interface)

    def add_from_model(self, model_json):
        if not os.path.exists(model_json):
            return

        model_dict = self.open_mds(model_json)
        for class_data in model_dict.values():
            for interface in class_data.get("interfaces", {}):
                self.pool[interface.split('.')[-1]].add(interface)

    def add_from_device_tree(self, intf_json):
        if not os.path.exists(intf_json):
            return

        intf_dict = self.open_mds(intf_json)
        for interface in intf_dict.keys():
            self.dev_pool[interface.split('.')[-1]].add(interface)

    def resolve_duplicates(self):
        while self.pool:
            temp_pool = self.pool
            self.pool = defaultdict(set)
            for alias, interfaces in temp_pool.items():
                if len(interfaces) == 1:
                    self.add_to_output(alias, interfaces)
                    continue
                for interface in interfaces:
                    self.pool[self.extend_alias(alias, interface)].add(interface)

        while self.dev_pool:
            temp_pool = self.dev_pool
            self.dev_pool = defaultdict(set)
            for alias, interfaces in temp_pool.items():
                if len(interfaces) == 1:
                    self.add_to_output(alias, interfaces)
                    continue
                for interface in interfaces:
                    self.dev_pool[self.extend_alias(alias, interface)].add(interface)

    def add_to_output(self, alias, interfaces):
        for interface in interfaces:
            self.output[interface] = alias.replace('.', '')

    def save_output(self, output_file):
        out_path = Path(output_file).resolve()
        out_dir = out_path.parent
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        with os.fdopen(os.open(out_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as out_fp:
            json.dump(self.output, out_fp)


def usage():
    logging.info("check_intfs.py -m <mds_dir> -o <output_file>")


def main(argv):
    logging.getLogger().setLevel(logging.INFO)
    options = dict()
    try:
        opts, _ = getopt.getopt(argv, "hd:n:s:m:o:", ["help", "service=", "model=",
        "out"])
    except getopt.GetoptError as getopt_error:
        logging.error(getopt_error)
        return
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            return
        elif opt in ("-d", "--dir"):
            mdb_path = arg
        elif opt in ("-n", "--project_name"):
            project_name = arg
        elif opt in ("-m", "--mds"):
            options["mds_dir"] = arg
        elif opt in ("-o", "--out"):
            options["output_file"] = arg
        else:
            raise RuntimeError("不支持的选项: {}".format(opt))

    IntfPool(project_name, mdb_path, options.get("mds_dir")).save_output(options.get("output_file"))


if __name__ == "__main__":
    main(sys.argv[1:])