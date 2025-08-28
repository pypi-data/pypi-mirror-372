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

import os
import re
from utils import Utils
from dto.options import Options
from render_utils.validate_lua import ValidateLua
from bmcgo.codegen.lua.script.mdb_register import MdbRegister
from bmcgo.codegen.lua.script.base import Base
from bmcgo.codegen.lua.script.factory import Factory


class ServicesUtils(Base, ValidateLua, Utils, MdbRegister):
    def __init__(self, data: dict, options: Options):
        super().__init__(data, options=options)

    @staticmethod
    def message_type(t):
        if t == ".google.protobuf.Empty":
            return "nil"
        return t[1:] if t.startswith(".") else t

    @staticmethod
    def count(params, name):
        num = 0
        for param in params:
            if param == name:
                num += 1
        return num

    @staticmethod
    def contains_csr(prop_configs):
        for prop_config in prop_configs.values():
            for usage in prop_config.get("usage", []):
                if usage == "CSR":
                    return True

        return False

    def err_module(self):
        return (
            "apps."
            + Utils(self.data, self.options).camel_to_snake(self.data["package"])
            + ".error"
        )

    def sig(self, msg_type):
        msg = Utils(self.data, self.options).make_get_message(msg_type)
        return "".join(
            [
                Utils(self.data, self.options).do_type_to_dbus(p["type"], p["repeated"])
                for p in msg.get("properties")
            ]
        )

    def params(self, msg_type):
        msg = Utils(self.data, self.options).make_get_message(msg_type)
        return ", ".join([p["name"] for p in msg.get("properties")])

    def cb_name(self, rpc):
        return Utils(self.data, self.options).camel_to_snake("__on" + rpc["name"])

    def rsp_message(self, rpc):
        return self.message_type(rpc["rsp"])

    def req_message(self, rpc):
        return self.message_type(rpc["req"])

    def props(self, msg_type):
        msg = Utils(self.data, self.options).make_get_message(msg_type)
        return msg.get("properties")

    def check_file_exist(self, file):
        return os.path.exists(file)

    def is_dynamic_obj(self, path):
        return path.find(':') != -1

    def make_path(self, path):
        path = self.force_to_colon(path)
        params = re.compile(r":([a-zA-Z_][0-9a-zA-Z_]+)").findall(path)
        if len(params) == 0:
            return f"'{path}'"
        result = []
        for name in params:
            path_s = path.partition(f":{name}")
            result.append(f"'{path_s[0]}'")
            result.append(name)
            path = path_s[2]

        return (f"{' .. '.join(result)}") if path == '' else (f"{' .. '.join(result)} .. '{path}'")

    def check_duplicate(self, params):
        for name in params:
            if self.count(params, name) > 1:
                raise RuntimeError(f"重复参数: {name}")

    def get_not_recover_tables(self, root):
        not_recover_tables = {}
        classes = {}
        classes.update(root.get("class_require", {}))
        classes.update(root.get("private_class_require", {}))
        for class_data in classes.values():
            data = class_data['data']
            if "tableName" not in data:
                continue

            if self.contains_csr(data.get("properties", {})):
                not_recover_tables[data["tableName"]] = True
                continue

            for intf_data in data.get("interfaces", {}).values():
                if self.contains_csr(intf_data.get("properties", {})):
                    not_recover_tables[data["tableName"]] = True
                    break

        return self.convert_to_lua(not_recover_tables)


Factory().register("service.lua.mako", ServicesUtils)
Factory().register("v1/templates/apps/service.lua.mako", ServicesUtils)
