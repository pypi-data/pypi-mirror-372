#!/usr/bin/env python3
# coding=utf-8
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

import json
import logging
import getopt
import sys
import os
import stat
from collections import OrderedDict
import mds_util as utils


MDB_INTF_ITEM = ["properties", "methods", "signals"]
MDB_METHOD_KEY = ["baseType", "items", "minimum", "maximum", "minLength", "maxLength", "pattern", "enum"]
MDB_PROPERTY_KEY = MDB_METHOD_KEY + ["readOnly", "deprecated", "constrait"]
OBJECT_PROPERTIES_INTERFACE = "bmc.kepler.Object.Properties"
BASETYPE = "baseType"
REQ = "req"
RSP = "rsp"


class MethodCheckArgs:
    def __init__(self, mdb_data, complete_data, class_name, intf_name, method, param_type):
        self.mdb_data = mdb_data
        self.complete_data = complete_data
        self.class_name = class_name
        self.intf_name = intf_name
        self.method = method
        self.param_type = param_type


def get_parent_path(origin_model, class_data):
    if "parent" in class_data and class_data["parent"] in origin_model and \
                "path" in origin_model[class_data["parent"]]:
        return get_parent_path(origin_model, origin_model[class_data["parent"]]) \
            + "/" + utils.cut_ids(class_data["path"])
    else:
        return utils.cut_ids(class_data["path"])


def check_prop_consistency(mdb_item, complete_item, class_name, intf_name, prop_keys):
    for prop in prop_keys:
        if BASETYPE in mdb_item[prop] and BASETYPE in complete_item[prop]:
            if mdb_item[prop][BASETYPE] != complete_item[prop][BASETYPE]:
                raise RuntimeError(f"组件模型中类{class_name}接口{intf_name}的属性{prop}的类型{complete_item[prop][BASETYPE]}"
                    f"与mdb_interface对应类型{mdb_item[prop][BASETYPE]}不一致"
                )


def check_method_params(args):
    mdb_keys = set(args.mdb_data.keys())
    complete_keys = set(args.complete_data.keys())
    label = "请求" if args.param_type == REQ else "响应"
    if mdb_keys != complete_keys:
        only_in_mdb = mdb_keys - complete_keys
        if only_in_mdb:
            raise RuntimeError(f"组件模型中类{args.class_name}接口{args.intf_name}的方法{args.method}中的{label}参数{only_in_mdb}"
                f"未实现，请检查model.json与mdb_interface定义"
            )
        only_in_complete = complete_keys - mdb_keys
        if only_in_complete:
            raise RuntimeError(f"组件模型中类{args.class_name}接口{args.intf_name}的方法{args.method}中的{label}参数{only_in_complete}"
                f"未在mdb_interface中定义，请检查model.json与mdb_interface定义"
            )
    
    for param in mdb_keys:
        if BASETYPE in args.mdb_data[param] and BASETYPE in args.complete_data[param]:
            if args.mdb_data[param][BASETYPE] != args.complete_data[param][BASETYPE]:
                raise RuntimeError(f"组件模型中类{args.class_name}接口{args.intf_name}的方法{args.method}中的{label}参数{param}的类型"
                    f"{args.complete_data[param][BASETYPE]}与mdb_interface对应类型{args.mdb_data[param][BASETYPE]}不一致"
                )


def check_method_consistency(mdb_item, complete_item, class_name, intf_name, method_keys):
    for method in method_keys:
        has_req_mdb = REQ in mdb_item[method]
        has_req_complete = REQ in complete_item[method]
        if has_req_mdb != has_req_complete:
            if has_req_mdb:
                raise RuntimeError(f"组件模型中类{class_name}的接口{intf_name}的方法{method}中未实现req，请检查model.json与mdb_interface定义")
            else:
                raise RuntimeError(f"组件模型中类{class_name}的接口{intf_name}的方法{method}中req未在mdb_interface中定义"
                    f"，请检查model.json与mdb_interface定义"
                )
        else:
            if has_req_mdb:
                method_req_params = MethodCheckArgs(mdb_item[method][REQ], complete_item[method][REQ], \
                                                    class_name, intf_name, method, REQ)
                check_method_params(method_req_params)

        has_rsp_mdb = RSP in mdb_item[method]
        has_rsp_complete = RSP in complete_item[method]
        if has_rsp_mdb != has_rsp_complete:
            if has_rsp_mdb:
                raise RuntimeError(f"组件模型中类{class_name}的接口{intf_name}的方法{method}中未实现rsp参数"
                    f"，请检查model.json与mdb_interface定义"
                )
            else:
                raise RuntimeError(f"组件模型中类{class_name}的接口{intf_name}的方法{method}中rsp未在mdb_interface中定义"
                    f"，请检查model.json与mdb_interface定义"
                )
        else:
            if has_rsp_mdb:
                method_rsp_params = MethodCheckArgs(mdb_item[method][RSP], complete_item[method][RSP], \
                                                    class_name, intf_name, method, RSP)
                check_method_params(method_rsp_params) 


