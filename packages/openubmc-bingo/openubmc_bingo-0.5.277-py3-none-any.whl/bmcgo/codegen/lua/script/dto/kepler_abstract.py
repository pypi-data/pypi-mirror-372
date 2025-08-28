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

from typing import Dict

from dto.url_route import Url


class KeplerAbstract:
    def __init__(self, url_path: str, interface: str, file_path: str, package: str, name: str):
        self.url = Url(url_path)
        self.interface = interface
        self.file_path = file_path
        self.package: str = package
        self.name: str = name

    @classmethod
    def from_json(cls, data: dict):
        return KeplerAbstract(data.get("path"), data.get("interface"), data.get("file_path"),
                              data.get("package"), data.get("name"))

    def to_json(self):
        return {"path": self.url.url, "interface": self.interface, "file_path": self.file_path,
                "package": self.package, "name": self.name}

    def class_type(self):
        return f"{self.package}.{self.name}"


class KeplerAbstractMgr:
    def __init__(self):
        self.url_abstract_map: Dict[str, KeplerAbstract] = {}

    def add(self, kepler_abstract: KeplerAbstract):
        self.url_abstract_map.setdefault(kepler_abstract.url.url_feature, kepler_abstract)

    def get(self, url_feature: str) -> KeplerAbstract:
        return self.url_abstract_map.get(url_feature)
