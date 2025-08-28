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

import re
from numbers import Number
from typeguard import typechecked, check_type, Optional


@typechecked
def lens(min_num: Optional[int], max_num: Optional[int]):
    return ("lens", [min_num, max_num])


@typechecked
def len_or_none(min_num: Optional[int], max_num: Optional[int]):
    return ("len_or_none", [min_num, max_num])


@typechecked
def ranges(min_num: Optional[Number], max_num: Optional[Number]):
    return ("ranges", [min_num, max_num])


@typechecked
def range_or_none(min_num: Optional[Number], max_num: Optional[Number]):
    return ("range_or_none", [min_num, max_num])


@typechecked
def regex(rx: str):
    try:
        check_type("rx", re.compile(rx), re.Pattern)
    except RuntimeError as ex:
        raise RuntimeError("(regex)正则表达式校验失败: {}".format(rx)) from e
    return ("regex", [rx])


@typechecked
def regex_or_none(rx: str):
    try:
        check_type("rx", re.compile(rx), re.Pattern)
    except RuntimeError as ex:
        raise RuntimeError(
            "(regexornone)正则表达式校验失败: {}".format(rx)) from e
    return ("regex_or_none", [rx])


@typechecked
def enum(enums: list):
    return ("enum", enums)


@typechecked
def enum_or_none(enums: list):
    return ("enum_or_none", enums)


validates = {
    "lens": lens,
    "len_or_none": len_or_none,
    "ranges": ranges,
    "range_or_none": range_or_none,
    "regex": regex,
    "regex_or_none": regex_or_none,
    "enum": enum,
    "enum_or_none": enum_or_none
}


def all_validates():
    return validates
