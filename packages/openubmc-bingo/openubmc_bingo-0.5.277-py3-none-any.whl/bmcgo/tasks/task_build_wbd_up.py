#!/usr/bin/env python3
# coding: utf-8
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
import shutil

from bmcgo.tasks.task import Task


class TaskClass(Task):
    def __init__(self, config, work_name=""):
        super(TaskClass, self).__init__(config, work_name=work_name)
        self.wbd_build_dir = os.path.join(self.config.build_path, "wbd_build_dir")

    def get_wbd_file_config(self):
        wbd_up_file_config = None
        if self.config.manufacture_code:
            wbd_config_path = f"manufacture/{self.config.manufacture_code}/wbd_up_files"
            wbd_up_file_config = self.get_manufacture_config(wbd_config_path)
        elif self.config.tosupporte_code:
            wbd_config_path = f"tosupporte/{self.config.tosupporte_code}/wbd_up_files"
            wbd_up_file_config = self.get_manufacture_config(wbd_config_path)
        else:
            pass
            
        wbd_up_file_config = wbd_up_file_config or self.get_manufacture_config("wbd_up_files")
        return wbd_up_file_config


    def generate_wbd_package(self, wbd_up_file_config):
        self.chdir(self.wbd_build_dir)

        if "repo" in wbd_up_file_config and "tag" in wbd_up_file_config:
            repo = wbd_up_file_config.get("repo")
            tag = wbd_up_file_config.get("tag")
            if not repo.startswith("https"):
                self.info("建议使用 https 协议的仓库地址")
            self.run_command(f"git clone {repo} -b {tag} --depth=1")
            
        # 复制manifest.yml中配置的文件到build目录
        files = wbd_up_file_config.get("files")
        self.copy_manifest_files(files)
        
        # 约定压缩打包wbd_up_file目录
        self.run_command(f"tar --format=gnu -zcvf wbd_up_file.tar.gz wbd_up_file")
        rootfs_wbd_path = os.path.join(self.config.rootfs_path, "opt/bmc/white_branding")
        self.run_command(f"mkdir -p {rootfs_wbd_path}", sudo=True)
        self.run_command(f"cp -f wbd_up_file.tar.gz {rootfs_wbd_path}", sudo=True)

    def run(self):
        wbd_up_file_config = self.get_wbd_file_config()
        if not wbd_up_file_config:
            self.info("未在manifest.yml中找到 wbd_up_files 配置, 跳过白牌打包")
            return

        shutil.rmtree(self.wbd_build_dir, ignore_errors=True)
        os.makedirs(self.wbd_build_dir, exist_ok=True)

        self.info(f"----打包 {self.config.board_name} wbd_up_file.tar.gz 到BMC hpm包中 ------------> [开始]")
        self.generate_wbd_package(wbd_up_file_config)
        self.info(f"----打包  {self.config.board_name}wbd_up_file.tar.gz 到BMC hpm包中 ----------> [结束]")
