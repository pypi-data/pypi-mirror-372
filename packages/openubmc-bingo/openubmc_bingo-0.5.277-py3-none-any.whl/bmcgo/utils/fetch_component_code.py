#!/usr/bin/env python3
# encoding=utf-8
# 描述：根据conan包拉取组件代码
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
import re
import shutil
import subprocess
from multiprocessing import Pool
import patch_ng
import yaml
from git import Repo

from bmcgo.misc import errors
from bmcgo import misc
from bmcgo.utils.tools import Tools

tools = Tools("fetch_component_code")
log = tools.log


def process_err_cb(err):
    log.error("!!!!!!!!!!!!!!!!!!!!!!!!!!! 拉取代码失败, 错误: %s", err)


class FetchComponentCode:
    def __init__(self, packages, target_dir, conan_remote, include_open_source=True):
        self.conan = shutil.which(misc.CONAN)
        if self.conan is None:
            raise RuntimeError("找不到 conan 工具")
        self.packages = packages
        self.target_dir = target_dir
        self.remote = conan_remote
        self.include_open_source = include_open_source

    @staticmethod
    def resolve_version_range(component_name, version_range):
        cmd = f"conan info '{version_range}' --package-filter={component_name}/*" \
             f" -r {misc.CONAN_REPO} --only None 2>/dev/null"
        ret, output = subprocess.getstatusoutput(cmd)
        output = output.strip()
        if ret != 0 or not output:
            return None
        return output.split("\n")[-1]

    @staticmethod
    def patch(patch_file=None):
        patchset = patch_ng.fromfile(patch_file)
        if not patchset:
            raise errors.BmcGoException("Failed to parse patch: %s" % (patch_file))
        if not patchset.apply(strip=0, root="./", fuzz=False):
            raise errors.BmcGoException("Failed to apply patch: %s" % patch_file)

    @staticmethod
    def _get_patch_changed_files(patch_file):
        files = {}
        for line in open(patch_file):
            if not line.startswith("diff --git"):
                continue
            line = line.strip()
            chunk = line.split()
            a_file = chunk[-2][2:]
            b_file = chunk[-1][2:]
            files[a_file] = b_file
        return files

    @staticmethod
    def _apply_patches_direct(real_patch, patch_file, changed_files):
        FetchComponentCode.patch(patch_file=real_patch)
        for a_file, b_file in changed_files.items():
            if a_file != b_file:
                if a_file != "/dev/null" and b_file != "/dev/null":
                    os.rename(a_file, b_file)
                    cmd = f"git rm -f {a_file}"
                    tools.run_command(cmd)
                elif a_file != "/dev/null":
                    cmd = f"git rm -f {a_file}"
                    tools.run_command(cmd)
                    continue
            cmd = f"git add {b_file}"
            tools.run_command(cmd)
        cmd = f"git commit -m \"{patch_file}\""
        tools.run_command(cmd)

    @staticmethod
    def __apply_patches(conandata_file, patches, code_dir):
        cwd = os.getcwd()
        recipe_folder = os.path.join(os.path.dirname(conandata_file), "..", "export_source")
        recipe_folder = os.path.realpath(recipe_folder)
        os.chdir(os.path.join(cwd, code_dir))
        for patch in patches:
            patch_file = patch.get("patch_file")
            if not patch_file:
                log.warning(f"{code_dir} 组件的conandata.yml文件缺少patch_file，跳过git apply操作")
            real_patch = os.path.join(recipe_folder, patch_file)
            if not os.path.isfile(real_patch):
                log.error(f"{code_dir} 组件申明的补丁文件{real_patch}不存在，可能产生错误，请人工处理")
                continue
            changed_files = FetchComponentCode._get_patch_changed_files(real_patch)
            log.info(f"{code_dir} 开始应用源码补丁{patch_file}")
            try:
                FetchComponentCode._apply_patches_direct(real_patch, patch_file, changed_files)
            except errors.BmcGoException:
                # 尝试还原文件修改
                for a_file, b_file in changed_files.items():
                    cmd = f"git checkout -- {a_file}"
                    tools.run_command(cmd, ignore_error=True)
                    cmd = f"git checkout -- {b_file}"
                    tools.run_command(cmd, ignore_error=True)
                cmd = "git am " + real_patch
                tools.run_command(cmd)
            log.info(f"{code_dir} 应用源码补丁{patch_file}")
        os.chdir(cwd)

    @staticmethod
    def __update_code_by_commit_id(code_dir, url, commit_id):
        if os.path.exists(code_dir):
            repo = Repo(code_dir)
            repo.git.fetch('origin')
        else:
            Repo.clone_from(url, to_path=code_dir)
            repo = Repo(code_dir)

        repo.index.reset(commit=commit_id, head=True, working_tree=True)
        repo.git.clean('-dfx')
        log.info("更新代码(组件: %s, 地址: %s, 提交节点: %s)", code_dir, url, commit_id)

    @staticmethod
    def __update_code_by_branch(code_dir, deps):
        url = deps['url']
        branch = deps['branch'].split('/')[-1]

        if os.path.exists(code_dir):
            repo = Repo(code_dir)
            repo.git.fetch('origin', branch)
            repo.git.pull('origin', branch)
            repo.git.checkout(branch)
        else:
            Repo.clone_from(url, to_path=code_dir, branch=branch)
            repo = Repo(code_dir)
        log.info("更新代码(组件: %s, 地址: %s, 分支: %s)", code_dir, url, branch)

    @staticmethod
    def __update_component_code_by_conandata(name, version, conandata_file):
        with open(conandata_file, 'r') as f_:
            conandata = yaml.safe_load(f_)
            deps = conandata.get("sources", {}).get(version, {})
            if 'url' in deps:
                FetchComponentCode.__update_code_by_branch(name, deps)
                patches = conandata.get("patches", {}).get(version)
                if patches:
                    FetchComponentCode.__apply_patches(conandata_file, patches, name)
            else:
                for comp, deps in deps.items():
                    FetchComponentCode.__update_code_by_branch(comp, deps)

    @staticmethod
    def __getinfo_from_conanfile(conanfile):
        with open(conanfile, "r") as file:
            lines = file.readlines()
            for idx, line in enumerate(lines):
                if line.find('scm = {"revision":') > 0:
                    revision = re.split(r'["]', line)[-2]
                    url = re.split(r'["]', lines[idx + 2])[-2]
                    break
            else:
                raise RuntimeError("无法找到版本(revision)和地址(url)字段")

            return revision, url

    def run(self):
        packages_to_fetch = dict()
        for component_name, package in self.packages.items():
            version_str = re.split("/|@", package)[1]
            if "[" not in version_str:
                if self.include_open_source or re.fullmatch("\d+\.\d+\.\d+", version_str) is not None:
                    packages_to_fetch[component_name] = package
                continue
            resolved_package = self.resolve_version_range(component_name, package)
            if resolved_package is None:
                log.warning("查找不到与 %s 范围匹配的版本", package)
            else:
                packages_to_fetch[component_name] = resolved_package
                log.info("查找到与 %s 范围匹配的版本 %s", package, resolved_package)

        process_count = min(len(packages_to_fetch), os.cpu_count())
        log.info("创建 %u 个进程拉取代码", process_count)
        pool = Pool(processes=process_count)
        for component_name, conan_version in packages_to_fetch.items():
            pool.apply_async(func=self.update_component_code, args=(component_name, conan_version),
                             error_callback=process_err_cb)
        pool.close()
        pool.join()

    def update_component_code(self, component_name, conan_version):
        """
        update component code by conan version
        """
        try:
            os.chdir(self.target_dir)
            log.info("更新 %s 组件代码到 %s 开始", component_name, conan_version)

            version_split = re.split(r'[/, @]', conan_version)
            conan_dir = os.path.join(os.path.expanduser('~'), '.conan/data/', *version_split, 'export')
            conandata = os.path.join(conan_dir, 'conandata.yml')
            if not os.path.exists(conan_dir):
                conan_remote_list = tools.get_conan_remote_list(self.remote)
                tools.download_conan_recipes(conan_version, conan_remote_list)
            if os.path.exists(conandata):
                FetchComponentCode.__update_component_code_by_conandata(version_split[0], version_split[1], conandata)
                return

            conanfile = os.path.join(conan_dir, 'conanfile.py')
            if os.path.exists(conanfile):
                revision, url = FetchComponentCode.__getinfo_from_conanfile(conanfile)
                FetchComponentCode.__update_code_by_commit_id(component_name, url, revision)
                return

            log.error("conandata(%s) 和 conanfile(%s) 都没有找到", conandata, conanfile)
            log.info("更新组件 %s 代码到 %s 失败, 无法获取到 conan 信息", component_name,
                     conan_version)
        except Exception as exp:
            log.error("工作状态错误: %s", exp)
            log.error("更新组件代码到 %s 失败", conan_version)