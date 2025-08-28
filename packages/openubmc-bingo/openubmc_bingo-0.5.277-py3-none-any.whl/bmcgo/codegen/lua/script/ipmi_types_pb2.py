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

import sys
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)
from google.protobuf import descriptor_pb2 as google_dot_protobuf_dot_descriptor__pb2


_b = sys.version_info[0] < 3 and (lambda x: x) or (lambda x: x.encode("latin1"))
_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor.FileDescriptor(
  name='ipmi_types.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x10ipmi_types.proto\x1a google/protobuf/descriptor.proto:7\n\x0f\x64\x65\x66\x61ult_channel\
\x12\x1c.google.protobuf.FileOptions\x18\xd9\xaa\x04 \x01(\t:2\n\x07\x63hannel\x12\x1f.google.protobuf.MessageOptions\
\x18\xe9\xf8\x04 \x01(\t:1\n\x06net_fn\x12\x1f.google.protobuf.MessageOptions\x18\xea\xf8\x04 \x01(\x05:.\n\x03\x63md\
\x12\x1f.google.protobuf.MessageOptions\x18\xeb\xf8\x04 \x01(\x05:/\n\x04prio\x12\x1f.google.protobuf.MessageOptions\
\x18\xec\xf8\x04 \x01(\t:4\n\tprivilege\x12\x1f.google.protobuf.MessageOptions\x18\xed\xf8\x04 \x01(\t:1\
\n\x06\x64\x65\x63ode\x12\x1f.google.protobuf.MessageOptions\x18\xee\xf8\x04 \x01(\t:1\n\x06\x65ncode\x12\x1f.google.\
protobuf.MessageOptions\x18\xef\xf8\x04 \x01(\t:2\n\x07\x66ilters\x12\x1f.google.protobuf.MessageOptions\
\x18\xf0\xf8\x04 \x01(\tb\x06proto3'),
  dependencies=[google_dot_protobuf_dot_descriptor__pb2.DESCRIPTOR, ])


DEFAULT_CHANNEL_FIELD_NUMBER = 71001
default_channel = _descriptor.FieldDescriptor(
  name='default_channel', full_name='default_channel', index=0,
  number=71001, type=9, cpp_type=9, label=1,
  has_default_value=False, default_value=_b("").decode('utf-8'),
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
CHANNEL_FIELD_NUMBER = 81001
channel = _descriptor.FieldDescriptor(
  name='channel', full_name='channel', index=1,
  number=81001, type=9, cpp_type=9, label=1,
  has_default_value=False, default_value=_b("").decode('utf-8'),
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
NET_FN_FIELD_NUMBER = 81002
net_fn = _descriptor.FieldDescriptor(
  name='net_fn', full_name='net_fn', index=2,
  number=81002, type=5, cpp_type=1, label=1,
  has_default_value=False, default_value=0,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
CMD_FIELD_NUMBER = 81003
cmd = _descriptor.FieldDescriptor(
  name='cmd', full_name='cmd', index=3,
  number=81003, type=5, cpp_type=1, label=1,
  has_default_value=False, default_value=0,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
PRIO_FIELD_NUMBER = 81004
prio = _descriptor.FieldDescriptor(
  name='prio', full_name='prio', index=4,
  number=81004, type=9, cpp_type=9, label=1,
  has_default_value=False, default_value=_b("").decode('utf-8'),
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
PRIVILEGE_FIELD_NUMBER = 81005
privilege = _descriptor.FieldDescriptor(
  name='privilege', full_name='privilege', index=5,
  number=81005, type=9, cpp_type=9, label=1,
  has_default_value=False, default_value=_b("").decode('utf-8'),
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
DECODE_FIELD_NUMBER = 81006
decode = _descriptor.FieldDescriptor(
  name='decode', full_name='decode', index=6,
  number=81006, type=9, cpp_type=9, label=1,
  has_default_value=False, default_value=_b("").decode('utf-8'),
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
ENCODE_FIELD_NUMBER = 81007
encode = _descriptor.FieldDescriptor(
  name='encode', full_name='encode', index=7,
  number=81007, type=9, cpp_type=9, label=1,
  has_default_value=False, default_value=_b("").decode('utf-8'),
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
FILTERS_FIELD_NUMBER = 81008
filters = _descriptor.FieldDescriptor(
  name='filters', full_name='filters', index=8,
  number=81008, type=9, cpp_type=9, label=1,
  has_default_value=False, default_value=_b("").decode('utf-8'),
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)

DESCRIPTOR.extensions_by_name['default_channel'] = default_channel
DESCRIPTOR.extensions_by_name['channel'] = channel
DESCRIPTOR.extensions_by_name['net_fn'] = net_fn
DESCRIPTOR.extensions_by_name['cmd'] = cmd
DESCRIPTOR.extensions_by_name['prio'] = prio
DESCRIPTOR.extensions_by_name['privilege'] = privilege
DESCRIPTOR.extensions_by_name['decode'] = decode
DESCRIPTOR.extensions_by_name['encode'] = encode
DESCRIPTOR.extensions_by_name['filters'] = filters
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(default_channel)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(channel)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(net_fn)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(cmd)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(prio)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(privilege)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(decode)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(encode)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(filters)

# @@protoc_insertion_point(module_scope)
