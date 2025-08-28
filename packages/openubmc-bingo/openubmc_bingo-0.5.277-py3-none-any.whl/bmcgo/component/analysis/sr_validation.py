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
import stat
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple
from colorama import Fore, Style
from bmcgo.logger import Logger

global log
log = Logger()

SOFT_SR_SUFFIX = "_soft.sr"
SOFTWARE_SUFFIX = "software"
CHIP_KEY = "Chip"
LEVEL_ERROR = "error"
LEVEL_WARNING = "warning"


class DirectedGraph:
    VISITING = 1
    VISITED = 2

    def __init__(self):
        self.edges = defaultdict(set)
        self.flags = dict()

    def add_edge(self, node_from: str, node_to: str):
        self.edges[node_from].add(node_to)

    def has_edge(self, node_from: str, node_to: str):
        return node_to in self.edges[node_from]

    def remove_edge(self, node_from: str, node_to: str):
        self.edges[node_from].discard(node_to)

    def check_loop(self):
        for node in self.edges:
            if node in self.flags:
                continue
            route = [node]
            if self.depth_first_search(node, route):
                return route
        return []

    def depth_first_search(self, node: str, route: List[str]):
        if node not in self.edges:
            self.flags[node] = self.VISITED
            return False
        self.flags[node] = self.VISITING
        for child in self.edges[node]:
            route.append(child)
            if child not in self.flags:
                if self.depth_first_search(child, route):
                    return True
            elif self.flags[child] == self.VISITING:
                return True
            route.pop()
        self.flags[node] = self.VISITED
        return False


class SrParser:
    def __init__(self, sr_dir: str):
        self.issues_report = defaultdict(set)
        self.sr_dir = sr_dir

    @staticmethod
    def get_obj_name(prop_val: str):
        obj_prop = prop_val.split('/', 1)[1]
        obj_name = obj_prop.split('.', 1)[0]
        if SrParser.is_sync(prop_val) and obj_name.startswith('::'):
            return obj_name[2:]
        return obj_name

    @staticmethod
    def get_class_name(obj_name: str):
        return obj_name.split('_', 1)[0]

    @staticmethod
    def is_ref(prop_val: str):
        return prop_val.startswith("#/")

    @staticmethod
    def is_sync(prop_val: str):
        return prop_val.startswith("<=/")

    @staticmethod
    def get_prop_name(prop_val: str):
        if '.' not in prop_val:
            return ""
        ret = prop_val.split('.', 2)[1]
        if "|>" in ret:
            ret = ret.split("|>", 1)[0].strip()
        return ret

    @staticmethod
    def get_logger(level: str):
        if level == 'error':
            return log.error
        if level == 'warning':
            return log.warning
        return log.info

    @staticmethod
    def get_log_color(level: str):
        if level == 'error':
            return Fore.RED
        if level == 'warning':
            return Fore.YELLOW
        return Fore.WHITE

    @staticmethod
    def log_issue(sr_path: str, level: str, msg: str):
        logger = SrParser.get_logger(level)
        if 'CLOUD_BUILD_RECORD_ID' in os.environ:
            logger("%s: %s: %s", sr_path, level, msg)
        else:
            color = SrParser.get_log_color(level)
            logger("%s: %s: %s%s%s", sr_path, level, color, msg, Style.RESET_ALL)

    def log_issues(self, issues_log_path=None):
        file_count = 0
        problems_total = 0
        issues_count = defaultdict(int)
        issues_content = ''
        for sr_path, issues in self.issues_report.items():
            if not issues:
                continue
            file_count += 1
            for level, msg in issues:
                problems_total += (level == LEVEL_ERROR or level == LEVEL_WARNING)
                issues_count[level] += 1
                issues_content += f'{sr_path}: {level}: {msg}\n'
                if issues_log_path is None or level == LEVEL_ERROR:
                    self.log_issue(sr_path, level, msg)
        if issues_log_path is not None:
            msg = f"Finished data dependency analysis: found {problems_total} issues in {file_count} files"
            if issues_count[LEVEL_ERROR]:
                msg += f', errors: {issues_count[LEVEL_ERROR]}'
            if issues_count[LEVEL_WARNING]:
                msg += f', warnings: {issues_count[LEVEL_WARNING]}'
            issues_content += msg
            with os.fdopen(os.open(issues_log_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                stat.S_IWUSR | stat.S_IRUSR), 'w') as fp:
                fp.write(issues_content)
        return file_count, problems_total, issues_count

    def walk_sr_dir(self):
        for root, _, files in os.walk(self.sr_dir):
            for file in files:
                if not file.endswith(".sr"):
                    continue
                self.load_sr(os.path.join(root, file))

    def load_sr(self, sr_path: str):
        relpath = os.path.relpath(sr_path, self.sr_dir)
        with open(sr_path, 'r') as file_descriptor:
            try:
                sr_content = json.load(file_descriptor)
            except json.decoder.JSONDecodeError as error:
                self.issues_report[relpath].add(("error", f"格式错误: {error.msg}"))
            except Exception as error:
                self.issues_report[relpath].add(("error", f"解析失败: {error}"))
            else:
                self.parse_sr(relpath, sr_content)

    def parse_sr(self, relpath: str, sr_content: Dict):
        # 由子类实现
        pass


