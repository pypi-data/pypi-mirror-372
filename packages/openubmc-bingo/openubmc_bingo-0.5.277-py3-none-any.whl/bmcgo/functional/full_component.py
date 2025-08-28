#!/usr/bin/env python3
# coding: utf-8
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
import itertools
import json
import sys
import re
import stat
import shutil
import argparse
import importlib
import inspect
import functools
import random
from concurrent.futures import ProcessPoolExecutor, Future
from typing import List

from conans.model.manifest import FileTreeManifest
import yaml

from bmcgo import misc
from bmcgo.utils.fetch_component_code import FetchComponentCode
from bmcgo.component.component_dt_version_parse import ComponentDtVersionParse
from bmcgo.component.component_helper import (
    ComponentHelper,
    STAGE_DEV,
    STAGE_STABLE,
    STAGE_RC,
    BUILD_TYPE_DT,
    BUILD_TYPE_DEBUG,
    BUILD_TYPE_RELEASE,
)
from bmcgo.misc import CommandInfo, CONAN_USER
from bmcgo.utils.tools import Tools
from bmcgo.bmcgo_config import BmcgoConfig
from bmcgo.component.build import BuildComp
from bmcgo.errors import BmcGoException
from bmcgo.tasks.misc import MODULE_SYMVERS, SDK_PATH

tool = Tools("build_full")
log = tool.log
command_info: CommandInfo = CommandInfo(
    group="Misc commands",
    name="build_full",
    description=["获取组件源码并构建出组件的全量二进制"],
    hidden=True,
)


def if_available(bconfig: BmcgoConfig):
    if bconfig.conan_index:
        return False
    return True


class BuildComponent:
    def __init__(
        self,
        comp,
        profile: str,
        stage: str,
        build_type: str,
        options: dict,
        code_path: str,
        remote=misc.CONAN_REPO,
        service_json="mds/service.json",
        upload=False,
    ):
        self.bconfig = BmcgoConfig()
        self.comp_name, self.comp_version, *_ = re.split("@|/", comp)
        self.profile = profile
        self.stage = stage
        self.build_type = build_type
        self.options = options
        self.code_path = code_path
        self.option_cmd = ""
        self.remote = remote
        self.upload = upload
        self.service_json = service_json

    def run(self):
        os.chdir(os.path.join(self.code_path, self.comp_name))
        for key, value in self.options.items():
            self.option_cmd = self.option_cmd + f" -o {self.comp_name}:{key}={value}"
        command = (
            f"--remote {self.remote} -nc --stage {self.stage} --build_type {self.build_type.lower()}"
            f" --profile {self.profile} {self.option_cmd}"
        )
        log.info(f"执行构建命令bingo build {command}")
        args = command.split()
        build = BuildComp(self.bconfig, args, service_json=self.service_json)
        # 恢复工作区为clean状态, 保证conan export时scm信息准确
        tool.run_command("git restore .")
        tool.run_command("git clean -fd")
        build.run()
        log.success("组件{}构建成功".format(self.comp_name))
        if self.upload:
            log.info("上传组件包至conan仓......")
            tool.run_command(f'conan upload "*" --all --remote {self.remote} -c --no-overwrite')


