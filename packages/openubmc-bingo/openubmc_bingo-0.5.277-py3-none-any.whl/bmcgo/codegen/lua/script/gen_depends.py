#!/usr/bin/env python3
# coding=utf-8
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

from graphviz import Digraph
from graphviz import Graph

new_dot = Digraph("G", filename="test.gv", engine="fdp")
new_dot.attr("graph", ranksep="equally")

A = {
    "model": {
        "A": {"path": "path/A", "interfaces": {"test.A": {}}},
        "D": {"path": "path/D", "interfaces": {"test.D": {}, "test.E": {}}},
    },
    "service": {
        "name": "service_a",
        "required": [{"interface": "test.B", "path": "path/B"}],
    },
}
B = {
    "model": {"B": {"path": "path/B", "interfaces": {"test.B": {}}}},
    "service": {
        "name": "service_b",
        "required": [
            {"interface": "test.C", "path": "path/C"},
            {"interface": "test.E", "path": "*"},
        ],
    },
}

C = {
    "model": {"C": {"path": "path/C", "interfaces": {"test.C": {}}}},
    "service": {
        "name": "service_c",
        "required": [{"interface": "test.D", "path": "path/D"}],
    },
}


def gen_cls(app, graph, subg):
    for cls, cls_data in app["model"].items():
        subg.node(cls, shape="oval")
        for intf in cls_data["interfaces"]:
            with graph.subgraph(name="cluster_mdb") as mdb:
                mdb.node(intf, shape="diamond", pos="bottom")
            graph.edge(
                cls,
                intf,
                arrowhead="onormal",
                style="dashed",
            )


def add_mds(app, graph):
    app_name = app["service"]["name"]
    subg_name = "cluster" + app_name
    with graph.subgraph(name=subg_name) as subg:
        subg.attr(label=app_name)
        gen_cls(app, graph, subg)

    for require in app["service"]["required"]:
        if require["path"] != "*":
            graph.edge(subg_name, require["path"].split("/")[-1], ltail=subg_name)
        else:
            with graph.subgraph(name="cluster_mdb") as mdb:
                mdb.node(require["interface"], shape="diamond", pos="bottom")
            graph.edge(
                subg_name,
                require["interface"],
                ltail=subg_name,
                arrowhead="vee",
                style="dashed",
            )


add_mds(A, new_dot)
add_mds(B, new_dot)
add_mds(C, new_dot)

new_dot.view()
