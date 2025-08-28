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

from dto.options import Options
from render_utils.utils_message_lua import UtilsMessageLua
from render_utils.validate_lua import ValidateLua
from bmcgo.codegen.lua.script.base import Base
from bmcgo.codegen.lua.script.factory import Factory


class IpmiMessageUtils(Base, ValidateLua, UtilsMessageLua):
    def __init__(self, data: dict, options: Options):
        super().__init__(data, options)

Factory().register("ipmi_message.lua.mako", IpmiMessageUtils)
