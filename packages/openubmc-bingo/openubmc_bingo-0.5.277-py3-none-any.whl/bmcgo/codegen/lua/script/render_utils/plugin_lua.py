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

from utils import Utils
from dto.options import Options
from bmcgo.codegen.lua.script.base import Base
from bmcgo.codegen.lua.script.factory import Factory


class PluginLuaUtils(Base, Utils):

    def __init__(self, data: dict, options: Options):
        super().__init__(data, options=options)

    def collect_features(self, intf_msg, features):
        for method_config in intf_msg.get('methods', {}).values():
            if "featureTag" in method_config:
                features.add(method_config["featureTag"])

    def get_features(self, root):
        features = set()
        if "private" in root:
            self.collect_features(root["private"], features)
        for msg in root.values():
            for intf_msg in msg.get('interfaces', {}).values():
                self.collect_features(intf_msg, features)
        return sorted(list(features))

Factory().register("plugin.lua.mako", PluginLuaUtils)
