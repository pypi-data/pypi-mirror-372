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
import os
import shutil
import stat
import yaml

from mako.lookup import TemplateLookup

from bmcgo.component.package_info import InfoComp
from bmcgo.component.component_helper import ComponentHelper
from bmcgo.codegen.c.helper import Helper
from bmcgo.logger import Logger
from bmcgo.bmcgo_config import BmcgoConfig
from bmcgo import misc

log = Logger("deploy")

cwd_script = os.path.split(os.path.realpath(__file__))[0]


class DeployComp():
    def __init__(self, bconfig: BmcgoConfig, info: InfoComp = None):
        self.info: InfoComp = info
        self.bconfig = bconfig
        self.folder = bconfig.component.folder
        os.chdir(self.folder)
        self.temp_path = os.path.join(self.folder, "temp")

    def get_dt_dependencies(self):
        user_channel = ComponentHelper.get_user_channel(self.info.stage)
        # DT专用的依赖，只在部署时添加
        dependencies = []
        with open(self.bconfig.conf_path, "r") as fp:
            config = yaml.safe_load(fp)
        dt_dependencies = config.get("dt_dependencies", {})
        lua_run_deps = [dt_dependencies.get("luaunit")]
        # 只有lua需要添加依赖
        if not os.path.isdir("test_package") and self.info.coverage:
            lua_run_deps.append(dt_dependencies.get("luacov"))
            lua_run_deps.append(dt_dependencies.get("luafilesystem"))
        for dep in lua_run_deps:
            for build_dep in self.info.build_dependencies:
                if build_dep.startswith(dep.split("/", -1)[0]):
                    dep = build_dep
                    break
            if "@" not in dep:
                dep += user_channel
            dependencies.append(dep)
        
        dependencies += self.info.test_dependencies
        return dependencies

    def gen_conanfile(self):
        dependencies = [f"{self.info.name}/{self.info.version}{self.info.channel}"]
        if self.info.build_type == "dt":
            dependencies += self.get_dt_dependencies()

        # 构建虚拟deploy组件，生成conanfile.py文件
        lookup = TemplateLookup(directories=os.path.join(cwd_script, "template"))
        template = lookup.get_template("conanfile.deploy.py.mako")
        conanfile = template.render(lookup=lookup, pkg=self.info, dependencies=dependencies)
        file_handler = os.fdopen(os.open("conanfile.py", os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                         stat.S_IWUSR | stat.S_IRUSR), 'w')
        file_handler.write(conanfile)
        file_handler.close()

    def run(self):
        # 生成虚拟deploy组件，仅用于安装
        deploy_conan = os.path.join(self.temp_path, ".deploy")
        os.makedirs(deploy_conan, exist_ok=True)
        os.chdir(deploy_conan)
        self.gen_conanfile()

        # 安装依赖制品到install目录
        install_path = os.path.join(self.temp_path, ".deploy", ".install")
        log.info("安装所有依赖到目录 %s", install_path)
        shutil.rmtree(install_path, ignore_errors=True)
        cmd = [misc.CONAN, "install"]
        append_cmd = ("%s -if=%s -g deploy" % (self.info.cmd_base, install_path))
        append_cmd = append_cmd.replace(self.info.package, self.info.channel)
        cmd += append_cmd.split()
        cmd.append("--build=missing")
        log.success("运行部署命令: %s", " ".join(cmd))
        Helper.run(cmd)
        # 复制制品到rootfs目录
        rootfs_path = self.temp_path
        log.info("复制所有依赖到目录 %s", rootfs_path)
        os.makedirs(rootfs_path, exist_ok=True)
        for sub_dir in os.listdir(install_path):
            dir_path = os.path.join(install_path, sub_dir)
            if os.path.isfile(dir_path):
                os.unlink(dir_path)
                continue
            for file in os.listdir(dir_path):
                source = os.path.join(dir_path, file)
                cmd = ["/usr/bin/cp", "-arf", source, rootfs_path]
                Helper.run(cmd)
        shutil.rmtree(install_path, ignore_errors=True)
