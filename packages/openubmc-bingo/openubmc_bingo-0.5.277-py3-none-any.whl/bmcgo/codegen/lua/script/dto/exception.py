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


class MessageParseException(Exception):
    pass


class UrlParseException(Exception):
    pass


class JsonTypeException(Exception):
    @staticmethod
    def check_dict(data):
        if not isinstance(data, dict):
            raise JsonTypeException(f"需要一个 dict 类型, 但是 '{data}' 类型为 '{type(data)}'")

    @staticmethod
    def check_list(data):
        if not isinstance(data, list):
            raise JsonTypeException(f"需要一个 list 类型, 但是 '{data}' 类型为 '{type(data)}'")

    @staticmethod
    def check_string(data: dict, attr_name):
        JsonTypeException.check_dict(data)
        if not isinstance(data.get(attr_name), (str, bytes)):
            raise JsonTypeException(f"需要一个 string 类型, 但是 '{attr_name}' 类型为 '{type(data.get(attr_name))}'")

    @staticmethod
    def check_integer(data: dict, attr_name):
        JsonTypeException.check_dict(data)
        if not isinstance(data.get(attr_name), (int, bool)):
            raise JsonTypeException(f"需要一个 integer 类型, 但是 '{attr_name}' 类型为 '{type(data.get(attr_name))}'")

    @staticmethod
    def check_float(data: dict, attr_name):
        JsonTypeException.check_dict(data)
        if not isinstance(data.get(attr_name), (int, bool, float)):
            raise JsonTypeException(f"需要一个 float 类型, 但是 '{attr_name}' 类型为 '{type(data.get(attr_name))}'")


class UrlNotMatchException(Exception):
    pass
