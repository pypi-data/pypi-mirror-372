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

HW_DEFINE_ATTR_OPTION_DICT = {"validate": "", "readonly": False, "rename": ""}
HW_DEFINE_MESSAGE_OPTION_DICT = {}


def merge_options(new_attr: dict, old_attr: dict, self_define_option_set: dict):
    options = old_attr.get("options")
    if not isinstance(options, dict):
        return
    for option in options.keys():
        if option in self_define_option_set:
            new_attr.setdefault(option, options.get(option))


def merge_property_list(new_property_dict, property_list):
    for pt in property_list:
        if not isinstance(pt, dict):
            continue
        attr_name = pt.get("name")
        new_attr = new_property_dict.get(attr_name)
        if not isinstance(new_attr, dict):
            continue
        merge_options(new_attr, pt, HW_DEFINE_ATTR_OPTION_DICT)


def merge_message(new_message: dict, message: dict):
    merge_options(new_message, message, HW_DEFINE_MESSAGE_OPTION_DICT)
    property_list = message.get("properties")
    if not isinstance(property_list, list):
        return
    new_property_dict = new_message.get("properties")
    if not isinstance(new_property_dict, dict):
        return

    merge_property_list(new_property_dict, property_list)


def merge_message_list(new_message_dict: dict, message_list: list):
    for message in message_list:
        name = message.get("name")
        new_message = new_message_dict.get(name)
        if not new_message:
            continue
        merge_message(new_message, message)


def merge_json(redfish_json: dict, proto_json: dict):
    if not isinstance(redfish_json, dict) or not isinstance(proto_json, dict):
        return redfish_json
    message_list = proto_json.get("data")
    if not isinstance(message_list, list):
        return redfish_json
    new_message_dict = redfish_json.get("definitions")
    if not isinstance(new_message_dict, dict):
        return redfish_json
    merge_message_list(new_message_dict, message_list)
    return redfish_json


def is_need_specify_option(key: str, value, option_dict: dict) -> bool:
    if key not in option_dict:
        return False
    default_value = option_dict.get(key)
    if default_value == value:
        return False
    return True


def is_message_option(key: str, value) -> bool:
    return is_need_specify_option(key, value, HW_DEFINE_MESSAGE_OPTION_DICT)


def is_attr_option(key: str, value) -> bool:
    return is_need_specify_option(key, value, HW_DEFINE_ATTR_OPTION_DICT)
