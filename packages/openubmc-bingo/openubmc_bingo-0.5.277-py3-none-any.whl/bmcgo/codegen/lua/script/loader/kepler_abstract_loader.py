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

import json
from typing import List

from dto.exception import JsonTypeException, UrlNotMatchException
from dto.kepler_abstract import KeplerAbstractMgr, KeplerAbstract
from dto.redfish_api import MessageSchemaMgr, MessageSchema
from loader.redfish_loader import RedfishLoader


def load(file_path) -> KeplerAbstractMgr:
    abstract_mgr = KeplerAbstractMgr()
    with open(file_path, "r", encoding="utf-8") as fd:
        json_str = json.load(fd)
        JsonTypeException.check_list(json_str)
        for data in json_str:
            JsonTypeException.check_dict(data)
            abstract_mgr.add(KeplerAbstract.from_json(data))
    return abstract_mgr


def load_related_kepler_schemas(root_path: str,
                                routes: List[MessageSchema],
                                redfish_schema_mgr: MessageSchemaMgr,
                                abstract_mgr: KeplerAbstractMgr) -> MessageSchemaMgr:
    schema_mgr = MessageSchemaMgr()
    parsed_file_set = set()
    for route in routes:
        url_dict = redfish_schema_mgr.related_objects(route)
        for url in url_dict.url_dict.values():
            abstract_info = abstract_mgr.get(url.url_feature)
            if not abstract_info:
                raise UrlNotMatchException(url.url)
            loader = RedfishLoader(root_path, abstract_info.file_path)
            loader.parse(schema_mgr, parsed_file_set)
    return schema_mgr
