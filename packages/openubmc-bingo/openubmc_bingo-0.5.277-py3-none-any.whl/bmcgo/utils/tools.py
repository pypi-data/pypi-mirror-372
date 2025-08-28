#!/usr/bin/env python
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
import argparse
import json
import time
import re
import subprocess
import shutil
import tarfile
import hashlib
import shlex
import fcntl
import stat
import functools
import inspect
import configparser
from typing import Callable
from tempfile import TemporaryFile
from string import Template
from subprocess import Popen, PIPE
from collections import OrderedDict

import jsonschema
import yaml
from conans.model.profile import Profile
from conans.client.profile_loader import read_profile

from bmcgo.logger import Logger
from bmcgo.errors import BmcGoException, EnvironmentException
from bmcgo import misc
from bmcgo import errors
from bmcgo.logger import Logger


class Tools():
    """
    功能描述：公共类定义全局变量,公共函数
    接口：无
    """
    print_cnt = 0

    def __init__(self, log_name="bingo", log_file=None):
        os.makedirs(misc.CACHE_DIR, exist_ok=True)
        self.lock_file = os.path.join(misc.CACHE_DIR, "frame_lock")
        if log_file is None:
            self.log_name = os.path.join(misc.CACHE_DIR, f"{log_name}.log")
        else:
            self.log_name = log_file
        self.log = Logger(log_name, log_file=self.log_name)
        file_handle = os.fdopen(os.open(self.lock_file, os.O_WRONLY | os.O_CREAT,
                                stat.S_IWUSR | stat.S_IRUSR), 'a')
        file_handle.close()

    @property
    def user_home(self):
        return os.environ["HOME"]

    @property
    def conan_home(self):
        return os.path.expanduser("~/.conan")

    @property
    def conan_profiles_dir(self):
        return os.path.join(self.conan_home, "profiles")

    @property
    def conan_profiles(self):
        profiles = []
        for profile in os.listdir(self.conan_profiles_dir):
            if os.path.isfile(os.path.join(self.conan_profiles_dir, profile)):
                profiles.append(profile)
        return profiles

    @property
    def conan_data(self):
        return os.path.join(self.conan_home, "data")

    @staticmethod
    def format_command(command, sudo=False):
        cmd_args: list[str] = []
        if isinstance(command, list):
            cmd_args = command
        elif isinstance(command, str):
            cmd_args = shlex.split(command)
            cmd = shutil.which(cmd_args[0])
            if cmd is None:
                raise EnvironmentException(f"{cmd_args[0]}不存在, 请检查命令或环境配置")
            cmd_args[0] = cmd
        else:
            raise BmcGoException(f"不支持的命令参数格式: {command}, 请检查命令格式")
        sudo_cmd = shutil.which("sudo")
        if sudo and sudo_cmd and cmd_args[0] != sudo_cmd:
            cmd_args.insert(0, sudo_cmd)
        return cmd_args

    @staticmethod
    def check_path(path):
        """
        功能描述：检查目录是否存在，没有就创建
        参数：path 要检查的目录
        返回值：无
        """
        if not os.path.exists(path) and not os.path.islink(path):
            os.makedirs(path, exist_ok=True)

    @staticmethod
    def copy(source, target):
        """
        功能描述：拷贝文件优化，如果存在目标文件先删除后拷贝
        参数：source 源文件 target 目标文件
        返回值：无
        """
        if not os.path.isfile(source):
            raise FileNotFoundError(f"Source file {source} does not exist.")
        if os.path.realpath(target) == os.path.realpath(source):
            return
        if os.path.isdir(target):
            target = os.path.join(target, os.path.basename(source))
        elif os.path.exists(target):
            os.unlink(target)
        shutil.copy(source, target)

    @staticmethod
    def sha256sum(file_path: str):
        # 为提高性能, 每次读取64KB数据
        data_block_size = 1024 * 64
        sha256hasher = hashlib.sha256()
        with open(file_path, 'rb') as fp:
            while True:
                data = fp.read(data_block_size)
                if not data:
                    break
                sha256hasher.update(data)
        sha256 = sha256hasher.hexdigest()
        return sha256

    @staticmethod
    def find_key_in_dict(f_dict: dict, key: str):
        results = []
        for k, v in f_dict.items():
            if k == key:
                results.append(v)
            elif isinstance(v, dict):
                results.extend(Tools.find_key_in_dict(v, k))
        return results

    @staticmethod
    def remove_path(path):
        """
        功能描述：删除指定的目录
        参数：path 要删除的目录
        返回值：无
        """
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)

    @staticmethod
    def has_kwargs(func: Callable):
        """
        功能描述: 检查function是否有可变的关键字参数**kwargs
        参数: 需要检查的function
        返回值: bool
        """
        signature = inspect.signature(func)
        parameters = signature.parameters
        for param in parameters.values():
            if param.kind == param.VAR_KEYWORD:
                return True
        return False

    @staticmethod
    def get_profile_arg_help():
        tools = Tools()
        profile_help_text = "显式指定conan构建使用的profile文件 (~/.conan/profiles目录下)别名, 默认为: 空\n可选值: "
        profile_help_text += ", ".join(tools.conan_profiles)
        return profile_help_text

    @staticmethod
    def get_conan_profile(profile: str, build_type: str, enable_luajit=False):
        """
        根据参数与配置获取conan构建使用的profile文件名。
        """
        if profile:
            return str(profile)

        if build_type == "dt":
            return "profile.dt.ini"

        return "profile.luajit.ini"

    @staticmethod
    def check_product_dependencies(top, base):
        for key, value in top.items():
            if (
                key == "dependencies"
                or key == "dt_dependencies"
                or key == "debug_dependencies"
            ):
                for com_package in value:
                    Tools().check_base_dependencies(base, com_package, key)

    @staticmethod
    def check_base_dependencies(base_manifest, com_package, dependency_type):
        name = com_package.get(misc.CONAN)
        action = com_package.get("action", "")
        pkg_info = name.split("/")
        pkg_name = pkg_info[0]
        has_version = len(pkg_info) > 1
        for sub in base_manifest.get(dependency_type, {}):
            sub_name = sub.get(misc.CONAN)
            sub_pkg_name = sub_name.split("/")[0]
            # 上下层具有相同组件名的组件
            if pkg_name == sub_pkg_name:
                if has_version or action:
                    raise errors.BmcGoException(
                        "配置错误: 不允许删除平台组件或定制平台组件版本号{}".format(name)
                    )
                else:
                    com_package[misc.CONAN] = sub_name
                break

    @staticmethod
    def merge_dependencies(top, base):
        ret = []
        for conan in top:
            name = conan.get(misc.CONAN)
            pkg_name = name.split("/")[0]
            found = False
            for sub in base:
                sub_name = sub.get(misc.CONAN)
                sub_pkg_name = sub_name.split("/")[0]
                # 上下层具有相同组件名的组件
                if pkg_name == sub_pkg_name:
                    found = True
                    break
            # 上下层具有相同组件名的组件
            if found:
                action = conan.get("action")
                if action and action == "delete":
                    # 但如果上层配置了delete的
                    continue
                else:
                    ret.append(conan)
            else:
                # 未找到下层组件时
                ret.append(conan)
        for sub in base:
            sub_name = sub.get(misc.CONAN)
            sub_pkg_name = sub_name.split("/")[0]
            found = False
            for conan in top:
                name = conan.get(misc.CONAN)
                pkg_name = name.split("/")[0]
                # 上下层具有相同组件名的组件
                if pkg_name == sub_pkg_name:
                    found = True
                    break
            # 当下层组件未在上层配置时,使用下层组件
            if not found:
                ret.append(sub)
        return ret

    @staticmethod
    def fix_platform(package, stage):
        version_split = re.split(r"[/, @]", package[misc.CONAN])
        if stage == misc.StageEnum.STAGE_DEV.value:
            # 开发者测试模式
            stage = misc.StageEnum.STAGE_RC.value
        # else: rc和stable模式
        channel = f"@{Tools().conan_user}/{stage}"

        if len(version_split) == 2:
            package[misc.CONAN] += channel

    @staticmethod
    def install_platform(platform_package, stage, remote):
        Tools().fix_platform(platform_package, stage)
        rtos_version = platform_package.get("options", {}).get(
            "rtos_version", "rtos_v2"
        )
        append_cmd = f"-r {remote}" if remote else ""
        Tools().run_command(
            f"conan install {platform_package[misc.CONAN]} {append_cmd} -o rtos_version={rtos_version}"
        )
        version_split = re.split(r"[/, @]", platform_package[misc.CONAN])
        package_conan_dir = os.path.join(
            os.path.expanduser("~"), ".conan/data/", *version_split
        )
        cmd = f"conan info {platform_package[misc.CONAN]} {append_cmd} -o rtos_version={rtos_version} -j"
        cmd_info = Tools().run_command(
            cmd,
            capture_output=True,
        )
        info = json.loads(cmd_info.stdout)
        for i in info:
            package_conan_dir = os.path.join(
                package_conan_dir, "package", i["id"], rtos_version
            )
        return package_conan_dir

    @staticmethod
    def get_manifest_dependencies(manifest_build_dir, file_path, stage, remote):
        with open(file_path, "r") as f_:
            base_manifest = yaml.safe_load(f_)
        top_dependencies = base_manifest[misc.CONAN_DEPDENCIES_KEY]
        platform_package = base_manifest.get("platform", {})
        if platform_package:
            package_conan_dir = Tools.install_platform(platform_package, stage, remote)
            top_dependencies.append(platform_package)
            platform_src = os.path.join(package_conan_dir, "manifest.yml")
            with open(platform_src, "r") as f_:
                platform_manifest = yaml.safe_load(f_)
            Tools.check_product_dependencies(base_manifest, platform_manifest)
            top_dependencies = Tools.merge_dependencies(
                top_dependencies, platform_manifest[misc.CONAN_DEPDENCIES_KEY]
            )
        inc_filename = base_manifest.get("include")
        if not inc_filename:
            return top_dependencies
        file_path = inc_filename.replace(
            "${product}", os.path.join(manifest_build_dir, "product")
        )
        base_dependencies = Tools.get_manifest_dependencies(manifest_build_dir, file_path, stage, remote)
        dep = Tools.merge_dependencies(top_dependencies, base_dependencies)
        return dep

    @staticmethod
    def create_common_parser(description):
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("-cp", "--conan_package", help="软件包名, 示例: kmc/24.0.0.B020", default="")
        parser.add_argument("-uci", "--upload_package", help="是否上传软件包", action=misc.STORE_TRUE)
        parser.add_argument("-o", "--options", help="组件特性配置, 示例: -o skynet:enable_luajit=True",
                            action='append')
        parser.add_argument("-r", "--remote", help="指定conan远端")
        parser.add_argument("-bt", "--build_type", help="构建类型，可选：debug（调试包）, release（正式包）, dt（开发者测试包）", 
                            default="debug")
        parser.add_argument("--stage", help="包类型，可选值为: dev(调试包), rc（预发布包）, stable（发布包）\n默认：dev", 
                            default="dev")
        parser.add_argument("-jit", "--enable_luajit", help="Enable luajit", action=misc.STORE_TRUE)
        parser.add_argument("-s", "--from_source", help="使能源码构建", action=misc.STORE_TRUE)
        parser.add_argument("-as", "--asan", help="Enable address sanitizer", action=misc.STORE_TRUE)
        parser.add_argument(
            "-pr",
            "--profile",
            help=Tools.get_profile_arg_help(),
            default="",
        )
        return parser

    @staticmethod
    def get_module_symver_option(module_symver_path: str):
        sha256 = Tools.sha256sum(module_symver_path)
        return ("module_symver", sha256)

    @staticmethod
    def clean_conan_bin(conan_bin):
        if os.path.isdir(conan_bin):
            for file in os.listdir(conan_bin):
                file_path = os.path.join(conan_bin, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        else:
            os.makedirs(conan_bin)

    @functools.cached_property
    def is_ubuntu(self):
        """
        功能描述: 判断当前环境是否为Ubuntu
        返回值: bool
        """
        if os.path.isfile("/etc/issue"):
            fp = open("/etc/issue", "r")
            issue = fp.read()
            fp.close()
            if issue.startswith("Ubuntu"):
                return True
        return False

    @functools.cached_property
    def conan_user(self):
        if os.access(misc.GLOBAL_CFG_FILE, os.R_OK):
            try:
                conf = configparser.ConfigParser()
                conf.read(misc.GLOBAL_CFG_FILE)
                return conf.get(misc.CONAN, "user")
            except (configparser.NoSectionError, configparser.NoOptionError):
                pass

        return misc.ConanUserEnum.CONAN_USER_RELEASE.value

    def get_conan_remote_list(self, remote):
        conan_remote_list = []
        if remote:
            conan_remote_list.append(remote)
        else:
            remote_list = self.run_command("conan remote list", capture_output=True).stdout.split("\n")
            conan_remote_list = [remote.split(":")[0] for remote in remote_list if remote]
        return conan_remote_list

    def download_conan_recipes(self, conan_version, conan_remote_list):
        download_flag = False
        for remote in conan_remote_list:
            try:
                self.run_command(f"conan download {conan_version} -r {remote} -re", show_error_log=False)
                download_flag = True
                break
            except Exception as e:
                self.log.info(f"Recipe not fount in {remote}: {conan_version}")
        if not download_flag:
            raise BmcGoException(f"Download {conan_version} failed")

    def yaml_load_template(self, yaml_name: str, template: dict, need_validate=True):
        with open(yaml_name, "r", encoding="utf-8") as fp:
            yaml_string = fp.read()
        yaml_string = Template(yaml_string)
        yaml_conf = yaml_string.safe_substitute(template)
        yaml_obj = yaml.full_load(yaml_conf)
        if need_validate:
            schema_file = misc.get_decleared_schema_file(yaml_name)
            if schema_file == "":
                return yaml_obj
            with open(schema_file, "rb") as fp:
                schema = json.load(fp)
            self.log.debug("开始校验 %s", yaml_name)
            try:
                jsonschema.validate(yaml_obj, schema)
            except jsonschema.exceptions.ValidationError as e:
                raise OSError('文件 {} 无法通过schema文件 {} 的校验\n    {}'.format(yaml_name, schema_file, str(e))) from e
        return yaml_obj

    def get_file_permission(self, path):
        with Popen(self.format_command(f"stat -c '%a' {path}", sudo=True), stdout=PIPE) as proc:
            data, _ = proc.communicate(timeout=50)
            return data.decode('utf-8')

    def copy_all(self, source_path, target_path):
        """
        功能描述：将 source_path 目录下所有文件全部复制到 target_path 下
                 如果要复制 source_path 文件夹，需指定 target_path 下同名文件夹
        参数：source_path 源目录 target_path 目标目录
        返回值：无
        """
        if not os.path.exists(source_path):
            raise OSError(f"源目录 ({source_path}) 不存在, 请检查源文件")
        for root, dirs, files in os.walk(source_path, topdown=True):
            for dirname in dirs:
                dest_dir_t = f"{target_path}/{root[len(source_path) + 1:]}/{dirname}"
                self.check_path(dest_dir_t)
            for file in files:
                src_file = os.path.join(root, file)
                dest_dir = os.path.join(target_path, root[len(source_path) + 1:])
                self.check_path(dest_dir)
                dest_file = os.path.join(dest_dir, os.path.basename(src_file))
                if os.path.isfile(dest_file):
                    os.unlink(dest_file)
                if os.path.islink(src_file):
                    shutil.copy2(src_file, dest_dir, follow_symlinks=False)
                else:
                    shutil.copy2(src_file, dest_dir)

    def untar_to_dir(self, targz_source, dst_dir="."):
        """
        功能描述：解压tar包到指定目录
        参数：targz_source tar包 ，dst_dir 目标目录
        返回值：无
        """
        self.log.info("解压 - 源文件: {}, 目标文件: {}".format(targz_source, dst_dir))
        tar_temp = tarfile.open(targz_source)
        tar_temp.extractall(dst_dir)
        tar_temp.close()

    def list_all_file(self, regular_exp, dir_path, recursive=False):
        """
        功能描述：在 dir_path 列表中，找出符合正则表达式的值路径，并返回列表
        参数：  regular_exp: 正则表达式
                dir_path: 需要查找的路径
                recursive： 是否递归查询(查询所有子文件夹)
        返回值：无
        """
        dir_match_list = []
        dir_list = os.listdir(dir_path)
        for element in dir_list:
            if recursive and os.path.isdir(f"{dir_path}/{element}"):
                dir_match_list.append(f"{dir_path}/{element}")
                dir_match_list += self.list_all_file(regular_exp, f"{dir_path}/{element}", recursive)
            else:
                ret = re.fullmatch(regular_exp, element)
                if ret is not None:
                    dir_match_list.append(f"{dir_path}/{element}")
        return dir_match_list

    def py_sed(self, src_file, regular_exp, instead_text, def_line="l"):
        self.log.info(f"要被替换文件: {src_file} -- 匹配正则表达式为: {regular_exp}")
        shutil.copy(src_file, f"{src_file}_bak")
        with open(src_file, "r", encoding="utf-8") as fp_r:
            lines = fp_r.readlines()
        fp_w = os.fdopen(os.open(src_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w')
        line_num = 0
        if def_line == "l":
            for line in lines:
                ret = re.search(regular_exp, line)
                if ret is None:
                    fp_w.write(line)
                    line_num = line_num + 1
                else:
                    self.log.info(f"字符串: {ret.group(0)}")
                    line = line.replace(ret.group(0), instead_text)
                    fp_w.write(line)
                    line_num = line_num + 1
                    break
            for i in range(line_num, len(lines)):
                fp_w.write(lines[i])
        elif def_line == "g":
            for line in lines:
                ret = re.search(regular_exp, line)
                if ret is not None:
                    line = line.replace(ret.group(0), instead_text)
                fp_w.write(line)
        fp_w.close()
        os.remove(f"{src_file}_bak")

    def make_img(self, img_path, mnt_datafs, size):
        try:
            self.run_command(f"/sbin/mkfs.ext4 -d {mnt_datafs} -r 1 -N 0 -m 5 -L \"rootfs\" -I 256 -O \
            ^64bit,^metadata_csum {img_path} \"{size}M\"", ignore_error=True, sudo=True)
            user_group = f"{os.getuid()}:{os.getgid()}"
            self.run_command(f"chown {user_group} {img_path}", sudo=True)
        except Exception:
            self.log.error(f"{img_path} 镜像制作失败")

    def get_studio_path(self):
        ret = self.run_command("whereis bmc_studio", sudo=True, ignore_error=True,
            command_echo=False, capture_output=True).stdout
        if not ret:
            return ""

        ret = ret.replace(" ", "").replace("\n", "")
        studio_split = ret.split(":")
        if len(studio_split) <= 1:
            return ""

        return studio_split[1]

    def run_command(self, command, ignore_error=False, sudo=False, **kwargs):
        """
        如果ignore_error为False，命令返回码非0时则打印堆栈和日志并触发异常，中断构建
        """
        # 如果run_command在同一行多次调用则无法区分执行的命令，command_key用于在日志中指示当前正在执行的命令关键字
        command_key = kwargs.get("command_key", None)
        command_echo = kwargs.get("command_echo", True)
        show_log = kwargs.get("show_log", False)
        uptrace = kwargs.get("uptrace", 0) + 1
        error_log = kwargs.get("error_log")
        warn_log = kwargs.get("warn_log")
        timeout = kwargs.get("timeout", 1200)
        capture_output = kwargs.get("capture_output", False)
        if command_key:
            key = command_key + ":"
        else:
            key = ""
        if command_echo and not self.log.is_debug:
            self.log.info(f">> {key}{command}", uptrace=uptrace)
        command = self.format_command(command, sudo)
        ret = None
        log_fd = os.fdopen(os.open(self.log_name, os.O_RDWR | os.O_CREAT | os.O_APPEND,
                        stat.S_IWUSR | stat.S_IRUSR), 'a+')
        try:
            check = False if ignore_error else True
            if show_log:
                ret = subprocess.run(command, check=check, timeout=timeout)
            elif capture_output:
                ret = subprocess.run(command, capture_output=capture_output, check=check, timeout=timeout, text=True)
                if ret.stdout:
                    log_fd.write(ret.stdout)
                if ret.stderr:
                    log_fd.write(ret.stderr)
            else:
                ret = subprocess.run(command, stdout=log_fd, stderr=log_fd, check=check, timeout=timeout)
        except Exception as e:
            if error_log:
                self.log.error(error_log, uptrace=uptrace)
            elif warn_log:
                self.log.warning(warn_log, uptrace=uptrace)
            else:
                self.log.error(f"执行命令 {key}{command} 错误, 日志: {self.log_name}", uptrace=uptrace)
            log_fd.flush()
            log_fd.close()
            raise e
        log_fd.close()
        return ret

    def pipe_command(self, commands, out_file=None, **kwargs):
        if not isinstance(commands, list):
            raise BmcGoException("命令必须为列表")
        # 创建一个空的文件
        flag = "w+b"
        if out_file:
            fp = os.fdopen(os.open(out_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                   stat.S_IWUSR | stat.S_IRUSR), flag)
            fp.close()
        stdin = None
        command_echo = kwargs.get("command_echo", True)
        uptrace = kwargs.get("uptrace", 0) + 1
        ignore_error = kwargs.get('ignore_error', False)
        capture_output = kwargs.get('capture_output', False)
        if command_echo and not self.log.is_debug:
            self.log.info(f">> " + ' | '.join(commands), uptrace=uptrace)
        for command in commands:
            stdout = TemporaryFile(flag)
            cmd = self.format_command(command, False)
            ret = subprocess.Popen(cmd, stdout=stdout, stdin=stdin)
            ret.wait()
            if ret.returncode != 0:
                if ignore_error:
                    return None, ret.returncode
                raise BmcGoException(f"运行命令 {command} 失败, 请分析执行的命令返回日志")
            if stdin is not None:
                stdin.close()
            stdin = stdout
            stdin.seek(0)
        if stdin:
            context = stdin.read()
            if out_file:
                with os.fdopen(os.open(out_file, os.O_WRONLY | os.O_CREAT,
                                    stat.S_IWUSR | stat.S_IRUSR), flag) as fp:
                    fp.write(context)
            stdin.close()
        if capture_output:
            return context.decode("utf-8"), 0
        return None, ret.returncode

    def sudo_passwd_check(self):
        self.log.info("测试sudo是否正常执行")
        try:
            self.run_command("ls .", sudo=True)
        except Exception as e:
            self.log.error("sudo命令无法正常执行")
            raise e
        else:
            self.log.info("sudo命令正常执行")

    def clean_locks(self):
        self.log.info("尝试清理conan组件锁")
        if not os.path.isdir(self.conan_data):
            return
        cmd = [f"find {self.conan_data} -maxdepth 4 -mindepth 4 -type f -name *.count*", "xargs rm -f"]
        _, _ = self.pipe_command(cmd, out_file=None)

    def get_profile_config(self, profile_name) -> (Profile, OrderedDict):
        """根据profile文件名获取~/.conan/profiles对应文件的配置内容"""
        if not profile_name:
            return None, None
        profile_file = os.path.join(self.conan_profiles_dir, profile_name)
        if not os.path.isfile(profile_file):
            raise BmcGoException(f"{profile_file} 文件不存在")

        profile, profile_vars = read_profile(profile_name, os.getcwd(), self.conan_profiles_dir)
        return profile, profile_vars

    def _save_tempfile_safety(self, temp_fd, target_file, show_log=False):
        lock_fd = open(self.lock_file, "r")
        temp_fd.seek(0)
        log_conent = temp_fd.read()
        if show_log:
            self.log.info(log_conent, uptrace=1)
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX)
        with os.fdopen(os.open(target_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w+') as log_fd:
            log_fd.write(log_conent)
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
