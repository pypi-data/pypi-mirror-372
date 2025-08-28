#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
from enum import Enum, EnumMeta, auto


class StringEnumMeta(EnumMeta):
    def __contains__(cls, value):
        return value in cls._value2member_map_

    def __iter__(cls):
        return (mem.value for mem in super().__iter__())

    def __repr__(cls):
        return repr(list(cls))

    def __str__(cls):
        return str(list(cls))


class BaseStringEnum(str, Enum, metaclass=StringEnumMeta):
    def __str__(self):
        return self.value

    def __repr__(self):
        return f"'{self.value}'"

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    @classmethod
    def _missing_(cls, value):
        for mem in cls:
            if mem.value.lower() == value:
                return mem
        return None
