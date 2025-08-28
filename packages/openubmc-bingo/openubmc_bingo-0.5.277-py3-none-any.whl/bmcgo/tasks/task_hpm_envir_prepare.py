#!/usr/bin/env python3
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
import os
import subprocess
import time
from multiprocessing import Process
from bmcgo.tasks.task import Task
from bmcgo import errors


class SignProcess(Process):
    def __init__(self, work: Task):
        super().__init__()
        self.work = work
        self.config = self.work.config

    def run(self):
        self.work.work_name = "sign_rootfs_image"
        self.work.chdir(self.config.build_path)
        if self.config.self_sign:
            self.work.signature(f"{self.config.work_out}/rootfs_BMC.img",
                                f"{self.config.work_out}/rootfs_BMC.img.cms",
                                f"{self.config.work_out}/cms.crl",
                                f"{self.config.work_out}/rootca.der")
        else:
            out_file = f"{self.config.work_out}/rootfs_BMC.img.cms"
            self.work.tools.pipe_command([f"echo 'cms placeholder'"], out_file=out_file)


class TarImageProcess(Process):
    def __init__(self, work):
        super().__init__()
        self.work: Task = work
        self.config = self.work.config

    def run(self):
        self.work.work_name = "tar_rootfs_image"
        self.work.chdir(self.config.work_out)
        self.work.run_command("tar --format=gnu --exclude BMC_rootfs.tar.gz -czf rootfs_BMC.tar.gz rootfs_BMC.img")
        self.work.success("tar BMC_rootfs.tar.gz successfully")


class TaskClass(Task):
    skip_post_hpm = False

    @staticmethod
    def get_shell_command_result(cmd):
        ret = subprocess.getstatusoutput(cmd)
        if ret[0] == 1:
            raise Exception(f"运行命令 {cmd} 失败")
        return ret[1]

    def set_skip_post_hpm(self, value):
        if value:
            self.skip_post_hpm = True
        else:
            self.skip_post_hpm = False

    def copy_file_or_dir(self, src_dir, dst_dir):
        self.pipe_command(["yes y", f"cp -ai {src_dir} {dst_dir}"])
        return

    def prepare_hpm(self):
        hpm_build_dir = self.config.hpm_build_dir
        hpm_build_dir_src = f"/usr/share/bmcgo/ipmcimage"
        self.tools.copy_all(hpm_build_dir_src, hpm_build_dir)

        self.run_command(f"cp {self.config.board_path}/update_ext4.cfg {hpm_build_dir}/update.cfg")

        self.chdir(hpm_build_dir)
        if not self.skip_post_hpm:
            self._component_cust_action("post_hpm")

        curr_ver = self.get_shell_command_result("cat update.cfg | grep '^Version=' | awk -F '=' '{print $2}'")

        # 读取发布时用的包名
        vs = self.config.version.split(".")
        if self.manufacture_version_check(f"{self.config.board_path}/manifest.yml") is True:
            vs[3] = str(int(vs[3]) + 1).zfill(2)
        ver = f"{vs[0]}.{vs[1]}.{vs[2]}.{vs[3]}"

        # 正常包
        self.info(f"bmc 版本: {ver}")
        self.run_command(
            f"sed -i \"/^Version=/s/{curr_ver}/{ver}/g\" update.cfg")
        self.run_command("chmod +x . -R")

    def run(self):
        # 创建签名进程
        sign = SignProcess(self)
        sign.start()

        self.prepare_hpm()

        # 创建压缩进程
        tar = TarImageProcess(self)
        tar.start()
        while True:
            if not sign.is_alive():
                if sign.exitcode is not None and sign.exitcode != 0:
                    raise errors.BmcGoException(f"签名进程发生错误, 返回值: {sign.exitcode}")
                break
            time.sleep(0.1)
        while True:
            if not tar.is_alive():
                if tar.exitcode is not None and tar.exitcode != 0:
                    raise errors.BmcGoException(f"打包进程发生错误, 返回值: {tar.exitcode}")
                break
            time.sleep(0.1)

