#!/usr/bin/env python3
# encoding=utf-8
# 描述：BMC Studio语法正确性与模型一致性检查
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
import json
import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone

from git import Repo

from bmcgo.codegen.c.helper import Helper
from bmcgo.utils.tools import Tools
from bmcgo.bmcgo_config import BmcgoConfig
from bmcgo.utils.fetch_component_code import FetchComponentCode
from bmcgo import misc
from bmcgo.functional.fetch import BmcgoCommand as FetchAgent

log = Tools().log
cwd = os.getcwd()
command_info: misc.CommandInfo = misc.CommandInfo(
    group=misc.GRP_STUDIO,
    name="check",
    description=["BMC Studio语法正确性与模型一致性检查"],
    hidden=False
)
ISSUE_TEMPLATE = '''问题{0}：
【规则名称】{1}
【文件路径】{2}
【错误提示】{3}
【修复建议】{4}
'''
_PACKAGE_INFO_HELP = """
1. 通过组件包名及版本拉取单个组件代码，格式：package/version@user/channel
2. 通过配置文件拉取部分指定版本的组件代码。支持一下2种配置文件：
    a. yml格式
        dependencies:
        - conan: "package/version@user/channel"
    b. 文本格式
        package/version@user/channel
"""
MODEL_CHOICES = ["all", "mds", "resource_tree", "csr", "interface_mapping"]


def if_available(bconfig: BmcgoConfig):
    return True


class BmcgoCommand:
    def __init__(self, bconfig: BmcgoConfig, *args):
        self.bconfig = bconfig
        parser = argparse.ArgumentParser(prog="bmcgo check", description="语法正确性与模型一致性检查", add_help=True,
            formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-b", "--board_name", help="指定单板获取配套全量源码，可选值为build/product目录下的单板名\n默认：openUBMC",
                            default="openUBMC")
        parser.add_argument("--stage", help="包类型，可选值为：rc(预发布包), stable(发布包)\n默认: stable", default="stable")
        parser.add_argument("-r", "--remote")
        parser.add_argument("-m", "--model", help=f"检查的模型，可选值为: {', '.join(MODEL_CHOICES)}\n默认: all",
                            choices=MODEL_CHOICES, default="all")
        parsed_args, _ = parser.parse_known_args(*args)
        self.board_name = parsed_args.board_name
        self.stage = parsed_args.stage
        self.remote = parsed_args.remote
        self.model = parsed_args.model
        self.community_issues = set()
        self.service_dict = {}
        self.packages = {}
        self.repo_brance = Repo(cwd).active_branch.name
        self.repo_name = "manifest"
        self.disabled = False
        self.studio_dir = "/usr/share/bmc_studio/server"
        self.studio_path = "/usr/share/bmc_studio/server/bmcstudio"
        # 初始化fetch命令对象
        if self.bconfig.manifest:
            self.fetch_agent = FetchAgent(self.bconfig, *args)
    
    @staticmethod
    def check_overdue(issue: dict):
        data = issue.get("deadline")
        if date is None:
            return False
        try:
            utc_8 = timezone(timedelta(hours=8))
            deadline = datetime.strptime(data, '%Y/%m/%d').replace(tzinfo=utc_8)
            return datetime.now(tz=utc_8) >= deadline + timedelta(days=1)
        except Exception as e:
            log.warning("日期 %s 解析失败：%s", date, e)
            return False
    
    @staticmethod
    def process_issues_group(issues, prefix, add_message=""):
        result = ""
        if issues:
            issues.sort()
            for index, (rule, filepath, error_message, repair_suggestion) in enumerate(issues):
                result += ISSUE_TEMPLATE.format(index + 1, rule, filepath, error_message, repair_suggestion)
            result = result.strip()
            if result and os.getenv("CLOUD_BUILD_RECORD_ID") is not None:
                result = "\n".join(map(lambda s: f'{prefix} {s}', result.split("\n")))
            if add_message:
                result = f"{result}\n{add_message}\n"
        return result
    
    @staticmethod
    def filter_output():
        output_path = os.path.join(os.environ["HOME"], "bmc_studio", "var", "data", "cli_data", "issues.json")
        try:
            with open(output_path, "r") as output_fp:
                items = json.load(output_fp)
        except json.decoder.JSONDecoderError as e:
            log.error("检查结果解析失败：%s", e.msg)
            return "", ""
        ci_enabled_issues = []
        disabled_issues = []
        for item in items:
            rule = item.get("rule")
            filepath = item.get("filepath")
            ci_enabled = item.get("ciEnabled")
            if ci_enabled:
                ci_enabled_issues.append(
                    (rule, filepath, item.get("errorMessage", ""), item.get("repairSuggestion", ""))
                )
            else:
                disabled_issues.append((rule, filepath, item.get("errorMessage", ""), item.get("repairSuggestion", "")))
        # 门禁环境下需要在每一行前加入ERROR，以红色显示
        error = BmcgoCommand.process_issues_group(ci_enabled_issues, "ERROR")
        warning = BmcgoCommand.process_issues_group(disabled_issues, "WARNING", "!!!!!以上是告警提示，后续门禁会逐步生效!!!!!")
        return error, warning

    def find_component_packages(self):
        dependencies = self.service_dict.get(misc.CONAN_DEPDENCIES_KEY, {})
        dep_list = dependencies.get("test", [])
        dep_list.extend(dependencies.get("build", []))
        for dep in dep_list:
            package = dep.get(misc.CONAN, "")
            comp_name = package.split("/")[0]
            if "@" not in package:
                package += f"@{misc.ConanUserEnum.CONAN_USER_RELEASE.value}/{misc.StageEnum.STAGE_RC.value}"
            self.packages[comp_name] = package

    def run(self):
        service_path = os.path.join(cwd, "mds", "service.json")
        if self.bconfig.manifest is None:
            if not os.path.isfile(service_path):
                raise RuntimeError("mds/service.json 文件不存在")
            with open(service_path, "r") as service_fp:
                self.service_dict = json.load(service_fp)
            if "name" not in self.service_dict:
                raise RuntimeError("mds/service.json 文件中缺少 name 配置")
            self.repo_name = self.service_dict.get("name")
            self.find_component_packages()
        if self.disabled:
            log.info("%s 仓库没有开启语法正确性和模型一致性检查", self.repo_name)
            return 0
        with tempfile.TemporaryDirectory(prefix="dependencies_repo_") as tempdir:
            if self.bconfig.manifest:
                self.fetch_agent.code_path = tempdir
                self.fetch_agent.run()
            elif self.packages:
                FetchComponentCode(self.packages, tempdir, self.remote, include_open_source=False).run()
            cmd = [self.studio_path, "check", "--repo", cwd, "--dependencies", tempdir, "--model", self.model]
            if self.bconfig.manifest:
                cmd.append("--manifest")
                cmd.append("true")
            os.chdir(self.studio_dir)
            Helper.run(cmd, stdout=subprocess.DEVNULL)
            os.chdir(cwd)
        error, warning = self.filter_output()
        if error:
            log.warning(warning)
            log.error("语法正确性和模型一致性检查不通过：\n%s\n", error)
            return -1
        log.warning(warning)
        log.success("语法正确性和模型一致性检查通过\n")
        return 0