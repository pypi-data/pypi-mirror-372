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
from bmcgo.codegen.c.annotation import Annotation
from bmcgo.codegen.c.argument import Argument
from bmcgo.codegen.c.comment import Comment
from bmcgo.codegen.c.helper import Helper
from bmcgo.logger import Logger

log = Logger("c_signal")


class Signal():
    def __init__(self, interface, node: Node, comment: Comment, prefix: str = ""):
        prefix = prefix + "    "
        self.name = Helper.get_node_value(node, "name", "")
        if self.name is None:
            log.error("方法缺少 'name' 属性")
        self.args: list[Argument] = []
        self.annotations: list[Annotation] = []
        self.deprecated = False
        self.interface = interface
        self.comment = comment or Comment()
        self.deprecated_str = ""
        log.debug("%s 信号名: %33s" % (prefix, self.name))
        if len(comment.texts) > 0:
            log.debug("%s 注释: %s" % (prefix, comment.texts))
        comment = Comment()
        for child in node.childNodes:
            if child.nodeType == Node.COMMENT_NODE:
                comment.append(child)
            elif child.nodeType == Node.ELEMENT_NODE:
                if child.nodeName == "annotation":
                    self.annotations.append(Annotation(child, comment, prefix))
                elif child.nodeName == "arg":
                    self.args.append(Argument(child, comment, prefix))
                comment = Comment()

        arg_id = 0
        for arg in self.args:
            arg.set_arg_id(arg_id)
            arg_id += 1

        # 是否已被弃用
        for annotation in self.annotations:
            if annotation.deprecated:
                self.deprecated = True
                self.deprecated_str = " __attribute__((__deprecated__(\"%s\"))) " % annotation.deprecated

    def msg_signature(self):
        signature = "("
        for arg in self.args:
            signature = signature + arg.signature
        signature = signature + ")"
        return signature