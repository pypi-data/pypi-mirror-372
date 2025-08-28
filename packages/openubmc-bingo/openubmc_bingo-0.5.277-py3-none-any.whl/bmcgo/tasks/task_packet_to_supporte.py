#!/usr/bin/env python
# coding: utf-8
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
import shutil
import time
import xml.etree.ElementTree as ET

from bmcgo.tasks.task import Task
from bmcgo.utils.config import Config
from bmcgo import errors

PACKAGE = "Package"


class TaskClass(Task):
    def __init__(self, config: Config, work_name=""):
        super().__init__(config, work_name)

    def version_xml_update(self, hpm_name, version_name):
        version_file = os.path.join(self.config.board_path, version_name)
        if not os.path.exists(version_file):
            return
        srv_tree = ET.parse(version_file)
        srv_root = srv_tree.getroot()
        package_name = srv_root.find(PACKAGE).find('PackageName').text
        vs = self.config.version.split(".")
        # 修正版本号
        if self.manufacture_version_check(f"{self.config.board_path}/manifest.yml") is True:
            vs[3] = str(int(vs[3]) + 1).zfill(2)
        ver = ".".join(vs[0:4])
        srv_root.find(PACKAGE).find('Version').text = ver
        srv_root.find(PACKAGE).find('PackageName').text = package_name.replace("TMP_VERSION", ver)
        srv_root.find(PACKAGE).find('FileName').text = \
            srv_root.find(PACKAGE).find('FileName').text.replace("TMP_VERSION", ver)
        srv_root.find(PACKAGE).find('Size').text = str(os.path.getsize(hpm_name))
        srv_tree.write(version_file)

    def run(self):
        if self.config.manufacture_code is not None:
            self.info(f"编码为 {self.config.manufacture_code} 为 togdp 编码, 跳过构建 tosupporte 包")
            return
        # 要打包的编码的配置
        supporte_config = "tosupporte/" + self.config.tosupporte_code
        build_type = self.get_manufacture_config(supporte_config + "/build_type")
        if build_type is not None and build_type != self.config.build_type:
            raise errors.BmcGoException("构建类型不匹配, 参数配置为: {}, 包 {} 对应构建类型配置为: {}".format(\
                self.config.build_type, supporte_config + "/build_type", build_type))
        # 文件的配置路径以及其名字
        package_name = self.get_manufacture_config(supporte_config + "/package_name")
        package_name = time.strftime(package_name, self.config.date)
        # 获取到文件名
        zip_name = os.path.basename(package_name)
        # 文件名同名目录
        build_path = os.path.join(self.config.temp_path, self.config.board_name, self.config.tosupporte_code,
                                  zip_name.replace(".zip", ""))
        self.info("构建 {}, 工作目录: {}".format(package_name, build_path))
        shutil.rmtree(build_path, ignore_errors=True)
        os.makedirs(build_path, exist_ok=True)

        # 切换到打包目录
        self.chdir(build_path)
        # 复制所需文件
        files = self.get_manufacture_config(supporte_config + "/files")
        self.version_xml_update(f"{self.config.work_out}/rootfs_{self.config.board_name}.hpm", "version.xml")
        self.copy_manifest_files(files)

        # 由于tosupporte解压后没有文件夹
        cmd = "zip -1 -rq {} .".format(zip_name)
        self.run_command(cmd)
        # 组装并新建目标目录
        dirname = os.path.dirname(package_name)
        target_dir = os.path.join(self.config.output_path, "packet", dirname)
        os.makedirs(target_dir, exist_ok=True)
        # 硬链接文件目标目录
        self.link(zip_name, os.path.join(target_dir, zip_name))

        self.chdir(self.config.temp_path)
        shutil.rmtree(build_path, ignore_errors=True)
