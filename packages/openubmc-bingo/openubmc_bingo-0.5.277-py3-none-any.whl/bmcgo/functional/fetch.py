#!/usr/bin/env python3
# encoding=utf-8
# 描述：拉取当前minifest快照下的全量代码
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
import json
import re
import argparse
from multiprocessing import Pool
import yaml
from git import Repo
from bmcgo.codegen.c.helper import Helper
from bmcgo.logger import Logger
from bmcgo.bmcgo_config import BmcgoConfig
from bmcgo.utils.tools import Tools
from bmcgo import misc
from bmcgo.errors import ParameterException
from bmcgo.utils.fetch_component_code import FetchComponentCode

tools = Tools()
log = Logger()

command_info: misc.CommandInfo = misc.CommandInfo(
    group=misc.GRP_MISC,
    name="fetch",
    description=["基于参数指定的单个、部分、全量组件版本拉取源代码"],
    hidden=False
)


def if_available(bconfig: BmcgoConfig):
    if bconfig.component:
        return False
    return True


def process_err_cb(err):
    log.error("进程运行失败, 错误: %s", err)


_PACKAGE_INFO_HELP = """
1. 通过组件包名及版本拉取单个组件源码，格式：package/version@user/channel
2. 通过配置文件拉取部分指定版本的组件源码。支持以下2种配置文件：
  a. yml格式
    dependencies:
    - conan: "package/version@user/channel"
  b. 文本格式
    package/version@user/channel
"""


