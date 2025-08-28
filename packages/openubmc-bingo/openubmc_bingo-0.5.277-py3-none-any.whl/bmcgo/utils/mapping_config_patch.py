#!/usr/bin/python
# -*- coding: UTF-8 -*-
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
import json
import copy
import stat
import re

from bmcgo.tasks.task import Task
from bmcgo.logger import Logger
from bmcgo import misc

log = Logger("mapping_config_patch")

permission_dict = {
    "redfish": {"rd": 550, "r": 440, "user": [104, 104]},
    "web_backend": {"rd": 550, "r": 440, "user": [104, 104]},
    "snmp": {"rd": 550, "r": 440, "user": [95, 95]},
    misc.CLI: {"rd": 555, "r": 444, "user": [0, 0]}
}


def is_valid_path(path, prefix, check_is_exist):
    real_path = os.path.realpath(path)
    if not real_path.startswith(prefix):
        log.error(f"无效的路径：{path}")
        return False

    if check_is_exist and not os.path.exists(path):
        log.error(f"无效的路径，指定的文件/目录不存在：{path}")
        return False
    return True


def load_json_file(json_file):
    with open(json_file, "r") as f:
        return json.load(f)


def save_json_file(json_file, json_dict):
    log.info(f"保存 json 文件到: {json_file}")
    with os.fdopen(os.open(json_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                            stat.S_IWUSR | stat.S_IRUSR), 'w') as fp:
        json.dump(json_dict, fp, separators=(',', ':'))


def split_prop_name(prop):
    array = prop.split("/")
    for i, x in enumerate(array):
        try:
            num = int(x)
            array[i] = num - 1
        except ValueError:
            pass

    return array


# 删除json节点
def remove_json_prop(obj, array, depth):
    if not isinstance(obj, (dict, list)):
        return

    size = len(array) - 1
    if depth > size:
        return
    elif depth == size:
        if isinstance(obj, dict) and array[depth] in obj:
            del obj[array[depth]]
        elif isinstance(obj, list) and array[depth] < len(obj):
            del obj[array[depth]]
    else:
        node = None
        if isinstance(obj, dict) and obj.get(array[depth]) is not None:
            node = obj.get(array[depth])
        elif isinstance(obj, list) and array[depth] < len(obj):
            node = obj[array[depth]]
        if node is not None:
            remove_json_prop(node, array, depth + 1)


# 深度合并两个json，list和dict采用合并，其他采用覆盖
def merge_json(obj1, obj2):
    if not isinstance(obj1, type(obj2)) or not isinstance(obj1, (dict, list)):
        return

    if isinstance(obj1, dict):
        for key, value in obj2.items():
            if not obj1.get(key) or not isinstance(obj1[key], type(value)) or not isinstance(value, (dict, list)):
                obj1[key] = copy.deepcopy(value)
            else:
                merge_json(obj1[key], obj2[key])

    if isinstance(obj1, list):
        for item in obj2:
            obj1.append(copy.deepcopy(item))


# 重命名json节点
def rename_json_prop(obj, array, depth, new_key):
    if not isinstance(obj, (dict, list)):
        return

    size = len(array) - 1
    if depth > size:
        return
    elif depth == size:
        if isinstance(obj, dict) and obj.get(array[depth]) is not None:
            obj[new_key] = obj.pop(array[depth])
        elif isinstance(obj, list) and array[depth] < len(obj):
            # 数组没有key值，无法重命名
            return
    else:
        node = None
        if isinstance(obj, dict) and obj.get(array[depth]) is not None:
            node = obj.get(array[depth])
        elif isinstance(obj, list) and array[depth] < len(obj):
            node = obj[array[depth]]
        if node is not None:
            remove_json_prop(node, array, depth + 1, new_key)


