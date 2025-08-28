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
from xml.dom import Node
import inflection
from bmcgo.codegen.c.property import Property
from bmcgo.codegen.c.method import Method
from bmcgo.codegen.c.signal import Signal
from bmcgo.codegen.c.comment import Comment
from bmcgo.codegen.c.annotation import Annotation
from bmcgo.codegen.c.helper import Helper
from bmcgo.logger import Logger

log = Logger("c_interface")


class Interface():
    def __init__(self, node: Node, comment: Comment, version):
        super().__init__()
        prefix = ""
        self.node = node
        self.name = Helper.get_node_value(node, "name")
        self.class_name = "_".join(self.name.split("."))
        self.version = version
        self.properties: list[Property] = []
        self.annotations: list[Annotation] = []
        self.methods: list[Method] = []
        self.signals: list[Signal] = []
        self.comment = comment or Comment()
        self.privilege = "0"
        log.debug("接口: %s, 版本: %s" % (self.name, version))
        if len(comment.texts) > 0:
            log.debug("%s 注释: %s" % (prefix, comment.texts))
        comment = Comment()
        for child in node.childNodes:
            if child.nodeType == Node.COMMENT_NODE:
                comment.append(child)
            if child.nodeType == Node.ELEMENT_NODE:
                if child.nodeName == "property":
                    prop = Property(self, child, comment, prefix)
                    self.properties.append(prop)
                elif child.nodeName == "annotation":
                    self.annotations.append(Annotation(child, comment, prefix))
                elif child.nodeName == "method":
                    self.methods.append(Method(self, child, comment, prefix))
                elif child.nodeName == "signal":
                    self.signals.append(Signal(self, child, comment, prefix))
                comment = Comment()

        for annotation in self.annotations:
            if annotation.name == "bmc.kepler.Interface.Alias":
                self.class_name = annotation.value
            elif annotation.name == "bmc.kepler.annotition.Privileges":
                self.privilege = Helper.get_privilege(annotation.value)
        self.upper_name = inflection.underscore(self.class_name).upper()