class SrValidate(SrParser):
    def __init__(self, sr_dir: str):
        super().__init__(sr_dir)
        self.sr_objs: Dict[str, Dict[str, Dict]] = dict()
        self.objects_used = defaultdict(set)
        self.soft_sr_objects = defaultdict(dict)
        self.soft_sr_files = dict()
        self.is_sr_repo = False
        self.is_product_sr_repo = False
        self.check_repo_type()
        self.smc_dfx_whitelist: Dict[str, Set[Tuple[int, int]]] = defaultdict(set)
        self.load_smc_dfx_whitelist()

    @staticmethod
    def merge_sr_objects(hardware_sr_objects: Dict[str, Dict], software_sr_objects: Dict[str, Dict]):
        for obj_name, obj_data in software_sr_objects.items():
            if obj_name not in hardware_sr_objects:
                hardware_sr_objects[obj_name] = obj_data
                continue
            for prop_name, prop_data in obj_data.items():
                if prop_name in hardware_sr_objects[obj_name]:
                    continue
                hardware_sr_objects[obj_name][prop_name] = prop_data

    @staticmethod
    def get_chip_ref(obj_data: Dict):
        value = obj_data.get(CHIP_KEY)
        if not isinstance(value, str) or not SrParser.is_ref(value):
            return ""
        return value[2:]

    def check_repo_type(self):
        service_path = os.path.join(self.sr_dir, 'mds/service.json')
        try:
            with open(service_path, 'r') as file_descriptor:
                content = json.load(file_descriptor)
                project_name = content.get('name')
                if project_name in ['vpd', 'TaiShanServer2.9.0_CSR', 'TS900-K2_5.0.0_CSR']:
                    self.is_sr_repo = True
                    self.is_product_sr_repo = (project_name != 'vpd')
        except Exception as e:
            log.error('mds/service.json 文件解析失败: %s', e)

    def load_smc_dfx_whitelist(self):
        whitelist_file = Path(__file__).parent.joinpath("smc_dfx_whitelist.json")
        if not os.path.exists(whitelist_file):
            return
        try:
            with open(whitelist_file, 'r') as file_descriptor:
                content = json.load(file_descriptor)
            for item in content:
                chip_type = item.get("ChipType")
                chip_address = item.get("ChipAddress")
                scanner_offset = item.get("ScannerOffset")
                if isinstance(chip_type, str) and isinstance(chip_address, int) and isinstance(scanner_offset, int):
                    self.smc_dfx_whitelist[chip_type].add((chip_address, scanner_offset))
        except Exception as e:
            log.error('smc_dfx_whitelist.json 文件解析失败: %s', e)

    def run(self):
        if not self.is_sr_repo:
            return True
        self.find_soft_sr_files()
        self.walk_sr_dir()
        file_count, problems_total, issues_count = self.log_issues()
        msg = f"Finished SR analysis: found {problems_total} issues in {file_count} files"
        if issues_count["error"]:
            msg += f', errors: {issues_count["error"]}'
        if issues_count["warning"]:
            msg += f', warnings: {issues_count["warning"]}'
        log.info(msg)
        if problems_total == 0:
            log.info("sr 校验通过")
        else:
            log.error("sr 校验失败")
        return problems_total == 0

    def find_soft_sr_files(self):
        for root, _, files in os.walk(self.sr_dir):
            for file in files:
                if not file.endswith(SOFT_SR_SUFFIX):
                    continue
                hard_sr_name = f"{file[:-len(SOFT_SR_SUFFIX)]}.sr"
                soft_sr_path = os.path.join(root, file)
                hard_sr_path = os.path.join(root, hard_sr_name)
                if not os.path.exists(hard_sr_path) and root.endswith(SOFTWARE_SUFFIX):
                    hard_sr_path = os.path.join(root[:-len(SOFTWARE_SUFFIX)], "src", hard_sr_name)
                self.soft_sr_files[hard_sr_path] = soft_sr_path


    def get_soft_sr_objects(self, relpath):
        sr_path = os.path.join(self.sr_dir, relpath)
        if sr_path not in self.soft_sr_files:
            return {}

        soft_sr_path = self.soft_sr_files[sr_path]
        if not os.path.exists(soft_sr_path):
            return {}
        try:
            with open(soft_sr_path, 'r') as file_descriptor:
                content = json.load(file_descriptor)
                return content.get("Objects", {})
        except Exception as e:
            log.error('sr 文件 %s 解析失败: %s', soft_sr_path, e)
            return {}

    def parse_sr(self, relpath: str, sr_content: Dict):
        if relpath.endswith(SOFT_SR_SUFFIX):
            return
        objs = sr_content.get("Objects", {})
        self.merge_sr_objects(objs, self.get_soft_sr_objects(relpath))
        self.sr_objs[relpath] = objs
        self.check_smc_dfx_info(relpath)
        if self.is_product_sr_repo:
            return

        for obj_name, obj_data in objs.items():
            for key, value in obj_data.items():
                if isinstance(value, str):
                    self.parse_prop_val(obj_name, key, value, relpath)

        if "ManagementTopology" in sr_content:
            self.check_topology(sr_content["ManagementTopology"], relpath)

    def parse_prop_val(self, obj_name: str, prop_key: str, prop_val: str, relpath: str):
        for global_sign, target_obj in re.findall(re.compile("(?:<=|#)\/(:*)(\w+)"), prop_val):
            self.objects_used[relpath].add(target_obj)
            if not global_sign and target_obj not in self.sr_objs[relpath]:
                self.issues_report[relpath].add(("error",
                                                 f"'{obj_name}.{prop_key}'同步或引用的对象'{target_obj}'没有在Objects中定义"))
        if not self.is_ref(prop_val) and not self.is_sync(prop_val):
            return

        for val in prop_val.split(';'):
            val = val.strip()
            if not (val.startswith('#/') or val.startswith("<=/")):
                self.issues_report[relpath].add(("error", f"对象'{obj_name}'的属性'{prop_key}'值不规范：{val}"))

    def check_topology(self, management_topology: dict, relpath: str):
        chips = set()
        for node_data in management_topology.values():
            for key, objects in node_data.items():
                for obj in objects:
                    self.objects_used[relpath].add(obj)
                    self.validate_topology_object(key, obj, chips, relpath)

    def validate_topology_object(self, key: str, obj: str, chips: set, relpath: str):
        if key not in ["Connectors", "Chips"]:
            return
        if obj not in self.sr_objs[relpath]:
            self.issues_report[relpath].add(("error", f"器件'{obj}'没有在Objects中列出"))
        if key == "Chips":
            if obj in chips:
                self.issues_report[relpath].add(("error", f"器件'{obj}'有多条上行总线"))
            chips.add(obj)

    def match_smc_dfx_whitelist(self, file_objs: Dict[str, Dict], chip: str, scanner_data: Dict):
        if chip not in file_objs:
            return False
        chip_data = file_objs.get(chip)
        chip_address = chip_data.get("Address")
        scanner_offset = scanner_data.get("Offset")
        if not chip_address or not scanner_offset:
            return False
        return (chip_address, scanner_offset) in self.smc_dfx_whitelist[SrParser.get_class_name(chip)]

    def check_smc_dfx_info(self, relpath: str):
        smc_dfx_info_objs = {}
        for obj_name, obj_data in self.sr_objs[relpath].items():
            chip = self.get_chip_ref(obj_data)
            if chip and self.get_class_name(obj_name) == "SmcDfxInfo":
                smc_dfx_info_objs[chip] = (obj_name, obj_data)
        if not smc_dfx_info_objs:
            return

        for obj_name, obj_data in self.sr_objs[relpath].items():
            chip = self.get_chip_ref(obj_data)
            condition = self.get_class_name(obj_name) == "Scanner" and obj_name != "Scanner_PowerGood" \
                and chip and chip in smc_dfx_info_objs
            condition = condition and not self.match_smc_dfx_whitelist(self.sr_objs[relpath], chip, obj_data)
            if not condition:
                continue
            smc_dfx_info_obj_name, smc_dfx_info_obj_data = smc_dfx_info_objs.get(chip)
            if obj_name not in smc_dfx_info_obj_data.get("Mapping", {}):
                error_msg = f"对象'{obj_name}'没有在对象'{smc_dfx_info_obj_name}'的Mapping中配置"\
                    "（特殊配套原因不能配置的场景，输出子系统DE讨论纪要后增加到白名单bmcgo/component/analysis/smc_dfx_whitelist.json）"
                self.issues_report[relpath].add(("error", error_msg))