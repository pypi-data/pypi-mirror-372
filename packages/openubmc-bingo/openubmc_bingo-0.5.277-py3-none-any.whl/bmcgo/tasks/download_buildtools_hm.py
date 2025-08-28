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
功    能：下载并安装V2X的rtos/hcc工具
修改记录：2024-08-29 创建
"""
import os
import shutil

from bmcgo.tasks.task import Task
from bmcgo.utils.config import Config
from bmcgo import misc


class DownloadHmBuildTools(Task):
    def __init__(self, config: Config):
        super(DownloadHmBuildTools, self).__init__(config, "DownloadHmBuildTools")
        self.dependency_file = os.path.realpath(
            os.path.join(self.config.code_path, self.get_manufacture_config("base/dependency_buildtools"))
        )
        self.rtos_sdk_dir = f"{self.config.tools_path}/rtos-sdk-arm64-hm"
        _, buildtool_config = self.get_profile_config()
        self.standalone_toolchain = buildtool_config.get("standalone_toolchain", self.config.cross_compile_install_path)
        self.sdkroot = buildtool_config.get("sdkroot", "/opt/hi1711sdk")
        self.rtos_root = buildtool_config.get("rtos_root", f"/opt/{self.config.rtos_offering}")
        self.sysroot = buildtool_config.get("sysroot", self.config.sysroot)
        self.target_host = buildtool_config.get("target_host", self.config.cross_prefix)
        self.dep_md5 = f"{self.rtos_root}/dependency.md5sum"
        self.dep_md5_new = f"{self.tools.user_home}/dependency.md5sum.new"
        self.skip_install = False

    def download_tools(self):
        self.info(f"移除下载路径: {self.rtos_sdk_dir}")
        self.run_command(f"rm -rf {self.rtos_sdk_dir}", ignore_error=True, sudo=True)
        self.info("开始下载依赖工具...")
        partner_tools_dir = f"{os.path.expanduser('~')}/rtos_compiler"
        if self.config.partner_mode:
            self.info(f"从缓存目录{partner_tools_dir}复制编译器工具")
            self.run_command(f"cp -rf {partner_tools_dir}/. {self.rtos_sdk_dir}")
        self.info("下载依赖工具结束")

    def check_rtos_sdk(self):
        is_ubuntu = self.tools.is_ubuntu
        self.chdir(self.rtos_sdk_dir)
        self.info("安装 rpm 包")
        self.info(f"删除目录 {self.rtos_root}")
        self.run_command(f"rm -rf {self.rtos_root}", sudo=True)
        for rpm in os.listdir("./"):
            if not os.path.isfile(rpm) or not rpm.endswith(".rpm"):
                continue
            self.info("安装 {}".format(rpm))
            if not is_ubuntu:
                self.run_command("rpm -ivh {}".format(rpm), sudo=True)
            else:
                self.pipe_command(["rpm2cpio {}".format(rpm), "sudo cpio -id -D /"])

        self.info(f"删除目录 {self.standalone_toolchain}")
        self.run_command(f"rm -rf {self.standalone_toolchain}", sudo=True)
        self.info("解压 hcc_arm64le")
        self.run_command("tar -xzf hcc_arm64le.tar.gz -C /opt", sudo=True)

        hm_tiny = "/opt/hcc_arm64le_hm_tiny"
        self.info(f"删除目录 {hm_tiny}")
        self.run_command(f"rm -rf {hm_tiny}", sudo=True)
        self.info("解压 hcc_arm64le_hm_tiny")
        self.run_command("tar -xzf hcc_arm64le_hm_tiny.tar.gz -C /opt", sudo=True)

        self.info(f"删除目录 {self.sdkroot}")
        self.run_command(f"rm -rf {self.sdkroot}", ignore_error=True, sudo=True)
        self.run_command(f"mkdir -p {self.sdkroot}", ignore_error=True, sudo=True)
        self.info("解压 hi1711sdk")
        self.run_command(f"tar -xzf hi1711sdk.tar.gz -C {self.sdkroot} Module.symvers", sudo=True)
        logname = os.getenv(misc.ENV_LOGNAME, None)
        if logname and logname != "root":
            self.run_command(f"chown {logname} {self.rtos_root} -R", sudo=True)
            self.run_command(f"chown {logname} {self.sdkroot} -R", sudo=True)
            self.run_command(f"chown {logname} {self.standalone_toolchain} -R", sudo=True)
            self.run_command(f"chown {logname} {hm_tiny} -R", sudo=True)

        self.chdir(self.config.code_path)

        libstdcpp_install_path = os.path.join(self.sysroot, "usr")
        os.makedirs(libstdcpp_install_path, exist_ok=True)

        cross_compile_lib64 = os.path.join(self.standalone_toolchain, self.target_host, "lib64")
        self.run_command(f"cp -rf {cross_compile_lib64} {libstdcpp_install_path}")

        cmake_platform, _ = self.pipe_command(
            ["find /usr/share -type d -wholename */Modules/Platform", "head -n 1"], sudo=True, capture_output=True
        )
        self.info(f"复制HongMeng.cmake到 {cmake_platform}")
        hm_cmake = os.path.join(libstdcpp_install_path, "share/cmake/Modules/Platform/HongMeng.cmake")
        self.run_command(f"cp -af {hm_cmake} {cmake_platform}", sudo=True)

        self.run_command("cp -af {} {}".format(self.dep_md5_new, self.dep_md5))
        # md5文件对齐其他分支
        dep_md5_br = f"{self.tools.user_home}/dependency.md5sum"
        self.run_command(f"cp -af {self.dep_md5_new} {dep_md5_br}")

    def run(self):
        self.pipe_command([f"md5sum {self.dependency_file}"], self.dep_md5_new)
        if os.path.isfile(self.dep_md5):
            with open(self.dep_md5, "r") as fp:
                md5old = fp.read()
            with open(self.dep_md5_new, "r") as fp:
                md5new = fp.read()
            if md5old == md5new:
                self.info("版本匹配, 跳过安装")
                self.skip_install = True
                return
        self.download_tools()

    def install(self):
        if self.skip_install:
            return
        # 检查rtos是否安装，未安装或版本不匹配时安装
        self.check_rtos_sdk()
