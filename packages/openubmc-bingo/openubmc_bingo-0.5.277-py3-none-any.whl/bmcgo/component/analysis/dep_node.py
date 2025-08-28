#!/usr/bin/env python
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

import json
import os
import sys

from typing import List, Set
from bmcgo.logger import Logger

global log
log = Logger()

TABLE_CONFLICT_WHITE_LIST = {"nsm": "t_snmp_config", "event_policy": "t_snmp_config"}


class DepNode():
    ref: str
    options: str
    package_id: str
    revision: str

    def __init__(self, node: dict, index):
        self.ref = node.get("ref")
        self.options = node.get("options")
        self.package_id = node.get("package_id", "")
        self.revision = node.get("revision")
        self.requires: List[DepNode] = []
        self.name = self.ref.split("@", 1)[0]
        self.package_name = self.name.split("/", 1)[0]
        self.package_version = self.name.split("/", 1)[-1]
        self.index = int(index)
        self.model_path = "unknown"
        self.subsys_name = "unknown"
        self.subsys_level = 1000
        self.package_type = []      # 可选library, app, tool, configuration, command
        self.intf_impl: Set[str] = set()
        self.intf_deps: Set[str] = set()
        self.local_tables = {}
        self.remote_tables = {}
        self.table_conflict = False
        self._parse_mds()

    @staticmethod
    def _get_class_properties(class_data):
        properties = set()
        for _, intf_data in class_data.get("interfaces", {}).items():
            for prop, prop_data in intf_data.get("properties", {}).items():
                properties.add(prop_data.get("alias", prop))
        for prop, prop_data in class_data.get("properties", {}).items():
            properties.add(prop_data.get("alias", prop))
        return properties

    def set_subsys(self, subsys_name, subsys_level):
        self.subsys_name = subsys_name
        self.subsys_level = subsys_level

    def set_package_type(self, package_type):
        if package_type not in ["Library", "App", "Tool", "Configuration", "Command"]:
            raise Exception("包类型错误")
        self.package_type.append(package_type)

    def _collect_table_info(self, class_data):
        if "tableName" not in class_data:
            return

        table_name = class_data["tableName"]
        if class_data.get("tableLocation", "") == "Local":
            if table_name in self.local_tables:
                log.error("%s中本地持久化表名冲突: %s", self.package_name, table_name)
                self.table_conflict = True
            self.local_tables[table_name] = True
        else:
            if table_name in self.remote_tables:
                log.error("%s中远程持久化表名冲突: %s", self.package_name, table_name)
                self.table_conflict = True
            if self.package_name in TABLE_CONFLICT_WHITE_LIST \
                and table_name == TABLE_CONFLICT_WHITE_LIST[self.package_name]:
                self.remote_tables[table_name] = DepNode._get_class_properties(class_data)
            else:
                self.remote_tables[table_name] = True

    def _parse_mds(self):
        pkg_dir = self.ref.split("#")[0].replace("@", "/")
        package_source = os.path.join(os.environ["HOME"], ".conan/data", pkg_dir, "package", self.package_id)
        mds_path = os.path.join(package_source, "include/mds")
        self.model_path = os.path.join(mds_path, "model.json")
        if os.path.exists(self.model_path):
            with open(self.model_path, "r") as file_descriptor:
                model_data = json.load(file_descriptor)
            for class_name in model_data:
                self._collect_table_info(model_data[class_name])
                for intf in model_data[class_name].get("interfaces", {}):
                    self.intf_impl.add(intf)
        service_path = os.path.join(mds_path, "service.json")
        if os.path.exists(service_path):
            with open(service_path, "r") as file_descriptor:
                service_data = json.load(file_descriptor)
            for intf_entry in service_data.get("required", []):
                if "interface" in intf_entry:
                    self.intf_deps.add(intf_entry.get("interface"))
