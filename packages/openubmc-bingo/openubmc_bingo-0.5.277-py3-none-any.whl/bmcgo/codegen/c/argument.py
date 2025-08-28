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
from bmcgo.codegen.c.ctype_defination import CTypes
from bmcgo.codegen.c.helper import Helper
from bmcgo.logger import Logger

log = Logger("c_argument")



class Argument():
    def __init__(self, node: Node, comment: Comment, prefix: str = ""):
        self.node = node
        prefix = prefix + "    "
        self.comment = comment or Comment()
        self.name = Helper.get_node_value(node, "name", "")
        self.direction = Helper.get_node_value(node, "direction", "in")
        self.signature = Helper.get_node_value(node, "type")
        if self.signature is None:
            log.error("参数缺少 'type' 属性")
        self.ctype = CTypes.types.get(self.signature, CTypes.types.get("*"))
        if self.ctype is None:
            log.error("未知的 C 类型: %s", self.signature)
        if self.direction != "in" and self.direction != "out":
            log.error("无效的方向参数: '%s', 其值必须为 [in out], 获取到 %s" % {self.name, self.direction})
        log.debug("%s 参数, 名称: %33s 签名: %4s 方向: %s" % (
            prefix, self.name + ",", self.signature + ",", self.direction))

    def set_arg_id(self, arg_id: int):
        if not self.name:
            self.name = "arg_" + str(arg_id)
