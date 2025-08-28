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
import hashlib
import json
import os
import subprocess
import stat
from xml.dom import minidom, Node
import yaml
import semver
from mako.lookup import TemplateLookup
from bmcgo.codegen.c.interface import Interface
from bmcgo.codegen.c.comment import Comment
from bmcgo.codegen.c.renderer import Renderer
from bmcgo.logger import Logger
cwd = os.path.split(os.path.realpath(__file__))[0]

global log
log = Logger()

PKG_PUBLIC = "public"
PKG_SERVER = "server"
PKG_CLIENT = "client"


class XmlInterfaces(Renderer):
    def __init__(self, lookup, xml_file, base_version):
        super(Renderer, self).__init__()
        self.base_version = base_version
        self.version = "0.0.1"
        self.name = os.path.basename(xml_file)[:-4]
        self.lookup = lookup
        self.introspect_xml_sha256 = None       # 自举文件的sha256值
        file_handler = open(xml_file)
        self.dom = minidom.parse(file_handler)
        file_handler.close()
        self.interfaces: list[Interface] = []
        for subnode in self.dom.childNodes:
            if subnode.nodeType == Node.DOCUMENT_TYPE_NODE:
                continue
            if subnode.nodeType == Node.ELEMENT_NODE:
                self._parse_subnode(subnode)

    def render_xml(self, template, out_file):
        file_handler = os.fdopen(os.open(out_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                         stat.S_IWUSR | stat.S_IRUSR), 'w')
        out = self.render(self.lookup, template, interfaces=self.interfaces, version=self.base_version)
        hash_val = hashlib.sha256()
        hash_val.update(out.encode('utf-8'))
        self.introspect_xml_sha256 = hash_val.hexdigest()
        log.info("The sha256sum of interface %s is %s", out_file, self.introspect_xml_sha256)
        file_handler.write(out)
        file_handler.close()

    def render_c_language(self, template, out_file):
        file_handler = os.fdopen(os.open(out_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                         stat.S_IWUSR | stat.S_IRUSR), 'w')
        out = self.render(self.lookup, template, xml=self, version=self.base_version)
        file_handler.write(out)
        file_handler.close()

    def _parse_subnode(self, subnode):
        remove_node = []
        comment = Comment()
        for child in subnode.childNodes:
            if child.nodeType == Node.COMMENT_NODE:
                comment.append(child)
            elif child.nodeType != Node.ELEMENT_NODE:
                continue
            if child.nodeName == "version":
                self.version = str(child.firstChild.nodeValue)
                ver = semver.parse(self.version, False)
                if ver is None:
                    raise Exception("Interface has version error, abort")
                for com in comment.nodes:
                    subnode.removeChild(com)
                remove_node.append(child)
            elif child.nodeName == "interface":
                intf = Interface(child, comment, self.version)
                self.interfaces.append(intf)
            comment = Comment()
        for node in remove_node:
            subnode.removeChild(node)


class CodeGen(object):
    def __init__(self, base_version):
        self.base_version = base_version

    def format(self, out_file):
        try:
            subprocess.run(["/usr/bin/clang-format", "--version"], stderr=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL)
        except Exception:
            log.error("Command clang-format not found, skip format %s/%s", os.getcwd(), out_file)
            return
        if not os.path.isfile(".clang-format"):
            log.error("the style file .clang-format is missing, skip format %s/%s", os.getcwd(), out_file)
            return
        subprocess.run(["/usr/bin/clang-format", "--style=file", "-i", out_file])

    def gen(self, xml_file, directory="."):
        os.makedirs(os.path.join(directory, PKG_PUBLIC), exist_ok=True)
        os.makedirs(os.path.join(directory, PKG_SERVER), exist_ok=True)
        os.makedirs(os.path.join(directory, PKG_CLIENT), exist_ok=True)
        lookup = TemplateLookup(directories=os.path.join(cwd, "template"))
        interfaces = XmlInterfaces(lookup, xml_file, self.base_version)
        out_file = os.path.join(directory, PKG_PUBLIC, os.path.basename(xml_file))
        interfaces.render_xml("interface.introspect.xml.mako", out_file)
        for code_type in [PKG_SERVER, PKG_CLIENT, PKG_PUBLIC]:
            out_file = os.path.join(directory, code_type, interfaces.name + ".h")
            interfaces.render_c_language(code_type + ".h.mako", out_file)
            self.format(out_file)
            out_file = os.path.join(directory, code_type, interfaces.name + ".c")
            interfaces.render_c_language(code_type + ".c.mako", out_file)
            self.format(out_file)
        json_file = os.path.join(directory, "package.yml")
        data = {
            "version": interfaces.version,
            "name": interfaces.name
        }
        with os.fdopen(os.open(json_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as file_handler:
            yaml.dump(data, file_handler, encoding='utf-8', allow_unicode=True)
        log.success("Generate code successfully, interface: %s", xml_file)

    def gen_mds(self, mds):
        file_handler = open(mds, "r")
        mds = json.load(file_handler)
        service_type = mds.get("type", [])
        if "application" not in service_type:
            return
        file_handler.close()
        service_name = mds.get("name", "")
        if service_name in ["ssdp", "libproto-mc4c", "file_transfer"]:
            return
        lookup = TemplateLookup(directories=os.path.join(cwd, "template"))
        template = lookup.get_template("micro_component.c.mako")
        out = template.render(lookup=lookup, mds=mds, version=self.base_version)
        os.makedirs("service", exist_ok=True)
        file_handler = os.fdopen(os.open("service/micro_component.c", os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                         stat.S_IWUSR | stat.S_IRUSR), 'w')
        file_handler.write(out)
        file_handler.close()
