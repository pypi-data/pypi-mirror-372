#!/usr/bin/env python
# coding:utf-8
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

"""
文件名：envir_prepare.py
功能：打包目录形成
版权信息：华为技术有限公司，版本所有(C) 2020-2021
"""
import os
import json
import shutil
import jsonschema
import yaml
from bmcgo.tasks.task import Task
from bmcgo import misc
from bmcgo import errors


class TaskClass(Task):
    # 构建AdaptiveLM依赖xmllint
    def check_xmllint(self):
        ret = self.run_command("xmllint --version", ignore_error=True)
        if ret.returncode != 0:
            self.run_command("apt install -y libxml2-utils", sudo=True)
        ret = self.run_command("ls /usr/bin/tclsh", ignore_error=True)
        if ret.returncode != 0:
            self.run_command("apt install -y tclsh", sudo=True)
        ret = self.run_command("ls /usr/bin/w3m", ignore_error=True)
        if ret.returncode != 0:
            self.run_command("apt install -y w3m", sudo=True)

    def build_config_check(self):
        # 不支持生产装备出包
        if self.config.manufacture_code is None:
            key = f"tosupporte/{self.config.tosupporte_code}"
            supporte_cfg = self.get_manufacture_config(key)
            if supporte_cfg is None:
                raise errors.ConfigException(f"参数 -sc 错误, 配置 (manifest.yml: {key}) 错误 !!!!")
            key += "/package_name"
            package_name = self.get_manufacture_config(key)
            if package_name is None:
                raise errors.ConfigException(f"获取包名错误, 配置 (manifest.yml: {key}) 错误 !!!!")
            return
        manufacture = self.get_manufacture_config("manufacture")
        if manufacture is None:
            raise errors.ConfigException("manufacture 编码(-z 编码) 无法被设置")

        codes = list(manufacture.keys())
        if self.config.manufacture_code not in codes:
            raise errors.ConfigException("manifest.yml 中 manufacture 错误, 可以被设置为: {}".format(codes))

        pkg_name_key = f"manufacture/{self.config.manufacture_code}/package_name"
        package_name = self.get_manufacture_config(pkg_name_key)
        if package_name is None:
            raise errors.ConfigException("manifest.yml 中 package_name 属性丢失, manufacture: {}".format(package_name))

    def run_signature_prepare(self):
        self.chdir(self.config.board_path)
        if not self.config.self_sign:
            # 复制签名需要使用的文件
            files = self.get_manufacture_config(f"base/signature/files")
            if files is None:
                raise errors.ConfigException("获取manifest.yml中base/signature/files失败, 请检查相关配置或生成是否正确")
            self.copy_manifest_files(files)

    def schema_subsys_valid(self, stage):
        for subsys_file in os.listdir(os.path.join(self.config.code_path, "subsys", stage)):
            file = os.path.join(self.config.code_path, "subsys", stage, subsys_file)
            self.debug("开始校验 %s", file)
            if not os.path.isfile(file):
                continue
            schema_file = misc.get_decleared_schema_file(file)
            if schema_file == "":
                raise errors.BmcGoException(f"schema校验文件{schema_file}未找到，本机绝对路径存储的schema文件且保证文件已存在")
            with open(schema_file, "rb") as fp:
                schema = json.load(fp)
            fp = open(file, "rb")
            subsys = yaml.safe_load(fp)
            fp.close()
            self.debug("开始校验 %s", file)
            jsonschema.validate(subsys, schema)

    def schema_valid(self):
        if self.config.target != "publish":
            return
        self.schema_subsys_valid("rc")
        self.schema_subsys_valid("stable")

    def run(self):
        self.built_type_check()
        self.prepare_conan()
        self.check_xmllint()
        self.build_config_check()
        self.run_signature_prepare()
        self.schema_valid()
        self.config.dump_manifest()
