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

import json
import os

from bmcgo import misc
from bmcgo.component.analysis.build_deps import BuildDependenciesAnalysis
from bmcgo.component.analysis.dep_node import DepNode
from bmcgo.component.analysis.intf_deps import InterfaceDependenciesAnalysis
from bmcgo.component.analysis.data_deps import DataDependenciesAnalysis
from bmcgo.component.analysis.rule import SubSys, Rules
from bmcgo.logger import Logger

global log
log = Logger()

script_dir = os.path.split(os.path.realpath(__file__))[0]
TABLE_CONFLICT_WHITE_LIST = {
    "nsm": ["t_snmp_config", set(["Id", "Enabled"])],
    "event_policy": ["t_snmp_config", set(["Id", "Enabled"])]
}


class AnalysisComp():
    def __init__(self, board_name, artifact_dir, lock_file, custom_sr_dir):
        self.board_name = board_name
        self.artifact_dir = artifact_dir
        self.lock_file = lock_file
        self.custom_sr_dir = custom_sr_dir
        if not self.artifact_dir:
            self.artifact_dir = os.path.join(os.getcwd(), "..", "output/packet/inner")
        if not lock_file:
            self.lock_file = os.path.join(os.getcwd(), "..", "output/package.lock")
        self.nodes: list[DepNode] = []
        self.subsystems = {}
        self.rules: list[Rules] = []

    def read_rules(self):
        rule_file = os.path.join(script_dir, "dep-rules.json")
        if not os.path.isfile(rule_file):
            raise Exception(f"依赖规则文件 {rule_file} 不存在")
        with open(rule_file) as file_descriptor:
            rules = json.load(file_descriptor)
        data = rules.get("Subsystems", [])
        for sub in data:
            sys_data = data[sub]
            level = sys_data.get("Level", 0)
            subsys = SubSys(int(level))
            apps = sys_data.get("Apps", [])
            for app in apps:
                subsys.apps.append(app)
            libs = sys_data.get("Libraries", [])
            for lib in libs:
                subsys.libraries.append(lib)
            tools = sys_data.get("Tools", [])
            for tool in tools:
                subsys.tools.append(tool)
            configurations = sys_data.get("Configurations", [])
            for config in configurations:
                subsys.configurations.append(config)
            commands = sys_data.get("Commands", [])
            for cmd in commands:
                subsys.commands.append(cmd)
            self.subsystems[sub] = subsys
        self.rules.append(Rules(rules.get("Allowed", []), True))
        self.rules.append(Rules(rules.get("UnAllowed", []), False))

    def set_node_subsys(self, node: DepNode):
        for key, subsys in self.subsystems.items():
            if node.package_name in subsys.apps:
                node.set_subsys(key, subsys.level)
                node.set_package_type("App")
            if node.package_name in subsys.libraries:
                node.set_subsys(key, subsys.level)
                node.set_package_type("Library")
            if node.package_name in subsys.tools:
                node.set_subsys(key, subsys.level)
                node.set_package_type("Tool")
            if node.package_name in subsys.configurations:
                node.set_subsys(key, subsys.level)
                node.set_package_type("Configuration")
            if node.package_name in subsys.commands:
                node.set_subsys(key, subsys.level)
                node.set_package_type("Command")
        log.debug("app 名字: %s,类型: (%s), 子系统: %s", node.package_name, ", ".join(node.package_type),
                      node.subsys_name)

    def read_package_lock(self):
        if not os.path.isfile(self.lock_file):
            raise Exception(f"无法找到 {self.lock_file} 构建信息用于分析")
        with open(self.lock_file) as file_descriptor:
            lock = json.load(file_descriptor)
        requires: dict = {}
        packages = {}
        for i in range(0, 10000):
            node_data = lock.get("graph_lock", {}).get("nodes", {}).get(str(i), None)
            if not node_data:
                break
            node = DepNode(node_data, i)
            # busybox是调测包，当dev包引入时忽略架构治理分析（由schema模型看护）
            user_stage = f"{misc.ConanUserEnum.CONAN_USER_DEV.value}/{misc.StageEnum.STAGE_DEV.value}"
            if node.package_name == "busybox" and user_stage in node.ref:
                continue
            packages[node.index] = node
            requires[node.index] = node_data.get("requires", [])
        for index, pkg in packages.items():
            if not pkg.name.startswith("openubmc"):
                self.set_node_subsys(pkg)
            for require_id in requires.get(index, []):
                pkg.requires.append(packages.get(int(require_id), None))
            if not pkg.name.startswith("openubmc"):
                self.nodes.append(pkg)

    def run(self):
        self.read_rules()
        self.read_package_lock()

        table_valid = self._check_table_conflict()

        build_deps_alys = BuildDependenciesAnalysis(self.nodes, self.rules)
        all_deps_valid = build_deps_alys.is_dependency_allowed()
        build_deps_alys.visualize_graph(
            os.path.join(self.artifact_dir, "build_dependencies_graph_{}.html".format(self.board_name)))
        build_deps_alys.assemble_deps_json_desc(
            os.path.join(self.artifact_dir, "build_dependencies_graph_{}.json".format(self.board_name)))

        intf_deps_alys = InterfaceDependenciesAnalysis(self.nodes, self.rules)
        all_deps_valid = intf_deps_alys.is_dependency_allowed() and all_deps_valid
        intf_deps_alys.visualize_graph(
            os.path.join(self.artifact_dir, "interface_dependencies_graph_{}.html".format(self.board_name)))
        intf_deps_alys.assemble_deps_json_desc(
            os.path.join(self.artifact_dir, "interface_dependencies_graph_{}.json".format(self.board_name)))

        data_deps_alys = DataDependenciesAnalysis(self.nodes, self.rules, self.custom_sr_dir)
        data_deps_valid = data_deps_alys.run(
            os.path.join(self.artifact_dir, "data_dependencies_graph_{}.html".format(self.board_name)),
            os.path.join(self.artifact_dir, "data_dependencies_graph_{}.json".format(self.board_name)),
            os.path.join(self.artifact_dir, "data_dependencies_issues_{}.log".format(self.board_name))
        )
        all_deps_valid = table_valid and data_deps_valid and all_deps_valid

        if all_deps_valid:
            log.info("依赖检查通过")
        else:
            log.error("依赖检查不通过")
        return all_deps_valid

    def _check_table_conflict(self):
        result = True
        remote_table_map = {}
        for node in self.nodes:
            if node.table_conflict:
                result = False
            for remote_table, value in node.remote_tables.items():
                if remote_table not in remote_table_map:
                    remote_table_map[remote_table] = [node.package_name, value]
                    continue

                hit_package_name = remote_table_map[remote_table][0]
                hit_info = remote_table_map[remote_table][1]
                if node.package_name not in TABLE_CONFLICT_WHITE_LIST \
                    or remote_table != TABLE_CONFLICT_WHITE_LIST[node.package_name][0] \
                    or hit_package_name not in TABLE_CONFLICT_WHITE_LIST:
                    log.error("%s与%s远程持久化表名冲突: %s", node.package_name, hit_package_name, remote_table)
                    result = False
                    continue

                intersection = hit_info.intersection(value) - TABLE_CONFLICT_WHITE_LIST[hit_package_name][1]
                if intersection:
                    log.error("%s与%s的远程持久化表%s存在历史冲突, 不允许再添加新的冲突字段%s", node.package_name, hit_package_name, remote_table,
                        intersection)
                    result = False
        return result