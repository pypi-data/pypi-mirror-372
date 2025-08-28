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
import json
import os
import re
import stat
from bmcgo.codegen.c.codegen import CodeGen as CodeGenC
from bmcgo.codegen.lua.codegen import CodeGen as CodeGenLua
from bmcgo.ipmigen.ipmigen import IpmiGen
from bmcgo.component.package_info import InfoComp
from bmcgo.codegen import __version__ as codegen_version
from bmcgo.logger import Logger
from bmcgo import misc
from bmcgo.component.component_helper import ComponentHelper

log = Logger("gen")

cwd = os.getcwd()
cwd_script = os.path.split(os.path.realpath(__file__))[0]


class ParameterError(OSError):
    """参数错误"""


class SmartFormatter(argparse.HelpFormatter):
    def _fill_text(self, text, width, indent):
        import textwrap
        text = textwrap.dedent(text)
        return ''.join(indent + line for line in text.splitlines(True))


class GenComp():
    def __init__(self, args):
        self.args = args

    @staticmethod
    def update_conanbase(gen_version: int):
        conanbase_path = os.path.join(cwd, "conanbase.py")
        if not os.path.isfile(conanbase_path):
            return
        conanbase_file = os.fdopen(os.open(conanbase_path, os.O_RDWR, stat.S_IWUSR | stat.S_IRUSR), 'w+')
        content = conanbase_file.read()
        content = re.sub(r"_codegen_version *= *\S+", f"_codegen_version = {gen_version}", content)
        conanbase_file.seek(0)
        conanbase_file.truncate()
        conanbase_file.write(content)
        conanbase_file.close()

    @staticmethod
    def get_codegen_version(args, base_version: int):
        if base_version != -1:
            return base_version
        if args.version != -1:
            return int(args.version)
        if not os.path.isfile(args.service_file):
            return codegen_version
        file_handler = open(args.service_file, "r")
        service = json.load(file_handler)
        file_handler.close()
        _, version = InfoComp.get_codegen_policy(service)
        return version

    @staticmethod
    def _gen_service(service_file, gen_version):
        """
        代码自动生成.

        支持自动生成服务端和客户端C代码
        """
        file_handler = open(service_file, "r")
        service = json.load(file_handler)
        file_handler.close()
        # 如果默认版本号为-1则使用service.json读取的版本号

        codegen = CodeGenC(gen_version)
        ipmigen = IpmiGen(gen_version)
        codegen.gen_mds(service_file)
        configs = service.get("codegen", [])
        for cfg in configs:
            file = cfg.get("file")
            if file is None:
                raise OSError("自动代码生成配置不正确, 缺少file元素指定描述文件")
            if not os.path.isfile(file):
                raise OSError(f"自动代码生成配置不正确, {file}不是一个文件")
            tpye = cfg.get("type", "interface_xml")
            output = cfg.get("output", ".")
            if tpye == "interface_xml":
                if not file.endswith(".xml"):
                    raise OSError(f"接口自动代码生成配置不正确, {file}的文件名不是以.xml结束")
                codegen.gen(file, output)
            elif tpye == "ipmi":
                if not file.endswith(".json"):
                    raise OSError(f"IPMI自动代码生成配置不正确, {file}的文件名不是以.json结束")
                ipmigen.gen(file, output)

    def run(self, base_version=-1):
        language = ComponentHelper.get_language().lower()
        parser = argparse.ArgumentParser(description="代码自动生成.",
                                         prog="bingo gen/当前只支持C和lua语言代码生成",
                                         formatter_class=SmartFormatter)
        parser.add_argument("-v", "--version", help="use specified version", type=int, default=-1)
        parser.add_argument("-r", "--remote", help="conan remote, 如不设置则默认读取本地conan配置")

        if language == "c":
            self.generate_c_run(parser, base_version)
        elif language == "lua":
            self.generate_lua_run(parser, base_version)

    def generate_lua_run(self, parser: argparse.ArgumentParser, base_version):
        parser.add_argument("-s", "--service_file", help='Service file')
        parser.add_argument("-w", "--with_template", help="generate with template", action=misc.STORE_TRUE)
        args, _ = parser.parse_known_args(self.args)

        if args.service_file is not None and not os.path.isfile(args.service_file):
            raise FileNotFoundError(f"配置文件{args.service_file}不存在")
        gen_version = self.get_codegen_version(args, base_version)
        self.update_conanbase(gen_version)
        codegen = CodeGenLua(cwd, gen_version, remote=args.remote)
        codegen.gen(args)

    def generate_c_run(self, parser: argparse.ArgumentParser, base_version):
        group1 = parser.add_mutually_exclusive_group()
        group1.add_argument("-s", "--service_file", help='Service file')
        group1.add_argument("-i", "--interface", help='interface name, e.g.: com.kepler.upgrade')
        group2 = parser.add_mutually_exclusive_group()
        group2.add_argument("-d", "--directory", help='generate code directory', default=".")
        parser.add_argument("-f", "--force", help='ignore the version configuration in the service.json file.',
                            action=misc.STORE_TRUE)

        args, _ = parser.parse_known_args(self.args)
        gen_version = self.get_codegen_version(args, base_version)
        self.update_conanbase(gen_version)
        if args.service_file is not None:
            if not os.path.isfile(args.service_file):
                raise FileNotFoundError(f"配置文件{args.service_file}不存在")
            self._gen_service(args.service_file, gen_version)
            return 0
        if args.interface is None:
            raise ParameterError("需要指定-s或-i参数")
        xml_file = None
        file = args.interface
        if file.endswith("ipmi.json"):
            ipmigen = IpmiGen(gen_version)
            ipmigen.gen(file, args.directory)
            return 0
        if file.endswith(".xml") and os.path.isfile(file):
            xml_file = file
        else:
            file += ".xml"
            if os.path.isfile(file):
                xml_file = file
        if not xml_file:
            raise FileNotFoundError(f"接口 {args.interface} 不存在")
        if not os.path.isdir(args.directory):
            raise NotADirectoryError(f"文件夹 {args.directory} 不存在")
        codegen = CodeGenC(gen_version)
        codegen.gen(xml_file, args.directory)
        return 0