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

import getopt
import importlib
import sys
import os
import stat
import json
import logging
import yaml


def generate(if_name, of_name, base):
    if importlib.util.find_spec('yamlinclude') is not None:
        # 兼容pyyaml-include 1.4.1 版本
        constructor = getattr(importlib.import_module('yamlinclude'), 'YamlIncludeConstructor')
        constructor.add_to_loader_class(loader_class=yaml.FullLoader, base_dir=base)
    else:
        constructor = getattr(importlib.import_module('yaml_include'), 'Constructor')
        yaml.add_constructor("!include", constructor(), yaml.Loader)

    with open(if_name) as f:
        data = yaml.safe_load(f)

        ofile = os.fdopen(os.open(of_name, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IWUSR | stat.S_IRUSR), 'w')
        ofile.write(json.dumps(data if data is not None else {}, indent=2))
        ofile.close()


def usage():
    logging.info('gen.py -i <inputfile> -b <base dir> -o <outfile>')


def main(argv):
    m_input = ''
    output = ''
    base = './datas'
    try:
        opts, _ = getopt.getopt(
            argv, "hi:b:o:", ["help", "input=", "base_dir=", "out="])
    except getopt.GetoptError:
        help()
        return
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            return
        elif opt in ("-i", "--input"):
            m_input = arg
        elif opt in ("-b", "--base_dir"):
            base = arg
        elif opt in ("-o", "--out"):
            output = arg
        else:
            raise RuntimeError("不支持的选项: {}".format(opt))
    if not m_input or not output:
        usage()
        return
    generate(m_input, output, base)


if __name__ == "__main__":
    main(sys.argv[1:])
