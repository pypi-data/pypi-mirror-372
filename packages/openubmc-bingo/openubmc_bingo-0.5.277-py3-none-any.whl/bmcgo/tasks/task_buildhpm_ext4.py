#!/usr/bin/env python
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

"""
文件名：buildhpm_ext4.py
功能：编译生成 hpm 包
输入参数：板名 board_name
调用方法：python3 -B buildhpm_ext4.py -b board_name -l support_list(-l 可选)
版权信息：华为技术有限公司，版本所有(C) 2019-2020
"""

import os
import stat
import shutil
import subprocess
from bmcgo.tasks.task import Task


class TaskClass(Task):
    def __init__(self, config, work_name=""):
        super(TaskClass, self).__init__(config, work_name)

    def create_empty_text_file(self, file_name):
        with os.fdopen(os.open(file_name, os.O_RDWR | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w+') as file_fp:
            file_fp.close

    def exit_with_create_flag(self, board_name):
        flag_file = f"{self.config.temp_path}/buildhpm_flag_{board_name}"
        if not os.path.isfile(flag_file):
            self.create_empty_text_file(flag_file)

    def build_hpm(self, board_name):
        self.chdir(self.config.hpm_build_dir)
        self.info(f"构建 {board_name} hpm 包...")
        cmd = f"ls -al {self.config.work_out}/{board_name}_gpp.bin"
        self.run_command(cmd)
        cmd = f"./packethpm_ext4.sh {self.config.work_out}/{board_name}_gpp.bin hpm_ipmc_ext4.config"
        self.run_command(cmd)
        cmd = f"mv ipmc-crypt-image.hpm {self.config.work_out}/rootfs_{board_name}.hpm -f"
        self.run_command(cmd)

        self.info("hpm 构建成功 !!")
        self.exit_with_create_flag(board_name)
        return

    def sign(self, filelist, hpm_file):
        self.chdir(self.config.work_out)
        digest = self.get_manufacture_config("base/signature/hpm_digest", ["sha256"])
        with os.fdopen(os.open(filelist, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as f:
            f.write('Manifest Version: 1.0\n')
            f.write('Create By: openUBMC\n')
            f.write(f'Name: {hpm_file}\n')
            if "sha256" in digest:
                sha256sum = shutil.which("sha256sum")
                cmd = [sha256sum, hpm_file]
                sha = subprocess.run(cmd, capture_output=True).stdout.decode().strip('\n').split("  ")[0]
                f.write(f"SHA256-Digest: {sha}\n")
            if "sha512" in digest:
                sha512sum = shutil.which("sha512sum")
                cmd = [sha512sum, hpm_file]
                sha = subprocess.run(cmd, capture_output=True).stdout.decode().strip('\n').split("  ")[0]
                f.write(f"SHA512-Digest: {sha}\n")

    def sign_filelist(self):
        hpm_file_list = os.path.join(self.config.work_out, f'rootfs_{self.config.board_name}.filelist')
        self.sign(hpm_file_list, f'rootfs_{self.config.board_name}.hpm')
        self.info(f"构建 {self.config.board_name} hpm 包结束 !")

    def run(self):
        self.build_hpm(self.config.board_name)
        self.sign_filelist()
