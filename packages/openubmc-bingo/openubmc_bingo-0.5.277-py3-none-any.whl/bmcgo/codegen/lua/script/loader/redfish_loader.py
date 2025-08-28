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

import os
from typing import Set, List, Dict

from dto.exception import MessageParseException
from dto.redfish_api import MessageSchemaMgr, MessageSchema, MessageType, join_father_options, ALLOW_BASIC_TYPES, \
    FatherFields
from loader.file_utils import load_json


def json_file_path(rel_path: str):
    if not rel_path.endswith(".json"):
        return f"{rel_path}.json"
    return rel_path


class RedfishLoader:
    def __init__(self, root_path: str, full_file_path: str, father_options_dict: Dict[str, dict] = None):
        self.root_path: str = root_path
        self.full_file_path: str = full_file_path
        self.father_options_dict: Dict[str, dict] = father_options_dict
        if self.father_options_dict is None:
            self.father_options_dict = {}

    @staticmethod
    def _get_property_json(msg: dict, attr_name: str) -> dict:
        for pt in msg.get("properties"):
            if pt.get("name") == attr_name:
                return pt
        raise MessageParseException(f"在 {msg.get('package')}.{msg.get('name')} 中无法找到 {attr_name}")

    @staticmethod
    def _extend_property_options(index, msg, parsed_msg_list):
        for pt in parsed_msg_list[index].properties:
            pt_json = RedfishLoader._get_property_json(msg, pt.attr_name)
            join_father_options(pt_json, msg.get("options"))
            pt.url_route.merge_options(pt_json.get("options"))

    def parse(self, schema_mgr: MessageSchemaMgr, parsed_file_set: Set[str] = None,
              father_options: dict = None) -> List[MessageSchema]:
        if parsed_file_set is None:
            parsed_file_set = set()
        json_data = load_json(self.full_file_path)
        father_fields = FatherFields()
        father_fields.father_options = father_options
        interfaces = self._parse_data(json_data.get("data"), schema_mgr, parsed_file_set, father_fields)
        self._parse_dependency(json_data, parsed_file_set, schema_mgr)
        return interfaces

    def interface_list(self, schema_mgr: MessageSchemaMgr) -> List[MessageSchema]:
        return [msg for msg in self.parse(schema_mgr) if msg.msg_type == MessageType.INTERFACE]

    def join_extend_options(self, father_options, msg):
        temp_father_options = self.father_options_dict.get(msg.get("package") + "." + msg.get("name"))
        if temp_father_options is None:
            temp_father_options = father_options
        join_father_options(msg, temp_father_options)

    def _collect_property_options(self, message, msg, force: bool = False):
        for pt in message.properties:
            if pt.attr_type not in ALLOW_BASIC_TYPES:
                if force:
                    self.father_options_dict[pt.attr_type] = msg.get("options")
                else:
                    self.father_options_dict.setdefault(pt.attr_type, msg.get("options"))

    def _parse_dependency(self, json_data, parsed_file_set, schema_mgr):
        if not json_data.get("dependency"):
            return
        for dependency in json_data.get("dependency"):
            if dependency == "types.proto":
                continue
            file_path = os.path.normpath(os.path.join(self.root_path, json_file_path(dependency)))
            if file_path in parsed_file_set:
                continue
            parsed_file_set.add(file_path)
            loader = RedfishLoader(self.root_path, file_path, self.father_options_dict)
            loader.parse(schema_mgr, parsed_file_set)

    def _parse_data(self, msg_list: List[dict], schema_mgr: MessageSchemaMgr, parsed_file_set: Set[str],
                    father_fields: FatherFields) -> List[MessageSchema]:
        if not msg_list:
            return []
        ret: List[MessageSchema] = []
        for msg in msg_list:
            self.join_extend_options(father_fields.father_options, msg)
            message = MessageSchema.from_proto_json(msg, father_fields.father, msg.get("options"))
            schema_mgr.append(message)
            self._collect_property_options(message, msg)
            ret.append(message)
            f_fields = FatherFields()
            f_fields.father_options = msg.get("options")
            f_fields.father = message.class_type()
            ret.extend(
                self._parse_data(msg.get("nested_type"), schema_mgr, parsed_file_set, f_fields))
        self._extend_msg_options(father_fields.father_options, msg_list, ret)
        return ret

    def _extend_msg_options(self, father_options: dict,
                            raw_msg_list: List[dict], parsed_msg_list: List[MessageSchema], input_index: int = 0):
        if not raw_msg_list:
            return input_index
        has_changed = True
        while has_changed:
            has_changed = False
            index = input_index
            for msg in raw_msg_list:
                self.join_extend_options(father_options, msg)
                if parsed_msg_list[index].url_route.merge_options(msg.get("options")):
                    has_changed = True
                    self._extend_property_options(index, msg, parsed_msg_list)
                    self._collect_property_options(parsed_msg_list[index], msg, force=True)
                index += 1
                index = self._extend_msg_options(msg.get("options"), msg.get("nested_type"),
                                                 parsed_msg_list, index)
        return index
