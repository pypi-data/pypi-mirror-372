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
import argparse
import logging
import os
import stat
import sys

from dto.exception import JsonTypeException
from dto.kepler_abstract import KeplerAbstractMgr, KeplerAbstract
from loader.file_utils import json_file_list, load_json


def collect_abstract_info(file_path, abstract_mgr: KeplerAbstractMgr):
    data = load_json(file_path)
    if not data:
        return
    JsonTypeException.check_list(data.get("data"))
    for msg in data.get("data"):
        JsonTypeException.check_dict(msg.get("options"))
        path = msg.get("options").get("path")
        interface = msg.get("options").get("interface")
        if not path and interface:
            continue
        abstract_mgr.add(KeplerAbstract(path, interface, file_path, msg.get("package"), msg.get("name")))


def collect_abstract_infos(root_path: str) -> KeplerAbstractMgr:
    abstract_mgr = KeplerAbstractMgr()
    file_path_list = json_file_list(root_path)
    for file_path in file_path_list:
        if not file_path.endswith(".proto.json"):
            continue
        collect_abstract_info(file_path, abstract_mgr)
    return abstract_mgr


def parse_option():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="root_path",
                      help="root path of Kepler *.proto.json", metavar="DIR")
    parser.add_argument("-o", "--out", dest="output_file_path",
                      help="Abstract file path", metavar="FILE")
    opt_dict = parser.parse_args()
    if not opt_dict.root_path or not opt_dict.output_file_path:
        parser.print_help()
        return False, opt_dict

    if os.path.isdir(opt_dict.root_path):
        logging.info("%s 不是一个文件夹", opt_dict.root_path)
        return False, opt_dict
    if os.path.isdir(os.path.dirname(opt_dict.output_file_path)):
        logging.info("%s 不存在", os.path.dirname(opt_dict.output_file_path))
        return False, opt_dict
    return True, opt_dict


def collect(root_path: str, output_file_path: str):
    abstract_mgr = collect_abstract_infos(root_path)
    with os.fdopen(os.open(output_file_path, os.O_WRONLY | os.O_CREAT, stat.S_IWUSR), 'w') as fd:
        json_obj = [abstract_mgr.url_abstract_map.get(key).to_json() for key in abstract_mgr.url_abstract_map.keys()]
        json.dump(json_obj, fd, indent=3)


if __name__ == '__main__':
    is_sucess, options = parse_option()
    if is_sucess:
        collect(options.root_path, options.output_file_path)
