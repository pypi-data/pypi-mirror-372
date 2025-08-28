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

import enum
from typing import Dict, List

from dto.print_simple import PrintSimple
from dto.url_route import UrlRoute, UrlRouteDict

ALLOW_BASIC_TYPES = {"bool", "string", "int32", "uint32", "int64", "uint64", "float", "double", "bytes"}


def join_father_options(data: dict, father_options: dict):
    if not father_options:
        return
    data.setdefault("options", {})
    for key in father_options.keys():
        data["options"].setdefault(key, father_options.get(key))


class Mapping(PrintSimple):
    def __init__(self, inner_attr_name: str = "", to_inner_func: str = "", from_inner_func: str = "",
                 auto_enable: bool = True):
        self.inner_attr_name: str = inner_attr_name
        self.to_inner_func: str = to_inner_func
        self.from_inner_func: str = from_inner_func
        self.auto_enable: bool = auto_enable

    @classmethod
    def from_proto_json(cls, data: Dict[str, str]):
        ret = cls()
        ret.inner_attr_name = data.get("v_attr")
        ret.to_inner_func = data.get("cvt_to_inner")
        ret.from_inner_func = data.get("cvt_to_out")
        ret.auto_enable = data.get("auto_map") in [True, 1, "true", "TRUE", "Y", "YES"]
        return ret


class Converter(PrintSimple):
    def __init__(self, raw_convert: str):
        self._raw_convert: str = raw_convert
        self.use_self: bool = False
        self.cvt_fun: str = None
        if raw_convert:
            self.cvt_fun: str = raw_convert.split("@")[0]
            if raw_convert.find("@self") >= 0:
                self.use_self = True

    def valid(self) -> bool:
        return self.cvt_fun not in ["", None]


class Property(PrintSimple):
    def __init__(self, attr_name: str, attr_type: str, route: UrlRoute, mapping: Mapping, out_attr_name: str = None,
                 dft_value: str = None, read_only: bool = False, repeated: bool = False, attr_to_view: Converter = "",
                 attr_from_view: Converter = ""):
        self.attr_name: str = attr_name
        self.attr_type: str = attr_type
        self.url_route: UrlRoute = route
        self.mapping: Mapping = mapping
        self.out_attr_name: str = out_attr_name
        if not self.out_attr_name:
            self.out_attr_name: str = self.attr_name
        self.dft_value: str = dft_value
        if not self.mapping.inner_attr_name:
            self.mapping.inner_attr_name = self.attr_name
        self.read_only: bool = read_only
        self.repeated: bool = repeated
        self.attr_to_view: Converter = attr_to_view
        self.attr_from_view: Converter = attr_from_view

    @classmethod
    def from_proto_json(cls, data: dict, father_options: dict = None):
        options = data.get("options")
        if options is None:
            options = {}
        join_father_options(data, father_options)
        return cls(
            attr_name=data.get("name"),
            attr_type=data.get("type"),
            route=UrlRoute(options),
            mapping=Mapping.from_proto_json(options),
            out_attr_name=options.get("rename"),
            dft_value=options.get("default"),
            read_only=options.get("read_only"),
            repeated=data.get("repeated"),
            attr_to_view=Converter(options.get("attr_to_view")),
            attr_from_view=Converter(options.get("attr_from_view"))
        )

    def complex_type(self, msg_mgr) -> bool:
        if self.attr_type in ALLOW_BASIC_TYPES:
            return False
        msg = msg_mgr.messages.get(self.attr_type)
        if msg is None:
            return False
        return not msg.msg_type.basic_attr()



class Value(PrintSimple):
    def __init__(self, name: str, value: int):
        self.name: str = name
        self.value: int = value

    @classmethod
    def from_proto_json(cls, data: dict):
        return cls(name=data.get("name"), value=data.get("value"))


class ServiceType(enum.Enum):
    DATA = ("_Data", "_data")
    GET = ("Get", "get")
    PUT = ("Put", "put")
    PATCH = ("Patch", "patch")
    POST = ("Post", "post")
    DELETE = ("Delete", "delete")

    def __init__(self, http_name: str, code_name: str):
        self.http_name: str = http_name
        self.code_name: str = code_name

    @classmethod
    def from_json(cls, data: dict):
        for service_type in cls:
            if service_type.http_name == data.get("name"):
                return service_type
        return cls.DATA


REQ_BODY_VAR_NAME = "Body"
REQ_RESPONSE_VAR_NAME = "Response"


class MessageType(enum.Enum):
    ENUM = "Enum"
    MESSAGE = "Message"
    INTERFACE = "Interface"

    @classmethod
    def from_json(cls, data: dict):
        service_type = ServiceType.from_json(data)
        if service_type != ServiceType.DATA:
            return cls.INTERFACE
        for msg_type in cls:
            if msg_type.value == data.get("type"):
                return msg_type
        return cls.MESSAGE

    def basic_attr(self) -> bool:
        return self == MessageType.ENUM


class MessageSchema(PrintSimple):
    def __init__(self):
        self.package: str = ""
        self.name: str = ""
        self.url_route: UrlRoute = UrlRoute({})
        self.auth_enable: bool = False
        self.msg_type: MessageType = MessageType.MESSAGE
        self.service_type: ServiceType = ServiceType.DATA
        self.properties: List[Property] = []
        self.values: List[Property] = []

    @classmethod
    def from_proto_json(cls, data: dict, father: str = "", father_options: dict = None):
        ret = cls()
        options = data.get("options")
        if options is None:
            options = {}
        join_father_options(data, father_options)
        if not father:
            ret.package = data.get("package")
        else:
            ret.package = father
        ret.name = data.get("name")
        ret.url_route = UrlRoute(options)
        if options.get("auth"):
            ret.auth_enable = options.get("auth")
        properties = data.get("properties")
        if properties is None:
            properties = []
        ret.properties = [Property.from_proto_json(pt, data.get("options")) for pt in properties if pt.get("name")]
        values = data.get("values")
        if values is None:
            values = []
        ret.values = [Value.from_proto_json(value) for value in values]
        ret.msg_type = MessageType.from_json(data)
        ret.service_type = ServiceType.from_json(data)
        return ret

    def class_type(self):
        return f"{self.package}.{self.name}"

    def class_var_name(self):
        return self.class_type().lower().replace(".", "_")


class MessageSchemaMgr(PrintSimple):
    def __init__(self):
        self.messages: Dict[str, MessageSchema] = {}
        self._msg_route_map: Dict[str, UrlRouteDict] = {}

    def append(self, msg: MessageSchema):
        self.messages.setdefault(msg.class_type(), msg)

    def related_objects(self, msg: MessageSchema) -> UrlRouteDict:
        if self._msg_route_map.get(msg.class_type()):
            return self._msg_route_map.get(msg.class_type())
        route_dict = self._calc_related_url_route(msg)
        self._msg_route_map.setdefault(msg.class_type(), route_dict)
        return route_dict

    def _calc_related_url_route(self, msg: MessageSchema):
        route_dict = UrlRouteDict()
        if not msg:
            return route_dict
        if msg.msg_type.basic_attr():
            return route_dict
        for pt in msg.properties:
            route_dict.add_url(pt.url_route, msg.url_route)
            if pt.attr_type not in ALLOW_BASIC_TYPES:
                sub_msg = self.messages.get(pt.attr_type)
                if sub_msg:
                    route_dict.extend(self.related_objects(sub_msg))
        return route_dict


class FatherFields:
    def __init__(self):
        self.father_options: dict = {}
        self.father: str = ""
