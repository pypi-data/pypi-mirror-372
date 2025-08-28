#!/usr/bin/env python3
# encoding=utf-8
# 描述：apt安装工具
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
from typing import Dict, List
from bmcgo.utils.installations import install_consts
from bmcgo.utils.installations.version_util import PkgVersion
from bmcgo.utils.installations.base_installer import BaseInstaller


class AptInstaller(BaseInstaller):
    type_name = "apt"

    def __init__(self):
        super().__init__()
        self._apt_cmd = None
        self._doc = None

    def pre_install(self):
        self._apt_cmd = shutil.which("apt-get")
        if not self._apt_cmd:
            raise RuntimeError("未找到 apt-get 指令")
        
        self._update_cache()
        try:
            self.tools.run_command(["apt", "policy", self._pkg_name], capture_output=True)
        except Exception as e:
            self.info(f"本地源未正确配置，请参考社区文档进行配置：{self._doc}")


    def install(self, force: bool):
        if self.current_version == self.target_version and not force:
            yes = input(f"[apt]当前版本已满足(=={self.target_version}), 是否覆盖安装?[Y/n]")
            if yes == "n":
                self.info(f"用户跳过覆盖安装{self._pkg_name}={self.target_version}")
                return

        pkg = f"{self._pkg_name}={self.target_version}"
        self.info(f"开始安装{pkg}")
        self._install_package(pkg, force)
        self.info(f"安装{pkg}完成！")

    def show_versions(self):
        versions = self.get_versions()
        if not versions:
            self.error("未找到可用的版本")
            return
        self.info(f"可用版本: {", ".join(versions)}")

    def get_versions(self) -> List[PkgVersion]:
        result = self.tools.run_command(["apt-cache", "madison", self._pkg_name], capture_output=True)
        if not result or not result.stdout:
            return []
        versions = [line.split("|")[1].strip() for line in result.stdout.splitlines()]
        versions.sort(key=PkgVersion, reverse=True)
        return versions
    
    def get_current_version(self):
        try:
            result = self.tools.run_command(["dpkg-query", "-W", "-f=${Version}", self._pkg_name], capture_output=True)
            if not result or not result.stdout:
                return
            self._cur_ver = result.stdout
        except Exception as e:
            return

    def parse_custom_plan(self, plan: Dict[str, List[str]]):
        self._doc = plan.get(install_consts.PLAN_DOC)
        if not self._doc:
            self.warning(f"未配置 {install_consts.PLAN_DOC}")

    def _update_cache(self):
        self.info("更新 apt 缓存")
        try:
            self.tools.run_command(["apt-get", "update"], sudo=(os.getuid() != 0))
        except Exception as e:
            raise RuntimeError(f"安装失败： {str(e)}")
        
    def _install_package(self, pkg: str, force: bool):
        self.info(f"安装: {pkg}")
        try:
            cmd = ["apt-get", "install", "--allow-downgrades", pkg]
            if force:
               cmd.append("-y") 
            self.tools.run_command(cmd, sudo=(os.getuid() != 0))

        except Exception as e:
            raise RuntimeError(f"安装失败: {str(e)}")
        