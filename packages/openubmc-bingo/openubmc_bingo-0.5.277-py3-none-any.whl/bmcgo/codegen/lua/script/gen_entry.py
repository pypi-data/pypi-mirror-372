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

from subprocess import Popen, PIPE
import json
import logging
import getopt
import sys
import os
import stat
import re

from mako.lookup import TemplateLookup

import mds_util
from utils import Utils
IPMI_DICT = "ipmi_dict"
MODEL_DICT = "model_dict"
APP_NAME = "app_name"
APP_SRC = "src"
IPMI_INPUT = "ipmi_input"
MODEL_INPUT = "model_input"


def gen_ipmi_cmd(options):
    output_file_path = os.path.join(options['output_dir'], APP_SRC, 'lualib', 'callbacks', 'ipmi_cmd.lua')
    template_path = os.path.join(options['template_dir'], 'ipmi_cmd.lua.mako')
    if not os.path.exists(output_file_path):
        template_render(options, template_path, output_file_path,
                        draft_info='本文件依据mds中定义的ipmi命令生成，完成ipmi命令回调函数')
        return

    output_file = os.fdopen(os.open(output_file_path, os.O_RDWR, stat.S_IWUSR | stat.S_IRUSR), 'w+')
    content = output_file.read()
    new_methods = []
    for ipmi_method in options[IPMI_DICT].get('cmds', []):
        pattern = re.compile(f'function ipmi_cmd.{ipmi_method}')
        result = re.search(pattern, content)
        if result is None:
            new_methods.append(ipmi_method)
    added_content = ""
    for ipmi_method in new_methods:
        added_content += f'''function ipmi_cmd.{ipmi_method}(req, ctx)
    return
end

'''
    end_line = 'factory.register_to_factory(\'ipmi_cmd\', ipmi_cmd)'
    content = content.replace(end_line, added_content + end_line)
    output_file.seek(0)
    output_file.truncate()
    output_file.write(content)
    output_file.close()


def gen_class(options, cls):
    output_file_path = os.path.join(options['output_dir'], APP_SRC, 'lualib',
                                    'callbacks', 'classes', cls.lower() + '.lua')
    if not os.path.exists(output_file_path):
        template_path = os.path.join(options['template_dir'], 'class.lua.mako')
        template_render(options, template_path, output_file_path, cls, '本文件依据mds中定义的类生成，完成对应接口方法的回调函数')
        return
    output_file = os.fdopen(os.open(output_file_path, os.O_RDWR, stat.S_IWUSR | stat.S_IRUSR), 'w+')
    content = output_file.read()

    cls_methods = dict()
    for interface, intf_dict in options[MODEL_DICT][cls].get('interfaces', {}).items():
        intf_name = interface.split('.')[-1]
        for method_name, method_dict in intf_dict.get('methods', {}).items():
            if intf_name == 'Default':
                pre_intf_name = interface.split('.')[-2]
                cls_methods[cls + pre_intf_name + intf_name + method_name] = list(method_dict.get('req', {}).keys())
            else:
                unique_intf_name = Utils.get_unique_intf_name(interface)
                cls_methods[cls + unique_intf_name + method_name] = list(method_dict.get('req', {}).keys())

    new_methods = []
    for method, args in cls_methods.items():
        pattern = f'function {cls.lower()}:{method}\s*\(([\s\w,]+)\)'
        pattern = re.compile(pattern)
        result = re.search(pattern, content)
        if result is None:
            new_method = f'{method}(obj, ctx'
            new_method += ''.join(map(lambda s: ', ' + s, args))
            new_method += ')'
            new_methods.append(new_method)
            continue

        user_args = [arg.strip() for arg in result.groups()[0].split(',')]
        if set(user_args[2:]) != set(args):
            replacement = f'function {cls.lower()}:{method}({user_args[0]}, {user_args[1]}'
            replacement += ''.join(map(lambda s: ', ' + s, args))
            replacement += ')'
            content = re.sub(pattern, replacement, content)

    added_content = ""
    for new_method in new_methods:
        added_content += f'''function {cls.lower()}:{new_method}

    return 0
end

'''
    end_line = f'factory.register_to_factory(\'{cls}\', {cls.lower()})'
    content = content.replace(end_line, added_content + end_line)
    output_file.seek(0)
    output_file.truncate()
    output_file.write(content)
    output_file.close()


def template_render(options, template_path, output_file_path, class_name="", draft_info=""):
    header = Utils.make_header(template_path, output_file_path, draft_info)
    lookup = TemplateLookup(directories=[options['template_dir']], input_encoding='utf-8')
    template = lookup.get_template(os.path.basename(template_path))
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    output_file = os.fdopen(os.open(output_file_path,
    os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IWUSR | stat.S_IRUSR), 'w')

    render_data = re.sub(r"\n\n\n+", "\n\n", template.render(
        ipmi=options[IPMI_DICT],
        model=options[MODEL_DICT],
        make_header=header,
        project_name=options[APP_NAME],
        class_name=class_name,
        render_utils=Utils,
        major_version=options["major_version"]
    ))
    output_file.write(render_data)
    output_file.close()

    if os.path.exists(options['formatter_path']):
        with Popen([options['formatter_path'], output_file_path], stdout=PIPE) as proc:
            data, _ = proc.communicate(timeout=50)
            output_file = os.fdopen(os.open(
                output_file_path, os.O_WRONLY | os.O_TRUNC, stat.S_IWUSR | stat.S_IRUSR), 'w')
            output_file.write(data.decode('utf-8'))
            output_file.close()


