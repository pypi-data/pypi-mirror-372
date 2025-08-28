#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 描述：检查当前目录下, .yml/.yaml 文件是否符合配置的 schema 规范
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
import json
import argparse

import yaml
import jsonschema
from jsonschema import exceptions as jc

from bmcgo.logger import Logger
from bmcgo.bmcgo_config import BmcgoConfig
from bmcgo import misc

log = Logger()
command_info: misc.CommandInfo = misc.CommandInfo(
    group=misc.GRP_MISC,
    name="validate_yml",
    description=["对指定目录下所有yaml文件或指定yaml文件进行 schema 规范检查"],
    hidden=True
)


def if_available(_: BmcgoConfig):
    return True


class BmcgoCommand:
    def __init__(self, bconfig: BmcgoConfig, *args):
        """ yaml 文件根据 schema 文件进行规则检查

        Args:
            bconfig (BmcgoConfig): bmcgo 配置
        """
        self.bconfig = bconfig
        parser = argparse.ArgumentParser(prog="bingo validate_yml", description="Validate yaml files", add_help=True,
                                         formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-t", "--target", help="目标文件夹或单个yaml文件，默认当前目录", default=".")

        parsed_args = parser.parse_args(*args)
        self.target = os.path.realpath(parsed_args.target)

    @staticmethod
    def schema_valid(check_file: str) -> bool:
        """ 有效性校验

        Args:
            check_file (str): 要校验的文件名称
        """
        schema_file = misc.get_decleared_schema_file(check_file)
        if schema_file == "":
            log.warning(f"文件 {check_file} 没有配置 schema 检查")
            return True
        with open(schema_file, "rb") as fp:
            schema = json.load(fp)
        with open(check_file, "r") as fp:
            check_data = yaml.safe_load(fp)
        log.info("开始校验文件: %s", check_file)
        try:
            jsonschema.validate(check_data, schema)
            log.success("校验成功: %s", check_file)
            return True
        except (jc.ValidationError, jc.SchemaError) as e:
            log.error(f" >>>>>> {check_file} 校验失败 <<<<<<\n{e}")
            return False

    @staticmethod
    def _is_yml_file(filename):
        if filename.endswith((".yml", ".yaml")):
            return True
        return False

    def run(self):
        """ 分析参数并启动校验
        """
        check_result = []

        if os.path.isfile(self.target):
            check_result.append(self.schema_valid(self.target))
            return 0

        check_result = self._validate_yml_files()

        if check_result and False in check_result:
            log.error("请仔细阅读报错日志, 日志中会提示哪些是必要属性, 或哪个属性配置错误")
            raise AttributeError(f"所有 .yml/.yaml 文件检查失败, 请仔细检查报错并解决问题项")
        if not check_result:
            log.warning("未找到yml文件")
        return 0

    def _validate_yml_files(self):
        check_result = []
        for root, _, files in os.walk(self.target):
            for filename in files:
                if not self._is_yml_file(filename):
                    continue
                schema_file = os.path.join(root, filename)
                check_result.append(self.schema_valid(schema_file))
        return check_result


