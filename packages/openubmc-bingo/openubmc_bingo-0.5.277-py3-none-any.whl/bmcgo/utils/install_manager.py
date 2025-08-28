#!/usr/bin/env python3
# encoding=utf-8
# 描述：安装管理器
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

from pathlib import Path
from typing import Dict, List
from bmcgo import misc
from bmcgo.utils.tools import Tools
from bmcgo.utils.installations import install_consts
from bmcgo.utils.installations.install_workflow import InstallWorkflow
from bmcgo.utils.installations.base_installer import BaseInstaller


tools = Tools("install")
logger = tools.log


class InstallManager:
    def __init__(self):
        self._custom_path = None
        self._workflows = []
        self._installers: Dict[str, List[BaseInstaller]] = {}

    @property
    def custom_installer_path(self):
        return self._custom_path / install_consts.PLUGIN_INSTALLER_PATH
    
    @property
    def custom_install_plan_path(self):
        return self._custom_path / install_consts.PLUGIN_INSTALL_PLAN_PATH
    
    def init(self, app_name, operator, version, custom_path):
        self._set_custom_path(custom_path)

        if app_name == install_consts.INSTALL_ALL:
            self._workflows = list(InstallWorkflow.get_all_plans())
        else:
            self._workflows = [app_name]
        
        for wname in self._workflows:
            workflow = InstallWorkflow.parse(wname)
            plans = workflow.get(install_consts.PLAN_STEPS, [])
            for plan in plans:
                inst_type = plan.get(install_consts.PLAN_INSTALL_TYPE)
                if not inst_type:
                    raise ValueError(f"未配置 {wname}/{install_consts.PLAN_STEPS}/{install_consts.PLAN_INSTALL_TYPE}")
                inst = BaseInstaller.get_installer(inst_type)
                inst.init(plan, operator, version)
                self._installers.setdefault(wname, []).append(inst)

    def show_versions(self):
        for wname in self._workflows:
            if wname not in self._installers:
                raise RuntimeError(f"初始化 {wname} 出现问题，请重试！")

            for inst in self._installers[wname]:
                logger.info(f"获取 {inst.package_name} {inst.type_name} 版本信息...")
                inst.show_versions()

    def pre_install(self):
        for wname in self._workflows:
            logger.info(f"安装 {wname} 前检查...")
            plans = InstallWorkflow.parse(wname)
            verisons = {}
            if wname not in self._installers:
                raise RuntimeError(f"初始化 {wname} 出现问题，请重试！")
            for inst in self._installers[wname]:
                inst.pre_install()
                verisons[inst.type_name] = inst.target_version

            require_version_homogeneous = plans.get(install_consts.PLAN_VERSION_HOMOGENEOUS, False)
            if require_version_homogeneous and len(set(verisons.values())) > 1:
                for t, v in verisons.items():
                    logger.error(f"{t}: {v}")
                raise ValueError("版本不一致，终止安装!")

    def install(self, force):
        logger.info("开始安装...")
        for wname in self._workflows:
            logger.info(f"安装{wname}...")
            try:
                if wname not in self._installers:
                    raise RuntimeError(f"初始化 {wname} 出现问题，请重试！")
                for inst in self._installers[wname]:
                    inst.install(force)
            except Exception as e:
                logger.info(f"安装失败，回退{wname}...")
                if wname not in self._installers:
                    raise RuntimeError(f"初始化 {wname} 出现问题，请重试！") from e
                for inst in self._installers[wname]:
                    inst.rollback()
                raise RuntimeError("安装失败") from e

    def post_install(self):
        for wname in self._workflows:
            logger.info(f"清理安装{wname}的中间文件...")
            if wname not in self._installers:
                raise RuntimeError(f"初始化 {wname} 出现问题，请重试！")
            for inst in self._installers[wname]:
                inst.post_install()

    def _set_custom_path(self, custom_path: str):
        self._custom_path = Path(custom_path).resolve()
        BaseInstaller.add_installer_dir(self.custom_installer_path)
        InstallWorkflow.add_plan_dir(self.custom_install_plan_path)
        BaseInstaller.discover_installers()
        InstallWorkflow.discover_workflows()
