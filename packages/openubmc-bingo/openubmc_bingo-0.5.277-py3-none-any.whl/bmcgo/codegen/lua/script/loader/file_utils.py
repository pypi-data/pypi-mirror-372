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
from typing import List


def load_json(file_path: str) -> dict:
    file_path = os.path.normpath(file_path)
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as fd:
        return json.loads(fd.read())


def json_file_list(root_path: str) -> List[str]:
    ret = []
    for root, _, files in os.walk(root_path):
        for file_name in files:
            if not file_name.endswith(".json"):
                continue
            ret.append(os.path.join(root, file_name))
    return ret
