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

import json
import argparse
import os
import stat
import re
from mako.lookup import TemplateLookup

import merge_proto_algo
import proto_loader
import utils
from dto.options import Options
from render_utils import Factory
from bmcgo import misc
from bmcgo.utils.tools import Tools

tools = Tools("bmcgo_config")
IMPORT_STR = "imports"
METAVAR = "FILE"


def parse_input_args() -> Options:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="source_file_path",
                        help="Source File Path", metavar=METAVAR)
    parser.add_argument("-t", "--tpl", dest="template_name",
                        help="Template File Name", metavar=METAVAR)
    parser.add_argument("-o", "--out", dest="output_file_path",
                        help="Path of the compilation result file", metavar=METAVAR)
    parser.add_argument("-d", "--dir", dest="proto_root_path",
                        help="Root directory of the proto file in the input file",
                        metavar=METAVAR, default="")
    parser.add_argument("-j", "--json_dir", dest="proto_json_root_path",
                        help="Root directory of the proto json file in the input file", metavar=METAVAR, default="")
    parser.add_argument("-n", "--project_name", dest="project_name",
                        help="project name",
                        default="")
    parser.add_argument("-p", "--major_version", dest="major_version",
                        help="major version",
                        default="")
    parser.add_argument("-v", "--version", dest="version",
                        help="version",
                        default=-1)
    parser.add_argument("--enable_auto_merge", dest="enable_auto_merge",
                        help="Whether result files are automatically combined when customized.",
                        action=misc.STORE_TRUE, default=False)
    parser.add_argument("-f", "--formatter", dest="formatter",
                        help="formatter targe file",
                        metavar=METAVAR, default="")
    options = parser.parse_args()
    if not options.template_name or not options.output_file_path:
        parser.print_help()
        return False, _
    return True, Options.from_parse_args_result(options)


def do_load_import(root, options: Options, proto_path, filename):
    json_file_path = f'{options.proto_json_root_path}/{proto_path}.json'
    if not os.path.exists(json_file_path):
        proto_loader.proto_to_json(
            options.proto_root_path, proto_path, options.proto_json_root_path)
    input_file = open(json_file_path, "r")
    data = json.loads(input_file.read())
    input_file.close()
    if IMPORT_STR not in root:
        root[IMPORT_STR] = {}
    root[IMPORT_STR][filename] = data
    return ''


def make_load_import(root, options: Options):
    return lambda path, filename: do_load_import(root, options, path, filename)


def load_imports(root, options: Options):
    if IMPORT_STR in root:
        imports = {}
        dependency = {}
        for i in root[IMPORT_STR]:
            is_proto = i.startswith("google/protobuf") or i == "types.proto" \
                or i == 'ipmi_types.proto' or i == 'types.proto'
            if is_proto:
                continue
            input_file = open(f'{options.proto_json_root_path}/{i}.json', "r")
            data = json.loads(input_file.read())
            input_file.close()
            imports[data["package"]] = data
            if i in root['dependency']:
                dependency[data["package"]] = data
        root[IMPORT_STR] = imports
        root['dependency'] = dependency


def load_dest_data(options: Options):
    return proto_loader.parse(
        options.proto_root_path,
        os.path.relpath(os.path.abspath(os.path.normpath(options.output_file_path)),
                        os.path.abspath(os.path.normpath(options.proto_root_path))),
        options.proto_json_root_path
    )


def generate(options: Options):
    data = {}
    if options.source_file_path:
        input_file = os.fdopen(
            os.open(options.source_file_path, os.O_RDONLY, stat.S_IRUSR), 'r')
        data = json.loads(input_file.read())
        input_file.close()
        if isinstance(data, dict) and data.get("disable_gen", False):
            return
    if options.enable_auto_merge:
        data = merge_proto_algo.merge_json(data, load_dest_data(options))

    header = utils.Utils(data, options).make_header(
        options.template_name, options.output_file_path)
    lookup = TemplateLookup(directories=[os.getcwd() + "/", os.getcwd() + "/../../"], input_encoding='utf-8')
    template = lookup.get_template(options.template_name)
    if os.path.exists(options.output_file_path):
        os.remove(options.output_file_path)
    load_imports(data, options)
    os.makedirs(os.path.dirname(options.output_file_path), exist_ok=True)
    output_file = os.fdopen(os.open(options.output_file_path,
                            os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IWUSR | stat.S_IRUSR), 'w')
    use_frame_log = options.project_name in [
        'hwdiscovery', 'key_mgmt', 'maca', 'persistence', 'hwproxy', 'soctrl'
    ]

    options.version = int(options.version)
    render_data = re.sub(r"\n\n\n+", "\n\n", template.render(
        root=data,
        utils_py=utils.Utils(data, options),
        render_utils=Factory().new_utils(
            template_name=options.template_name, data=data, options=options),
        make_header=header,
        load_import=make_load_import(data, options),
        project_name=options.project_name,
        version=options.version,
        major_version=options.major_version,
        use_frame_log=use_frame_log,
    ))
    output_file.write(render_data)
    output_file.close()

    if len(options.formatter) > 0 and os.path.exists(options.formatter):
        tools.run_command(["python3", options.formatter, options.output_file_path], command_echo=False)

    os.chmod(options.output_file_path, 0o444)


def main():
    ok, options = parse_input_args()
    if not ok:
        return
    generate(options)


if __name__ == "__main__":
    main()
