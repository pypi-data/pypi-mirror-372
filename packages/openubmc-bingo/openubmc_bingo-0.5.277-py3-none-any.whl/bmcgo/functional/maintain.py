#!/usr/bin/env python3
# encoding=utf-8
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
import argparse
import tempfile
import stat
import shutil
import re
import filecmp
import yaml
from colorama import Fore, Style
from git import Repo
from git import Commit
from bmcgo.misc import CommandInfo
from bmcgo.utils.tools import Tools
from bmcgo.component.build import BuildComp
from bmcgo import errors
from bmcgo.bmcgo_config import BmcgoConfig
from bmcgo import misc

tool = Tools("maintain")
log = tool.log
command_info: CommandInfo = CommandInfo(
    group="Misc commands",
    name="maintain",
    description=["组件维护,按conan方式生成维护组件构建脚本, 同时维护版本号、patch等"],
    hidden=True
)
CONANDATA_SOURCES = "sources"
CONANDATA_VERSIONS = "versions"
CONANDATA_PATCHES = "patches"
PATCH_FILE_KEY = "patch_file"


def if_available(bconfig: BmcgoConfig):
    return bconfig.conan_index is not None


class PatchInfo():
    def __init__(self, commit: Commit):
        self.commit = commit
        log.info("补丁提交信息 =============================>>>>")
        log.info(self.commit.message)
        log.info("补丁提交信息 =============================<<<<")

    @property
    def author(self):
        return self.commit.author.name

    @property
    def description(self):
        match = re.search("(【修改描述】(.*))\n", self.commit.message)
        if match:
            return match.group(1)
        lines = self.commit.message.split("\n")
        for line in lines:
            if line.strip() == "":
                continue
            if re.search("merge.*into.*", line):
                continue
            return line.strip()

    @property
    def merged_by(self):
        match = re.search("Merged-by: (.*)\n", self.commit.message)
        if match:
            return match.group(1)
        raise RuntimeError("无法找到合法的Merged-by合入人信息，请检查待提取的提交节点是否正确配置")


