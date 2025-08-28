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

from typing import Optional

from dto.options import Options
from base import Base


class NoRenderUtilsException(Exception):
    pass


class Factory:
    _instance = None
    _has_init = False

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not isinstance(Factory._instance, Factory):
            Factory._instance = object.__new__(cls)
        return Factory._instance

    def __init__(self):
        if Factory._has_init:
            return
        self._utils_dict: dict = {}
        Factory._has_init = True

    def new_utils(self, template_name: str, data: dict, options: Options) -> Optional[Base]:
        if not self._utils_dict.get(template_name):
            return NoRenderUtilsException

        if template_name == 'model.lua.mako' and options.version < 4:
            template_name = 'old_model.lua.mako'

        return self._utils_dict.get(template_name)(data, options)

    def register(self, template_name: str, utils_type: type):
        self._utils_dict.setdefault(template_name, utils_type)

    def get(self, template_name: str):
        return self._utils_dict.get(template_name)