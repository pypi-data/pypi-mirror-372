#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

'''
功    能：
版权信息：华为技术有限公司，版本所有(C) 2021
修改记录：2021-10-11 创建
'''
import os
import re
import shutil

from bmcgo.tasks.task import Task
from bmcgo import misc
from bmcgo.tasks.misc import MODULE_SYMVERS, SDK_PATH, SDK_SHA256_PATH


class TaskClass(Task):
    def __init__(self, config, work_name=""):
        super().__init__(config, work_name)
        self.sdk_dir = f"{self.config.tools_path}/sdk"
        self.sdk_new_sha256 = f"{self.config.tools_path}/sdk_new.sha256"
        self.skip_install = False

    def download_dependency(self):
        self.info('开始下载依赖组件 ...')
        partner_sdk_dir = f"{os.path.expanduser('~')}/sdk"
        self.info(f"从缓存目录{partner_sdk_dir}复制sdk和rtos二进制文件")
        self.run_command(f"cp -rf {partner_sdk_dir}/. {self.sdk_dir}")

    def move_dependency(self):
        # 移动到tools/build_tools目录中
        if os.path.isdir(self.config.sdk_path):
            shutil.rmtree(self.config.sdk_path)
        self.run_command(f"cp -rf {self.sdk_dir} {self.config.sdk_path}")
        self.info("移动依赖组件结束")
        self.chdir(self.config.sdk_path)
        for file in os.listdir("."):
            if re.match("^Hi1711_[0-9]{8}_[0-9a-f]{40}.tar.gz$", file) is None:
                continue
            self.run_command(f"tar -xvf {file}")
            break
        if self.skip_install:
            self.info("sdk版本匹配")
            return
        old_sdk_dir = "/opt/hi1711sdk"
        self.run_command(f"rm -rf {SDK_SHA256_PATH}", sudo=True)
        self.run_command(f"rm -rf {SDK_PATH}", sudo=True)
        self.run_command(f"rm -rf {old_sdk_dir}", sudo=True)
        self.run_command(f"mkdir -p {SDK_PATH}", ignore_error=True, sudo=True)
        self.run_command(f"tar -xzf hi1711sdk.tar.gz -C {SDK_PATH} {MODULE_SYMVERS}", sudo=True)
        logname = os.getenv(misc.ENV_LOGNAME, None)
        if logname and logname != "root":
            user_group = f"{os.getuid():{os.getgid()}}"
            self.run_command(f"chown {user_group} {SDK_PATH} -R", sudo=True)
        self.run_command(f"ln -s {SDK_PATH} {old_sdk_dir}", sudo=True)
        self.run_command("cp -af {} {}".format(self.sdk_new_sha256, SDK_SHA256_PATH), sudo=True)

    def run(self):
        self.download_dependency()
        self.info('下载依赖组件结束')
        self.skip_install = not self.check_need_install(self.sdk_dir, SDK_SHA256_PATH, self.sdk_new_sha256)
        self.move_dependency()
