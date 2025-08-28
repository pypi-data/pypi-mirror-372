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
from bmcgo.codegen.c.comment import Comment
from bmcgo.codegen.c.helper import Helper
from bmcgo.logger import Logger

log = Logger("c_annotation")


class AnnotationBase():
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.comment = Comment()

    @property
    def deprecated(self):
        if self.name == "bmc.kepler.annotition.Deprecated":
            return False if (self.value.lower() == "false" or self.value.lower() == "0") else True
        else:
            return False

    def is_private(self):
        return self.name == "bmc.kepler.annotition.Property.Private" and self.value.lower() == "true"

    def is_emit_changed_signal(self):
        return self.name == "org.freedesktop.DBus.Property.EmitsChangedSignal"


class Annotation(AnnotationBase):
    def __init__(self, node: Node, comment, prefix: str = ""):
        prefix += "    "
        self.node = node
        name = Helper.get_node_value(node, "name")
        value = Helper.get_node_value(node, "value")
        super(Annotation, self).__init__(name, value)
        self.comment = comment or Comment()
        if self.name is None:
            log.error("注释缺少 'name' 属性")
        if self.value is None:
            log.error("注释 %s 缺少 'value' 属性" % ("self.name"))
        log.debug("%s 注释, 名字: %s, 值: %s" % (prefix, self.name, self.value))
