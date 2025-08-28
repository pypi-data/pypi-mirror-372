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

import itertools
import json
import sys
import types_pb2
import ipmi_types_pb2

from google.protobuf.descriptor_pb2 import DescriptorProto, \
    EnumDescriptorProto, FieldDescriptorProto, ServiceDescriptorProto
from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest, CodeGeneratorResponse

BASIC_TYPES = {
    getattr(FieldDescriptorProto, t):
        t 
        for t in dir(FieldDescriptorProto)
        if t.startswith("TYPE_")
        }

ALLOW_BASIC_TYPES = {
    FieldDescriptorProto.TYPE_BOOL: "bool",
    FieldDescriptorProto.TYPE_STRING: "string",
    FieldDescriptorProto.TYPE_INT32: "int32",
    FieldDescriptorProto.TYPE_UINT32: "uint32",
    FieldDescriptorProto.TYPE_INT64: "int64",
    FieldDescriptorProto.TYPE_UINT64: "uint64",
    FieldDescriptorProto.TYPE_FLOAT: "float",
    FieldDescriptorProto.TYPE_DOUBLE: "double",
    FieldDescriptorProto.TYPE_BYTES: "bytes",
}


def get_type_name(n_type, t_name, label):
    if n_type == FieldDescriptorProto.TYPE_MESSAGE or n_type == FieldDescriptorProto.TYPE_ENUM:
        if t_name.startswith("."):
            return t_name[1:]
        return t_name
    elif n_type in ALLOW_BASIC_TYPES:
        type_allow = ALLOW_BASIC_TYPES[n_type]
        return type_allow if label != FieldDescriptorProto.LABEL_REPEATED else f'{type_allow}[]'
    raise RuntimeError("无效类型 {}({})".format(BASIC_TYPES[n_type], n_type))


def traverse(proto_file):
    def _traverse(package, items):
        for item in items:
            yield item, package

    return itertools.chain(
        _traverse(proto_file.package, proto_file.enum_type),
        _traverse(proto_file.package, proto_file.message_type),
        _traverse(proto_file.package, proto_file.service),
    )


def process_item(item, package):
    data = {
        'package': package or 'root',
        'name': item.name,
        'options': {op.name: item.options.Extensions[op] for op in item.options.Extensions}
    }

    if isinstance(item, DescriptorProto):
        data.update({
            'type': 'Message',
            "properties": [{
                "name": f.name,
                'type': get_type_name(f.type, f.type_name, f.label),
                "options": {op.name: f.options.Extensions[op] for op in f.options.Extensions},
                'id': f.number,
                'repeated': f.label == FieldDescriptorProto.LABEL_REPEATED
            } for f in item.field],
            "nested_type": [process_item(nested_item, package) for nested_item in item.nested_type]})
    elif isinstance(item, EnumDescriptorProto):
        data.update({
            'type': 'Enum',
            'values': [{
                'name': v.name,
                'value': v.number,
                'id': v.number
            } for v in item.value]
        })
    return data


def generate_code(req, resp):
    imports = []
    for proto_file in req.proto_file:
        if proto_file.name not in req.file_to_generate:
            imports.append(proto_file.name)
            continue

        o_put = []
        service = []
        for item, package in traverse(proto_file):
            if isinstance(item, ServiceDescriptorProto):
                [service.append({
                    'method_options': {op.name: v.options.Extensions[op] for op in v.options.Extensions},
                    'options': {op.name: item.options.Extensions[op] for op in item.options.Extensions},
                    'name': v.name,
                    'req': v.input_type,
                    'rsp': v.output_type,
                }) for v in item.method]
            else:
                o_put.append(process_item(item, package))

        file = resp.file.add()
        file.name = proto_file.name + '.json'
        file.content = json.dumps({
            'imports': imports,
            'dependency': [v for v in proto_file.dependency],
            'data': o_put,
            'service': service,
            'filename': proto_file.name,
            'package': proto_file.package,
            'options': {op.name: proto_file.options.Extensions[op] for op in proto_file.options.Extensions}
        }, indent=2)


def read_data():
    data = sys.stdin.buffer.read()
    return data

if __name__ == '__main__':
    request = CodeGeneratorRequest()
    request.ParseFromString(read_data())
    response = CodeGeneratorResponse()
    generate_code(request, response)
    output = response.SerializeToString()
    sys.stdout.buffer.write(output)
