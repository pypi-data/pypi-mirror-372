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
    arg_in: str     # 做为函数的入参参数
    arg_out: str    # 做为函数的出差参数
    write_type: str  # 属性写函数关键字，前加mdb_set_xxx得到真实函数名
    variant_type: str  # 属性的gvariant type(signature)字符串

    def __init__(self, variant_type, write_type, arg_in, arg_out, arg_decode,
                 arg_encode,
                 args_write_remote_declear, arg_free):
        self.variant_type = variant_type
        self.write_type = write_type
        self.arg_in = arg_in
        self.arg_out = arg_out
        self.arg_decode = arg_decode
        self.arg_encode = arg_encode
        self.arg_free = arg_free
        self.args_write_remote_declear = args_write_remote_declear
        pass

    def render_in_args(self, prop_name: str, is_const: bool):
        return self._replace(self.arg_in, prop_name, is_const)

    def render_out_args(self, prop_name, is_const: bool):
        return self._replace(self.arg_out, prop_name, is_const)

    def render_in_encode(self, prop_name):
        pass

    def render_out_decode(self, prop_name):
        pass

    def is_array(self):
        glib_type = ["b", "y", "n", "q", "i", "u", "x", "t", "d", "h", "s", "o", "g"]
        if self.variant_type.startswith("a") and self.variant_type[1:] in glib_type:
            return True
        else:
            return False

    def _replace(self, template: str, prop_name: str, is_const: bool):
        out = template.replace("<arg_name>", prop_name)
        const_str = ""
        if is_const:
            const_str = "const "
        return out.replace("<const>", const_str)


