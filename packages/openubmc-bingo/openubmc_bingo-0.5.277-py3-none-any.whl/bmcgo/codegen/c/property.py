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
from bmcgo.codegen.c.annotation import Annotation, AnnotationBase
from bmcgo.codegen.c.comment import Comment
from bmcgo.codegen.c.ctype_defination import CTypeBase, CTypes
from bmcgo.codegen.c.helper import Helper
from bmcgo.logger import Logger

log = Logger("c_property")


class MdsFormatError(OSError):
    """测试失败"""


class Property():
    def __init__(self, interface, node: Node, comment, prefix: str = ""):
        prefix = prefix + "    "
        self.interface = interface
        self.node = node
        self.comment = comment or Comment()
        self.name = Helper.get_node_value(node, "name")
        self.read_privilege = "0"
        self.write_privilege = "0"
        if self.name == "_base" or self.name == "__reserved__":
            raise MdsFormatError("格式错误, 属性 _base 被保留")
        self.signature = Helper.get_node_value(node, "type")
        self.ctype: CTypeBase = CTypes.types.get(self.signature, CTypes.types.get("*"))
        self.access = Helper.get_node_value(node, "access", "")
        if self.access not in ["readwrite", "read", "write", ""]:
            log.error("不支持的属性访问类型: " + self.access)
        log.debug("%s 属性, 名字: %s, 类型: %s, 访问: %s" % (
            prefix, self.name, self.signature, self.access))
        if len(comment.texts) > 0:
            log.debug("%s 注释: %s" % (prefix, comment.texts))
        self.annotations: list[Annotation] = []
        comment = Comment()
        for child in node.childNodes:
            if child.nodeType == Node.COMMENT_NODE:
                comment.append(child)
            elif child.nodeType == Node.ELEMENT_NODE:
                if child.nodeName == "annotation":
                    self.annotations.append(Annotation(child, comment, prefix))
                comment = Comment()

        # 是否已被弃用
        self.deprecated = False
        self.deprecated_str = ""
        # 是否是私有数据
        self.private = False
        # 是否发送信号
        self.emit_changed_signal = "true"
        # 是否是引用对象
        self.ref_object = False;
        # 是否是主键
        self.primary_key = False;
        # Reset_per持久化
        self.reset_per = False;
        # PoweroffPer持久化
        self.poweroff_per = False;
        # 永久持久化
        self.permanent_per = False;
        self.__annotations_proc()
        ### 如果是对象引用属性，则必须是私有属性
        if self.ref_object and not self.private:
            self.annotations.append(AnnotationBase("bmc.kepler.annotition.Property.Private", "true"))
            self.private = True
        self.__proc_flags()

    @property
    def default_value(self):
        for annotation in self.annotations:
            if annotation.name == "bmc.kepler.annotition.Property.Default":
                return annotation.value;
        return ""

    # 输出类结构体成员定义，　如"guint32 id"
    def struct_member(self):
        render_str = self.ctype.render_in_args(self.name, False).replace("const gchar *", "gchar *")
        splits = render_str.split(",", -1)
        out = ";".join(splits) + self.deprecated_str + ";"
        return out

    # 定义服务端属性值写函数参数
    def server_in_args_str(self):
        return self.ctype.render_in_args("value", True)

    # 定义客户端属性值写参数原型
    def client_in_args_str(self):
        return self.ctype.render_in_args(self.name, True)

    def get_flags(self):
        if self.access == "readwrite":
            return "G_DBUS_PROPERTY_INFO_FLAGS_WRITABLE | G_DBUS_PROPERTY_INFO_FLAGS_READABLE"
        elif self.access == "write":
            return "G_DBUS_PROPERTY_INFO_FLAGS_WRITABLE"
        elif self.access == "read":
            return "G_DBUS_PROPERTY_INFO_FLAGS_READABLE"
        else:
            return "G_DBUS_PROPERTY_INFO_FLAGS_NONE"

    def __annotations_proc(self):
        for annotation in self.annotations:
            if annotation.deprecated:
                self.deprecated = True
                self.deprecated_str = " __attribute__((__deprecated__(\"%s\"))) " % annotation.deprecated
            elif annotation.is_private():
                self.private = True
            elif annotation.is_emit_changed_signal():
                self.emit_changed_signal = annotation.value
            elif annotation.name == "bmc.kepler.annotition.Privileges.Read":
                self.read_privilege = Helper.get_privilege(annotation.value)
            elif annotation.name == "bmc.kepler.annotition.Privileges.Write":
                self.write_privilege = Helper.get_privilege(annotation.value)
            elif annotation.name == "bmc.kepler.annotition.RefObject":
                self.ref_object = Helper.string_to_bool(annotation.value)
            elif annotation.name == "bmc.kepler.annotition.PrimaryKey":
                self.primary_key = Helper.string_to_bool(annotation.value)
            elif annotation.name == "bmc.kepler.annotition.ResetPer":
                self.reset_per = Helper.string_to_bool(annotation.value)
            elif annotation.name == "bmc.kepler.annotition.PoweroffPer":
                self.poweroff_per = Helper.string_to_bool(annotation.value)
            elif annotation.name == "bmc.kepler.annotition.PermanentPer":
                self.permanent_per = Helper.string_to_bool(annotation.value)

    def __proc_flags(self):
        flags = []
        if self.private:
            flags.append("MDB_FLAGS_PROPERTY_PRIVATE")
        elif self.emit_changed_signal == "const":
            flags.append("MDB_FLAGS_PROPERTY_EMIT_CONST")
        elif self.emit_changed_signal == "true":
            flags.append("MDB_FLAGS_PROPERTY_EMIT_TRUE")
        elif self.emit_changed_signal == "false":
            flags.append("MDB_FLAGS_PROPERTY_EMIT_FALSE")
        elif self.emit_changed_signal == "invalidates":
            flags.append("MDB_FLAGS_PROPERTY_EMIT_INVALIDATES")
        if self.deprecated:
            flags.append("MDB_FLAGS_PROPERTY_DEPRECATED")
        if self.ref_object:
            flags.append("MDB_FLAGS_PROPERTY_REFOBJECT")
        if self.primary_key:
            flags.append("MDB_FLAGS_PROPERTY_PRIMARY_KEY")
            if self.reset_per or self.poweroff_per or self.permanent_per:
                raise MdsFormatError("持久化属性不能是主键")
        if self.reset_per:
            flags.append("MDB_FLAGS_PROPERTY_RESET_PER")
        if self.poweroff_per:
            flags.append("MDB_FLAGS_PROPERTY_POWEROFF_PER")
        if self.permanent_per:
            flags.append("MDB_FLAGS_PROPERTY_PERMANENT_PER")
        # 重置为v
        if self.signature == "*":
            flags.append("MDB_FLAGS_PROPERTY_ANY")
            self.signature = "v"
        if len(flags) == 0:
            self.desc_flags = "0"
        else:
            self.desc_flags = " | ".join(flags)
        self._access_proc()

    def _access_proc(self):
        if self.access == "readwrite":
            self.access_flags = "G_DBUS_PROPERTY_INFO_FLAGS_WRITABLE | G_DBUS_PROPERTY_INFO_FLAGS_READABLE"
        elif self.access == "write":
            self.access_flags = "G_DBUS_PROPERTY_INFO_FLAGS_WRITABLE"
        elif self.access == "read":
            self.access_flags = "G_DBUS_PROPERTY_INFO_FLAGS_READABLE"
        else:
            self.access_flags = "G_DBUS_PROPERTY_INFO_FLAGS_NONE"