class BmcgoCommand:
    url = None
    tag = None
    revision = None
    next_version = None
    sub_folder = None
    recipe_folder = None
    conan_folder = None

    def __init__(self, bconfig: BmcgoConfig, *args):
        self.patch_file = []
        self.bconfig = bconfig
        parser = argparse.ArgumentParser(prog="bmcgo maintain", description="BMC组件的维护管理工具", add_help=True,
                                         formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-cp", "--conan_package", help="指定需要维护的组件版本，示例：component/1.2.3", required=True)
        parser.add_argument("-p", "--patch_file", help="添加patch文件，可指定多个，顺序追加到代码中", action='append')
        parser.add_argument("-b", "--branch", help="用于提取patch的分支，与commit_id配合使用", default="master")
        parser.add_argument("-c", "--commit_id", help="需要生成patch的提交节点，长度不低于8个字符，可指定多个，顺序追加到代码中",
                            action='append')
        parser.add_argument("-v", "--version", help="指定需要生成的组件版本号", default=None)
        parser.add_argument("-r", "--remote", default=misc.CONAN_REPO,
                            help="conan远程仓，请检查conan remote list查看已配置的conan仓")
        parsed_args = parser.parse_args(*args)
        cp = parsed_args.conan_package
        if (not re.match("^[a-zA-Z0-9_-]+/([1-9][0-9]*|[0-9])\.[0-9]+\.[0-9]+$", cp) and
           not re.match("^[a-zA-Z0-9_-]+/(([1-9][0-9]*|[0-9])\.[0-9]+\.[0-9]+)(-build\.[0-9]+)$", cp) and
           not re.match("^[a-zA-Z0-9_-]+/(([1-9][0-9]*|[0-9])\.[0-9]+\.[0-9]+)(.p[0-9]+)$" + cp)):
            raise errors.BmcGoException("-cp参数错误，不满足格式\"<name>/<version>\"要求")
        self.conan_package = cp
        self.name = self.conan_package.split("/")[0]
        self.base_version = self.conan_package.split("/")[1]
        self.remote = parsed_args.remote
        self.arg_special_version = parsed_args.version
        if parsed_args.patch_file is None:
            parsed_args.patch_file = []
        for patch_file in parsed_args.patch_file:
            if not os.path.isfile(patch_file):
                raise errors.BmcGoException(f"补丁文件 {patch_file} 不存在")
            self.patch_file.append(os.path.realpath(patch_file))

        # 待提取的提交节点基本信息
        self.patch_commit: dict[str, PatchInfo] = {}
        self.branch = parsed_args.branch
        self.commit_id = parsed_args.commit_id
        if self.commit_id is None:
            self.commit_id = []
        for commit in self.commit_id:
            if re.match(r"^[a-f0-9]{8,40}$", commit) is None:
                raise errors.ConfigException(f"参数错误, --commit_id({commit}) 格式错误")
        self.patch_description = ""
        self.dir = tempfile.TemporaryDirectory(prefix="bmcgo_maint")
        for file in self.patch_file:
            if not os.path.isfile(file):
                raise errors.BmcGoException(f"补丁文件 {file} 不存在")
        log.debug(f"临时文件夹: {self.dir.name}")

    def run(self):
        self._fetch_conan_info()
        os.chdir(self.dir.name)
        log.info(f"开始克隆 {self.url}")
        repo = Repo.clone_from(self.url, ".")
        repo.git.checkout(self.tag)
        if not os.path.isfile("mds/service.json"):
            raise errors.NotFoundException("文件 mds/service.json 不存在, 可能不是一个有效的组件")
        # 生成conanbase.py和conanfile.yml
        log.info(f"生成 conanfil.py 和conanbase.py")
        bconfig = BmcgoConfig()
        comp = BuildComp(bconfig, ["--maintain"], gen_conanbase=True)
        self.recipe_folder = os.path.join(self.bconfig.conan_index.folder, comp.info.name)
        if not os.path.isdir(self.recipe_folder):
            os.makedirs(self.recipe_folder)
        self._update_next_version()

        conanfile = os.path.realpath("conanfile.py")
        conanbase = os.path.realpath("conanbase.py")
        if not os.path.isfile(conanfile):
            raise errors.NotFoundException("文件 conanfile.py 不存在, 可能不是一个有效的组件")
        if not os.path.isfile(conanbase):
            raise errors.NotFoundException("文件 conanbase.py 不存在, 可能不是一个有效的组件")
        # 计算recipe目录
        self.sub_folder = self.next_version + ".x"
        while self.sub_folder != ".x":
            self.conan_folder = os.path.join(self.recipe_folder, self.sub_folder)
            # 找到recipe
            if not self._recipe_need_change(conanfile, conanbase):
                break
            self.conan_folder = None
            self.sub_folder = ".".join(self.sub_folder.split(".")[0:-2]) + ".x"
        if not self.conan_folder:
            # 默认是版号前2段 + ".x"
            self.sub_folder = ".".join(self.next_version.split(".")[0:2]) + ".x"

        self.conan_folder = os.path.join(self.recipe_folder, self.sub_folder)
        if not os.path.isdir(self.conan_folder):
            os.makedirs(self.conan_folder)

        self._gen_patches(repo)
        if not self._gen_conandata():
            return -1
        self._gen_config()
        shutil.copyfile(conanfile, os.path.join(self.conan_folder, "conanfile.py"))
        shutil.copyfile(conanbase, os.path.join(self.conan_folder, "conanbase.py"))
        log.success(f"生成维护版本 {self.name}/{self.next_version} 成功")
        return 0

    def _fetch_conan_info(self):
        user = tool.conan_user
        export_path = os.path.join(tool.conan_data, self.conan_package, f"{user}/stable", "export")
        if not os.path.isdir(export_path):
            cmd = f"conan download {self.conan_package}@{user}/stable -r {self.remote} -re"
            tool.run_command(cmd, error_log=f"组件 {self.conan_package} 未找到，请检查网络连接以及该版本是否已发布")
        conanfile = os.path.join(export_path, "conanfile.py")
        conandata = os.path.join(export_path, "conandata.yml")
        if os.path.isfile(conandata):
            log.info(f"从 {conandata} 读取源码tag的url")
            # 尝试从conandata中获取代码仓地址
            with open(conandata, "r") as fp:
                data = yaml.safe_load(fp)
            cfg = data.get("sources", {}).get(self.base_version)
            if cfg is None:
                raise RuntimeError(f"${conandata}不存在组件 {self.conan_package} 配置, 请检查是否正确")
            self.url = cfg.get("url")
            branch = cfg.get("branch")
            if re.match("^refs/tags/[0-9]+\\.[0-9]+\\.[0-9]+$", branch):
                self.tag = branch[len("refs/tags/"):]
            else:
                raise RuntimeError(f"${conandata}的组件 {self.conan_package} 配置错误, 未找到有效的tag")
        else:
            log.info(f"从 {conanfile} 读取源码tag的url")
            self.tag = self.base_version
            with open(conanfile, "r") as fp:
                lines = fp.readlines()
            for idx, line in enumerate(lines):
                if line.find('scm = {"revision":') > 0:
                    self.url = re.split(r'["]', lines[idx + 2])[-2]
                    break
            else:
                raise RuntimeError("无法找到版本(revision)和地址(url)字段")

    def _update_next_version(self):
        self.next_version = self.arg_special_version
        if not self.next_version:
            if re.match("^(([1-9][0-9]*|[0-9])\.[0-9]+\.[0-9]+)(-build\.[0-9]+)$", self.base_version):
                temp_version = self.base_version.split(".")
                temp_version[-1] = str(int(temp_version[-1]) + 1)
                self.next_version = ".".join(temp_version)
            else:
                self.next_version = self.base_version.split("-")[0] + "-build.1"
            log.info(f"自动生成的版本号为 {Fore.GREEN}{self.next_version}{Style.RESET_ALL}")
            version = input("请回车确认 或者 输入你期望的版本号(必须以-build.x结束，如1.2.3-build.1): ").strip()
            if version:
                self.next_version = version
        if not self.arg_special_version and "-build." not in self.next_version:
            raise errors.BmcGoException(f"版本号格式必须以-build.x结束，如1.2.3-build.1")
        restr = r"^(([1-9][0-9]*|[0-9])\.[0-9]+\.[0-9]+)(-build\.[1-9][0-9]*)?$"
        match = re.match(restr, self.next_version)
        if not match:
            raise errors.BmcGoException(f"版本号 {self.next_version} 不满足正则表达式 '{restr}' 要求")
        log.info(f"创建组件版本 {Fore.GREEN}{self.next_version}{Style.RESET_ALL}")

    def _gen_patches(self, repo: Repo):
        # 用户指定patch
        patches_dir = os.path.join(self.conan_folder, "..", CONANDATA_PATCHES)
        if len(self.patch_file) > 0 and not os.path.isdir(patches_dir):
            os.makedirs(patches_dir)
        for file in self.patch_file:
            patch_file = os.path.join(patches_dir, os.path.basename(file))
            if not os.path.isfile(patch_file) or not filecmp.cmp(file, patch_file):
                log.info(f"复制补丁文件 {patch_file}")
                shutil.copyfile(file, patch_file)

        if len(self.commit_id) == 0:
            return
        # 从代码仓生成patch
        if not os.path.isdir(patches_dir):
            os.makedirs(patches_dir)

        repo.git.checkout(self.branch)
        for commit_id in self.commit_id:
            found = False
            for commit in repo.iter_commits():
                if commit.hexsha.startswith(commit_id):
                    commit_id = commit.hexsha
                    found = True
                    break
            if not found:
                raise errors.ParameterException(f"无效的提交节点: {commit_id}")
            log.info(f"开始生成补丁文件, 提交节点: {commit_id}")
            patch_info = PatchInfo(commit)
            cmd = f"git format-patch -1 {commit_id} --numbered-files -- ':!mds/service.json' ':!CHANGELOG*'"
            cmd += " ':!ChangeLog*'"
            tool.run_command(cmd)
            patch_id = 0
            while True:
                if patch_id == 0:
                    patch_file = os.path.join(patches_dir, commit.hexsha + ".patch")
                else:
                    patch_file = os.path.join(patches_dir, commit.hexsha + f"_{patch_id}.patch")
                if not os.path.isfile(patch_file) or filecmp.cmp("1", patch_file):
                    break
                log.warning(f"待生成的补丁 与 {patch_file} 不一致，尝试生成新的补丁文件名")
                patch_id += 1
            shutil.copyfile("1", patch_file)
            log.success(f"补丁文件 {patch_file} 创建成功")
            self.patch_file.append(patch_file)
            self.patch_commit[patch_file] = patch_info

    def _gen_config(self):
        """生成config.yml文件"""
        config_file = os.path.join(self.recipe_folder, "config.yml")
        config = {}
        if os.path.isfile(config_file):
            with open(config_file, "r") as fp:
                config = yaml.safe_load(fp)
        if config.get(CONANDATA_VERSIONS) is None:
            config[CONANDATA_VERSIONS] = {}
        config[CONANDATA_VERSIONS][self.next_version] = {
            "folder": os.path.basename(self.sub_folder)
        }
        with os.fdopen(os.open(config_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as file_handler:
            yaml.dump(config, file_handler, encoding='utf-8', allow_unicode=True)

    def _recipe_need_change(self, conanfile, conanbase):
        """检查recipe目录是否需要切换"""
        ori_conanfile = os.path.join(self.conan_folder, "conanfile.py")
        ori_conanbase = os.path.join(self.conan_folder, "conanbase.py")
        # 文件不存在时无需切换
        if not os.path.isfile(ori_conanfile) or not os.path.isfile(ori_conanbase):
            return True
        # 文件完全相同时无需切换
        if filecmp.cmp(ori_conanfile, conanfile) and filecmp.cmp(ori_conanbase, conanbase):
            return False
        # 其它场景需要切换
        return True

    def _get_prev_patches(self):
        """获取上个版本的补丁列表"""
        config_file = os.path.join(self.recipe_folder, "config.yml")
        if not os.path.isfile(config_file):
            return []
        with open(config_file, "r") as fp:
            config = yaml.safe_load(fp)
        folder = config.get("versions", {}).get(self.base_version, {}).get("folder")
        if folder is None:
            return []
        config_file = os.path.join(self.recipe_folder, folder, "conandata.yml")
        if not os.path.isfile(config_file):
            return []
        with open(config_file, "r") as fp:
            config = yaml.safe_load(fp)
        return config.get("patches", {}).get(self.base_version, [])

    def _gen_conandata(self):
        """生成conandata.yml文件"""
        config_file = os.path.join(self.conan_folder, "conandata.yml")
        config = {}
        if os.path.isfile(config_file):
            with open(config_file, "r") as fp:
                config = yaml.safe_load(fp)
        if config.get(CONANDATA_SOURCES) is None:
            config[CONANDATA_SOURCES] = {}
        source = {
            "url": self.url,
            "branch": f"refs/tags/{self.tag}",
            "shallow": True
        }
        if config.get(CONANDATA_PATCHES) is None:
            config[CONANDATA_PATCHES] = {}
        patches = config[CONANDATA_PATCHES].get(self.next_version, [])
        if not patches:
            patches = self._get_prev_patches()
        for file in self.patch_file:
            found = False
            for patch in patches:
                if patch.get(PATCH_FILE_KEY, "") == "patches/" + os.path.basename(file):
                    found = True
                    break
            if found:
                continue
            patch_item = {}
            commit = self.patch_commit.get(file)
            if commit:
                patch_item["description"] = commit.description
                patch_item["author"] = commit.author
                patch_item["merged_by"] = commit.merged_by
                patch_item["commit_id"] = commit.commit.hexsha
            patch_item[PATCH_FILE_KEY] = "patches/" + os.path.basename(file)
            patches.append(patch_item)
        for patch in patches:
            log.success(f"组件 {self.next_version} 包含补丁文件: " + patch.get(PATCH_FILE_KEY))
            log.info(f"    description: " + patch.get("description", ""))
            log.info(f"    author: " + patch.get("author", ""))
            log.info(f"    merged_by: " + patch.get("merged_by", ""))
            log.info(f"    commit_id: " + patch.get("commit_id", ""))
        config[CONANDATA_SOURCES][self.next_version] = source
        config[CONANDATA_PATCHES][self.next_version] = patches
        log.info(f"生成 {config_file}")
        with os.fdopen(os.open(config_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as file_handler:
            yaml.dump(config, file_handler, encoding='utf-8', allow_unicode=True, sort_keys=False)
        return True