class CTypes():
    types = {
        "b": CTypeBase(variant_type="b",
                       write_type="boolean",
                       arg_in="gboolean <arg_name>",
                       arg_out="gboolean *<arg_name>",
                       args_write_remote_declear="g_variant_new_boolean(<arg_name>)",
                       arg_decode=[
                           "<req><arg_name> = parameter_get_boolean(parameters, arg_id);"],
                       arg_free=[],
                       arg_encode=[
                           "g_variant_builder_add_value(&builder, g_variant_new_boolean(<req><arg_name>));"],),
        "ab": CTypeBase(variant_type="ab",
                        write_type="array_boolean",
                        arg_in="gsize n_<arg_name>, <const>gboolean *<arg_name>",
                        arg_out="gsize *n_<arg_name>, gboolean **<arg_name>",
                        args_write_remote_declear="BUILD_BASIC_TYPE_ARRAY(\"b\", n_<arg_name>, <arg_name>)",
                        arg_decode=["ITER_BASIC_TYPE_ARRAY(parameters, arg_id, <req>n_<arg_name>, " +
                                    "<req><arg_name>, boolean, \"b\");"],
                        arg_free=["g_free(<req><arg_name>);"],
                        arg_encode=[
                            "tmp_v = BUILD_BASIC_TYPE_ARRAY(\"b\", <req>n_<arg_name>, <req><arg_name>);",
                            "g_variant_builder_add_value(&builder, tmp_v);"],
                        ),
        "y": CTypeBase(variant_type="y",
                       write_type="uint8",
                       arg_in="guint8 <arg_name>",
                       arg_out="guint8 *<arg_name>",
                       args_write_remote_declear="g_variant_new_byte(<arg_name>)",
                       arg_decode=["<req><arg_name> = parameter_get_uint8(parameters, arg_id);"],
                       arg_free=[],
                       arg_encode=[
                           "g_variant_builder_add_value(&builder, g_variant_new_byte(<req><arg_name>));"]),
        "ay": CTypeBase(variant_type="ay",
                        write_type="array_uint8",
                        arg_in="gsize n_<arg_name>, <const>guint8 *<arg_name>",
                        arg_out="gsize *n_<arg_name>, guint8 **<arg_name>",
                        args_write_remote_declear="BUILD_BASIC_TYPE_ARRAY(\"y\", n_<arg_name>, <arg_name>)",
                        arg_decode=["ITER_BASIC_TYPE_ARRAY(parameters, arg_id, <req>n_<arg_name>, <req><arg_name>," +
                                    " uint8, \"y\");"],
                        arg_free=["g_free(<req><arg_name>);"],
                        arg_encode=[
                            "tmp_v = BUILD_BASIC_TYPE_ARRAY(\"y\", <req>n_<arg_name>, <req><arg_name>);",
                            "g_variant_builder_add_value(&builder, tmp_v);"],
                        ),
        "n": CTypeBase(variant_type="n",
                       write_type="int16",
                       arg_in="gint16 <arg_name>",
                       arg_out="gint16 *<arg_name>",
                       args_write_remote_declear="g_variant_new_int16(<arg_name>)",
                       arg_decode=["<req><arg_name> = parameter_get_int16(parameters, arg_id);"],
                       arg_free=[],
                       arg_encode=[
                           "g_variant_builder_add_value(&builder, g_variant_new_int16(<req><arg_name>));"]),
        "an": CTypeBase(variant_type="an",
                        write_type="array_int16",
                        arg_in="gsize n_<arg_name>, <const>gint16 *<arg_name>",
                        arg_out="gsize *n_<arg_name>, gint16 **<arg_name>",
                        args_write_remote_declear="BUILD_BASIC_TYPE_ARRAY(\"n\", n_<arg_name>, <arg_name>)",
                        arg_decode=["ITER_BASIC_TYPE_ARRAY(parameters, arg_id, <req>n_<arg_name>, <req><arg_name>," +
                                    " int16, \"n\");"],
                        arg_free=["g_free(<req><arg_name>);"],
                        arg_encode=[
                            "tmp_v = BUILD_BASIC_TYPE_ARRAY(\"n\", <req>n_<arg_name>, <req><arg_name>);",
                            "g_variant_builder_add_value(&builder, tmp_v);"],
                        ),
        "q": CTypeBase(variant_type="q",
                       write_type="uint16",
                       arg_in="guint16 <arg_name>",
                       arg_out="guint16 *<arg_name>",
                       args_write_remote_declear="g_variant_new_uint16(<arg_name>)",
                       arg_decode=["<req><arg_name> = parameter_get_uint16(parameters, arg_id);"],
                       arg_free=[],
                       arg_encode=[
                           "g_variant_builder_add_value(&builder, g_variant_new_uint16(<req><arg_name>));"]),
        "aq": CTypeBase(variant_type="aq",
                        write_type="array_uint16",
                        arg_in="gsize n_<arg_name>, <const>guint16 *<arg_name>",
                        arg_out="gsize *n_<arg_name>, guint16 **<arg_name>",
                        args_write_remote_declear="BUILD_BASIC_TYPE_ARRAY(\"q\", n_<arg_name>, <arg_name>)",
                        arg_decode=["ITER_BASIC_TYPE_ARRAY(parameters, arg_id, <req>n_<arg_name>, <req><arg_name>," +
                                    " uint16, \"q\");"],
                        arg_free=["g_free(<req><arg_name>);"],
                        arg_encode=[
                            "tmp_v = BUILD_BASIC_TYPE_ARRAY(\"q\", <req>n_<arg_name>, <req><arg_name>);",
                            "g_variant_builder_add_value(&builder, tmp_v);"],
                        ),
        "i": CTypeBase(variant_type="i",
                       write_type="int32",
                       arg_in="gint32 <arg_name>",
                       arg_out="gint32 *<arg_name>",
                       args_write_remote_declear="g_variant_new_int32(<arg_name>)",
                       arg_decode=[
                           "<req><arg_name> = parameter_get_int32(parameters, arg_id);"],
                       arg_free=[],
                       arg_encode=[
                           "g_variant_builder_add_value(&builder, g_variant_new_int32(<req><arg_name>));"]),
        "ai": CTypeBase(variant_type="ai",
                        write_type="array_int32",
                        arg_in="gsize n_<arg_name>, <const>gint32 *<arg_name>",
                        arg_out="gsize *n_<arg_name>, gint32 **<arg_name>",
                        args_write_remote_declear="BUILD_BASIC_TYPE_ARRAY(\"i\", n_<arg_name>, <arg_name>)",
                        arg_decode=["ITER_BASIC_TYPE_ARRAY(parameters, arg_id, <req>n_<arg_name>, <req><arg_name>," +
                                    " int32, \"i\");"],
                        arg_free=["g_free(<req><arg_name>);"],
                        arg_encode=[
                            "tmp_v = BUILD_BASIC_TYPE_ARRAY(\"i\", <req>n_<arg_name>, <req><arg_name>);",
                            "g_variant_builder_add_value(&builder, tmp_v);"],
                        ),
        "u": CTypeBase(variant_type="u",
                       write_type="uint32",
                       arg_in="guint32 <arg_name>",
                       arg_out="guint32 *<arg_name>",
                       args_write_remote_declear="g_variant_new_uint32(<arg_name>)",
                       arg_decode=["<req><arg_name> = parameter_get_uint32(parameters, arg_id);"],
                       arg_free=[],
                       arg_encode=[
                           "g_variant_builder_add_value(&builder, g_variant_new_uint32(<req><arg_name>));"]),
        "au": CTypeBase(variant_type="au",
                        write_type="array_uint32",
                        arg_in="gsize n_<arg_name>, <const>guint32 *<arg_name>",
                        arg_out="gsize *n_<arg_name>, guint32 **<arg_name>",
                        args_write_remote_declear="BUILD_BASIC_TYPE_ARRAY(\"u\", n_<arg_name>, <arg_name>)",
                        arg_decode=["ITER_BASIC_TYPE_ARRAY(parameters, arg_id, <req>n_<arg_name>, <req><arg_name>," +
                                    " uint32, \"u\");"],
                        arg_free=["g_free(<req><arg_name>);"],
                        arg_encode=[
                            "tmp_v = BUILD_BASIC_TYPE_ARRAY(\"u\", <req>n_<arg_name>, <req><arg_name>);",
                            "g_variant_builder_add_value(&builder, tmp_v);"],
                        ),
        "x": CTypeBase(variant_type="x",
                       write_type="int64",
                       arg_in="gint64 <arg_name>",
                       arg_out="gint64 *<arg_name>",
                       args_write_remote_declear="g_variant_new_int64(<arg_name>)",
                       arg_decode=["<req><arg_name> = parameter_get_int64(parameters, arg_id);"],
                       arg_free=[],
                       arg_encode=[
                           "g_variant_builder_add_value(&builder, g_variant_new_int64(<req><arg_name>));"]),
        "ax": CTypeBase(variant_type="ax",
                        write_type="array_int64",
                        arg_in="gsize n_<arg_name>, <const>gint64 *<arg_name>",
                        arg_out="gsize *n_<arg_name>, gint64 **<arg_name>",
                        args_write_remote_declear="BUILD_BASIC_TYPE_ARRAY(\"x\", n_<arg_name>, <arg_name>)",
                        arg_decode=["ITER_BASIC_TYPE_ARRAY(parameters, arg_id, <req>n_<arg_name>, <req><arg_name>," +
                                    " int64, \"x\");"],
                        arg_free=["g_free(<req><arg_name>);"],
                        arg_encode=[
                            "tmp_v = BUILD_BASIC_TYPE_ARRAY(\"x\", <req>n_<arg_name>, <req><arg_name>);",
                            "g_variant_builder_add_value(&builder, tmp_v);"],
                        ),
        "t": CTypeBase(variant_type="t",
                       write_type="uint64",
                       arg_in="guint64 <arg_name>",
                       arg_out="guint64 *<arg_name>",
                       args_write_remote_declear="g_variant_new_uint64(<arg_name>)",
                       arg_decode=[
                           "<req><arg_name> = parameter_get_uint64(parameters, arg_id);"],
                       arg_free=[],
                       arg_encode=[
                           "g_variant_builder_add_value(&builder, g_variant_new_uint64(<req><arg_name>));"]),
        "at": CTypeBase(variant_type="at",
                        write_type="array_uint64",
                        arg_in="gsize n_<arg_name>, <const>guint64 *<arg_name>",
                        arg_out="gsize *n_<arg_name>, guint64 **<arg_name>",
                        args_write_remote_declear="BUILD_BASIC_TYPE_ARRAY(\"t\", n_<arg_name>, <arg_name>)",
                        arg_decode=["ITER_BASIC_TYPE_ARRAY(parameters, arg_id, <req>n_<arg_name>, <req><arg_name>," +
                                    " uint64, \"t\");"],
                        arg_free=["g_free(<req><arg_name>);"],
                        arg_encode=[
                            "tmp_v = BUILD_BASIC_TYPE_ARRAY(\"t\", <req>n_<arg_name>, <req><arg_name>);",
                            "g_variant_builder_add_value(&builder, tmp_v);"],
                        ),
        "d": CTypeBase(variant_type="d",
                       write_type="double",
                       arg_in="gdouble <arg_name>",
                       arg_out="gdouble *<arg_name>",
                       args_write_remote_declear="g_variant_new_double(<arg_name>)",
                       arg_decode=[
                           "<req><arg_name> = parameter_get_double(parameters, arg_id);"],
                       arg_free=[],
                       arg_encode=[
                           "g_variant_builder_add_value(&builder, g_variant_new_double(<req><arg_name>));"]),
        "ad": CTypeBase(variant_type="ad",
                        write_type="array_double",
                        arg_in="gsize n_<arg_name>, <const>gdouble *<arg_name>",
                        arg_out="gsize *n_<arg_name>, gdouble **<arg_name>",
                        args_write_remote_declear="BUILD_BASIC_TYPE_ARRAY(\"d\", n_<arg_name>, <arg_name>)",
                        arg_decode=["ITER_BASIC_TYPE_ARRAY(parameters, arg_id, <req>n_<arg_name>, <req><arg_name>," +
                                    " double, \"d\");"],
                        arg_free=["g_free(<req><arg_name>);"],
                        arg_encode=[
                            "tmp_v = BUILD_BASIC_TYPE_ARRAY(\"d\", <req>n_<arg_name>, <req><arg_name>);",
                            "g_variant_builder_add_value(&builder, tmp_v);"],
                        ),
        "h": CTypeBase(variant_type="h",
                       write_type="handle",
                       arg_in="gint32 <arg_name>",
                       arg_out="gint32 *<arg_name>",
                       args_write_remote_declear="g_variant_new_handle(<arg_name>)",
                       arg_decode=[
                           "<req><arg_name> = parameter_get_handle(parameters, arg_id);"],
                       arg_free=[],
                       arg_encode=[
                           "g_variant_builder_add_value(&builder, g_variant_new_handle(<req><arg_name>));"]),
        "ah": CTypeBase(variant_type="ah",
                        write_type="array_handle",
                        arg_in="gsize n_<arg_name>, <const>gint32 *<arg_name>",
                        arg_out="gsize *n_<arg_name>, gint32 **<arg_name>",
                        args_write_remote_declear="BUILD_BASIC_TYPE_ARRAY(\"h\", n_<arg_name>, <arg_name>)",
                        arg_decode=["ITER_BASIC_TYPE_ARRAY(parameters, arg_id, <req>n_<arg_name>, <req><arg_name>," +
                                    " int32, \"h\");"],
                        arg_free=["g_free(<req><arg_name>);"],
                        arg_encode=[
                            "tmp_v = BUILD_BASIC_TYPE_ARRAY(\"h\", <req>n_<arg_name>, <req><arg_name>);",
                            "g_variant_builder_add_value(&builder, tmp_v);"],
                        ),
        "s": CTypeBase(variant_type="s",
                       write_type="string",
                       arg_in="<const>gchar *<arg_name>",
                       arg_out="gchar **<arg_name>",
                       args_write_remote_declear="g_variant_new_string(<arg_name> ? <arg_name> : \"\")",
                       arg_decode=[
                           "<req><arg_name> = parameter_get_string(parameters, arg_id);"],
                       arg_free=["g_free(<req><arg_name>);"],
                       arg_encode=[
                           "g_variant_builder_add_value(&builder, g_variant_new_string(<req><arg_name>));"]),
        "as": CTypeBase(variant_type="as",
                        write_type="array_string",
                        arg_in="<const>gchar *<const>*<arg_name>",
                        arg_out="gchar ***<arg_name>",
                        args_write_remote_declear="BUILD_STRING_TYPE_ARRAY(\"s\", <arg_name>)",
                        arg_decode=["ITER_STRING_TYPE_ARRAY(parameters, arg_id, <req><arg_name>, char *, \"s\");"],
                        arg_free=["g_strfreev(<req><arg_name>);"],
                        arg_encode=[
                            "tmp_v = BUILD_STRING_TYPE_ARRAY(\"s\", <req><arg_name>);",
                            "g_variant_builder_add_value(&builder, tmp_v);"],
                        ),
        "g": CTypeBase(variant_type="g",
                       write_type="signature",
                       arg_in="<const>gchar *<arg_name>",
                       arg_out="gchar **<arg_name>",
                       args_write_remote_declear="g_variant_new_signature(<arg_name> ? <arg_name> : \"\")",
                       arg_decode=[
                           "<req><arg_name> = parameter_get_signature(parameters, arg_id);"],
                       arg_free=["g_free(<req><arg_name>);"],
                       arg_encode=[
                           "g_variant_builder_add_value(&builder, g_variant_new_signature(<req><arg_name>));"]),
        "ag": CTypeBase(variant_type="ag",
                        write_type="array_signature",
                        arg_in="<const>gchar *<const>*<arg_name>",
                        arg_out="gchar ***<arg_name>",
                        args_write_remote_declear="BUILD_STRING_TYPE_ARRAY(\"g\", <arg_name>)",
                        arg_decode=["ITER_STRING_TYPE_ARRAY(parameters, arg_id, <req><arg_name>, char *, \"g\");"],
                        arg_free=["g_strfreev(<req><arg_name>);"],
                        arg_encode=[
                            "tmp_v = BUILD_STRING_TYPE_ARRAY(\"g\", <req><arg_name>);",
                            "g_variant_builder_add_value(&builder, tmp_v);"],
                        ),
        "o": CTypeBase(variant_type="o",
                       write_type="object_path",
                       arg_in="<const>gchar *<arg_name>",
                       arg_out="gchar **<arg_name>",
                       args_write_remote_declear="g_variant_new_object_path(<arg_name> ? <arg_name> : \"\")",
                       arg_decode=[
                           "<req><arg_name> = parameter_get_object_path(parameters, arg_id);"],
                       arg_free=["g_free(<req><arg_name>);"],
                       arg_encode=[
                           "g_variant_builder_add_value(&builder, g_variant_new_object_path(<req><arg_name>));"]),
        "ao": CTypeBase(variant_type="ao",
                        write_type="array_object_path",
                        arg_in="<const>gchar *<const>*<arg_name>",
                        arg_out="gchar ***<arg_name>",
                        args_write_remote_declear="BUILD_STRING_TYPE_ARRAY(\"o\", <arg_name>)",
                        arg_decode=[
                            "ITER_STRING_TYPE_ARRAY(parameters, arg_id, <req><arg_name>, char *, \"o\");"],
                        arg_free=["g_strfreev(<req><arg_name>);"],
                        arg_encode=[
                            "tmp_v = BUILD_STRING_TYPE_ARRAY(\"o\", <req><arg_name>);",
                            "g_variant_builder_add_value(&builder, tmp_v);"],
                        ),
        "*": CTypeBase(variant_type="v",
                       write_type="variant",
                       arg_in="GVariant *<arg_name>",
                       arg_out="GVariant **<arg_name>",
                       args_write_remote_declear="g_variant_ref(<arg_name>)",
                       arg_decode=[
                           "<req><arg_name> = g_variant_get_child_value(parameters, arg_id);"],
                       arg_free=["if (<req><arg_name>) {",
                                 "    g_variant_unref(<req><arg_name>);", "}"],
                       arg_encode=[
                           "g_variant_take_ref(<req><arg_name>);",
                           "g_variant_builder_add_value(&builder, <req><arg_name>);"])
    }
