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

from typing import Dict, List, Optional

from dto.exception import UrlParseException
from dto.print_simple import PrintSimple

GET_URL_SEG_FUNC = "GetUrl"  # 传入URL路径和参数位置，获取参数值的函数, 如: GetUrl(path, id)
REQ_PARAMS = "req.params"


class Variable(PrintSimple):
    def __init__(self, name: str, segment_pos: int, order: int):
        self.name: str = name
        self.segment_pos: int = segment_pos
        self.order: int = order

    def to_param_name(self):
        return self.name.lower().replace(":", "")


class Url(PrintSimple):
    def __init__(self, url: str):
        self.url = url
        self.segments: List[str] = []
        if self.url:
            self.segments: List[str] = url.split("/")
        self.variable_list: List[Variable] = []
        self.url_feature: str = ""
        self._parse_url_variable_id(url)

    def __eq__(self, other) -> bool:
        return self.url == other.url

    def relative_json_path(self):
        return "/".join([seg for seg in self.segments if seg.find(":") < 0]) + ".proto.json"

    def find_variable_by_name(self, mapping_name: str) -> Optional[Variable]:
        ret = None
        for variable in self.variable_list:
            if variable.name == mapping_name:
                return variable
        return ret

    def find_variable_by_variable(self, outer_var: Variable) -> Optional[Variable]:
        var = None
        var = self.find_variable_by_name(outer_var.name)
        if var:
            return var
        for variable in self.variable_list:
            if variable.order == outer_var.order:
                return variable
        return var

    def find(self, outer_var: Variable, mapping_name: str = None) -> Optional[Variable]:
        var = self.find_variable_by_name(mapping_name)
        if var:
            return var
        return self.find_variable_by_variable(outer_var)

    def _parse_url_variable_id(self, url):
        self.url_feature = ""
        if url is None:
            return
        seg_list = []
        pos = 0
        for name in self.segments:
            if name.startswith(":"):
                self.variable_list.append(Variable(name, pos, len(self.variable_list)))
                seg_list.append(":id")
            else:
                seg_list.append(name)
            pos += 1
        self.url_feature = "/".join(seg_list)


class UrlRoute(PrintSimple):
    def __init__(self, options: Dict[str, str]):
        if options.get("url"):
            self.outer = Url(options.get("url"))
        else:
            self.outer = Url(options.get("path"))
        self.inner = Url(options.get("inner_url"))
        self.interface: str = options.get("interface")
        self.outer_variable_mapping: Dict[str, str] = {}
        self.inner_variable_mapping: Dict[str, str] = {}
        variable_mapping = options.get("variable_mapping")
        self._parse_variable_mapping(variable_mapping)

    def __eq__(self, other):
        return self.outer == other.outer and self.inner == other.inner and \
               self.inner_variable_mapping == other.inner_variable_mapping and \
               self.outer_variable_mapping == other.outer_variable_mapping

    @staticmethod
    def _check_variable_exists(mapping: str, url: Url, variable_id: str):
        if url.url is None:
            return
        if not url.find_variable_by_name(variable_id):
            raise UrlParseException(f"{mapping} 错误, {variable_id} 不在 {url.url} 中")

    @staticmethod
    def _merge_code(ret_list, join_tag=".."):
        ret = ""
        for i, _ in enumerate(ret_list):
            if i != 0:
                ret += join_tag
            if ret_list[i].find(REQ_PARAMS) >= 0:  # 该段是变量场景
                ret += ret_list[i]
                if i < len(ret_list) - 1 and ret_list[i + 1].find(REQ_PARAMS) >= 0:  # 紧跟着的也是变量
                    ret += join_tag + '"/"'
                continue
            if len(ret_list) > 1 + i:
                ret += f'"{ret_list[i]}/"'
            else:
                if i > 0:
                    ret += f'"/{ret_list[i]}"'
                else:
                    ret += f'"{ret_list[i]}"'
        return ret

    def valid(self) -> bool:
        return self.inner.url not in [None, ""] and self.outer.url not in [None, ""]

    def merge_options(self, options: dict) -> bool:
        if self.outer.url != options.get("url") or self.inner.url != options.get("inner_url"):
            self.outer = Url(options.get("url"))
            self.inner = Url(options.get("inner_url"))
            return True
        return False

    def inner_url_code(self, join_tag="..") -> str:
        ret_list = []
        start_pos = 0
        for variable in self.inner.variable_list:
            buff = "/".join(self.inner.segments[start_pos:variable.segment_pos])
            if buff:
                ret_list.append(f'{buff}')
            out_var = self.outer.find(variable, self.inner_variable_mapping.get(variable.name))
            if out_var is None:
                raise UrlParseException(f"没有匹配到变量: {variable}")
            ret_list.append(f"{REQ_PARAMS}.{out_var.to_param_name()}")
            start_pos = variable.segment_pos + 1
        buff = "/".join(self.inner.segments[start_pos:])
        if buff:
            ret_list.append(f'{buff}')
        return self._merge_code(ret_list, join_tag)

    def _parse_variable_mapping(self, variable_mapping):
        if len(self.inner.variable_list) > len(self.outer.variable_list):
            raise UrlParseException("内部地址变量数量 %s > 外部地址变量 %s." % (
                len(self.inner.variable_list), len(self.outer.variable_list)))
        if variable_mapping is not None:
            self._parse_user_define_mapping(variable_mapping)

    def _parse_user_define_mapping(self, variable_mapping):
        for kv in variable_mapping.split():
            if kv.find("=") <= 0:
                continue
            outer_variable_id = kv.split("=")[0].strip()  # 前面有find判断, 这里是=前面部分
            inner_variable_id = kv.split("=")[1].strip()  # 前面有find判断, 这里是=后面部分
            self._check_variable_exists(kv, self.outer, outer_variable_id)
            self._check_variable_exists(kv, self.inner, inner_variable_id)
            self.outer_variable_mapping[outer_variable_id] = inner_variable_id
            self.inner_variable_mapping[inner_variable_id] = outer_variable_id


class UrlRouteDict:
    def __init__(self):
        self.url_dict: Dict[str, Url] = {}  # kepler 访问代码 --> Url的映射

    def add_url(self, attr_route: UrlRoute, class_route: UrlRoute):
        if attr_route.valid():
            if class_route.valid():
                if attr_route == class_route:
                    self.url_dict.setdefault(class_route.inner_url_code(), class_route.inner)
                    return
            self.url_dict.setdefault(attr_route.inner_url_code(), attr_route.inner)
        else:
            if class_route.valid():
                self.url_dict.setdefault(class_route.inner_url_code(), class_route.inner)

    def extend(self, other):
        for key in other.url_dict.keys():
            self.url_dict.setdefault(key, other.url_dict.get(key))
