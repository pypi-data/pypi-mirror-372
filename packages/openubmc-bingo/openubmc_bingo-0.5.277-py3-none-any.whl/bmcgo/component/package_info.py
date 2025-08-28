#!/usr/bin/python3
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
import argparse
import datetime
import json
import os
import re
import configparser
from configparser import NoSectionError, NoOptionError
from typing import Tuple

from bmcgo.codegen import __version__ as codegen_version
from bmcgo.logger import Logger
from bmcgo.utils.tools import Tools
from bmcgo import misc
from bmcgo.component.component_helper import ComponentHelper

global log
log = Logger()

cwd = os.getcwd()
cwd_script = os.path.split(os.path.realpath(__file__))[0]


class CodegenVersionNotMatchError(OSError):
    """版本号不满足要求"""


class CodegenPolicyError(OSError):
    """代码自动生成策略配置错误"""


class InfoComp():
    def __init__(self, args=None, service_json="mds/service.json", partner_mode=False):
        parser = self.arg_parser(True, partner_mode)
        self.parse_args(parser, args, service_json)

    @staticmethod
    def arg_parser(add_help=False, partner_mode=False):
        stage_values = [member.value for member in misc.StageEnum]
        parser = argparse.ArgumentParser(prog="bingo build", description="Build conan", add_help=add_help,
                                         formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-bt", "--build_type", default="debug", help="构建类型，可选：dt,debug,release\n默认：debug")
        parser.add_argument(
            "--stage", 
            help=f"组件包发布阶段, 可选: {stage_values}\n默认：{misc.StageEnum.STAGE_DEV.value}", 
            default=misc.StageEnum.STAGE_DEV.value
        )
        parser.add_argument("-u", "--upload", action=misc.STORE_TRUE, help="上传组件包到conan仓")
        parser.add_argument(
            "-r", "--remote", help=f"conan仓别名，请检查conan remote list查看已配置的conan仓"
        )
        parser.add_argument(
            "-s",
            "--from_source",
            help=(
                argparse.SUPPRESS
                if partner_mode
                else "Build from source, include dependency component"
            ),
            action=misc.STORE_TRUE,
        )
        parser.add_argument("-nc", "--no_cache",
                            help="不使用~/.conan/data目录下的缓存包(构建前删除缓存)", action=misc.STORE_FALSE)
        parser.add_argument("-o", "--options", help="Define options values (host machine), e.g.: -o Pkg:with_qt=true",
                            action='append', default=[])
        parser.add_argument(
            "--user",
            help=f"指定conan包的user字段，尝试从{misc.GLOBAL_CFG_FILE}文件读取conan.user字段，否则由程序管理",
            default=None
        )
        parser.add_argument("-cov", "--coverage", help=argparse.SUPPRESS, action=misc.STORE_TRUE)
        parser.add_argument(
            "-as",
            "--asan",
            help=argparse.SUPPRESS if partner_mode else "Enable address sanitizer",
            action=misc.STORE_TRUE,
        )
        parser.add_argument("-maint", "--maintain", help=argparse.SUPPRESS, action=misc.STORE_TRUE)
        parser.add_argument(
            "-pr",
            "--profile",
            help=argparse.SUPPRESS if partner_mode else Tools.get_profile_arg_help(),
            default="",
        )
        parser.add_argument(
            "-jit",
            "--enable_luajit",
            help=argparse.SUPPRESS if partner_mode else "Enable luajit",
            action=misc.STORE_FALSE if partner_mode else misc.STORE_TRUE,
        )
        return parser

    @staticmethod
    def get_codegen_policy(service_data) -> Tuple[str, int]:
        # 代码自动生成工具版本号检查
        policy = ComponentHelper.get_config_value(service_data, "codegen_policy", {})
        code_version = policy.get("version", ">=0")
        if not isinstance(code_version, str):
            code_version = str(code_version)
        code_language = policy.get("language", "c")
        if not re.fullmatch("^(>=)?[0-9]+$", code_version):
            raise CodegenPolicyError("codegen_policy.version配置错误，需要满足如下要求 ^(>=)?[0-9]+$")
        if code_language != "c":
            raise CodegenPolicyError("codegen_policy.language当前只支持C语言$")
        # 生成代码需要使用的自动生成工具基础版本号
        if code_version.startswith(">="):
            codegen_base_version = int(code_version[2:])
            if codegen_base_version > codegen_version:
                raise CodegenVersionNotMatchError("代码自动生成要求的版本号大于当前bmcgo工具提供的版本号，建议升级到最新版本")
            codegen_base_version = codegen_version
        else:
            codegen_base_version = int(code_version)
        return code_language, codegen_base_version

    def parse_args(self, parser, args, service_json):
        self.args, _ = parser.parse_known_args(args)
        self.build_type = self.args.build_type
        self.stage = self.args.stage
        self.upload = self.args.upload
        self.from_source = self.args.from_source
        self.options = self.args.options
        self.coverage = self.args.coverage
        self.asan = self.args.asan
        self.remote = self.args.remote
        self.no_cache = self.args.no_cache and (not os.getenv('NOT_CLEAN_CONAN_CACHE') == 'True')
        # 是否是维护模式
        self.is_maintain = self.args.maintain
        self.enable_luajit = self.args.enable_luajit
        self.profile = Tools.get_conan_profile(self.args.profile, self.build_type, self.enable_luajit)

        os.environ["ROOTFS_DIR"] = os.path.join(cwd, "temp")
        stage_values = [member.value for member in misc.StageEnum]
        if self.stage not in stage_values:
            raise OSError(f"参数 stage 错误, 请从 {stage_values} 中选择")
        # 构建阶段检查
        build_types = ["dt", "debug", "release"]
        if self.build_type not in build_types:
            raise OSError("参数 build_type 错误, 请从 [debug, release, dt] 中选择")
        if self.upload and not self.remote:
            raise OSError("参数 remote 必填")

        # 只有指定为pre时才增加prerelease编码
        pre = ""
        if self.stage == misc.StageEnum.STAGE_PRE:
            self.stage = misc.StageEnum.STAGE_DEV
            now = datetime.datetime.utcnow()
            pre = "-pre." + now.strftime("%Y%m%d%H%M%S")

        # 尝试从/etc/bmcgo.conf读取user配置
        user = self._get_package_user()
        self.channel = f"@{user}/{self.stage}"

        self._parse_service_json(service_json, pre)
        self._conan_define()

    def get_dependencies(self, service_data, key):
        dependencies = []
        user_channel = ComponentHelper.get_user_channel(self.stage)
        deps = ComponentHelper.get_config_value(service_data, key, [])
        for dep in deps:
            conan = dep.get(misc.CONAN)
            if conan is None:
                log.info("获取 conan 依赖失败, 跳过未知组件")
                continue
            if conan.find("@") > 0:
                dependencies.append(conan)
            else:
                dependencies.append(conan + user_channel)
        return dependencies

    def _conan_define(self):
        self.package = "%s/%s%s" % (self.name, self.version, self.channel)
        profiles = [f"-pr:h {self.profile}"]
        if self.build_type == "dt":
            self.setting = "-s build_type=Dt"
        else:
            profiles.append("-pr:b profile.dt.ini")
            if self.enable_luajit:
                self.options.append("skynet:enable_luajit=True")
            if self.build_type == "debug":
                self.setting = "-s build_type=Debug"
            else:
                self.setting = "-s build_type=Release"
        self.full_profile = " ".join(profiles)
        self.cmd_base = ". %s %s %s " % (self.package, self.full_profile, self.setting)
        if self.remote:
            self.cmd_base += "-r %s " % self.remote
        if self.options:
            for option in self.options:
                self.cmd_base += " -o " + option
        if self.coverage:
            self.cmd_base += f" -o {self.name}:gcov=True"
        if self.asan:
            self.cmd_base += f" -o {self.name}:asan=True"

    def _get_package_user(self):
        """ 尝试从/etc/bmcgo.conf读取user配置 """
        user = self.args.user
        try:
            if user is None and os.access(misc.GLOBAL_CFG_FILE, os.R_OK):
                conf = configparser.ConfigParser()
                conf.read(misc.GLOBAL_CFG_FILE)
                user = conf.get(misc.CONAN, "user")
        except (NoSectionError, NoOptionError):
            user = None
        if user is None:
            if self.stage == misc.StageEnum.STAGE_DEV.value:
                user = misc.ConanUserEnum.CONAN_USER_DEV.value
            else:
                user = misc.ConanUserEnum.CONAN_USER_RELEASE.value
        return user

    def _parse_service_json(self, service_json: str, pre: str):
        self.language = ComponentHelper.get_language(service_json=service_json)
        with open(service_json, "r", encoding="UTF-8") as file_handler:
            data = json.load(file_handler)
            self.version = ComponentHelper.get_config_value(data, "version") + pre
            self.name = data.get("name")
            # 编译依赖
            self.build_dependencies = self.get_dependencies(data, "dependencies/build")
            # 开发者测试依赖
            self.test_dependencies = self.get_dependencies(data, "dependencies/test")
            self.design_options = ComponentHelper.get_config_value(data, "options", {})
            self.package_type = ComponentHelper.get_config_value(data, "type", [])
            self.package_info = ComponentHelper.get_config_value(data, "package_info")
            self.code_language, self.codegen_base_version = self.get_codegen_policy(data)
