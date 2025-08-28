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
from typing import Dict

from dto.exception import UrlNotMatchException
from dto.kepler_abstract import KeplerAbstractMgr
from dto.options import Options
from dto.redfish_api import MessageSchemaMgr, MessageSchema, Property
from dto.url_route import UrlRouteDict
from loader import kepler_abstract_loader
from loader.redfish_loader import RedfishLoader
from bmcgo.codegen.lua.script.factory import Factory
from bmcgo.codegen.lua.script.base import Base


class RequestLua:
    def __init__(self, msg_mgr: MessageSchemaMgr, abstract_mgr: KeplerAbstractMgr, kepler_msg_mgr: MessageSchemaMgr):
        self.msg_mgr = msg_mgr
        self.abstract_mgr = abstract_mgr
        self.msg_route_map: Dict[str, UrlRouteDict] = {}
        self.kepler_msg_mgr: MessageSchemaMgr = kepler_msg_mgr

    def get(self, message_name: str) -> MessageSchema:
        return self.msg_mgr.messages.get(message_name)

    def related_objects(self, message_name: str) -> UrlRouteDict:
        if self.msg_route_map.get(message_name):
            return self.msg_route_map.get(message_name)
        msg = self.get(message_name)
        ret = self.msg_mgr.related_objects(msg)
        self.msg_route_map.setdefault(message_name, ret)
        return ret

    def related_message(self, url_feature: str) -> MessageSchema:
        abstract = self.abstract_mgr.get(url_feature)
        if not abstract:
            raise UrlNotMatchException(url_feature)
        return self.kepler_msg_mgr.messages.get(abstract.class_type())

    def inner_var(self, message_name: str, pt: Property) -> str:
        url_feature = self.related_objects(message_name).url_dict.get(pt.url_route.inner_url_code()).url_feature
        return self.related_message(url_feature).class_var_name()


class RequestLuaExt(RequestLua):
    def __init__(self, data, options: Options):
        self.data = data
        loader = RedfishLoader(options.proto_json_root_path, options.source_file_path)
        schema_mgr = MessageSchemaMgr()
        interfaces = loader.interface_list(schema_mgr)
        abstract_mgr = kepler_abstract_loader.load(os.path.join(options.kepler_root_path, "abstract.json"))
        kepler_schema_mgr = kepler_abstract_loader.load_related_kepler_schemas(
            options.kepler_root_path, interfaces, schema_mgr, abstract_mgr)
        super().__init__(schema_mgr, abstract_mgr, kepler_schema_mgr)


class RequestLuaUtils(Base, RequestLuaExt):
    def __init__(self, data: dict, options: Options):
        super().__init__(data=data, options=options)

    def name(self) -> str:
        return "request.lua.mako"


Factory().register("request.lua.mako", RequestLuaUtils)