def generate(options):
    options[IPMI_DICT] = dict()
    options[MODEL_DICT] = dict()
    if os.path.exists(options[IPMI_INPUT]):
        ipmi_f = mds_util.open_file(options[IPMI_INPUT])
        options[IPMI_DICT] = json.load(ipmi_f)
        ipmi_f.close()
    if os.path.exists(options[MODEL_INPUT]):
        model_f = mds_util.open_file(options[MODEL_INPUT])
        options[MODEL_DICT] = json.load(model_f)
        model_f.close()

    if options[IPMI_DICT]:
        gen_ipmi_cmd(options)
    for cls in options[MODEL_DICT]:
        gen_class(options, cls)

    overwrite_main_lua = options[APP_NAME] not in ['oms', 'nsm', 'ddns', 'ssdp', 'usb_entry',
        'event_policy', 'remote_console', 'license', 'cli', 'web_backend', 'redfish', 'firmware_mgmt',
        'bmc_upgrade', 'libroute_mapper', 'snmp', 'critical_rest', 'rmcp', 'ipmi_core']

    output_files_info = [
        (os.path.join(APP_SRC, 'lualib', 'app.lua'), '本文件为微组件app的用户代码入口，本组件的初始化入口', False),
        (os.path.join(APP_SRC, 'lualib', 'callbacks', 'mc.lua'), '本文件为框架回调函数的实现', False),
        (os.path.join('gen', options[APP_NAME], 'entry.lua'), '', True),
        (os.path.join('gen', options[APP_NAME], 'signal_listen.lua'), '', True),
        (os.path.join(APP_SRC, 'service', 'main.lua'), '', overwrite_main_lua)
    ]
    for name, draft_info, overwrite in output_files_info:
        mako_name = os.path.basename(name) + '.mako'
        template_path = os.path.join(options['template_dir'], mako_name)
        output_file_path = os.path.join(options['output_dir'], name)
        if os.path.exists(output_file_path):
            if not overwrite:
                continue
            os.remove(output_file_path)
        template_render(options, template_path, output_file_path, draft_info=draft_info)


def gen_factory(options):
    factory_path = os.path.join(options['output_dir'], 'gen', options[APP_NAME], 'factory.lua')
    if os.path.exists(factory_path):
        os.remove(factory_path)
    factory_content = '''local factory = {}
function factory.register_to_factory(class_name, cls)
    factory[class_name] = cls
end

function factory.get_obj_cb(class_name, method)
    local cls = factory[class_name]
    return function(...)
        return cls[method](cls, ...)
    end
end

return factory
'''
    factory_file = os.fdopen(os.open(factory_path,
    os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IWUSR | stat.S_IRUSR), 'w')
    factory_file.write(factory_content)
    factory_file.close()


def usage():
    logging.info("gen_entry.py -i <ipmifile> -m <modelfile> -o <outdir> -n <appname> -f <formatter> -t <template>")


def main(argv):
    logging.getLogger().setLevel(logging.INFO)
    options = dict()
    try:
        opts, _ = getopt.getopt(argv, "hi:m:o:n:f:t:v:p:", ["help", "ipmi=", "model=",
        "out=", "name=", "formatter=", "template=", "version=", "major_version="])
    except getopt.GetoptError as getopt_error:
        logging.error(getopt_error)
        return
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            return
        elif opt in ("-i", "--ipmi"):
            options[IPMI_INPUT] = arg
        elif opt in ("-m", "--model"):
            options[MODEL_INPUT] = arg
        elif opt in ("-o", "--out"):
            options['output_dir'] = arg
        elif opt in ("-n", "--name"):
            options[APP_NAME] = arg
        elif opt in ("-f", "--formatter"):
            options['formatter_path'] = arg
        elif opt in ("-t", "--template"):
            options['template_dir'] = arg
        elif opt in ("-v", "--version"):
            options['version'] = arg
        elif opt in ("-p", "--major_version"):
            options['major_version'] = arg
        else:
            raise RuntimeError("不支持的选项: {}".format(opt))
    required_keys = {
        IPMI_INPUT, MODEL_INPUT, 'output_dir', APP_NAME,
        'formatter_path', 'template_dir'
    }
    if set(options.keys()) != required_keys:
        logging.error("缺少选项")
        usage()
        return
    if not os.path.exists(options[IPMI_INPUT]):
        logging.warning("mds/ipmi.json 文件不存在")
    if not os.path.exists(options[MODEL_INPUT]):
        logging.warning("mds/model.json 文件不存在")

    generate(options)
    gen_factory(options)


if __name__ == "__main__":
    main(sys.argv[1:])
