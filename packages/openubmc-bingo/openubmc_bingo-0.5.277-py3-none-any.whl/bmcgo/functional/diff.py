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
import subprocess
import re
import shutil
import json
from tempfile import NamedTemporaryFile
from git import Repo
from bmcgo import misc
from bmcgo.utils.tools import Tools
from bmcgo.bmcgo_config import BmcgoConfig
from bmcgo import errors

tools = Tools()
log = Tools().log

command_info: misc.CommandInfo = misc.CommandInfo(
    group=misc.GRP_MISC,
    name="diff",
    description=["获取两个产品版本间, 组件版本变更时的合并记录"],
    help_info=["usage: bingo diff <commit id before> <commit id after>"],
    hidden=False
)


def if_available(bconfig: BmcgoConfig):
    if bconfig.manifest is None:
        return False
    return True

CONAN_DATA = ".conan/data"
VERSION_KEY = "revision"


class BmcgoCommand:
    def __init__(self, bconfig: BmcgoConfig, *args):
        # 这里可以是两个版本号, 也可以是两个version id, 版本号功能不开放
        self.bconfig = bconfig
        if len(args) != 1 or len(args[0]) != 2:
            log.info("\n".join(command_info.help_info))
            raise errors.BmcGoException("参数格式错误, 请查看上述提示")
        self.version_before = args[0][0]
        self.version_after = args[0][1]

    @staticmethod
    def check_path(version):
        # 获取组件名称, 并作为下载的目标目录
        component_name = version.split('/')[0]
        to_path = f"temp/cmp_diff/{component_name}"
        # 清空下载的目标目录
        if os.path.exists(to_path):
            shutil.rmtree(to_path)
        os.makedirs(to_path)
        return to_path, component_name

    @staticmethod
    def log_print(version_msg: dict, log_list: list):
        description = ""
        commit_index = 0
        new_commit = False
        edit_description = False

        def printall(current_commit: list, description: str, version_msg: dict):
            description = description.strip()
            description = "当前MR未填写修改描述" if description == '' else description
            cur_version = version_msg.get('url')[:-4]
            for _log in current_commit[::-1]:
                if "See merge request" in _log:
                    line = re.search("(?<=!)\d+", _log)[0]
                    log.info("%s/merge_requests/%s: %s", cur_version, line, description)
                    break
        #将数据分割为一个一个commit
        for i, _log in enumerate(log_list):
            if re.match('^\s*Created-by:', _log):
                new_commit = False
                edit_description = False
            #都为真时记录描述信息
            if new_commit and edit_description:
                description += _log
            if re.match('^\s*merge', _log):
                edit_description = True
            if re.match('^commit', _log):
                new_commit = True
                if i != 0:
                    current_commit = log_list[commit_index: i - 1]
                    printall(current_commit, description, version_msg)
                    description = ''
                    commit_index = i
            if i == len(log_list) - 1:
                current_commit = log_list[commit_index:]
                printall(current_commit, description, version_msg)

    @staticmethod
    def get_version_msg(version):
        tempfile = NamedTemporaryFile()
        # 过滤只包含scm的信息, 并将其生成为字典对象
        ret = tools.run_command(f"conan info {version} --json {tempfile.name} \
              -r {misc.CONAN_REPO}", ignore_error=True, command_echo=False, capture_output=True)
        file_handler = open(tempfile.name, "r")
        conan_comps = json.load(file_handler)
        version_msg = ""
        for conan_comp in conan_comps:
            comp_ref = conan_comp.get("reference", "")
            if comp_ref == version:
                version_msg = conan_comp.get("scm", "")
                break
        file_handler.close()
        if ret.returncode != 0 or version_msg == "":
            log.info(version)
            log.info("仅自研软件支持版本对比功能!")
            return 1, version_msg
        # 由于两个组件版本之间的依赖可能冲突，所以清理一遍data
        if os.path.exists(os.path.join(os.path.expanduser('~'), CONAN_DATA)):
            shutil.rmtree(os.path.join(os.path.expanduser('~'), CONAN_DATA))
        return ret.returncode, version_msg

    def stage_match_parse(self, repo, stage):
        merge_time_1 = repo.git.log("--pretty=format:%at", "-1", self.version_before)
        merge_time_2 = repo.git.log("--pretty=format:%at", "-1", self.version_after)
        # 先对比两个version id的subsys目录下的几个文件, 并获取到有差异的组件
        if merge_time_1 > merge_time_2:
            self.version_before, self.version_after = self.version_after, self.version_before

        diff_list = repo.git.diff(self.version_before, self.version_after, "--", f"build/subsys/{stage}").split('\n')
        log.info("====>>>>>> manifest 由 %s 演进至 %s <<<<<<====", self.version_before, self.version_after)
        # 由于git diff会打印许多的无关内容, 这里对其过滤
        cmp_bef_dict = {}
        cmp_aft_dict = {}
        for diff in diff_list:
            # 时间旧的 version id
            match_bef = None
            match_bef = re.search("(?<=^-  - conan: ).*", diff)
            if match_bef is not None:
                match_bef = match_bef[0].replace('"', '')
                cmp_bef_dict[match_bef.split('/')[0]] = match_bef

            # 时间新的 version id
            match_aft = None
            match_aft = re.search("(?<=^\+  - conan: ).*", diff)
            if match_aft is not None:
                match_aft = match_aft[0].replace('"', '')
                cmp_aft_dict[match_aft.split('/')[0]] = match_aft

        # 差集列表
        bef_aft_diff_set_list = []
        aft_bef_diff_set_list = []
        for match_name, match in cmp_bef_dict.items():
            if match_name not in cmp_aft_dict.keys():
                bef_aft_diff_set_list.append(match)
            else:
                self.parse_component_merge(match, cmp_aft_dict.get(match_name))
                cmp_aft_dict.pop(match_name)

        aft_bef_diff_set_list = cmp_aft_dict.values()
        for del_cmp in bef_aft_diff_set_list:
            log.info("---- ---- 由 %s 演进至 %s 删除组件 ---- ----", self.version_before, self.version_after)
            self.parse_component_merge(del_cmp)
        for del_cmp in aft_bef_diff_set_list:
            log.info("++++ ++++ 由 %s 演进至 %s 新增组件 ++++ ++++", self.version_before, self.version_after)
            self.parse_component_merge(del_cmp)

    def parse_component_merge(self, version_before=None, version_after=None, sigle_commit_mode=False):
        """如果传入的是两个组件的版本，使用此接口分析
        """
        # 单个提交模式下，执行这个if会自动退出
        to_path, component_name = self.check_path(version_before)

        ret, version_msg1 = self.get_version_msg(version_before)
        if ret != 0:
            return
        if version_after:
            ret, version_msg2 = self.get_version_msg(version_after)
            if ret != 0:
                return

        # 由于组件在版本变更时，可能存储地址发生了改变，旧地址不存在，导致下载失败,同时输入的新地址可能也不存在
        # 故用try进行确认，确保创建目标目录和下载正确执行
        try:
            Repo.clone_from(version_msg1.get("url"), to_path=to_path, branch='main')
        except Exception as e1:
            if version_after:
                try:
                    Repo.clone_from(version_msg2.get("url"), to_path=to_path, branch='main')
                except Exception as e2:
                    log.error(f"远程软件仓库地址不存在：{version_msg2.get('url')}")
                    raise e2
            else:
                log.error(f"远程软件仓库地址不存在：{version_msg1.get('url')}")
                raise e1
        repo = Repo(to_path)

        if version_after is None:
            log.info("== %s: %s", component_name, version_before)
            merge_log = repo.git.log('--merges', version_msg1.get(VERSION_KEY), '--remotes=main', "-3")
            self.log_print(version_msg1, merge_log.split('\n'))
            return

        # 获取两个节点的提交时间, 使用 ‘old..new' 格式进行对比
        merge_time_1 = repo.git.log("--pretty=format:%at", "-1", version_msg1.get(VERSION_KEY))
        merge_time_2 = repo.git.log("--pretty=format:%at", "-1", version_msg2.get(VERSION_KEY))
        if merge_time_1 > merge_time_2:
            merge_time_1, merge_time_2 = merge_time_2, merge_time_1
            version_before, version_after = version_after, version_before
        log.info("==== ==== %s 由 %s 演进至 %s ==== ====", component_name, version_before, version_after)
        merge_log = repo.git.log('--merges', f"{version_msg1.get(VERSION_KEY)}..{version_msg2.get(VERSION_KEY)}",
                                '--remotes=main')
        self.log_print(version_msg1, merge_log.split('\n'))

    def parse_commit_merge(self):
        """如果是两个commit id, 那么使用此接口进行分析
        """
        log.info(f"合并记录为时间排序，并非编号排序")
        log.info(f"版本演进均为旧版本演进为新版本, 回滚提交也视为演进")
        repo = Repo(self.bconfig.manifest.folder)
        self.stage_match_parse(repo, "stable")
        self.stage_match_parse(repo, "rc")

    def run(self):
        if "@" in self.version_before and "@" in self.version_after:
            raise errors.BmcGoException(f"不支持两个组件版本对比")
        elif "@" not in self.version_before and "@" not in self.version_after:
            self.parse_commit_merge()
        else:
            raise errors.BmcGoException("输入的版本号无法解析")
        return 0