def check_intf_item_consistency(mdb_item, complete_item, class_name, intf_name, item_type):
    mdb_keys = set(mdb_item.keys())
    complete_keys = set(complete_item.keys())
    diff_keys = mdb_keys.symmetric_difference(complete_keys)
    if diff_keys:
        only_in_mdb = diff_keys - complete_keys
        only_in_complete = diff_keys - mdb_keys
        if only_in_mdb:
            raise RuntimeError(f"组件模型中类{class_name}的接口{intf_name}的{item_type}未实现{only_in_mdb}"
                f"，请检查model.json与mdb_interface定义"
            )
        if only_in_complete:
            raise RuntimeError(f"组件模型中类{class_name}的接口{intf_name}的{item_type}中的{only_in_complete}"
                f"未在mdb_interface中定义，请检查model.json与mdb_interface定义"
            )

    if item_type == "properties":
        check_prop_consistency(mdb_item, complete_item, class_name, intf_name, mdb_keys)
    elif item_type == "methods":
        check_method_consistency(mdb_item, complete_item, class_name, intf_name, mdb_keys)


def check_intf_consistency(mdb_intf, complete_intf, class_name, intf_name):
    for item in MDB_INTF_ITEM:
        if item in mdb_intf and item not in complete_intf:
            if mdb_intf[item]:
                raise RuntimeError(f"组件模型中类{class_name}的接口{intf_name}未实现{item}，请检查model.json与mdb_interface定义")
        elif item not in mdb_intf and item in complete_intf:
            if complete_intf[item]:
                raise RuntimeError(f"组件模型中类{class_name}的接口{intf_name}的{item}未在mdb_interface中定义"
                    f"，请检查model.json与mdb_interface定义"            
                )
        elif item in mdb_intf and item in complete_intf:
            check_intf_item_consistency(mdb_intf[item], complete_intf[item], class_name, intf_name, item)


def check_model_consistency(class_name, complete_model, mdb_obj, mdb_path):
    intf_complete = set(complete_model["interfaces"].keys())
    intf_mdb = set(mdb_obj[class_name]["interfaces"])
    if intf_complete != intf_mdb:
        intf_only_in_mds = intf_complete - intf_mdb
        intf_only_in_mds.discard(OBJECT_PROPERTIES_INTERFACE)
        if intf_only_in_mds:
            raise RuntimeError(f"组件模型中类{class_name}的接口{intf_only_in_mds}未在mdb_interface中定义"
                f"，请检查model.json与mdb_interface定义"
            )
        intf_only_in_mdb = intf_mdb - intf_complete
        if intf_only_in_mdb:
            raise RuntimeError(f"组件模型中类{class_name}未实现{intf_only_in_mdb}接口，请检查model.json与mdb_interface定义")

    for intf_name in intf_complete:
        mdb_intf_json = utils.get_intf(intf_name, mdb_path)
        check_intf_consistency(mdb_intf_json[intf_name], complete_model["interfaces"][intf_name], class_name, intf_name)


def check(if_name, mdb_path):
    load_dict = {}
    if os.path.exists(if_name):
        load_f = os.fdopen(os.open(if_name, os.O_RDONLY, stat.S_IRUSR), "r")
        load_dict = OrderedDict(json.load(load_f))
        load_f.close()

    for class_name, class_data in load_dict.items():
        if "path" in class_data and class_name != "defs":
            class_path = get_parent_path(load_dict, class_data)
            mdb_obj = utils.get_path(class_name, mdb_path, class_path)
            check_model_consistency(class_name, class_data, mdb_obj, mdb_path)


def get_all_modelx_json(mds_dir):
    load_dict = {}
    for root, _, files in os.walk(mds_dir):
        for file in files:
            if file == 'modelx.json':
                file_path = os.path.join(root, file)
                load_f = os.fdopen(os.open(file_path, os.O_RDONLY, stat.S_IRUSR), "r")
                load_modelx_dict = OrderedDict(json.load(load_f))
                load_dict.update(load_modelx_dict)

    return load_dict


def access_check(mds_dir, mdb_path):
    load_dict = get_all_modelx_json(mds_dir)

    for class_name, class_data in load_dict.items():
        if "path" in class_data and class_name != "defs":
            class_path = get_parent_path(load_dict, class_data)
            mdb_obj = utils.get_path(class_name, mdb_path, class_path)
            check_model_consistency(class_name, class_data, mdb_obj, mdb_path)

    return True   
    

def usage():
    logging.info("model_consistency_check.py -i <inputfile> -d <MdbInterfaceDir>")


def main(argv):
    m_input = ""
    mdb_path = ""
    try:
        opts, _ = getopt.getopt(argv, "hi:d:", ["help", "input=", "mdb_interface_path="])
    except getopt.GetoptError:
        help()
        return
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            return
        elif opt in ("-i", "--input"):
            m_input = arg
        elif opt in ("-d", "--dir"):
            mdb_path = arg
        else:
            raise RuntimeError("不支持的选项: {}".format(opt))
    if not m_input:
        usage()
        return
    check(m_input, mdb_path)


if __name__ == "__main__":
    main(sys.argv[1:])
