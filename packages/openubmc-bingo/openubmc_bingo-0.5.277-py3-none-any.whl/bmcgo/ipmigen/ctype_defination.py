#!/usr/bin/python3
# coding: utf-8
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.


class CTypeBase(object):
    def __init__(self, c_type, c_len):
        self.c_type = c_type
        self.c_len = c_len
        pass


class CTypes():
    types: dict = {
        "U8": CTypeBase(
                       c_type="guint8 <arg_name><bit_field>",
                       c_len=1),
        "U8[]": CTypeBase(
                       c_type="guint8 <arg_name>[<type_len>]<bit_field>",
                       c_len=1),
        "S16": CTypeBase(
                        c_len=2,
                        c_type="gint16 <arg_name><bit_field>"),
        "S16[]": CTypeBase(
                       c_type="gint16 <arg_name>[<type_len>]<bit_field>",
                       c_len=2),
        "U16": CTypeBase(
                       c_type="guint16 <arg_name><bit_field>",
                       c_len=2),
        "U16[]": CTypeBase(
                       c_type="guint16 <arg_name>[<type_len>]<bit_field>",
                       c_len=2),
        "S32": CTypeBase(
                       c_type="gint32 <arg_name><bit_field>",
                       c_len=4),
        "S32[]": CTypeBase(
                       c_type="gint32 <arg_name>[<type_len>]<bit_field>",
                       c_len=4),
        "U32": CTypeBase(
                       c_type="guint32 <arg_name><bit_field>",
                       c_len=4),
        "U32[]": CTypeBase(
                       c_type="guint32 <arg_name>[<type_len>]<bit_field>",
                       c_len=4,
                       ),
        "S64": CTypeBase(
                       c_type="gint64 <arg_name><bit_field>",
                       c_len=8),
        "S64[]": CTypeBase(
                       c_type="gint64 <arg_name>[<type_len>]<bit_field>",
                       c_len=8,),
        "U64": CTypeBase(
                       c_type="guint64 <arg_name><bit_field>",
                       c_len=8),
        "U64[]": CTypeBase(
                       c_type="guint64 <arg_name>[<type_len>]<bit_field>",
                       c_len=8,
                       ),
        "Double": CTypeBase(
                       c_type="gdouble <arg_name>",
                       c_len=8),
        "Double[]": CTypeBase(
                       c_type="gdouble <arg_name>[<type_len>]",
                       c_len=8,),
        "String": CTypeBase(
                       c_type="gchar <arg_name>[<type_len>]",
                       c_len=1),
        "String *": CTypeBase(
                       c_type="gchar *<arg_name>",
                       c_len=1),
        "U8 *": CTypeBase(
                       c_type="guint8 *<arg_name>",
                       c_len=1),
    }
