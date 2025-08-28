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
from typing import Dict, List
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
INTERFACE_DEPENDENCIES = "interfaceDependencies"


class InterfaceDependenciesAnalysis():
    def __init__(self, nodes: List[DepNode], rules: List[Rules]):
        # All packages in the conan build data
        self._nodes: List[DepNode] = list()
        # Select packages that have dependencies on d-bus
        for node in nodes:
            if len(node.intf_impl) != 0 or len(node.intf_deps) != 0:
                self._nodes.append(node)
        self._rules = rules

        # All d-bus interfaces that the package implements
        self.node_impl_intfs: Dict[str, List[DepNode]] = defaultdict(list)

        # All d-bus interfaces the package depends on
        self.node_deps_intfs: Dict[str, List[DepNode]] = defaultdict(list)

        # The package dependency graph: vertex are conan packages and edges are interfaces
        self.intf_deps_graph: Dict[str, Dict[str, List[str]]] = defaultdict(dict)
        self.intf_deps_unallowed_graph: Dict[str, Dict[str, List[str]]] = defaultdict(dict)

        self._node_intf_relation()

    def is_dependency_allowed(self):
        return not bool(self.intf_deps_unallowed_graph)

    def assemble_deps_json_desc(self, path):
        node_name_map = dict()
        for node in self._nodes:
            node_name_map[node.package_name] = {
                misc.NAME: node.package_name,
                "version": node.package_version,
                "subsystem": node.subsys_name,
                "type": node.package_type
            }

        json_dict = {"InterfaceDependencyGraph": [], "IllegalInterfaceDependencyGraph": []}
        for src in self.intf_deps_graph:
            entry = {"sourceComponent": node_name_map.get(src), INTERFACE_DEPENDENCIES: []}
            for tgt, intfs in self.intf_deps_graph[src].items():
                entry[INTERFACE_DEPENDENCIES].append({"targetComponent": node_name_map.get(tgt), "interfaces": intfs})
            json_dict["InterfaceDependencyGraph"].append(entry)

        for src in self.intf_deps_unallowed_graph:
            entry = {"sourceComponent": node_name_map.get(src), INTERFACE_DEPENDENCIES: []}
            for tgt, intfs in self.intf_deps_unallowed_graph[src].items():
                entry[INTERFACE_DEPENDENCIES].append({"targetComponent": node_name_map.get(tgt), "interfaces": intfs})
            json_dict["IllegalInterfaceDependencyGraph"].append(entry)

        log.info("保存 BMC 组件 d-bus 接口依赖信息到: %s", path)
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
            graph_nodes.append(GraphNode(name=pkg.package_name, symbol_size=5, \
                    category=category_id_map.get(pkg.subsys_name, len(categories))))

        links: list[GraphLink] = []
        for src in self.intf_deps_graph:
            for dest, intfs in self.intf_deps_graph[src].items():
                if src in self.intf_deps_unallowed_graph and dest in self.intf_deps_unallowed_graph[src]:
                    links.append(GraphLink(
                        source=src,
                        target=dest,
                        linestyle_opts=opts.LineStyleOpts(color=misc.COLOR_RED, curve=0.2, width=1.5),
                        value=self.intf_deps_unallowed_graph[src][dest]))
                else:
                    links.append(GraphLink(source=src, target=dest, value=intfs))

        log.info("保存 BMC 组件 d-bus 接口依赖信息到: %s", path)
        (Graph(init_opts=opts.InitOpts(width="100%", height="1200px", page_title="BMC-Interface-Dependency-Graph"))
        .add("", graph_nodes, links, categories,
             repulsion=100,
             is_draggable=False,
             edge_symbol="arrow",
             edge_symbol_size=[0, 5],
             is_layout_animation=False,
             label_opts=opts.LabelOpts(position="right", formatter="{b}"))
             .set_global_opts(
            title_opts=opts.TitleOpts(title="Graph-BMC-Interface-Dependency-Graph"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_left="2%", pos_top="20%"))
            .render(path))

    def _node_intf_relation(self):
        self._construct_node_intf_detail()

        for intf, nodes in self.node_deps_intfs.items():
            if intf not in self.node_impl_intfs:
                continue
            for src in nodes:
                for tgt in self.node_impl_intfs[intf]:
                    self._add_two_node_relation(src, tgt, intf)

    def _construct_node_intf_detail(self):
        for node in self._nodes:
            for intfi in node.intf_impl:
                self.node_impl_intfs[intfi].append(node)
            for intfd in node.intf_deps:
                self.node_deps_intfs[intfd].append(node)

    def _add_two_node_relation(self, src: DepNode, tgt: DepNode, intf: str):
        interface_relation = self.intf_deps_graph[src.package_name].get(tgt.package_name, [])
        interface_relation.append(intf)
        self.intf_deps_graph[src.package_name][tgt.package_name] = interface_relation
        if self._check_intf_dependency(src, tgt, intf):
            return
        unallowed_interface_relation = self.intf_deps_unallowed_graph[src.package_name].get(tgt.package_name, [])
        unallowed_interface_relation.append(intf)
        self.intf_deps_unallowed_graph[src.package_name][tgt.package_name] = unallowed_interface_relation

    def _check_intf_dependency(self, src: DepNode, tgt: DepNode, intf: str):
        for rules in self._rules:
            if rules.intf_dep_check(src, tgt, intf):
                return True
        log.error("发现不合规的总线接口依赖, 源包: %s, 目标包: %s",
                src.name, tgt.name)
        return False
