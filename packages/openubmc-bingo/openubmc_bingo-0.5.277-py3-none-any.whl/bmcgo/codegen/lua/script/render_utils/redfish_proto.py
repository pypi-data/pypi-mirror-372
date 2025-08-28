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

import merge_proto_algo
from dto.options import Options
from bmcgo.codegen.lua.script.base import Base
from bmcgo.codegen.lua.script.factory import Factory


class RedfishProtoUtils(Base):
    def __init__(self, data: dict, options: Options):
        super().__init__(data, options=options)

    @staticmethod
    def replace_tag(field):
        return field.translate(str.maketrans({'@': '', '#': '', '.': '_', '-': '_', '+': '_', ' ': '_'}))

    @staticmethod
    def get_class_name(file_name):
        resource_string_fields = {'Id', 'Name', 'UUID', 'Description', 'VLANPriority', 'SubnetMask', 'MACAddress'}
        should_in32_fields = {'VLANId', 'PrefixLength'}
        target = file_name.split('/')[-1]
        if target in resource_string_fields:
            return 'string'
        if target in should_in32_fields:
            return 'int32'
        if 'http' in file_name:
            if 'Resource.json' in file_name:
                return 'Resource.' + file_name.split('/')[-1]
            elif 'odata' in file_name:
                return 'string'
            else:
                return 'Common.ODataID'
        return file_name.split('/')[-1]

    @staticmethod
    def get_lua_type(field, para_type):
        type_map = {
            'array': 'repeated ' + field, 'boolean': 'bool', 'integer': 'int32',
            'number': 'int32', 'string': 'string'
        }
        return type_map.get(para_type, '')

    @staticmethod
    def attr_option_field(field):
        option_list = []
        for attr in field.keys():
            value = field.get(attr)
            if merge_proto_algo.is_attr_option(attr, value):
                if isinstance(value, (bytes, str)):
                    option_list.append('''(%s) = "%s"''' % (attr, value))
                else:
                    option_list.append("(%s) = %s" % (attr, ("%s" % value).lower()))
        if not option_list:
            return ""
        return "[%s]" % (",".join(option_list))

    def get_type(self, field, para_type):
        all_type = ['array', 'boolean', 'integer', 'number', 'string']
        ret = ''
        if isinstance(para_type, list):
            for sub_type in para_type:
                if sub_type in all_type:
                    ret = self.get_lua_type(field, sub_type)
                    return ret
        else:
            ret = self.get_lua_type(field, para_type)
        return ret

    def get_file_name(self):
        temp = self.data['$id'].split('/')[-1]
        return temp.split('.')[0]




Factory().register("redfish.proto.mako", RedfishProtoUtils)
