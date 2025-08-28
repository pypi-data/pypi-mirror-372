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
import stat
from collections import defaultdict
from typing import Dict, List, Set
from pyecharts import options as opts
from pyecharts.charts import Graph
from pyecharts.options import GraphLink, GraphNode, LineStyleOpts

from bmcgo.component.analysis.dep_node import DepNode
from bmcgo.component.analysis.rule import Rules
from bmcgo.component.analysis.sr_validation import SrParser, DirectedGraph
from bmcgo.logger import Logger
from bmcgo import misc

global log
log = Logger()
CONAN_DATA = ".conan/data"
DATA_DEPENDENCIES = "dataDependencies"


class ClassPropMap:
    def __init__(self, nodes: List[DepNode], mdb_interface_dir: str) -> None:
        self.class_map: Dict[str, DepUnit] = dict()
        self.prop_map: Dict[tuple[str, str], DepUnit] = dict()
        self.intf_props: Dict[str, set[str]] = defaultdict(set)
        self.class_intf_props: Dict[str, set[str]] = defaultdict(set)
        self.map_mdb_interface(mdb_interface_dir)
        for node in nodes:
            if not os.path.exists(node.model_path):
                continue
            with open(node.model_path, "r") as file_descriptor:
                model_dict = json.load(file_descriptor)
            for class_name, class_data in model_dict.items():
                self.add_from_model(node.package_name, class_name, class_data)

    def add_class(self, app_name: str, class_name: str, usage_csr: bool):
        if class_name in self.class_map and self.class_map[class_name].usage_csr:
            return
        self.class_map[class_name] = DepUnit(app_name, class_name, usage_csr=usage_csr)

    def map_mdb_interface(self, mdb_interface_dir):
        if not mdb_interface_dir:
            return

        for root, _, files in os.walk(mdb_interface_dir):
            for file in files:
                if not file.endswith(".json"):
                    continue
                intf_json = os.path.join(root, file)
                with open(intf_json, 'r') as fp:
                    content = json.load(fp)
                for intf, intf_data in content.items():
                    self.intf_props[intf] = set(intf_data.get('properties', {}).keys())

    def add_from_model(self, app_name: str, class_name: str, class_data: Dict):
        has_usage_csr = False
        for intf, intf_data in class_data.get("interfaces", {}).items():
            self.class_intf_props[class_name].update(self.intf_props[intf])
            has_usage_csr |= self.parse_prop_data(app_name, class_name,
                                                        intf_data.get("properties", {}), intf=intf)

        has_usage_csr |= self.parse_prop_data(app_name, class_name,
                                                    class_data.get("properties", {}))
        self.add_class(app_name, class_name, has_usage_csr)

    def check_class_exists(self, class_name: str):
        return class_name in self.class_map

    def check_prop_exists(self, class_name: str, prop: str):
        if not prop:
            return True
        return (class_name, prop) in self.prop_map and prop in self.class_intf_props[class_name]

    def get_app(self, class_name: str):
        if class_name in self.class_map:
            return self.class_map[class_name].app
        return 'hwproxy'

    def get_intf(self, class_name: str, prop: str):
        if not prop or (class_name, prop) not in self.prop_map:
            return ""
        return self.prop_map.get((class_name, prop)).intf

    def get_ref_intf(self, class_name: str, prop: str):
        if not prop or (class_name, prop) not in self.prop_map:
            return ""
        return self.prop_map.get((class_name, prop)).ref_intf

    def parse_prop_data(self, app_name: str, class_name: str, properties_dict: Dict, intf: str = ""):
        no_csr = True
        for prop, prop_data in properties_dict.items():
            usage_csr = "CSR" in prop_data.get("usage", [])
            ref_intf = prop_data.get("refInterface", "")
            self.prop_map[(class_name, prop)] = DepUnit(app_name, class_name, 
            usage_csr=usage_csr, prop=prop, intf=intf, ref_intf=ref_intf)
            no_csr = no_csr and not usage_csr
        return not no_csr


class DepUnit:
    def __init__(self, app_name: str, class_name: str, **kwargs) -> None:
        self.app = app_name
        self.class_name = class_name
        self.usage_csr = kwargs.get("usage_csr", False)
        self.prop = kwargs.get("prop", "")
        self.obj_name = kwargs.get("obj_name", "")
        self.ref_intf = kwargs.get("ref_intf", "")
        self.intf = kwargs.get("intf", None)
        self.obj_prop = f"{self.obj_name}.{self.prop}" if self.prop else self.obj_name