class MappingConfigPatch(Task):
    def __init__(self, config, work_name="", config_path=""):
        super(MappingConfigPatch, self).__init__(config, work_name=work_name)
        self.config_path = config_path
        self.config_patch_path = os.path.join(self.config_path, 'config_patch')

    def uri_remove_in_file(self, target_path, target_uri, target_method):
        target_object = load_json_file(target_path)
        resources = target_object.get("Resources")
        if resources is None:
            log.info(f"Uri移除场景，{target_path}无Resources配置")
            return

        flag = False
        # 倒序遍历
        for i in range(len(resources) - 1, -1, -1):
            uri = resources[i].get("Uri")
            if uri != target_uri:
                continue
            # 有Uri无Method，删除文件中指定Uri
            if target_method is None:
                flag = True
                del resources[i]
                continue

             # 有Uri、Method配置，删除指定配置
            interfaces = resources[i].get("Interfaces", [])
            # 倒序遍历
            for j in range(len(interfaces) - 1, -1, -1):
                method = interfaces[j].get("Type", "").lower()
                if method in target_method:
                    flag = True
                    del interfaces[j]
            if len(interfaces) == 0 and flag:
                del resources[i]

        if flag:
            save_json_file(target_path, target_object)
        else:
            log.error(f"Uri移除场景，没有找到Uri({target_uri})或Method({target_method})指定的配置")

    # Uri移除
    def uri_remove(self, actions):
        for action in actions:
            target = action.get("Target")
            target_uri = action.get("Uri")
            target_method = action.get("Method")
            if target is None:
                log.error(f"Uri移除场景，Target参数必须存在")
                continue
            target_path = os.path.join(self.config_path, target)
            if target_method is not None:
                # 将目标Method转为全小写，方便比较
                target_method = [method.lower() for method in target_method]

            if not is_valid_path(target_path, self.config_path, True):
                continue

            if os.path.isdir(target_path):
                # 删除整个路径
                if target_uri is not None or target_method is not None:
                    log.error(f"Uri移除场景，删除整个路径时，无需Uri和Method配置，路径为{target_path}")
                self.run_command(f"rm -rf {target_path}", sudo=True)
                continue

            if os.path.isfile(target_path):
                # 无Uri配置，删除整个文件
                if target_uri is None:
                    self.run_command(f"rm -rf {target_path}", sudo=True)
                    continue
                self.uri_remove_in_file(target_path, target_uri, target_method)
                continue

            log.error(f"Uri移除场景，没有Target{target}对应的文件或目录")

    # Uri增加
    def uri_copy(self, actions):
        for action in actions:
            source = action.get("Source")
            target = action.get("Target")
            if source is None or target is None:
                log.error(f"Uri增加场景，Source和Target参数必须存在")
                continue
            source_path = os.path.join(self.config_patch_path, source)
            target_path = os.path.join(self.config_path, target)

            if not is_valid_path(source_path, self.config_patch_path, True) or\
            not is_valid_path(target_path, self.config_path, False):
                continue

            if os.path.exists(target_path):
                log.info(f"Uri增加场景，Target({target})指定的文件或目录已存在，删除原有的")
                self.run_command(f"rm -rf {target_path}", sudo=True, command_echo=False)

            if os.path.isfile(source_path):
                dir_name = os.path.dirname(target_path)
                if not os.path.exists(dir_name):
                    # 目标路径不存在时，需要递归创建
                    os.makedirs(dir_name)
                shutil.copyfile(source_path, target_path)
            elif os.path.isdir(source_path):
                shutil.copytree(source_path, target_path)
            log.info(f"复制 {source_path} 到 {target_path}")

    # Uri重命名
    def uri_rename(self, actions):
        for action in actions:
            target = action.get("Target")
            origin_uri = action.get("OriginUri")
            new_uri = action.get("NewUri")
            if target is None or origin_uri is None or new_uri is None:
                log.error(f"Uri重命名场景，Target、OriginUri、NewUri参数必须存在")
                continue
            target_path = os.path.join(self.config_path, target)
            if not is_valid_path(target_path, self.config_path, True):
                continue

            target_object = load_json_file(target_path)
            resources = target_object.get("Resources")
            if resources is None:
                log.info(f"Uri重命名场景，文件{target_path}无Resources配置")
                continue

            flag = False
            for resource in resources:
                uri = resource.get("Uri")
                if uri == origin_uri:
                    flag = True
                    resource["Uri"] = new_uri

            if flag:
                save_json_file(target_path, target_object)
            else:
                log.error(f"Uri重命名场景，没有找到Uri({origin_uri})指定的配置")


    def uri_actions(self, actions):
        self.uri_remove(actions.get("Remove", []))
        self.uri_copy(actions.get("Copy", []))
        self.uri_rename(actions.get("Rename", []))


    def adjust_processingflow_sequence(self, base, actions):
        if base is None or len(base) == 0:
            return
        base = len(base)

        def replace_processing_flow(s):
            pattern = r"ProcessingFlow\[(\d+)\]"

            def replace(match):
                n = int(match.group(1))
                return f"ProcessingFlow[{n + base}]"
            t = re.sub(pattern, replace, s)
            return s == t, t

        def traversal(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    is_equal, new = replace_processing_flow(key)
                    if not is_equal:
                        obj[new] = obj[key].pop()
                    if isinstance(value, (dict, list)):
                        traversal(value)
                        continue
                    if not isinstance(value, str):
                        continue
                    is_equal, new = replace_processing_flow(value)
                    if not is_equal:
                        obj[key] = new
            elif isinstance(obj, list):
                for i, _ in enumerate(obj):
                    if isinstance(obj[i], (dict, list)):
                        traversal(obj[i])
                        continue
                    if not isinstance(obj[i], str):
                        continue
                    is_equal, new = replace_processing_flow(obj[i])
                    if not is_equal:
                        obj[i] = new
        traversal(actions)

    # 属性移除
    def property_remove(self, interface, actions):
        for prop in actions:
            remove_json_prop(interface, split_prop_name(prop), 0)

    # 属性变更
    def property_modify(self, interface, actions):
        self.adjust_processingflow_sequence(interface.get("ProcessingFlow"), actions)
        merge_json(interface, actions)

    # 属性重命名
    def property_rename(self, interface, actions):
        for key, value in actions.items():
            rename_json_prop(interface, split_prop_name(key), 0, value)

    def property_action(self, resources, target_method, target_uri, action):
        flag = False
        for resource in resources:
            uri = resource.get("Uri")
            if uri != target_uri:
                continue
            interfaces = resource.get("Interfaces", [])
            for interface in interfaces:
                method = interface.get("Type", "")
                if method.lower() != target_method.lower():
                    continue
                flag = True
                self.property_remove(interface, action.get("Remove", []))
                self.property_modify(interface, action.get("Modify", {}))
                self.property_rename(interface, action.get("Rename", {}))
        return flag

    def property_actions(self, actions):
        for action in actions:
            target = action.get("Target")
            target_uri = action.get("Uri")
            target_method = action.get("Method")
            if target is None or target_uri is None or target_method is None:
                log.error(f"属性变更场景，Target、Uri、Method参数必须存在")
                continue
            target_path = os.path.join(self.config_path, target)
            if not is_valid_path(target_path, self.config_path, True):
                continue

            target_object = load_json_file(target_path)
            resources = target_object.get("Resources")
            if resources is None:
                log.info(f"属性变更场景，文件{target_path}无Resources配置")
                continue
            flag = self.property_action(resources, target_method, target_uri, action)

            if flag:
                save_json_file(target_path, target_object)
            else:
                log.error(f"属性变更场景，没有找到Uri({target_uri})指定的配置")


    def global_variables(self, global_variable):
        if global_variable is None:
            return
        target_path = os.path.join(self.config_path, "config.json")
        if not os.path.exists(target_path):
            return
        target_object = load_json_file(target_path)
        target_global_variable = target_object.get("GlobalVariable")
        if target_global_variable is None:
            log.info(f"平台层文件{target_path}无GlobalVariable配置")
            return
        merge_json(target_global_variable, global_variable)
        save_json_file(target_path, target_object)


    def restore_permission(self):
        p = {"rd": 550, "r": 440, "user": [0, 0]}
        for key, value in permission_dict.items():
            app = "opt/bmc/apps/" + key
            if app in self.config_path:
                p = value

        self.pipe_command([f"sudo find {self.config_path} -type d", f"sudo xargs -P 0 -i. chmod {p['rd']} ."])
        self.pipe_command([f"sudo find {self.config_path} -type f", f"sudo xargs -P 0 -i. chmod {p['r']} ."])
        self.pipe_command([f"sudo find {self.config_path} -type d",
                           f"sudo xargs -P 0 -i. chown {p['user'][0]}:{p['user'][1]} ."])
        self.pipe_command([f"sudo find {self.config_path} -type f",
                           f"sudo xargs -P 0 -i. chown {p['user'][0]}:{p['user'][1]} ."])

    def config_patch(self):
        patch_file = os.path.join(self.config_patch_path, 'config.json')
        if not os.path.isfile(patch_file):
            return

        patch_object = load_json_file(patch_file)
        self.uri_actions(patch_object.get("Uri.Actions", {}))
        self.property_actions(patch_object.get("Property.Actions", []))
        self.global_variables(patch_object.get("GlobalVariable", {}))


    def run(self):
        if not os.path.isdir(self.config_patch_path):
            return

        # 给予权限方便对文件做变更
        self.run_command(f"chmod -R 777 {self.config_path}", sudo=True)

        self.config_patch()

        # 变更完成恢复权限
        self.restore_permission()
        self.run_command(f"rm -rf {self.config_patch_path}", sudo=True)


class MappingConfigGenerate(MappingConfigPatch):
    def __init__(self, config, work_name="", config_path="", custom="default"):
        super(MappingConfigPatch, self).__init__(config, work_name=work_name)
        self.config_path = config_path
        self.config_patch_path = os.path.join(self.config_path, 'customer', custom)

    def run(self):
        if not os.path.isdir(self.config_patch_path):
            return

        # 给予权限方便对文件做变更
        self.run_command(f"chmod -R 777 {self.config_path}", sudo=True)

        self.config_patch()

        # 变更完成恢复权限
        self.restore_permission()