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

from collections import defaultdict
from typing import Dict, Set
import json
import os
import re
import shutil
import subprocess

from bmcgo.logger import Logger
from bmcgo.codegen.c.helper import Helper
from bmcgo import misc

global log
log = Logger()


class InterfaceValidation:
    def __init__(self, remote):
        self.intf_impl: Set[str] = set()
        self.intf_deps: Set[str] = set()
        self.intf_hardcoded: Dict[str, Set[str]] = defaultdict(set)
        self.all_predefined_intfs: Set[str] = set()
        self.remote = remote
        self._parse_mds_interfaces()
        self._parse_hardcoded_interfaces()
        self._pull_all_interfaces()

    @staticmethod
    def extract_dbus_intf_in_file(file_path):
        all_intfs = list()
        with open(file_path, "r") as file_descriptor:
            # iBMC d-bus interface pattern: bmc.(kepler|dev).[A-Z]
            pattern = "[\"\']bmc\.(?:kepler|dev)(?:\.[A-Z].*?)?[\"\']"
            intf_match = re.findall(pattern, file_descriptor.read())
            for intf in intf_match:
                all_intfs.append(intf[1:-1])
        return all_intfs

    @staticmethod
    def _check_bus_call_in_file(file_path):
        patterns = ["bus:p?call\(.+\n?"]
        has_pattern = False
        with open(file_path, "r") as file_descriptor:
            src_lua = file_descriptor.read()
            for pattern in patterns:
                bus_call = re.findall(pattern, src_lua)
                if len(bus_call) != 0:
                    log.error("在 %s 发现非自动生成的代码调用, 匹配到: %s. 请使用代码自动生成(generation)", file_path, pattern)
                    has_pattern = True
        return has_pattern

    @staticmethod
    def _parse_mds_package_deps():
        channel = f"@{misc.ConanUserEnum.CONAN_USER_RELEASE.value}/{misc.StageEnum.STAGE_RC.value}"
        package = f"mdb_interface/[>=0.0.1]{channel}"
        service_path = os.path.join(os.getcwd(), "mds/service.json")
        if not os.path.exists(service_path):
            return package
        with open(service_path, "r") as service_fp:
            try:
                content = json.load(service_fp)
            except json.decoder.JSONDecodeError as error:
                return package
        dependencies = content.get("dependencies")
        if not dependencies:
            return package
        dep_list = dependencies.get("test", [])
        dep_list.extend(dependencies.get("build", []))
        for dep in dep_list:
            conan_package = dep.get(misc.CONAN, "")
            if not conan_package.startswith("mdb_interface"):
                continue
            if "@" in conan_package:
                package = conan_package
            else:
                package = f"{conan_package}{channel}"
        return package

    def run(self):
        intf_validation_passed = self._validate_mds_intf() and self._validate_hardcoded_intf() and \
                self._check_dbus_call()
        if intf_validation_passed:
            log.info("接口检验通过")
        else:
            log.error("接口校验未通过")
        return intf_validation_passed

    def _parse_mds_interfaces(self):
        mds_model_path = os.path.join(os.getcwd(), "mds/model.json")
        if not os.path.exists(mds_model_path):
            return
        with open(mds_model_path, "r") as file_descriptor:
            try:
                model_data = json.load(file_descriptor)
            except json.decoder.JSONDecodeError as error:
                raise OSError(f"无法加载文件 {mds_model_path}, 错误消息: {error.msg}") from error
            else:
                for class_name in model_data:
                    self.intf_impl.update(model_data[class_name].get("interfaces", {}).keys())

        mds_service_path = os.path.join(os.getcwd(), "mds/service.json")
        if not os.path.exists(mds_service_path):
            return
        with open(mds_service_path, "r") as file_descriptor:
            try:
                service_data = json.load(file_descriptor)
            except json.decoder.JSONDecodeError as error:
                raise OSError(f"无法加载文件 {mds_model_path}, 错误消息: {error.msg}") from error
            else:
                for require_object in service_data.get("required", []):
                    self.intf_deps.add(require_object.get("interface"))

    """
    @brief: parse the d-bus interface claimed in the source code
    """
    def _parse_hardcoded_interfaces(self):
        for root, _, files in os.walk(os.path.join(os.getcwd(), "", "src")):
            for file_name in files:
                if not file_name.endswith(".lua"):
                    continue
                file_path = os.path.join(root, file_name)
                for intf in self.extract_dbus_intf_in_file(file_path):
                    self.intf_hardcoded[intf].update([file_path])

    def _pull_interfaces_from_repo(self):
        mdb_interface_repo_url = "https://gitcode.com/openUBMC/mdb_interface.git"
        mktemp_cmd = subprocess.run(["/usr/bin/mktemp", "-d", "--suffix", "_mdb_interface"], capture_output=True)
        if mktemp_cmd.returncode != 0:
            raise OSError(f"创建文件夹失败, 错误消息: {mktemp_cmd.stderr}")
        temp_dir = mktemp_cmd.stdout.decode().strip('\n')

        git_cmd = Helper.get_git_path()
        repo_fetch = subprocess.run(
            [git_cmd, "clone", mdb_interface_repo_url, temp_dir, "--depth=1"],
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        if repo_fetch.returncode != 0:
            log.error("克隆远端仓库 %s 失败, 错误信息: %s", mdb_interface_repo_url, repo_fetch.stderr)
        intf_dir = os.path.join(temp_dir, "json/intf/mdb/bmc")

        for root, _, files in os.walk(intf_dir):
            for file_name in files:
                if not file_name.endswith(".json"):
                    continue
                file_path = os.path.join(root, file_name)
                self.all_predefined_intfs.update(intf for intf in self.extract_dbus_intf_in_file(file_path))

        shutil.rmtree(temp_dir, ignore_errors=True)

    def _pull_interfaces_from_conan(self):
        pkg = self._parse_mds_package_deps()
        mktemp_cmd = subprocess.run(["/usr/bin/mktemp", "-d", "--suffix", "_mdb_interface"], capture_output=True)
        if mktemp_cmd.returncode != 0:
            raise OSError(f"创建文件夹失败, 错误消息: {mktemp_cmd.stderr}")
        temp_dir = mktemp_cmd.stdout.decode().strip('\n')
        cmd = [misc.CONAN, "install", pkg, f"-if={temp_dir}", "--build=missing", "-g", "deploy", "-s", "build_type=Dt"]
        if self.remote:
            cmd += ["-r", self.remote]
        subprocess.call(cmd)
        intf_dir = os.path.join(temp_dir, "mdb_interface/opt/bmc/apps/mdb_interface/intf/mdb/bmc")

        for root, _, files in os.walk(intf_dir):
            for file_name in files:
                if not file_name.endswith(".json"):
                    continue
                file_path = os.path.join(root, file_name)
                self.all_predefined_intfs.update(intf for intf in self.extract_dbus_intf_in_file(file_path))
        shutil.rmtree(temp_dir, ignore_errors=True)

    def _pull_interfaces_from_codegen(self):
        service_path = os.path.join(os.getcwd(), "mds/service.json")
        try:
            with open(service_path, 'r') as file_descriptor:
                repo_name = json.load(file_descriptor).get('name')
        except Exception as e:
            log.error('mds/service.json 文件解析失败: %s', e)
            return
        generated_intf_dir = os.path.join(os.getcwd(), "gen", repo_name, "json_types")
        for root, _, files in os.walk(generated_intf_dir):
            for file_name in files:
                if not file_name.endswith(".lua"):
                    continue
                file_path = os.path.join(root, file_name)
                self.all_predefined_intfs.update(intf for intf in self.extract_dbus_intf_in_file(file_path))
        client_intf_path = os.path.join(os.getcwd(), "gen", repo_name, "client.lua")
        if not os.path.exists(client_intf_path):
            return
        self.all_predefined_intfs.update(intf for intf in self.extract_dbus_intf_in_file(client_intf_path))

    """
    @brief: fetch the mdb_interface repository and parse all predefined d-bus interfaces
    """
    def _pull_all_interfaces(self):
        self._pull_interfaces_from_repo()
        self._pull_interfaces_from_conan()
        self._pull_interfaces_from_codegen()

    """
    @brief: check the d-bus interfaces claimed in mds are defined in mdb_interface
    """
    def _validate_mds_intf(self):
        intf_impl_in_mdb = True
        intf_deps_in_mdb = True
        for intf in self.intf_impl:
            if intf not in self.all_predefined_intfs:
                log.error("在 mds/model.json 中找到未定义的接口: %s", intf)
                intf_impl_in_mdb = False

        for intf in self.intf_deps:
            if intf not in self.all_predefined_intfs:
                log.error("在 mds/service.json 找到未定义的接口: %s", intf)
                intf_deps_in_mdb = False

        return intf_impl_in_mdb and intf_deps_in_mdb

    """
    @brief: check the hardcoded d-bus interfaces in the source lua code are claimed in mds and mdb_interface
    """
    def _validate_hardcoded_intf(self):
        hardcoded_intf_in_mdb = True
        hardcode_intf_in_mds = True
        for intf, paths in self.intf_hardcoded.items():
            if intf not in self.all_predefined_intfs:
                log.error("在 %s 找到 未定义的接口 %s. 请检查你的源码", paths, intf)
                hardcoded_intf_in_mdb = False
            if intf not in self.intf_impl and intf not in self.intf_deps:
                log.warning("在 %s 找到 未定义的接口 %s. 请使用 mds 模板", paths, intf)
                hardcoded_intf_in_mds = False
        return hardcoded_intf_in_mdb

    """
    @brief: check d-bus call snippet in source code. It is recommend to use generated templates for d-bus call.
    """
    def _check_dbus_call(self):
        has_pattern = False
        for root, _, files in os.walk(os.path.join(os.getcwd(), "src")):
            for file_name in files:
                if not file_name.endswith(".lua"):
                    continue
                file_path = os.path.join(root, file_name)
                if self._check_bus_call_in_file(file_path):
                    has_pattern = True
        return not has_pattern