class DataDependenciesAnalysis(SrParser):
    def __init__(self, nodes: List[DepNode], rules: List[Rules], custom_sr_dir: str):
        mdb_interface_dir = ""
        for node in nodes:
            if node.package_name == 'vpd':
                pkg_dir = node.ref.split("#")[0].replace("@", "/")
                sr_dir = os.path.join(os.environ["HOME"], CONAN_DATA, pkg_dir, "source")
            if node.package_name == 'mdb_interface':
                pkg_dir = node.ref.split("#")[0].replace("@", "/")
                mdb_interface_dir = os.path.join(os.environ["HOME"], CONAN_DATA, pkg_dir,
                "package", node.package_id, "opt/bmc/apps/mdb_interface/intf/mdb/bmc")
        if custom_sr_dir:
            sr_dir = custom_sr_dir
        super().__init__(sr_dir)
        self._nodes = nodes
        self._rules = rules
        self.cp_map = ClassPropMap(nodes, mdb_interface_dir)
        self.dependencies: Dict[tuple[str, str], tuple[bool, str]] = dict()
        self.correct_sr_deps_graph: Dict[str, Dict[str, List[Dict[str, str]]]] = defaultdict(dict)
        self.wrong_sr_deps_graph: Dict[str, Dict[str, List[Dict[str, str]]]] = defaultdict(dict)
        self.app_deps: Dict[str, Dict[tuple[str, str], tuple[str, str]]] = defaultdict(dict)
        self.links: List[GraphLink] = []
        self.involved_apps: set[str] = set()
        self.nodes_by_app: Dict[str, DepNode] = dict()
        for node in self._nodes:
            self.nodes_by_app[node.package_name] = node

    @staticmethod
    def get_loop_error_msg(loop: List[str], dep_data: Dict):
        route = []
        for i in range(len(loop) - 1):
            obj_prop_from, obj_prop_to = dep_data[(loop[i], loop[i + 1])]
            route.append(f"{obj_prop_from}({loop[i]}) -> {obj_prop_to}({loop[i + 1]})")
        return ", ".join(route)

    @staticmethod
    def is_in_whitelist(dep_unit: DepUnit):
        return dep_unit.app == 'event' or dep_unit.class_name == 'Event'

    def run(self, html_output_path: str, json_output_path: str, issues_log_path: str):
        self.walk_sr_dir()
        for sr_path, dep_data in self.app_deps.items():
            graph = DirectedGraph()
            for app_pair in dep_data:
                graph.add_edge(*app_pair)
            loop = graph.check_loop()
            if loop:
                self.issues_report[sr_path].add(("error", 
                    f"引用关系构成了组件间环形依赖: {self.get_loop_error_msg(loop, dep_data)}"))
        _, _, issues_count = self.log_issues(issues_log_path)
        self.set_links()
        self.visualize_graph(html_output_path)
        self.assemble_deps_json_desc(json_output_path)
        return issues_count["error"] == 0 and not bool(self.wrong_sr_deps_graph)

    def parse_sr(self, relpath: str, sr_content: Dict):
        for obj_name, obj_data in sr_content.get("Objects", {}).items():
            class_name = self.get_class_name(obj_name)
            if not self.cp_map.check_class_exists(class_name):
                continue
            app_name = self.cp_map.get_app(class_name)

            for key, value in obj_data.items():
                intf = self.cp_map.get_intf(class_name, key)
                dep_from = DepUnit(app_name, class_name, prop=key, obj_name=obj_name, intf=intf)
                if isinstance(value, str) and (self.is_ref(value) or self.is_sync(value)):
                    self.parse_prop_val(dep_from, value, relpath)

    def parse_prop_val(self, dep_from: DepUnit, prop_val: str, relpath: str):
        for val in prop_val.split(';'):
            val = val.strip()
            if not (self.is_ref(val) or self.is_sync(val)):
                continue
            target_obj = self.get_obj_name(val)
            target_class = self.get_class_name(target_obj)
            target_prop = self.get_prop_name(val)
            target_class_exists = self.cp_map.check_class_exists(target_class)
            target_prop_exists = self.cp_map.check_prop_exists(target_class, target_prop)
            if not target_class_exists or not target_prop_exists or self.is_sync(val):
                continue

            target_app = self.cp_map.get_app(target_class)
            intf = self.cp_map.get_intf(target_class, target_prop)
            dep_to = DepUnit(target_app, target_class, prop=target_prop, intf=intf, obj_name=target_obj)
            self.add_dep(dep_from, dep_to, relpath)

    def add_dep(self, dep_from: DepUnit, dep_to: DepUnit, relpath: str):
        self.involved_apps.add(dep_from.app)
        self.involved_apps.add(dep_to.app)
        dependency_allowed = True

        if dep_from.app != dep_to.app:
            self.app_deps[relpath][(dep_from.app, dep_to.app)] = (dep_from.obj_prop, dep_to.obj_prop)
            dependency_allowed = self.check_sr_dependency(dep_from, dep_to, relpath)

        if dependency_allowed and dep_to.intf and dep_to.intf != dep_from.ref_intf:
            level = "notice" if self.is_in_whitelist(dep_from) else "warning"
            self.issues_report[relpath].add((level, f"'{dep_from.obj_prop}'对'{dep_to.obj_prop}'的引用\
没有在组件'{dep_from.app}'的MDS中用refInterface声明对接口'{dep_to.intf}'的依赖"))

    def set_links(self):
        for (app_from, app_to), (allowed, violation) in self.dependencies.items():
            if allowed:
                link_opts = GraphLink(source=app_from, target=app_to,
                                      linestyle_opts=LineStyleOpts(color="GREEN", curve=0.2))
            else:
                link_opts = GraphLink(source=app_from, target=app_to,
                                      linestyle_opts=LineStyleOpts(color=misc.COLOR_RED, curve=0.2), value=violation)
            self.links.append(link_opts)

    def check_sr_dependency(self, dep_from: DepUnit, dep_to: DepUnit, relpath: str):
        if dep_from.app == dep_to.app or dep_from.app not in self.nodes_by_app \
            or dep_to.app not in self.nodes_by_app:
            return True
        node_from = self.nodes_by_app.get(dep_from.app)
        node_to = self.nodes_by_app.get(dep_to.app)
        allowed = False
        for rules in self._rules:
            if rules.intf_dep_check(node_from, node_to, dep_to.intf):
                allowed = True
                break
        dep_detail = {
            "sr_path": relpath,
            "source": dep_from.obj_prop,
            "target": dep_to.obj_prop
        }
        if allowed:
            self.dependencies[(dep_from.app, dep_to.app)] = self.dependencies.get((dep_from.app, dep_to.app), 
                                                                                    (True, ""))
            self.correct_sr_deps_graph[dep_from.app][dep_to.app] = \
                self.correct_sr_deps_graph[dep_from.app].get(dep_to.app, list())
            self.correct_sr_deps_graph[dep_from.app][dep_to.app].append(dep_detail)
            return True

        whitelisted = self.is_in_whitelist(dep_from)
        level = "notice" if whitelisted else "error"
        same_sub = node_from.subsys_name == node_to.subsys_name
        violation = "违反子系统内依赖约束" if same_sub else "违反子系统间依赖约束"
        detail = f"'{dep_from.obj_prop}'对'{dep_to.obj_prop}'的引用属于组件'{dep_from.app}'对组件'{dep_to.app}'的依赖"
        self.issues_report[relpath].add((level, f"数据依赖违反依赖约束: {detail}"))
        if whitelisted:
            return True
        self.dependencies[(dep_from.app, dep_to.app)] = (False, violation)
        self.wrong_sr_deps_graph[dep_from.app][dep_to.app] = \
            self.wrong_sr_deps_graph[dep_from.app].get(dep_to.app, list())
        self.wrong_sr_deps_graph[dep_from.app][dep_to.app].append(dep_detail)
        return False

    def visualize_graph(self, output_path: str):
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
            if pkg.package_name in self.involved_apps:
                graph_nodes.append(GraphNode(name=pkg.package_name, symbol_size=10, \
                    category=category_id_map.get(pkg.subsys_name, len(categories))))

        log.info("保存 BMC 依赖信息图到 %s", output_path)
        output_graph = Graph(init_opts=opts.InitOpts(width="100%", height="1200px", 
                                                    page_title="BMC-Data-Dependency-Graph"))
        output_graph.add("", graph_nodes, self.links, categories,
             repulsion=100,
             is_rotate_label=True, 
             edge_symbol=["", "arrow"],
             label_opts=opts.LabelOpts(position="right", formatter="{b}"))
        output_graph.set_global_opts(
            title_opts=opts.TitleOpts(title="Graph-BMC-Data-Dependency-Graph"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_left="2%", pos_top="20%"))
        output_graph.options.get("series")[0]["zoom"] = 4
        output_graph.render(output_path)

    def assemble_deps_json_desc(self, output_path: str):
        node_name_map = dict()

        for node in self._nodes:
            node_name_map[node.package_name] = {
                misc.NAME: node.package_name,
                "version": node.package_version,
                "subsystem": node.subsys_name,
                "type": node.package_type
            }

        json_dict = {"DataDependencyGraph": [], "IllegalDataDependencyGraph": []}
        for (app_from, dep_data) in self.correct_sr_deps_graph.items():
            entry = {"sourceComponent": node_name_map.get(app_from), DATA_DEPENDENCIES: []}
            for app_to, detail in dep_data.items():
                entry[DATA_DEPENDENCIES].append({"targetComponent": node_name_map.get(app_to), "detail": detail})
            json_dict["DataDependencyGraph"].append(entry)

        for (app_from, dep_data) in self.wrong_sr_deps_graph.items():
            entry = {"sourceComponent": node_name_map.get(app_from), DATA_DEPENDENCIES: []}
            for app_to, detail in dep_data.items():
                entry[DATA_DEPENDENCIES].append({"targetComponent": node_name_map.get(app_to), "detail": detail})
            json_dict["IllegalDataDependencyGraph"].append(entry)

        log.info("保存 BMC 依赖信息到 %s", output_path)
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        modes = stat.S_IWUSR | stat.S_IRUSR 
        with os.fdopen(os.open(output_path, flags, modes), 'w') as file_descriptor:
            file_descriptor.write(json.dumps(json_dict, indent=4))
