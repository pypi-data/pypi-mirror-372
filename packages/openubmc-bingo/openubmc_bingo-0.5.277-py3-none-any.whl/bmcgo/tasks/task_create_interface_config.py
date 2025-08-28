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

import os
import shutil
from functools import wraps
from bmcgo.utils.config import Config
from bmcgo.tasks.task import Task
from bmcgo.utils.mapping_config_patch import MappingConfigGenerate
from bmcgo import misc


class TaskClass(Task):
    def __init__(self, config: Config, work_name=""):
        super(TaskClass, self).__init__(config, work_name)
        self.interface_config_path = os.path.join(os.path.dirname(self.config.inner_path), "interface_config")
        self.product_path = os.path.join(self.interface_config_path, "Product/interface_config_Product")
        self.interface_config_temp_path = os.path.join(self.config.build_path, 'temp_interface_config')
        self.product_temp_path = os.path.join(self.interface_config_temp_path, "resource")
        self.rootfs_path = os.path.join(self.config.buildimg_dir, 'rtos_with_driver/rootfs')
        self.custom_list = {}

    @staticmethod
    def execute_all_interface(func):
        interface_list = ["redfish", "web_backend", misc.CLI, "snmp"]

        @wraps(func)
        def wrapper(*args, **kwargs):
            for interface in interface_list:
                # 遍历所有北向接口
                func(interface=interface, *args, **kwargs)

        return wrapper

    def clear_dir(self, dst_file_path, if_init=True):
        if os.path.exists(dst_file_path):
            shutil.rmtree(dst_file_path)
        if if_init:
            os.makedirs(dst_file_path, exist_ok=True)

    @execute_all_interface
    def get_resource_config_file(self, interface):
        config_path = os.path.join(self.rootfs_path, "opt/bmc/apps", interface, "interface_config")
        if not os.path.isdir(config_path):
            self.error(f"{interface}接口配置文件不存在")
            return
        os.makedirs(self.product_temp_path, exist_ok=True)
        output_config_path = os.path.join(self.product_temp_path, interface)
        if os.path.exists(output_config_path):
            shutil.rmtree(output_config_path)
        shutil.copytree(config_path, output_config_path)

    @execute_all_interface
    def get_custom_list(self, interface):
        custom_dir_path = os.path.join(self.product_temp_path, interface, "customer")
        if os.path.isdir(custom_dir_path):
            for custom in os.listdir(custom_dir_path):
                self.custom_list[custom] = True

    @execute_all_interface
    def custom_config_patch(self, interface, custom_temp_path, custom):
        config_file_path = os.path.join(custom_temp_path, interface)
        if not os.path.exists(config_file_path):
            return
        generate_work = MappingConfigGenerate(self.config, config_path=config_file_path, custom=custom)
        try:
            generate_work.run()
        except Exception as e:
            self.error("生成{}接口配置时发生错误: {}".format(custom, e))

    @execute_all_interface
    def remove_custom_patch(self, interface, custom):
        customer_patch_file = os.path.join(self.interface_config_temp_path, custom, interface, "customer")
        if os.path.exists(customer_patch_file):
            shutil.rmtree(customer_patch_file)

    def create_custom_config(self):
        for custom in self.custom_list:
            custom_temp_path = os.path.join(self.interface_config_temp_path, custom)
            if os.path.exists(custom_temp_path):
                shutil.rmtree(custom_temp_path)
            shutil.copytree(self.product_temp_path, custom_temp_path)
            self.custom_config_patch(custom_temp_path=custom_temp_path, custom=custom)
            self.remove_custom_patch(custom=custom)
            custom_path = os.path.join(self.interface_config_path, custom, "interface_config_" + custom)
            self.clear_dir(os.path.dirname(custom_path))
            shutil.make_archive(custom_path, "zip", custom_temp_path)
        self.remove_custom_patch(custom="resource")
        self.clear_dir(os.path.dirname(self.product_path))
        shutil.make_archive(self.product_path, "zip", self.product_temp_path)

    def create_interface_config(self):
        self.clear_dir(self.interface_config_path)
        self.clear_dir(self.interface_config_temp_path)

        os.makedirs(self.product_temp_path, exist_ok=True)
        # 获取配置文件
        self.get_resource_config_file()
        # 获取客户定制厂商名
        self.get_custom_list()
        # 生成映射配置
        self.create_custom_config()
        # 清理临时目录
        self.clear_dir(self.interface_config_temp_path, if_init=False)

    def run(self):
        try:
            self.info("开始生成全量接口配置")
            self.create_interface_config()
            self.info("生成全量接口配置完成")

        except Exception as e:
            self.error("生成全量接口配置时发生错误: {}".format(e))