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
功    能：下载并安装rtos/hcc工具
修改记录：2021-10-11 创建
'''
import os
import shutil

from bmcgo.tasks.task import Task
from bmcgo.tasks.misc import BUILD_TOOLS_SHA256_PATH
from bmcgo.utils.config import Config
from bmcgo import misc


class DownloadDefaultBuildtools(Task):
    def __init__(self, config: Config):
        super(DownloadDefaultBuildtools, self).__init__(config, "DownloadDefaultBuildtools")
        self.rtos_sdk_dir = f"{self.config.tools_path}/rtos-sdk-arm64"
        self.buildtools_new_sha256 = f"{self.config.tools_path}/buildtools_new.sha256"
        self.skip_install = False

    def download_tools(self):
        self.info(f"移除下载路径: {self.rtos_sdk_dir}")
        self.run_command(f"rm -rf {self.rtos_sdk_dir}", ignore_error=True, sudo=True)
        self.info('开始下载依赖工具...')
        partner_tools_dir = f"{os.path.expanduser('~')}/rtos_compiler"
        if self.config.partner_mode:
            self.info(f"从缓存目录{partner_tools_dir}复制编译器工具")
            self.run_command(f"cp -rf {partner_tools_dir}/. {self.rtos_sdk_dir}")

    def install_buildtools(self):
        is_ubuntu = self.tools.is_ubuntu
        self.chdir(self.rtos_sdk_dir)
        self.info("删除目录 /opt/RTOS")
        self.run_command(f"rm -rf {BUILD_TOOLS_SHA256_PATH}", sudo=True)
        self.run_command("rm -rf /opt/RTOS", sudo=True)
        self.info("安装 rpm 包")
        for rpm in os.listdir("./"):
            if not os.path.isfile(rpm) or not rpm.endswith(".rpm"):
                continue
            self.info("安装 {}".format(rpm))
            if not is_ubuntu:
                self.run_command("rpm -ivh {}".format(rpm), sudo=True)
            else:
                self.pipe_command(["rpm2cpio {}".format(rpm), "sudo cpio -id -D /"])

        self.info("删除目录 /opt/hcc_arm64le")
        self.run_command("rm -rf /opt/hcc_arm64le", sudo=True)
        self.info("解压 hcc_arm64le")
        self.run_command("tar -xzf hcc_arm64le.tar.gz -C /opt", sudo=True)

        logname = os.getenv(misc.ENV_LOGNAME, None)
        if logname and logname != "root":
            user_group = f"{os.getuid():{os.getgid()}}"
            self.run_command(f"chown {user_group} /opt/hcc_arm64le -R", sudo=True)
            self.run_command(f"chown {user_group} /opt/RTOS -R", sudo=True)
        self.chdir(self.config.code_path)

        libstdcpp_install_path = f"{self.config.sysroot}/usr/"
        os.makedirs(libstdcpp_install_path, exist_ok=True)
        self.run_command(f"cp -rf {self.config.cross_compile_install_path}/{self.config.cross_prefix}/lib64/" +
                         f" {libstdcpp_install_path}")
        self.run_command("cp -af {} {}".format(self.buildtools_new_sha256, BUILD_TOOLS_SHA256_PATH), sudo=True)

    def run(self):
        self.download_tools()
        self.info("下载依赖工具结束")

    def install(self):
        self.skip_install = not self.check_need_install(self.rtos_sdk_dir, BUILD_TOOLS_SHA256_PATH,
                                                        self.buildtools_new_sha256)
        if self.skip_install:
            self.info("buildtools版本匹配，跳过安装")
            return
        # 检查rtos是否安装，未安装或版本不匹配时安装
        self.install_buildtools()


class TaskClass(Task):
    def __init__(self, config, work_name=""):
        super(TaskClass, self).__init__(config, work_name)
        self.download_buildtools = DownloadDefaultBuildtools(config)

    def run(self):
        self.download_buildtools.run()

    def install(self):
        self.download_buildtools.install()