class BmcgoCommand:
    def __init__(self, bconfig: BmcgoConfig, *args):
        parser = argparse.ArgumentParser(description="Fetch component source code and build all binaries.")
        parser.add_argument("-comp", "--component", help="软件包名, 示例: oms/1.2.6", required=True)
        parser.add_argument("-r", "--remote", help="远端仓库名称", default=misc.CONAN_REPO)
        parser.add_argument(
            "-p",
            "--path",
            help="指定拉取源代码的存放路径\n默认：./temp/source_code",
            default="./temp/source_code",
        )
        parser.add_argument("-pi", "--package_info", help="package_info文件路径", required=True)
        parser.add_argument("-u", "--upload", action=misc.STORE_TRUE, help="上传组件包到conan仓")
        parser.add_argument("--config_file", help="全量二进制配置文件")
        parser.add_argument("--skip_fetch", action=misc.STORE_TRUE, help="跳过fetch")
        parser.add_argument("--build_type", action="append", help="构建类型")

        parsed_args, _ = parser.parse_known_args(*args)
        self.bconfig = bconfig
        self.comp = parsed_args.component
        self.comp_name, self.comp_version, *_ = re.split("@|/", self.comp)
        self.code_path = os.path.realpath(os.path.join(bconfig.cwd, parsed_args.path))
        self.comp_path = os.path.join(self.code_path, self.comp_name)
        self.remote = parsed_args.remote
        self.package_info_path = os.path.realpath(os.path.join(bconfig.cwd, parsed_args.package_info))
        self.upload = parsed_args.upload
        self.config_file = parsed_args.config_file
        self.skip_fetch = parsed_args.skip_fetch
        self.profile_list = ["profile.dt.ini", "profile.luajit.ini"]
        self.stage_list = [STAGE_STABLE]
        self.built_type_list = [BUILD_TYPE_DT, BUILD_TYPE_DEBUG, BUILD_TYPE_RELEASE]
        if parsed_args.build_type:
            self.built_type_list = parsed_args.build_type
        self.options_dict = {}

    @staticmethod
    def get_conan_file_cls(comp_path):
        os.chdir(comp_path)
        # 先生成conanbase.py文件
        BuildComp(BmcgoConfig(), gen_conanbase=True)
        # 去除ConanFile, Conanbase继承, 用于方便区分
        tool.run_command("sed -i s/(ConanFile)/()/ conanbase.py")
        tool.run_command("sed -i s/(ConanBase)/()/ conanfile.py")
        # 动态导入conanfile.py模块
        sys.path.append(comp_path)
        conan_file_module = importlib.import_module("conanfile")
        conan_base_cls = conan_file_module.ConanBase
        cls_in_module = [member[1] for member in inspect.getmembers(conan_file_module) if inspect.isclass(member[1])]

        # 删除导入的conanbase和conanfile, 保证后续组件的导入是最新的conanbase和conanfile模块
        sys.modules.pop("conanbase")
        sys.modules.pop("conanfile")
        sys.path.pop()
        # 清空编译的conanbase缓存, 防止后续构建时使用了缓存的conanbase（未继承ConanFile版本)
        tool.run_command("rm -rf __pycache__")
        # 恢复工作区为clean状态, 保证conan export时scm信息准确
        tool.run_command("git restore .")
        tool.run_command("git clean -fd")

        conan_file_cls = None
        for conan_cls in cls_in_module:
            if conan_cls != conan_base_cls:
                conan_file_cls = conan_cls
                break
        if hasattr(conan_file_cls, "options"):
            return conan_file_cls

        return conan_base_cls

    @staticmethod
    def get_build_options(conan_file_cls, config_file):
        options_dict = {}
        if hasattr(conan_file_cls, "options"):
            options_dict = conan_file_cls.options

        # 添加module_symver选项
        module_symvers_path = os.path.join(SDK_PATH, MODULE_SYMVERS)
        module_symver_key, module_symver_value = tool.get_module_symver_option(module_symvers_path)
        if module_symver_key in options_dict:
            options_dict[module_symver_key] = [module_symver_value]
        if config_file:
            with open(config_file, "r") as yaml_fp:
                obj = yaml.safe_load(yaml_fp)
            BmcgoCommand.exclude_com_options(conan_file_cls, obj, options_dict)
            BmcgoCommand.exclude_all_options(obj, options_dict)
        tool.log.info(f"组件全量options选项为: {options_dict}")
        return options_dict

    @staticmethod
    def exclude_com_options(conan_file_cls, obj, options_dict):
        if conan_file_cls.name in obj:
            for exclude_option in obj[conan_file_cls.name]["exclude_options"]:
                del options_dict[exclude_option]

    @staticmethod
    def exclude_all_options(obj, options_dict):
        if obj.get("all", {}):
            for exclude_option in obj["all"]["exclude_options"]: 
                if exclude_option in options_dict:
                    del options_dict[exclude_option]

    @staticmethod
    def copy_stable2rc(comp: str):
        com_folder = os.path.join(tool.conan_data, comp)
        for version in os.listdir(com_folder):
            pkg = f"{comp}/{version}@{CONAN_USER}.release/{STAGE_STABLE}"
            if not os.path.exists(os.path.join(tool.conan_data, pkg.replace("@", "/"))):
                continue
            tool.run_command(f"conan copy {pkg} {CONAN_USER}.release/{STAGE_RC} --all --force")

    @staticmethod
    def copy_all_stable2rc(tools: Tools):
        comps = os.listdir(tools.conan_data)
        tools.log.info(f"创建多进程获取复制conan data下所有组件的stable到rc版本...")
        pool = ProcessPoolExecutor()
        future_tasks: List[Future] = []
        for comp in comps:
            task = pool.submit(BmcgoCommand.copy_stable2rc, comp)
            future_tasks.append(task)

        pool.shutdown()
        for task in future_tasks:
            task_exception = task.exception()
            if task_exception is not None:
                raise task_exception

    @staticmethod
    def _replace_dev_version(temp_service_json: str):
        version_parse = ComponentDtVersionParse(serv_file=temp_service_json)
        for pkg in version_parse.conan_list:
            component = pkg[misc.CONAN]
            if "@" not in component:
                continue
            comp_version, user_channel = component.split("@")
            if user_channel.endswith(STAGE_DEV):
                pkg[misc.CONAN] = f"{comp_version}{ComponentHelper.get_user_channel(STAGE_DEV)}"

        version_parse.write_to_serv_file()

    @functools.cached_property
    def _full_reference(self) -> str:
        comp_pkg = self.comp if "@" in self.comp else f"{self.comp}@{CONAN_USER}.release/{STAGE_STABLE}"
        return comp_pkg

    @functools.cached_property
    def _is_self_developed(self) -> bool:
        tool.run_command(f"conan download {self._full_reference} --recipe -r {self.remote}")
        comp_package_path = os.path.join(tool.conan_data, self.comp_name)
        ret = tool.run_command(f"find {comp_package_path} -name 'conanbase.py'", capture_output=True)
        return bool(ret.stdout)

    def fetch_code(self):
        conan_path = os.path.join(tool.conan_data, self.comp_name)
        if os.path.isdir(conan_path):
            shutil.rmtree(conan_path)
        if os.path.isdir(self.code_path):
            shutil.rmtree(self.code_path)
        os.makedirs(self.code_path)
        packages = {self.comp_name: self._full_reference}
        FetchComponentCode(packages, self.code_path, self.remote).run()

    def revise_comp_version(self, service_json: str):
        """修订version为当前指定的版本, 以支持x.y.z-build.x格式的补丁版本

        Args:
            service_json (str): service.json文件路径
        """
        os.chdir(self.comp_path)
        file_open_mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
        with os.fdopen(os.open(service_json, flags=os.O_RDWR, mode=file_open_mode), "w+") as file_handler:
            service_json_data = json.load(file_handler)
            service_json_data["version"] = self.comp_version
            file_handler.seek(0)
            file_handler.truncate()
            json.dump(service_json_data, file_handler, indent=4, ensure_ascii=False)
            file_handler.close()

    def revise_service_dependencies(self, service_json: str):
        """修订build/test的依赖组件的版本为patch范围版本

        Args:
            service_json (str): service.json文件路径
        """
        os.chdir(self.comp_path)
        with open(service_json, "r", encoding="UTF-8") as file_handler:
            service_json_data = json.load(file_handler)
        dependencies = service_json_data.get(misc.CONAN_DEPDENCIES_KEY, {})
        if not dependencies:
            # service.json中没有依赖，可直接构建
            return
        ComponentDtVersionParse(serv_file=service_json).manifest_version_revise(
            self.package_info_path, use_patch_range=True
        )
        self._replace_dev_version(service_json)

    def run(self):
        if not self.skip_fetch:
            if not self._is_self_developed:
                tool.log.warning(f"非自研组件{self.comp}不支持该功能。")
                return
            self.fetch_code()
        self._package_docs_from_source()
        conan_file_cls = self.get_conan_file_cls(self.comp_path)
        self.options_dict = self.get_build_options(conan_file_cls, self.config_file)
        service_json = self._create_temp_service_json()
        self.revise_comp_version(service_json)
        self.revise_service_dependencies(service_json)
        self.build_all_packages(service_json)
        self.copy_all_stable2rc(tool)
        if self.upload:
            log.info("上传组件包至conan仓......")
            tool.run_command(f'conan upload "*" --all --remote {self.remote} -c --no-overwrite')

    def build_all_packages(self, service_json: str):
        """构建出组件所有组合的package包

        Args:
            service_json (str): 显式指定用于生成conanbase.py依赖的service.json路径
        """

        all_attributes = {
            "profile": self.profile_list,
            "stage": self.stage_list,
            "build_type": self.built_type_list,
        }
        # 不参与构建二进制的选项
        block_options = ["asan", "gcov"]
        options_dict = self.options_dict
        for block in block_options:
            options_dict.pop(block, None)

        all_attributes = {**all_attributes, **options_dict}
        # 设置变量让所有场景（包括DT）构建lua代码时都进行编译
        os.environ["TRANSTOBIN"] = "true"
        log.info(f"构建组件{self.comp}的全量二进制, 选项包含：{options_dict}")
        all_build_params = list(itertools.product(*all_attributes.values()))
        if not self.skip_fetch:
            random.shuffle(all_build_params)
        for build_args in all_build_params:
            profile, stage, build_type, *option_values = build_args
            if profile == "profile.dt.ini" and build_type.lower() != BUILD_TYPE_DT.lower():
                continue
            if profile != "profile.dt.ini" and build_type.lower() == BUILD_TYPE_DT.lower():
                continue
            build_options = dict(zip(options_dict.keys(), option_values))
            task = BuildComponent(
                self.comp,
                profile,
                stage,
                build_type,
                build_options,
                self.code_path,
                remote=self.remote,
                service_json=service_json,
                upload=self.upload,
            )
            task.run()

    def _create_temp_service_json(self):
        temp_path = os.path.join(self.comp_path, "temp")
        os.makedirs(temp_path, exist_ok=True)
        temp_service_json = os.path.join(temp_path, "service.json")
        if not os.path.isfile(temp_service_json):
            tool.copy(os.path.join(self.comp_path, "mds/service.json"), temp_service_json)
        return temp_service_json

    def _package_docs_from_source(self):
        os.chdir(self.comp_path)
        current_path = os.getcwd()
        package_folder = []
        for entry in os.listdir(current_path):
            entry_l = entry.lower()
            if entry_l == "mds" or entry_l == "docs":
                package_folder.append(entry)
            elif "changelog" in entry_l or entry_l.endswith(".md"):
                package_folder.append(entry)
        if not package_folder:
            tool.log.info("无docs文档, 跳过文档打包。")
            return
        tar_cmd = ["tar", "-czvf", f"{self.code_path}/{self.comp_name}_docs.tar.gz"] + package_folder
        tool.run_command(tar_cmd)
