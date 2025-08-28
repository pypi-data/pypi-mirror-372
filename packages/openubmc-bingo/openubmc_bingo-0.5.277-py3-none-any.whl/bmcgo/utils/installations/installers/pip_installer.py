#!/usr/bin/env python3
# encoding=utf-8
# 描述：pip安装工具
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import sys
from importlib.metadata import distributions
from typing import Dict, List
from bmcgo.utils.installations import install_consts
from bmcgo.utils.installations import version_util
from bmcgo.utils.installations.base_installer import BaseInstaller


class PipInstaller(BaseInstaller):
    type_name = "pip"

    def __init__(self):
        super().__init__()
        self._app_name = None

    def install(self, force):
        if self.current_version == self.target_version and not force:
            yes = input(f"[pip]: 当前版本已满足(=={self.target_version}), 是否覆盖安装?[Y/n]")
            if yes == "n":
                self.info(f"用户跳过覆盖安装{self._pkg_name}={self.target_version}")
                return

        pkg_info = f"{self._pkg_name}=={self.target_version}"
        cmds = [sys.executable, "-m", "pip", "install", "--upgrade", pkg_info]
        
        with open("/etc/issue", "r") as fp:
            issue = fp.readline()
            if issue.startswith("Ubuntu 24.04"):
                cmds.append("--break-system-packages")

        self.info(f"pip 开始安装{pkg_info}")
        self.tools.run_command(cmds, show_log=True)
        self.info(f"pip 安装{pkg_info}完成！")

    def parse_custom_plan(self, plan: Dict[str, List[str]]):
        self._app_name = plan.get(install_consts.PLAN_MODULE_NAME)

    def show_versions(self):
        versions_mirror = self.get_versions()
        if not versions_mirror:
            self.error(f"未找到可用的版本")
        self.info(f"可用版本: {", ".join(versions_mirror)}")

    def get_versions(self, index_url=None):
        cmd = [sys.executable, "-m", "pip", "index", "versions", self._pkg_name]
        if index_url is not None:
            cmd.extend(["-i", index_url])
        ret = self.tools.run_command(cmd, capture_output=True)
        for l in ret.stdout.splitlines():
            if l.strip().startswith("Available versions: "):
                # 跳过 Available, versions:
                versions = [v.strip() for v in l.replace("Available versions:", "").split(",")]
                versions.sort(key=version_util.PkgVersion, reverse=True)
                return versions
        else:
            if index_url:
                self.error(f"从 {index_url} 获取版本号失败!")
            else:
                self.error("获取版本号失败!")
        return []
    
    def get_current_version(self):
        for dist in distributions():
            metadata = dist.metadata
            if self._pkg_name == metadata["Name"]:
                self._cur_ver = metadata["Version"]
                break
        