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
import subprocess
import sys
import os
from xml.dom import minidom, Node
from colorama import Fore, Style
from bmcgo.logger import Logger

global log
log = Logger()


class Helper():
    @staticmethod
    def get_node_value(dom: Node, name, default=None):
        node: minidom.Attr = dom.attributes.get(name)
        if node is None:
            if default is None:
                raise Exception("节点分析失败, 终止构建")
            return default
        return node.childNodes[0].nodeValue.strip()

    @staticmethod
    def get_git_path():
        if os.path.isfile("/usr/bin/git"):
            return "/usr/bin/git"
        elif os.path.isfile("/usr/local/bin/git"):
            return "/usr/local/bin/git"
        elif os.path.isfile("/usr/sbin/git"):
            return "/usr/sbin/git"
        else:
            raise OSError("git 命令未找到, 请检查 git 是否安装或是否安装到系统路径")

    @staticmethod
    def get_privilege(value):
        splits = value.split(",", -1)
        privilege = []
        for split in splits:
            split = split.strip()
            if split == "UserMgmt":
                privilege.append("PRI_USER_MGMT")
            elif split == "BasicSetting":
                privilege.append("PRI_BASIC_SETTING")
            elif split == "KVMMgmt":
                privilege.append("PRI_KVM_MGMT")
            elif split == "VMMMgmt":
                privilege.append("PRI_VMM_MGMT")
            elif split == "SecurityMgmt":
                privilege.append("PRI_SECURITY_MGMT")
            elif split == "PowerMgmt":
                privilege.append("PRI_POWER_MGMT")
            elif split == "DiagnoseMgmt":
                privilege.append("PRI_DIAGNOSE_MGMT")
            elif split == "ReadOnly":
                privilege.append("PRI_READ_ONLY")
            elif split == "ConfigureSelf":
                privilege.append("PRI_CONFIG_SELF")
        if len(privilege) == 0:
            return "0"
        return " | ".join(privilege)

    @staticmethod
    def run(cmd, check=True, stderr=sys.stderr, stdout=sys.stdout):
        log.info("开始运行命令: %s %s %s", Fore.GREEN,
                     " ".join(cmd), Style.RESET_ALL)
        ret = subprocess.run(cmd, check=check, stderr=stderr, stdout=stdout)
        return ret.returncode

    @staticmethod
    def string_to_bool(str_value):
        if str_value.lower() == "false":
            return False
        if str_value == "":
            return False
        if str_value == "0":
            return False
        return True
