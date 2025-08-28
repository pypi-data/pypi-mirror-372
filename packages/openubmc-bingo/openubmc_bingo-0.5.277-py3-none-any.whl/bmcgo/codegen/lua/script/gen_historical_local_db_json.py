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

import logging
import getopt
import sys
import os
import re
import mds_util as utils


def get_historical_tables(file):
    historical_tables = {}
    hit_class = ''
    table_pattern = r'\.([^\s]+)\s'
    field_pattern = r'([^\s]+) =.*:cid\((\d+)\)'

    for line in file:
        if 'db:Table' in line:
            match = re.search(table_pattern, line)
            if not match:
                continue
            hit_class = match.group(0)[1:-1]
            historical_tables[hit_class] = []
        elif hit_class != '':
            match = re.search(field_pattern, line)
            if not match:
                continue
            field_name = match.group(1)
            cid = match.group(2)
            extend_field = ':extend_field()' in line
            historical_tables[hit_class].append({"name": field_name, "cid": int(cid), "extend_field": extend_field})
        elif 'create_if_not_exist' in line:
            hit_class = ''

    return historical_tables


def generate(if_name, of_name):
    if not os.path.exists(if_name):
        return

    historical_tables = {}
    with open(if_name, 'r') as file:
        historical_tables = get_historical_tables(file)

    utils.save_proto_json(of_name, historical_tables)


def usage():
    logging.info("gen_db_json.py -i <inputfile> -o <file>")


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
