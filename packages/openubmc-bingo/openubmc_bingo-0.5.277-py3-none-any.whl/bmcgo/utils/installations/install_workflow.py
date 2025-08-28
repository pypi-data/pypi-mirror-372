#!/usr/bin/env python3
# encoding=utf-8
# 描述：安装流程配置
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

from typing import Dict, List
from pathlib import Path
import yaml
from bmcgo.utils.tools import Tools
from bmcgo.utils.installations import install_consts


tools = Tools("install")


class InstallWorkflow:
    logger = tools.log
    _workflows: Dict[str, List[str]] = {}
    search_paths: List[Path] = [Path(__file__).resolve().parent / install_consts.PLUGIN_INSTALL_PLAN_PATH]

    @staticmethod
    def tool_exists(tool_name: str, install_type: str):
        try:
            if install_type == "pip":
                ret = tools.run_command(f"pip show {tool_name}", capture_output=True, ignore_error=True)
                return ret.returncode == 0
            if install_type == "apt":
                ret = tools.run_command(f"dpkg -s {tool_name}", capture_output=True, ignore_error=True)
                return "Status: install ok installed" in ret.stdout
        except Exception as e:
            tools.log.info(f"校验工具存在性时报错：{str(e)}")

        return False
    
    @classmethod
    def discover_workflows(cls):
        for path in cls.search_paths:
            if not path.exists():
                cls.logger and cls.logger.warning(f"未找到安装配置路径：{str(path)}, 跳过")
                continue

            for yml_file in path.glob("*.yml"):
                with open(yml_file) as conf:
                    file_content = yaml.safe_load(conf)
                    cls._register_workflows(yml_file=yml_file, file_content=file_content)

    @classmethod
    def parse(cls, name: str) -> List[str]:
        workflow = cls._workflows.get(name)
        if not workflow:
            raise ValueError(f"未找到安装配置：{str(workflow)}")
        return workflow

    @classmethod
    def add_plan_dir(cls, directory: Path):
        if directory not in cls.search_paths:
            cls.search_paths.append(directory)

    @classmethod
    def get_all_plans(cls):
        return cls._workflows.keys()
    
    @classmethod
    def _register_workflows(cls, yml_file, file_content):
        plans = file_content.get(install_consts.PLAN_STEPS, [])
        for plan in plans:
            inst_type = plan.get(install_consts.PLAN_INSTALL_TYPE)
            if not inst_type:
                raise ValueError(f"未配置 {yml_file}/{install_consts.PLAN_STEPS}/{install_consts.PLAN_INSTALL_TYPE}")
            package_name = plan.get(install_consts.PLAN_PACKAGE_NAME)
            if cls.tool_exists(package_name, inst_type): # 未安装的工具不加入_workflows
                cls._workflows[yml_file.stem] = file_content
