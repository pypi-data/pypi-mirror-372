#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import json
import stat
from collections import OrderedDict
from bmcgo.tasks.task import Task
from bmcgo.logger import Logger

log = Logger("combine_json_schemas")


class CombineJsonSchemas(Task):
    '''
    用途: 支持产品定制差异化json schema文件, 用于产品扩展装备定制化的默认值和属性
    说明:
        1、该脚本在构建阶段整合组件原始schema和产品差异化schema文件, 同时生成装备定制化默认配置default_settings.json
        2、json schema文件来自装备定制化定义的schema文件(复用配置导入导出schema文件)
        3、该脚本属于装备定制化处理产品差异的通用机制, 虽然与产品有关, 但是脚本本身不处理产品差异(由一级流水线完成产品差异处理)
    '''
    def __init__(self, config, schema_path, work_name=""):
        super(CombineJsonSchemas, self).__init__(config, work_name)
        self.schema_path = schema_path
        self.custom_path_name = "custom"
        self.default_settings = "default_settings.json"
        self.config = config
        self.schema_tmp = os.path.join(config.build_path, "profile_schema")

    def handle_type_change(self, dict1, dict2):
        # 键值相同，但是类型由object变化为array
        if "type" in dict1 and dict1["type"] == "object" and dict2["type"] == "array":
            dict1.pop("properties")
        # 键值相同，但是类型由array变化为object
        if "type" in dict1 and dict1["type"] == "array" and dict2["type"] == "object":
            dict1.pop("items")

    # 将dict2合并到dict1
    def merge_dicts(self, dict1, dict2):
        for key, value in dict2.items():
            if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
                # 处理键值相同，但是类型发生变化的情况
                self.handle_type_change(dict1[key], value)
                self.merge_dicts(dict1[key], value)
            else:
                dict1[key] = value

    def has_key(self, dict_ins, key_str):
        if not dict_ins:
            return False

        if not isinstance(dict_ins, dict):
            return False

        return key_str in dict_ins.keys()

    # 递归解析schema内部结构
    def rec_parse(self, data):
        if data['type'] == 'array':    # 定制数据是明确的条目，配置不存在于数组中
            return {}

        if data['type'] == 'object':
            sub_objs = data['properties']
            ret_data = OrderedDict()
            for key in sub_objs:
                tmp = self.rec_parse(sub_objs[key])
                if tmp != {}:
                    ret_data[key] = tmp

            return ret_data

        if self.has_key(data, 'CustomDefault'):
            return {'AttributeType':'ImportAndExport', 'Import': True, 'Value': data['CustomDefault']}

        return {}

    def load_schema(self, path, product_schema_path, com_obj):
        # 临时的产品schema路径下无需求处理
        if product_schema_path == os.path.dirname(path):
            return
        with open(path, 'r') as handle:
            data = json.load(handle, object_pairs_hook=OrderedDict)
            tmp = self.rec_parse(data['properties']['ConfigData'])
            if tmp != {}:
                com_obj['ConfigData'] = tmp

    def load_json_file(self, json_file):
        with open(json_file) as f:
            return json.load(f, object_pairs_hook=OrderedDict)

    def save_json_file(self, json_file, mode, json_dict):
        log.info(f"保存 json 文件: {json_file}")
        with os.fdopen(os.open(json_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as fp:
            json.dump(json_dict, fp, indent=4)
        self.run_command(f"chmod {mode} {json_file}")

    # 将原始schema文件和产品差异化schema文件结合后生成组件新的schema文件
    def regenerate_schema(self, path, product_schema_path, origin_schema):
        # 不存在产品差异化schema时则无需处理; 临时的产品schema路径下无需求处理
        if not os.path.exists(product_schema_path) or product_schema_path == os.path.dirname(path):
            return
        product_schemas = sorted(os.listdir(product_schema_path))
        # 存在与原始schema名称一致的产品差异化schema文件时，合并schema文件
        if origin_schema in product_schemas:
            origin_dict = self.load_json_file(os.path.join(path, origin_schema))
            product_dict = self.load_json_file(os.path.join(product_schema_path, origin_schema))
            self.merge_dicts(origin_dict, product_dict)
            self.save_json_file(os.path.join(path, origin_schema), 440, origin_dict)

    # 遍历所有schema文件
    def walk_schema(self, path, product_schema_path, com_objs):
        files = sorted(os.listdir(path))
        for file in files:
            sub_path = os.path.join(path, file)
            if os.path.isdir(sub_path):
                self.walk_schema(sub_path, product_schema_path, com_objs)
            else:
                seps = file.split('.')
                if seps[1] != 'json':
                    continue
                self.regenerate_schema(path, product_schema_path, file)
                app_name = seps[0]
                if not self.has_key(com_objs, app_name):
                    com_objs[app_name] = {}

                self.load_schema(sub_path, product_schema_path, com_objs[app_name])

    def gen_default_settings(self):
        log.info(f"开始生成配置: {self.default_settings}")
        if not os.path.isdir(self.schema_path):
            raise Exception('schema 文件的目标必须为文件夹')

        # 1.准备临时目录，支持非root构建
        # 清理临时schema路径, 防止上次构建失败导致路径残留
        if os.path.exists(self.schema_tmp):
            self.run_command(f"rm -rf {self.schema_tmp}", sudo=True)
        # 拷贝schema路径到构建临时路径
        self.run_command(f"cp -r {self.schema_path} {self.config.build_path}", sudo=True)
        # 修改权限为当前用户
        user_group = f"{os.getuid()}:{os.getgid()}"
        self.run_command(f"chown -R {user_group} {self.schema_tmp}", sudo=True)
        self.run_command(f"chmod -R 750 {self.schema_tmp}", sudo=True) # 增加写权限, 防止创建子目录失败
        # 创建custom路径存放默认配置
        custom_tmp = os.path.join(self.schema_tmp, self.custom_path_name)
        if not os.path.exists(custom_tmp):
            self.run_command(f"mkdir {custom_tmp}")
        self.run_command(f"chmod +w {custom_tmp}") # 增加写权限, 保存default_settings.json

        # 2.整合schema文件
        product_schema_tmp = os.path.join(self.schema_tmp, "product")
        com_objs = OrderedDict()
        ret_data = {'Components': com_objs}
        self.walk_schema(self.schema_tmp, product_schema_tmp, com_objs)
        self.save_json_file(os.path.join(custom_tmp, self.default_settings), 440, ret_data)

        # 3.拷贝整合后的schema文件到源目录
        self.run_command(f"cp -rf {self.schema_tmp}/. {self.schema_path}", sudo=True)
        self.run_command(f"chmod 550 {os.path.join(self.schema_path, self.custom_path_name)}", sudo=True)
        # 4.清理临时目录
        self.run_command(f"rm -rf {self.schema_tmp}", sudo=True)