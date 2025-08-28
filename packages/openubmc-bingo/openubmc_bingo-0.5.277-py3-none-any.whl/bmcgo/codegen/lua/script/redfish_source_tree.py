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
import json
import os
import re
import stat
import sys

from mako.template import Template


def find_all_file(base):
    for root, _, fs in os.walk(base):
        for f in fs:
            if '_' in f:
                continue
            if f.endswith('Collection.json'):
                continue
            else:
                fullname = os.path.join(root, f)
                yield fullname


def generate_route(resource_path, template, out_dir):
    exclude_file = ['LogEntry']
    redfish_url = [
        'Managers', 'Systems', 'Chassis', 'SessionService',
        'AccountService', 'UpdateService', 'TaskService',
        'EventService', 'Sms', 'Fabrics', 'DataAcquisitionService'
    ]
    my_template = Template(filename=template)
    for i in find_all_file(resource_path):
        temp_name = i.split("/")[-1]
        file_name = temp_name.split(".")[0]
        if file_name in exclude_file:
            continue
        with open(i, 'r') as temp:
            load_json = json.load(temp)
            if 'definitions' not in load_json:
                continue
            if file_name not in load_json['definitions']:
                continue
            if 'uris' in load_json['definitions'][file_name]:
                # 拼接uris数组
                temp_list = []
                _format_url(file_name, load_json, redfish_url, temp_list)
                _generate_proto(file_name, my_template, out_dir, temp_list)


def _format_url(file_name, load_json, redfish_url, temp_list):
    for url in load_json['definitions'][file_name]['uris']:
        if url == '/redfish/v1':
            continue
        url = url.translate(str.maketrans({'{': ':', '}': ''}))
        temp = url.split('/')[3]
        if temp in redfish_url:
            url = url.replace('/redfish/v1/', '')
            temp_list.append(url)


def _generate_proto(file_name, my_template, out_dir, temp_list):
    if len(temp_list) > 0:
        for i, url_temp in enumerate(temp_list):
            dir_temp = out_dir + '/' + url_temp.replace(':', "")
            if not os.path.exists(dir_temp):
                os.makedirs(dir_temp)
            # 生成proto文件
            writer = os.fdopen(os.open(dir_temp + '/' + file_name + '.proto',
                                       os.O_WRONLY | os.O_CREAT, stat.S_IWUSR), 'w')
            writer.write(re.sub(r"\n\n\n+", "\n\n", my_template.render(
                filename=file_name,
                url=url_temp,
                i=i
            )))
            writer.close()


def main(argv):
    resource_path = ''
    template = ''
    out_dir = ''
    try:
        opts, _ = getopt.getopt(
            argv, "hi:t:d:", ["help", "input=", "tpl=", "dir="])
    except getopt.GetoptError:
        help()
        return
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            return
        elif opt in ("-i", "--input"):
            resource_path = arg
        elif opt in ("-t", "--tpl"):
            template = arg
        elif opt in ("-d", "--dir"):
            out_dir = arg
        else:
            raise RuntimeError("不支持的选项: {}".format(opt))
    if not resource_path or not template or not out_dir:
        usage()
        return
    generate_route(resource_path, template, out_dir)


if __name__ == "__main__":
    main(sys.argv[1:])
