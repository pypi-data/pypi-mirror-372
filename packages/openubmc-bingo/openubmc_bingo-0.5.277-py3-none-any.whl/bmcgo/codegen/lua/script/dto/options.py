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

import os


class Options:
    def __init__(self, options):
        self.source_file_path: str = options.source_file_path
        self.template_name: str = options.template_name
        self.output_file_path: str = options.output_file_path
        self.enable_auto_merge: bool = options.enable_auto_merge
        self.project_name = options.project_name
        self.version = options.version
        self.major_version = options.major_version
        self.proto_root_path = os.path.normpath(options.proto_root_path)
        self.proto_json_root_path = os.path.normpath(
            options.proto_json_root_path)
        self.kepler_root_path = os.path.join(
            options.proto_json_root_path, "mdb", "bmc", "kepler")
        self.formatter = options.formatter

    @staticmethod
    def from_parse_args_result(options):
        return Options(options)
