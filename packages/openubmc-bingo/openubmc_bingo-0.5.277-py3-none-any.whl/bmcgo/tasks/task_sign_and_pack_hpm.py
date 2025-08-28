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
from bmcgo.tasks.task import Task


class TaskClass(Task):
    def sign_hpms(self):
        self.chdir(self.config.work_out)
        if self.config.self_sign:
            self.chdir(self.config.work_out)
            # 复制预置的ca, crl作为签名文件，并复制cms
            self.signature(f"rootfs_{self.config.board_name}.filelist",
                           f"rootfs_{self.config.board_name}.filelist.cms",
                           "cms.crl", "rootca.der")
        else:
            self.run_command(f"touch {self.config.work_out}/rootfs_{self.config.board_name}.filelist.cms")
            self.run_command(f"cp {self.config.board_path}/cms.crl {self.config.work_out}/cms.crl")
            self.chdir(self.config.work_out)
        
        # 生成的文件为rootfs_{board_name}.hpm.signed
        self.info(f"给 hpm 包 rootfs_{self.config.board_name}.hpm 签名")
        self.run_command(f"cms_sign_hpm.sh 2 rootfs_{self.config.board_name}.hpm")
        if self.config.enable_arm_gcov:
            self.link(f"rootfs_{self.config.board_name}.hpm.signed", os.path.join(
                self.config.inner_path, f"{self.config.board_name}_gcov.hpm"))
        else:
            self.link(f"rootfs_{self.config.board_name}.hpm.signed", os.path.join(
                self.config.output_path, f"rootfs_{self.config.board_name}.hpm"))

    def run(self):
        self.sign_hpms()