class BmcgoCommand:
    conan_package_re = r"^[^@|/]+/[^@|/]+@[^@|/]+/(rc|stable|dev)$"

    def __init__(self, bconfig: BmcgoConfig, *args):
        self.bconfig = bconfig
        parser = argparse.ArgumentParser(prog="bingo fetch", description="BMC source code fetch", add_help=True,
                                         formatter_class=argparse.RawTextHelpFormatter)
        if self.bconfig.manifest:
            manifest_exclusive_group = parser.add_mutually_exclusive_group()
            manifest_exclusive_group.add_argument(
                "-b",
                "--board_name",
                help="指定单板获取配套全量源码，可选值为build/product目录下的单板名\n默认：openUBMC",
                default="openUBMC",
            )
            manifest_exclusive_group.add_argument("--manifest_yml", help="指定manifest.yml文件获取源码", default=None)
            manifest_exclusive_group.add_argument("-pi", "--package_info", help=_PACKAGE_INFO_HELP, default=None)
            manifest_exclusive_group.add_argument("-sys", "--subsystem", help="根据平台获取源码，可选平台包括（opensource、public、\
framework、bmc_core、security、hardware、ras、energy、om、interface、product_extension、customer_extension）", default=None)
            parser.add_argument("--stage", help="包类型，可选值为: rc（预发布包）, stable（发布包）\n默认：stable", default='stable')
            parser.add_argument("-a", "--all", help="拉取全部conan代码", action=misc.STORE_TRUE)
        else:
            parser.add_argument("-pi", "--package_info", help=_PACKAGE_INFO_HELP, required=True)

        parser.add_argument("-p", "--path", help="指定拉取源代码的存放路径\n默认：./source_code", default="./source_code")

        parser.add_argument("-r", "--remote", help=f"conan仓别名，请检查conan remote list查看已配置的conan仓")

        parsed_args, _ = parser.parse_known_args(*args)
        self.component_ver = {}
        self.remote = parsed_args.remote
        self.code_path = os.path.realpath(os.path.join(os.getcwd(), parsed_args.path))
        self.package_info = parsed_args.package_info
        if self.bconfig.manifest:
            self.stage = parsed_args.stage
            self.board_name = parsed_args.board_name
            self.manifest_yml_path = parsed_args.manifest_yml
            self.manifest_build_dir = os.path.join(self.bconfig.manifest.folder, "build")
            self.fetch_all = parsed_args.all
            self.subsystem = parsed_args.subsystem
            self.script_dir = os.path.join(os.path.dirname(os.path.split(os.path.realpath(__file__))[0]), 
            "component/analysis/dep-rules.json")

    def get_subsys_file_components(self, stage):
        components = {}
        version_config_dir = os.path.join(self.manifest_build_dir, "subsys", stage)
        for file_name in os.listdir(version_config_dir):
            with open(os.path.join(version_config_dir, file_name)) as f_:
                ver_descp = yaml.safe_load(f_).get(misc.CONAN_DEPDENCIES_KEY)
                for ver in ver_descp:
                    components[ver[misc.CONAN].split('/')[0]] = ver[misc.CONAN]
        return components

    def run(self):
        if self.package_info:
            self.__parse_package_info()
        # 增加判断情况，使用提取的方法和平台组件对比
        elif self.subsystem:
            log.info("====== 开始更新源码, 平台名: %s 代码路径: %s ======",
                self.subsystem, self.code_path)

            self.__load_config_json(self.stage)

        else:
            os.chdir(self.manifest_build_dir)
            log.info("====== 开始更新源码, 单板名: %s 代码路径: %s ======",
                self.board_name, self.code_path)

            self.__update_manifest_path()

            self.__load_config_yml(self.stage)

        if not os.path.exists(self.code_path):
            os.makedirs(self.code_path)
        FetchComponentCode(self.component_ver, self.code_path, self.remote).run()
        return 0

    def __update_manifest_path(self):
        if self.manifest_yml_path:
            return
        for root, _, files in os.walk(os.path.join(self.manifest_build_dir, "product")):
            if "manifest.yml" in files and root.endswith(self.board_name):
                self.manifest_yml_path = os.path.join(root, "manifest.yml")
                return

        raise RuntimeError("在单板配置目录下, 无法找到 manifest.yml 文件")

    def __update_component_ver(self, comp, subsys_file_components):
        component = comp if self.subsystem else comp[misc.CONAN]
        # 此处判断manifest.yml中组件是否已指定版本
        is_comfirm = component.find("/") > 0
        component_name = component.split('/')[0]
        if not self.fetch_all and component_name in self.bconfig.conan_blacklist:
            return
        if is_comfirm:
            self.component_ver[component_name] = comp[misc.CONAN]
        else:
            self.component_ver[component_name] = subsys_file_components[component_name]
        self._fix_com_package(self.component_ver, component_name)

    def _fix_com_package(self, com_package, index):
        com_package_split = com_package[index].split("/")
        if len(com_package_split) == 2:
            stage = self.stage
            if stage != misc.StageEnum.STAGE_STABLE.value:
                stage = misc.StageEnum.STAGE_RC.value
            user_channel = f"@{tools.conan_user}/{stage}"
            com_package[index] += user_channel

    def __load_config_json(self, stage):
        if not os.path.exists(self.script_dir):
            raise RuntimeError("json 文件不存在")
        with open(self.script_dir, 'r') as f_:
            subsystems = json.load(f_)["Subsystems"]
        if self.subsystem not in subsystems:
            raise AttributeError(f"平台 {self.subsystem} 不存在于 {subsystems.keys()}")
        subsys_file_components = self.get_subsys_file_components(self.manifest_build_dir, stage)
        for items in subsystems[self.subsystem]:
            if items == "Level":
                continue
            components = subsystems[self.subsystem].get(items, [])
            for component in components:
                self.__update_component_ver(component, subsys_file_components)
        if len(self.component_ver) == 0:
            raise RuntimeError(f"平台 {self.subsystem} 没有任何组件信息")

    def __load_config_yml(self, stage):
        if not os.path.exists(self.manifest_yml_path):
            raise RuntimeError("manifest 文件不存在")
        components = tools.get_manifest_dependencies(
            self.manifest_build_dir, self.manifest_yml_path, self.stage, self.remote
        )
        subsys_file_components = self.get_subsys_file_components(stage)
        for component in components:
            self.__update_component_ver(component, subsys_file_components)

    def __load_version_yml(self, package_info):
        try:
            with open(package_info) as f_:
                ver_descp = yaml.safe_load(f_).get(misc.CONAN_DEPDENCIES_KEY)
                for v in ver_descp:
                    ver = v[misc.CONAN]
                    comp_name = ver.split('/')[0]
                    self.component_ver[comp_name] = ver
            return True
        except Exception as exp:
            log.warning("尝试以yml格式解析配置文件(%s)失败, 错误信息: %s", self.package_info, exp)
            return False

    def __load_version_file(self, package_info):
        with open(package_info, encoding="UTF-8") as fp:
            for line_num, line in enumerate(fp.readlines()):
                package = line.strip()
                if re.match(self.conan_package_re, package):
                    comp_name = package.split('/')[0]
                    self.component_ver[comp_name] = package
                elif package != "":
                    log.error(f"第{line_num + 1}行不满足conan包格式要求, 跳过: {package}")

    def __parse_package_info(self):
        log.info("====== 开始获取组件包信息: %s ======", self.package_info)
        package_match = re.match(self.conan_package_re, self.package_info)
        package_info_path = os.path.relpath(os.path.join(self.bconfig.cwd, self.package_info))
        if not (package_match or os.path.isfile(package_info_path)):
            raise ParameterException(f"{self.package_info}文件不存在 或 不满足conan包格式要求。")

        if package_match:
            comp_name = self.package_info.split('/')[0]
            self.component_ver[comp_name] = self.package_info
            return

        log.info("按照 yml 格式解析配置文件.")
        ret = self.__load_version_yml(package_info_path)
        if not ret:
            log.info("按照 /etc/package_info 格式解析配置文件.")
            self.__load_version_file(package_info_path)
