#!/usr/bin/env python3
# encoding=utf-8
# 描述：创建组件
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
import sys
import select
import argparse
import shutil
import subprocess
from bmcgo.bmcgo_config import BmcgoConfig
from bmcgo.utils.tools import Tools
from bmcgo import misc

tools = Tools("new")
log = tools.log
cwd = os.getcwd()

command_info: misc.CommandInfo = misc.CommandInfo(
    group="Misc commands",
    name="new",
    description=["创建组件"],
    hidden=False
)


def if_available(bconfig: BmcgoConfig):
    return True


_LUA = "lua"
_APP = "application"
_DEFAULT = ""
# 必选项：选项缩写，选项，选项的中文说明
_REQUIRES = [["n", "name", "组件名"]]
# 可选项：选项缩写，选项，选项的中文说明，可选值，默认值
_OPTIONS = [["t", "type", "组件类型", ["application"], "application"], ["l", "language", "组件编程语言", ["lua"], "lua"]]
# 环境中存放bmcgo自动生成工具相对的目录，组件中存放bmcgo自动生成工具的临时相对目录，模板脚本的相对路径，模板的相对目录
_TEMPLATES = {
    _LUA : {
        _APP : ['codegen/lua', 'temp/lua_codegen', 'script/template.py', 'templates/new_app']
    }
}


class BmcgoCommand:
    def __init__(self, bconfig: BmcgoConfig, *args):
        self.bconfig = bconfig
        parser = argparse.ArgumentParser(prog="bingo new", description="创建组件", add_help=True,
                                         formatter_class=argparse.RawTextHelpFormatter)
        for item in _REQUIRES:
            parser.add_argument(f"-{item[0]}", f"--{item[1]}", help=f"指定{item[2]}", required=True)
        for item in _OPTIONS:
            parser.add_argument(f"-{item[0]}", f"--{item[1]}", help=f"指定{item[2]}, " +
                f"可选值: {', '.join(item[3])}\n默认: {item[4]}")

        parsed_args, _ = parser.parse_known_args(*args)
        self.name = parsed_args.name
        self.type = parsed_args.type
        self.language = parsed_args.language
        self.path = os.path.join(cwd, self.name)

    def run(self):
        if os.path.exists(self.path):
            log.error(f"当前目录下已存在{self.name}子目录, 无法创建{self.name}组件")
            return -1

        if not self._check_options():
            return -1

        self._ask_options()

        self._render()
        
        return 0

    def _check_options(self):
        for item in _OPTIONS:
            val = getattr(self, item[1])
            if not val:
                continue

            if val.lower() not in item[3]:
                log.error(f"无效的{item[2]}: {val}")
                return False

            setattr(self, item[1], val.lower())

        return True

    def _ask_options(self):
        for item in _OPTIONS:
            if not getattr(self, item[1]):
                self._ask_option(item)
    
    def _ask_option(self, item):
        option_str = ''
        index = 0
        while index < len(item[3]):
            if index != 0:
                option_str += ', '
            option_str += str(index + 1) + ": " + item[3][index]
            index += 1

        log.info(f"请指定{item[2]}后回车({option_str}), 不指定则使用默认值{item[4]}")
        while True:
            select_in, _, _ = select.select([sys.stdin], [], [], 10)
            c_item = sys.stdin.readline().strip().lower()
            if c_item == _DEFAULT:
                c_item = item[4]
            elif c_item.isdigit() and (int(c_item) >= 1 and int(c_item) <= len(item[3])):
                c_item = item[3][int(c_item) - 1]
            if select_in is None or c_item not in item[3]:
                log.error(f"不支持的{item[2]}选项, 请重新输入")
                continue
            
            setattr(self, item[1], c_item)
            break

    def _render(self):
        log.info(f"请稍等, 组件生成中...")
        template = _TEMPLATES[self.language][self.type]
        gen_tool_dir = os.path.join(self.name, template[1])
        shutil.rmtree(gen_tool_dir, ignore_errors=True)
        shutil.copytree(f"{os.path.dirname(__file__)}/../{template[0]}", gen_tool_dir)

        script_file = os.path.join(gen_tool_dir, template[2])
        template_dir = os.path.join(gen_tool_dir, template[3])

        for root, _, files in os.walk(template_dir):
            rel_dir = os.path.relpath(root, template_dir)
            out_dir = os.path.join(cwd, self.name, rel_dir)
            os.makedirs(out_dir, exist_ok=True)
            for file in files:
                template_path = os.path.join(root, file)
                out_file = file.replace("${project_name}", self.name)
                out_file = out_file[:(len(out_file)-5)]
                if file.endswith('.link'):
                    self._link(out_dir, template_path, out_file)
                    continue

                out_path = os.path.join(out_dir, out_file)
                cmd = [
                    "python3", script_file, "-n", self.name, "-t", template_path, "-o", out_path
                ]
                subprocess.run(cmd, env=dict(os.environ), check=True)
                cmd = ["chmod", '644', out_path]
                subprocess.run(cmd, env=dict(os.environ), check=True)
        log.success(f"组件已生成到{self.path}目录")

    def _link(self, out_dir, path, file_name):
        with open(path, "r") as fp:
            src_file = fp.read()
            src_file = src_file.replace("${project_name}", self.name)
            os.chdir(out_dir)
            cmd = ["ln", "-s", src_file, file_name]
            subprocess.run(cmd, env=dict(os.environ), check=True)
            os.chdir(cwd)