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

from enum import Enum

from bmcgo.component.analysis.dep_node import DepNode
from bmcgo.logger import Logger

global log
log = Logger()


class SubSys():
    def __init__(self, level: int):
        self.level = level
        self.apps: list[str] = []
        self.libraries: list[str] = []
        self.tools: list[str] = []
        self.configurations: list[str] = []
        self.commands: list[str] = []


class DepExcept():
    def __init__(self, obj):
        self.tag = obj.get("tag")
        self.operator = obj.get("op")
        self.value = obj.get("value", [])


class DepWhen():
    def __init__(self, obj):
        self.tag = obj.get("tag")
        self.operator = obj.get("op")
        self.value = obj.get("value", [])


class DepRuleType(Enum):
    SUBSYSTEM_DEP = 1
    INTERFACE_DEP = 2
    BUILD_DEP = 3


class Rule():
    def __init__(self, rule_type: DepRuleType, obj):
        self.rule_type = rule_type
        self.from_key = obj.get("from")
        self.to_key = obj.get("to")
        self.description = obj.get("description")
        self.message = obj.get("message")
        if not self.from_key or not self.to_key:
            log.error("无法从 json 对象中获取 'from' 或 'to'")
        self.whe = None
        self.excpt = None
        excpt = obj.get("except")
        if excpt:
            self.excpt = DepExcept(excpt)
        whe = obj.get("when")
        if whe:
            self.whe = DepWhen(whe)

    # 检查src和tgt是否适用当前的规则
    def match_rule(self, src: DepNode, tgt: DepNode):
        from_matched = self.from_key == "*" or self.from_key in src.package_type
        to_matched = self.to_key == "*" or self.to_key in tgt.package_type
        return from_matched and to_matched

    # 检查from_key和to_key是否适用当前的规则
    def match_rule(self, from_key: str, to_key: str):
        from_matched = self.from_key == "*" or self.from_key == from_key
        to_matched = self.to_key == "*" or self.to_key == to_key
        return from_matched and to_matched

    def build_dep_check(self, src: DepNode, tgt: DepNode):
        if self.rule_type != DepRuleType.BUILD_DEP:
            return False
        return not self.whe

    def subsystem_dep_check(self, src: DepNode, tgt: DepNode, intf: str):
        if self.rule_type != DepRuleType.SUBSYSTEM_DEP:
            return False
        if self.from_key != src.subsys_name or self.to_key != tgt.subsys_name:
            return False
        if not self.excpt:
            return True
        # Currently the input rule only defines one single exception
        return self.excpt.tag == "Interface" and self.excpt.operator == "oneOf" and intf not in self.excpt.value

    def intf_dep_check(self, src: DepNode, tgt: DepNode, intf: str):
        if self.rule_type != DepRuleType.INTERFACE_DEP:
            return False
        if self.from_key != src.package_name or self.to_key != tgt.package_name:
            return False
        if not self.excpt:
            return True
        return self.excpt.tag == "Interface" and self.excpt.operator == "oneOf" and intf not in self.excpt.value


class Rules():
    def __init__(self, obj, allow: bool):
        self.description = obj.get("description", "")
        self.subsystem_deps: list[Rule] = []
        self.interface_deps: list[Rule] = []
        self.build_rules: list[Rule] = []
        self.allow = allow

        for rule in obj.get("SubsystemDeps", []):
            self.subsystem_deps.append(Rule(DepRuleType.SUBSYSTEM_DEP, rule))

        for sub in obj.get("IntfDeps", []):
            for rules in sub.values():
                for rule in rules:
                    self.interface_deps.append(Rule(DepRuleType.INTERFACE_DEP, rule))

        for rule in obj.get("BuildDeps", []):
            self.build_rules.append(Rule(DepRuleType.BUILD_DEP, rule))

    # Check if the interface dependency between two packages is allowed based on the rules
    def intf_dep_check(self, src: DepNode, tgt: DepNode, intf: str):
        # Whitelist rules
        if self.allow:
            return self._intf_dep_check_whitelist(src, tgt, intf)

        # Blacklist rules
        return self._intf_dep_check_blacklist(src, tgt, intf)

    def build_dep_check(self, src: DepNode, tgt: DepNode):
        # Whitelist rules
        if self.allow:
            return self._build_dep_check_whitelist(src, tgt)

        # Blacklist rules
        return self._build_dep_check_blacklist(src, tgt)

    def _intf_dep_check_whitelist(self, src: DepNode, tgt: DepNode, intf: str):
        if src.package_name in ['event', 'sensor']:
            return True
        # Check the subsystem rules first and then interface rules
        subsys_allowed = False
        for rule in self.subsystem_deps:
            if rule.subsystem_dep_check(src, tgt, intf):
                subsys_allowed = True
                break

        if src.subsys_name != tgt.subsys_name or not subsys_allowed:
            return subsys_allowed

        intf_allowed = False
        for rule in self.interface_deps:
            if rule.intf_dep_check(src, tgt, intf):
                intf_allowed = True
                break
        return intf_allowed

    def _intf_dep_check_blacklist(self, src: DepNode, tgt: DepNode, intf: str):
        subsys_unallowed = False
        for rule in self.subsystem_deps:
            if rule.subsystem_dep_check(src, tgt, intf):
                subsys_unallowed = True
                break
        if src.subsys_name != tgt.subsys_name or subsys_unallowed:
            return not subsys_unallowed

        intf_unallowed = False
        for rule in self.interface_deps:
            if rule.intf_dep_check(src, tgt, intf):
                intf_unallowed = True
                break
        return not intf_unallowed

    def _build_dep_check_whitelist(self, src: DepNode, tgt: DepNode):
        for rule in self.build_rules:
            # 跳过不适用的规则
            if not rule.match_rule(src, tgt):
                continue
            result = rule.build_dep_check(src, tgt)
            # 白名单有一个匹配就满足
            if result:
                return True
        # 白名单都不匹配时不满足
        return False

    def _match_rule(self, src: DepNode, tgt: DepNode, from_key: str, to_key: str):
        for rule in self.build_rules:
            if not rule.match_rule(from_key, to_key):
                continue
            if rule.build_dep_check(src, tgt):
                return True

        return False

    def _build_dep_check_blacklist(self, src: DepNode, tgt: DepNode):
        # 未配置黑名单时默认满足
        if not bool(self.build_rules):
            return True

        # 源组件和目标组件只要有一组类型不在黑名单内就满足
        for from_key in src.package_type:
            for to_key in tgt.package_type:
                if not self._match_rule(src, tgt, from_key, to_key):
                    return True

        return False