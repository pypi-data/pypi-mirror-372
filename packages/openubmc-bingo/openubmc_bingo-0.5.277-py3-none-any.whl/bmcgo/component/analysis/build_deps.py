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

from collections import defaultdict
from typing import Dict, List, Set

import json
import os
import stat

from pyecharts import options as opts
from pyecharts.charts import Graph
from pyecharts.options import GraphLink, GraphNode

from bmcgo.component.analysis.dep_node import DepNode
from bmcgo.component.analysis.rule import Rules
from bmcgo.logger import Logger
from bmcgo import misc

global log
log = Logger()
TARGET_COMPONENTS = "targetComponents"


class BuildDependenciesAnalysis():
    def __init__(self, nodes: List[DepNode], rules: List[Rules]):
        self._nodes = nodes
        self._rules = rules
        self.build_deps_graph: Dict[str, Set[str]] = defaultdict(set)
        self.build_deps_unallowed_graph: Dict[str, Set[str]] = defaultdict(set)
        self.isolated_packages: Set[str] = set()
        self._node_build_relation()
        self._get_isolated_packages()

    def is_dependency_allowed(self):
        is_allowed = True
        for pkg in self._nodes:
            if pkg.subsys_name == "unknown":
                is_allowed = False
                log.error("发现一个不在子系统中的包, 包名为: %s", pkg.name)
            if pkg.package_name in self.isolated_packages and "Library" in pkg.package_type:
                if pkg.subsys_name != "opensource" and pkg.subsys_name != "public":
                    is_allowed = False
                    log.error("找到一个孤立的库, 库名为: %s", pkg.name)
                else:
                    log.warning("找到一个孤立的开源/平台公共库, 库名为: %s", pkg.name)
        return is_allowed and not bool(self.build_deps_unallowed_graph)

    def assemble_deps_json_desc(self, path):
        node_name_map = dict()
        for node in self._nodes:
            node_name_map[node.package_name] = {
                misc.NAME: node.package_name,
                "version": node.package_version,
                "subsystem": node.subsys_name,
                "type": node.package_type
            }

        json_dict = {"AllBuildDependencyGraph": [], "IllegalBuildDependencyGraph": []}
        for src in self.build_deps_graph:
            entry = {"sourceComponent": node_name_map.get(src), TARGET_COMPONENTS: []}
            for tgt in self.build_deps_graph[src]:
                entry[TARGET_COMPONENTS].append(node_name_map.get(tgt))
            json_dict["AllBuildDependencyGraph"].append(entry)

        for src in self.build_deps_unallowed_graph:
            entry = {"sourceComponent": node_name_map.get(src), TARGET_COMPONENTS: []}
            for tgt in self.build_deps_unallowed_graph[src]:
                entry[TARGET_COMPONENTS].append(node_name_map.get(tgt))
            json_dict["IllegalBuildDependencyGraph"].append(entry)

        log.info("保存 BMC 组件构建依赖信息到: %s", path)
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        modes = stat.S_IWUSR | stat.S_IRUSR 
        with os.fdopen(os.open(path, flags, modes), 'w') as file_descriptor:
            file_descriptor.write(json.dumps(json_dict, indent=4))

    def visualize_graph(self, path):
        subsystems = set()
        for pkg in self._nodes:
            subsystems.add(pkg.subsys_name)
        categories = []
        for subsys in subsystems:
            categories.append({misc.NAME: subsys, "symbolSize": 100})
        categories.append({misc.NAME: "unknown", "symbolSize": 100})
        category_id_map: Dict[str, int] = dict()
        for index, category in enumerate(categories):
            category_id_map[category[misc.NAME]] = index

        graph_nodes: List[GraphNode] = []
        for pkg in self._nodes:
            label_opts = None
            if pkg.subsys_name == "unknown":
                label_opts = opts.LabelOpts(color=misc.COLOR_RED)
            if pkg.package_name in self.isolated_packages and "Library" in pkg.package_type:
                label_opts = opts.LabelOpts(color=misc.COLOR_RED)
            graph_nodes.append(GraphNode(
                name=pkg.package_name,
                symbol_size=5,
                category=category_id_map.get(pkg.subsys_name, len(categories)),
                label_opts=label_opts))

        links: list[GraphLink] = []
        for src in self.build_deps_graph:
            for dest in self.build_deps_graph[src]:
                if src in self.build_deps_unallowed_graph and dest in self.build_deps_unallowed_graph[src]:
                    links.append(GraphLink(source=src, target=dest,
                                           linestyle_opts=opts.LineStyleOpts(color=misc.COLOR_RED, width=1.5)))
                else:
                    links.append(GraphLink(source=src, target=dest))

        log.info("保存 BMC 组件构建依赖图到 %s", path)
        (Graph(init_opts=opts.InitOpts(width="100%", height="1200px", page_title="BMC构建依赖关系图"))
        .add("", graph_nodes, links, categories,
             repulsion=100,
             is_draggable=False,
             edge_symbol="arrow",
             edge_symbol_size=[0, 5],
             is_layout_animation=False,
             label_opts=opts.LabelOpts(position="right", formatter="{b}"))
             .set_global_opts(
            title_opts=opts.TitleOpts(title="Graph-BMC构建依赖关系图"), 
            legend_opts=opts.LegendOpts(orient="vertical", pos_left="2%", pos_top="20%"))
            .render(path))

    def _node_build_relation(self): 
        for src in self._nodes:
            for dest in src.requires:
                self.build_deps_graph[src.package_name].add(dest.package_name)
                if not self._check_build_dependency(src, dest):
                    self.build_dependency_allowed = False
                    self.build_deps_unallowed_graph[src.package_name].add(dest.package_name)

    def _check_build_dependency(self, src: DepNode, tgt: DepNode):
        if src.subsys_level < tgt.subsys_level:
            log.error("发现不被允许的构建依赖. 源包: %s, 目标包: %s",
                    src.name, tgt.name)
            return False
        for rules in self._rules:
            if rules.build_dep_check(src, tgt):
                log.debug("源名: %s, 目标: %s", src.name, tgt.name)
                return True
        log.error("发现不被允许的构建依赖. 源包: %s, 目标包: %s", src.name, tgt.name)
        return False

    def _get_isolated_packages(self):
        indegree: Dict[str, int] = dict()
        for node in self._nodes:
            indegree[node.package_name] = 0
        for src in self.build_deps_graph:
            for dest in self.build_deps_graph[src]:
                indegree[dest] += 1

        for pkg, degree in indegree.items():
            if degree == 0:
                self.isolated_packages.add(pkg)