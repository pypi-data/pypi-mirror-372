#!/usr/bin/env python3
# encoding=utf-8
# 描述：bingo 配置默认参数功能
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import os
import re
import argparse
from pathlib import Path

from bmcgo import misc
from bmcgo.utils.tools import Tools
from bmcgo.utils.json_validator import JsonTypeEnum, JSONValidator, get_cpu_count
from bmcgo.bmcgo_config import BmcgoConfig


tools = Tools("JSONChecker")
logger = tools.log


command_info: misc.CommandInfo = misc.CommandInfo(
    group=misc.GRP_MISC,
    name="json_check",
    description=["json 文件检查"],
    hidden=False
)


def if_available(bconfig: BmcgoConfig):
    return True


CMD = "bingo"


def get_desc(cmd):
    
    return f"""
json 文件合法性检查工具:

1. 检查当前路径下所有 sr 文件:
>> {cmd} json_test -e sr

2. 检查其他路径下所有 sr, json, jn 文件:
>> {cmd} json_test -p /path/to/test/ -e .sr,json，jn

3. 用其他工具检查，比如 pyjson5, json5 (需要提前通过 pip 安装):
>> {cmd} json_test -e sr -j pyjson5
"""

DEFAULT_JSON_TYPE = JsonTypeEnum.JSON


class BmcgoCommand:
    def __init__(self, bconfig: BmcgoConfig, *args):
        self.bconfig = bconfig
        jc = self.bconfig.bmcgo_config_list.get(misc.ENV_CONST, {}).get(misc.JSON_CHECKER, DEFAULT_JSON_TYPE)

        parser = argparse.ArgumentParser(
            prog=f"{CMD}参数配置",
            description=get_desc(CMD),
            add_help=True,
            formatter_class=argparse.RawTextHelpFormatter
        )
        parser.add_argument(
            "-p",
            "--path",
            type=Path,
            default=Path(".").resolve(),
            help="文件路径：检查单个文件合法性；文件夹路径：递归遍历所有指定拓展名文件合法性"
        )
        parser.add_argument(
            "-e",
            "--extensions",
            type=lambda s: [ext.strip().lstrip('.').lower() for ext in re.split(r'\s*[，,]\s*', s) if ext],
            required=True,
            help="需要检查的文件后缀，通过','分隔，比如 -e sr,json"
        )
        parser.add_argument(
            "-j",
            "--json-type",
            choices=list(JsonTypeEnum),
            default=jc,
            help=f"选择检查工具，可以通过 {CMD} config {misc.ENV_CONST}.{misc.JSON_CHECKER}=json/json5/pyjson5 指定默认值，当前为：{jc}\n"
            "选择其他工具请先确认是否已经安装"
        )
        parser.add_argument(
            "-n",
            "--worker-num",
            type=int,
            default=get_cpu_count() * 2,
            help=f"指定并行处理器数目，默认为{get_cpu_count() * 2}"
        )

        self.args, self.kwargs = parser.parse_known_args(*args)
        self.logger = tools.log
        self._json_checker = JSONValidator()

    def run(self):
        self._json_checker.validate_files(
            self.args.path, self.args.extensions, self.args.json_type, self.args.worker_num)
        return 0
