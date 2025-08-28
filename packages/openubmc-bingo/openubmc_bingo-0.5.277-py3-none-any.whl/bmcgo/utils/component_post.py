#!/usr/bin/env python
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

"""
文件名：component_post.py
功能：获取对应路径下的python脚本，并执行其中的方法
"""

import os
import importlib
import sys
from inspect import getmembers, isfunction

from conans.model.profile import Profile
from bmcgo.utils.config import Config
from bmcgo.utils.tools import Tools
from bmcgo.logger import Logger

log = Logger("component_post")


class ComponentPost():
    def __init__(self, config: Config, component_path, profile: Profile):
        sys.path.insert(0, os.path.dirname(component_path))
        cust_py = importlib.import_module(f"{os.path.basename(component_path)}.include.customization", "customization")
        self.cust_cls = getattr(cust_py, "Customization")
        self.config = config
        self.component_path = component_path
        self.profile = profile

    def post_work(self, work_path, func_name):
        if Tools.has_kwargs(self.cust_cls.__init__):
            # 支持组件新的Customization的__init__(board_name, rootfs_path, **kwargs)
            real_post = self.cust_cls(self.config.board_name, work_path, profile=self.profile)
        else:
            # 兼容之前组件Customization的__init__(board_name, rootfs_path)
            real_post = self.cust_cls(self.config.board_name, work_path)
        func_tuple_list = getmembers(self.cust_cls, isfunction)
        func_list = [func_tuple_list[i][0] for i in range(len(func_tuple_list))]
        if func_name not in func_list:
            log.info(f"组件 {os.path.basename(self.component_path)} 中没有 {func_name} 方法")
        else:
            getattr(real_post, func_name)()
            log.info(f"组件 {os.path.basename(self.component_path)} {func_name} 执行完成")
        sys.path.pop(0)
