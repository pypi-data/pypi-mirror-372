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
import os
import stat
import subprocess

proto_cvt_plugin_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "proto_plugin.py"))


def proto_to_json(proto_root_path: str, relative_path: str, proto_json_root_path: str):
    os.makedirs(proto_json_root_path, exist_ok=True)
    cmd = [
        "protoc",
        f"--plugin=protoc-gen-custom={proto_cvt_plugin_path}",
        f"--custom_out={proto_json_root_path}",
        f"-I{proto_root_path}",
        relative_path
    ]
    subprocess.run(cmd, shell=False)


def parse(proto_root_path, relative_path: str, proto_json_root_path: str) -> dict:
    json_file_path = os.path.abspath(os.path.join(proto_json_root_path, relative_path + ".json"))
    proto_file_path = os.path.abspath(os.path.join(proto_root_path, relative_path))
    if not os.path.exists(proto_file_path):
        return {}
    if not os.path.exists(json_file_path):
        proto_to_json(proto_root_path, relative_path, proto_json_root_path)
    json_stat = os.stat(json_file_path)
    proto_stat = os.stat(proto_file_path)
    if json_stat[stat.ST_MTIME] <= proto_stat[stat.ST_MTIME]:
        proto_to_json(proto_root_path, relative_path, proto_json_root_path)
    if not os.path.exists(json_file_path):
        return {}
    with open(json_file_path, "r", encoding="utf-8") as fd:
        return json.load(fd)
