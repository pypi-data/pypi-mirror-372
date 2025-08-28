#!/usr/bin/env python3
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
import time
import json
import re
from typing import List
from multiprocessing import Process
from tempfile import NamedTemporaryFile
from packaging import version

from bmcgo.utils.tools import Tools
from bmcgo.bmcgo_config import misc
from bmcgo.errors import BmcGoException

STAGE_DEV = "dev"
STAGE_PRE = "pre"
STAGE_RC = "rc"
STAGE_STABLE = "stable"

BUILD_TYPE_DT = "DT"
BUILD_TYPE_DEBUG = "Debug"
BUILD_TYPE_RELEASE = "Release"


class DownloadComponentRecipe(Process):
    def __init__(self, tools: Tools, comp, remote_list: list):
        super().__init__()
        self.comp = comp
        self.tools = tools
        self.remote_list = remote_list

    def run(self):
        dep_path = os.path.join(self.tools.conan_data, self.comp.replace("@", "/"))
        if os.path.isdir(dep_path):
            return
        self.tools.download_conan_recipes(self.comp, self.remote_list)


class ComponentHelper:
    CONAN_PAKCAGE_RE = r"^[^@|/]+/[^@|/]+@[^@|/]+/(rc|stable|dev)$"

    @staticmethod
    def get_language(service_json="mds/service.json", allow_non_service_json=False):
        if not os.path.isfile(service_json):
            if allow_non_service_json:
                return "lua"
            raise RuntimeError(f"{service_json}文件不存在")
        with open(service_json, "r", encoding="UTF-8") as service_fp:
            content = json.load(service_fp)
        return content.get("language", "lua")

    @staticmethod
    def compare_versions(version_str, target_version="1.80.35"):
        # 处理简单版本号格式 a/1.1xxx
        simple_match = re.match(r'[^/]+/(\d+\.\d+(?:\.\d+)?)', version_str)
        if simple_match:
            return version.parse(simple_match.group(1)) >= version.parse(target_version)
        
        # 处理待条件的版本号
        condition_match = re.findall(r'\[([^]]+)\]', version_str)
        if condition_match:
            conditions = condition_match[0].split()

            # 只有>或>=
            if len(conditions) == 1 and any(op in conditions[0] for op in [">", ">="]):
                return True
            
            # 包含<或<=
            for cond in conditions:
                if "<=" in cond:
                    ver = cond.lstrip("<=>")
                    return version.parse(ver) >= version.parse(target_version)
                elif "<" in cond:
                    ver = cond.lstrip("<=>")
                    return version.parse(ver) > version.parse(target_version)
            
            ver = conditions[0].lstrip("<=>")
            return version.parse(ver) >= version.parse(target_version)
        
        return False

    @staticmethod
    def enable_new_major_version(dependencies):
        if not dependencies:
            return False
        
        for dependency in dependencies:
            version_str = dependency.get("conan", "")
            if not version_str.startswith("libmc4lua"):
                continue
            return ComponentHelper.compare_versions(version_str)

        return False

    @staticmethod
    def get_major_version(service_json="mds/service.json"):
        if not os.path.isfile(service_json):
            raise RuntimeError(f"{service_json}文件不存在")
        with open(service_json, "r", encoding="UTF-8") as service_fp:
            content = json.load(service_fp)
        
        return 1 if (ComponentHelper.enable_new_major_version(content.get("dependencies", {}).get("build", {})) or \
                ComponentHelper.enable_new_major_version(content.get("dependencies", {}).get("test", {}))) else 0

    @staticmethod
    def get_config_value(json_data, key: str, default=None):
        for sub_key in key.split("/"):
            json_data = json_data.get(sub_key, None)
            if json_data is None:
                return default
        return json_data

    @staticmethod
    def download_recipes(depdencies: List[str], tools: Tools, remote_list):
        pools = []
        for dep in depdencies:
            task = DownloadComponentRecipe(tools, dep, remote_list)
            task.start()
            pools.append(task)

        while pools:
            time.sleep(0.1)
            for pool in pools.copy():
                if pool.is_alive():
                    continue
                if pool.exitcode is not None and pool.exitcode != 0:
                    raise BmcGoException(f"下载组件 ({pool.comp}) 的构建配方(recipe)失败, 退出码: {pool.exitcode}")
                pools.remove(pool)

    @staticmethod
    def get_all_dependencies(components: List[str], remote) -> List[str]:
        """获取给定的多个组件com/x.yz@user/channel的直接及间接依赖的所有组件及版本。"""
        tools = Tools()
        dependencies = set()
        tempfile = NamedTemporaryFile()
        for comp in components:
            if not re.match(ComponentHelper.CONAN_PAKCAGE_RE, comp):
                raise BmcGoException(f"组件 {comp} 不符合正则 {ComponentHelper.CONAN_PAKCAGE_RE}")
            cmd = f'conan info "{comp}" --remote {remote} --json {tempfile.name}'
            tools.run_command(cmd)

            file_handler = open(tempfile.name, "r")
            conan_comps = json.load(file_handler)
            for conan_comp in conan_comps:
                comp_ref = conan_comp.get("reference", "")
                if not comp_ref or comp_ref == comp:
                    continue
                dependencies.add(comp_ref)
            file_handler.close()

        return list(dependencies)

    @staticmethod
    def get_user_channel(stage: str):
        if stage == misc.StageEnum.STAGE_DEV.value:
            stage = misc.StageEnum.STAGE_RC.value
        user_channel = f"@{Tools().conan_user}/{stage}"
        return user_channel
