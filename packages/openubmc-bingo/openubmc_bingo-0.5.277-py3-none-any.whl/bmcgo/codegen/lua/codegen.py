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
import configparser
import json
import os
import re
import subprocess
import shutil
from pathlib import Path
from bmcgo.codegen.c.helper import Helper
from bmcgo import misc
from bmcgo.utils.tools import Tools
cwd = os.path.split(os.path.realpath(__file__))[0]


class CodeGen(object):
    def __init__(self, project_dir, version, remote, major_version=0):
        self.gen_tool_dir = os.path.join(project_dir, 'temp/lua_codegen')
        self.project_dir = project_dir
        self.project_name = self.get_project_name()
        self.version = version
        self.major_version = major_version
        self.remote = remote

    def read_service_json(self):
        service_path = os.path.join(self.project_dir, "mds", "service.json")
        if not os.path.isfile(service_path):
            raise RuntimeError("mds/service.json文件不存在")
        with open(service_path, "r") as service_fp:
            content = json.load(service_fp)
        return content

    def get_project_name(self):
        project_name = self.read_service_json().get("name")
        if not project_name:
            raise RuntimeError("需要在mds/service.json中配置name")
        return project_name

    def get_lua_format(self):
        lua_format = shutil.which("lua-format")
        if lua_format:
            return lua_format

    def get_mdb_interface_package(self):
        channel = f"@{Tools().conan_user}/{misc.StageEnum.STAGE_RC.value}"
        package = f"mdb_interface/[>=0.0.1]{channel}"
        dependencies = self.read_service_json().get(misc.CONAN_DEPDENCIES_KEY)
        if not dependencies:
            return package
        dep_list = dependencies.get("test", [])
        dep_list.extend(dependencies.get("build", []))
        for dep in dep_list:
            conan_package = dep.get("conan", "")
            if not conan_package.startswith("mdb_interface"):
                continue
            if "@" in conan_package:
                package = conan_package
            else:
                package = conan_package + channel
        return package

    def get_mdb_interface_url(self, temp_dir, target_dir):
        ini_parser = configparser.ConfigParser()
        ok = ini_parser.read(misc.GLOBAL_CFG_FILE)
        if not ok or not ini_parser.has_option("codegen", "mdb_interface_url"):
            return False
        mdb_interface_url = ini_parser["codegen"]["mdb_interface_url"]

        git_cmd = Helper.get_git_path()
        cmd = [git_cmd, "clone", mdb_interface_url, os.path.join(temp_dir, "mdb_interface"), "--depth=1"]
        subprocess.run(cmd, stdout=subprocess.DEVNULL)
        shutil.copytree(os.path.join(temp_dir, "mdb_interface/json"), target_dir)
        return True

    def setup_mdb_interface(self):
        target_dir = os.path.join(self.project_dir, 'temp/opt/bmc/apps/mdb_interface')
        shutil.rmtree(target_dir, ignore_errors=True)
        temp_dir = os.path.join(self.project_dir, 'temp/.mdb_interface_temp')
        shutil.rmtree(temp_dir, ignore_errors=True)
        os.makedirs(temp_dir, exist_ok=True)
        if self.get_mdb_interface_url(temp_dir, target_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            return
        package = self.get_mdb_interface_package()
        cmd = ["conan", "install", package, f"-if={temp_dir}", "--build=missing", "-g", "deploy"]
        cmd += ["-pr=profile.dt.ini", "-s", "build_type=Dt"]
        if self.remote:
            cmd += ["-r", self.remote]
        subprocess.call(cmd)
        shutil.copytree(os.path.join(temp_dir, "mdb_interface/opt/bmc/apps/mdb_interface"), target_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)

    def setup_latest_mdb_interface(self):
        target_dir = os.path.join(self.project_dir, 'temp/opt/bmc/apps/latest_mdb_interface')
        shutil.rmtree(target_dir, ignore_errors=True)
        temp_dir = os.path.join(self.project_dir, 'temp/.latest_mdb_interface_temp')
        shutil.rmtree(temp_dir, ignore_errors=True)
        os.makedirs(temp_dir, exist_ok=True)

        conan_home = Path(os.environ.get("CONAN_HOME", Path.home() / ".conan/data"))
        mdb_interface_tmp_dir = os.path.join(conan_home, "latest_mdb_interface")
        env = dict(os.environ, CONAN_STORAGE_PATH=mdb_interface_tmp_dir)

        channel = f"@{Tools().conan_user}/{misc.StageEnum.STAGE_RC.value}"
        package = f"mdb_interface/[>=0.0.1]{channel}"
        
        cmd = ["conan", "install", package, f"-if={temp_dir}", "--update", "--build=missing", "-g", "deploy"]
        cmd += ["-pr=profile.dt.ini", "-s", "build_type=Dt"]
        if self.remote:
            cmd += ["-r", self.remote]

        subprocess.run(cmd, env=env)
        shutil.copytree(os.path.join(temp_dir, "mdb_interface/opt/bmc/apps/mdb_interface"), target_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)

    def is_valid_date(self, date_str):
        pattern = r'^-- Create: \d{4}-\d{1,2}-\d{1,2}$'
        return bool(re.match(pattern, date_str))

    def process_file_header(self, filepath, bak_filepath):
        with open(filepath, 'r') as file1, open(bak_filepath, 'r') as file2:
            # 逐行读取文件内容
            file1_lines = file1.readlines()
            file2_lines = file2.readlines()
        file1_lines_num = len(file1_lines)
        if file1_lines_num != len(file2_lines):
            return

        # 比较文件内容
        for i in range(file1_lines_num):
            if file1_lines[i] == file2_lines[i]:
                continue
            if 'Copyright' in file2_lines[i]:
                continue
            if not self.is_valid_date(file1_lines[i]) or not self.is_valid_date(file2_lines[i]):
                return
        shutil.move(bak_filepath, filepath)

    def process_file_headers(self, gen_dir, gen_bak_dir):
        for subdir, _, files in os.walk(gen_dir):
            for file in files:
                filepath = os.path.join(subdir, file)
                bak_filepath = os.path.join(gen_bak_dir, os.path.relpath(filepath, gen_dir))
                if os.path.exists(bak_filepath):
                    self.process_file_header(filepath, bak_filepath)

        # 可能包含手写代码的文件需要保留
        whitelist = ['entry.lua', 'signal_listen.lua', 'factory.lua']
        for item in whitelist:
            old_filepath = os.path.join(gen_bak_dir, self.project_name, item)
            new_filepath = os.path.join(gen_dir, self.project_name, item)
            if os.path.exists(old_filepath):
                shutil.copy(old_filepath, new_filepath)

    def generate_code_run(self, args):
        shutil.rmtree(self.gen_tool_dir, ignore_errors=True)
        shutil.copytree(cwd, self.gen_tool_dir)
        self.setup_mdb_interface()
        self.setup_latest_mdb_interface()
        lua_format = self.get_lua_format()
        cmd = [
            "/usr/bin/make", "-j12", f"PROJECT_NAME={self.project_name}", f"TPL_DIR={self.gen_tool_dir}",
            f"VERSION={self.version}", f"MAJOR_VERSION={self.major_version}", "gen"
        ]
        subprocess.run(cmd, env=dict(os.environ, LUA_FORMAT=lua_format, LUA_CODEGEN_VERSION=str(self.version),
                                     MAJOR_VERSION=str(self.major_version),
                                     PROJECT_NAME=self.project_name), check=True)
        if args.with_template:
            script_path = os.path.join(cwd, 'script', 'gen_entry.py')
            mako_dir = os.path.join(cwd, 'templates', 'apps')
            model_path = os.path.join(self.gen_tool_dir, self.project_name, '_model.json')
            ipmi_path = os.path.join(self.project_dir, 'mds', 'ipmi.json')
            subprocess.run(["/usr/bin/python3", script_path, "-i", ipmi_path, "-m", model_path, "-o", self.project_dir,
            "-n", self.project_name, "-f", lua_format, "-t", mako_dir, "-v", self.version, "-p", self.major_version],
            check=True)

    def gen(self, args):
        check_cmd_file = os.path.join(self.project_dir, 'temp/lua_codegen/temp/check_cmd.json')
        if os.path.exists(check_cmd_file):
            os.remove(check_cmd_file)

        gen_dir = os.path.join(self.project_dir, 'gen')
        gen_bak_dir = os.path.join(self.project_dir, 'gen_bak')
        if os.path.exists(gen_dir) and not os.path.exists(gen_bak_dir):
            shutil.move(gen_dir, gen_bak_dir)
        self.generate_code_run(args)

        if os.path.exists(gen_bak_dir):
            self.process_file_headers(gen_dir, gen_bak_dir)
            shutil.rmtree(gen_bak_dir)
