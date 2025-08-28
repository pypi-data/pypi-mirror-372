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

import re
import os
import sys
import json
import stat
import logging
import shutil
from typing import List, Dict
from bmcgo.utils.tools import Tools

tools = Tools("bmcgo_config")


def get_package_name(ipmi_json_filename: str) -> str:
    """ 从ipmi.json中读取package名 """
    with os.fdopen(os.open(ipmi_json_filename, os.O_RDONLY, stat.S_IRUSR), "r") as json_f:
        ipmi_json_dict = json.load(json_f)
        return ipmi_json_dict.get("package")


def get_cmd_names(ipmi_json_filename: str) -> List[str]:
    """ 从ipmi.json中读取所有命令名 """
    with os.fdopen(os.open(ipmi_json_filename, os.O_RDONLY, stat.S_IRUSR), "r") as json_f:
        ipmi_json_dict = json.load(json_f)
        cmds_dict = ipmi_json_dict.get("cmds")
        return list(cmds_dict.keys())


def get_copyright_comments(lines: List[str]) -> List[str]:
    """ 取出ipmi_message的copyright注释 """
    comments_end = -1

    # 找到copyright注释的结束位置
    for i, line in enumerate(lines):
        match_obj = re.search(f"local (.+) = require (.+)", line)
        if match_obj:
            comments_end = i
            break

    copyright_comments = lines[:comments_end]

    return copyright_comments


def filter_out_cmds_requires(lines: List[str], package_name: str) -> List[str]:
    """ 取出ipmi_message的require语句, 并从lines中删除 """
    requires_end = -1
    requires = []
    remove_lines = []

    # 找到require语句的结束位置
    for i, line in enumerate(lines):
        match_obj = re.search(f"local {package_name}Msg = ", line)
        if match_obj:
            requires_end = i
            break

    for i, line in enumerate(lines):
        if i >= requires_end:
            break
        match_obj = re.search(f"local (.+) = require (.+)", line)
        if match_obj:
            remove_lines.append(i)
            requires.append(line)

    # 从lines中删除require语句
    for i in reversed(remove_lines):
        del lines[i]

    return requires


def save_cmds_to(output_dir: str, ipmi_cmd_dict: Dict, package_name: str, requires: List[str], 
                copyright_comments: List[str]):
    """ 将每个命令保存到output_dir目录单独的文件中 """
    requires_s = ''.join(requires) # require语句
    copyright_comments_s = ''.join(copyright_comments) # copyright注释
    file_list = []

    for cmd_name in ipmi_cmd_dict:
        cmd_filename = os.path.join(output_dir, f"{cmd_name}.lua")
        with os.fdopen(os.open(cmd_filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as output_f:
            code_prepend = f"\nlocal {cmd_name} = " + "{}\n\n" # declaration语句
            code_append = f"\nreturn {cmd_name}" # return语句
            code = copyright_comments_s + requires_s + code_prepend + ipmi_cmd_dict[cmd_name]['code'] + code_append
            code = code.replace(f'{package_name}Msg', cmd_name)
            output_f.write(code)
        file_list.append(cmd_filename)
    return file_list


def modify_ipmi_message_lines(lines: List[str], ipmi_cmd_dict: Dict, package_name: str, project_name: str):
    """ 修改lines, 删除多余的命令信息, 添加require语句引用单独的命令文件 """
    trim_start = -1
    trim_end = -1

    # 找到需要删除的首行和尾行
    for i, line in enumerate(lines):
        match_obj = re.search(f"local {package_name}Msg = ", line)
        if match_obj:
            trim_start = i
        match_obj = re.search(f"return {package_name}Msg", line)
        if match_obj:
            trim_end = i

    del lines[trim_start: trim_end]

    # 添加require语句引用单独的命令文件
    requires = [f"local {package_name}Msg = " + "{\n"]
    for i, cmd_name in enumerate(ipmi_cmd_dict):
        requires.append(f"    {cmd_name}Req = (require '{project_name}.ipmi.cmds.{cmd_name}').{cmd_name}Req,\n")
        if i == len(ipmi_cmd_dict) - 1:
            requires.append(f"    {cmd_name}Rsp = (require '{project_name}.ipmi.cmds.{cmd_name}').{cmd_name}Rsp\n")
        else:
            requires.append(f"    {cmd_name}Rsp = (require '{project_name}.ipmi.cmds.{cmd_name}').{cmd_name}Rsp,\n")
    requires.append("}\n")
    requires.append("\n")

    lines[:] = lines[:trim_start] + requires + lines[trim_start:]


def get_ipmi_cmd_dict(lines: List[str], cmd_names: List[str], package_name: str):
    """ 读取lines, 生成并返回ipmi_cmd_dict """
    ipmi_cmd_dict = {} # cmd_name -> {start: int, end: int, code: str}

    for i, line in enumerate(lines):
        match_obj = re.search(f"@class {package_name}.(.+)", line)
        if match_obj:
            cmd_name = match_obj.group(1)[:-3] # 最后三位是Rsp/Req
            if cmd_name not in ipmi_cmd_dict:
                ipmi_cmd_dict[cmd_name] = {
                    "start": i,
                    "end": -1,
                    "code": ''
                }
        for cmd_name in cmd_names:
            found_cmd_end = (f'{package_name}Msg.{cmd_name}Req' in line) or (f'{package_name}Msg.{cmd_name}Rsp' in line)
            if cmd_name in ipmi_cmd_dict and found_cmd_end:
                ipmi_cmd_dict[cmd_name]['end'] = i
                code_start = ipmi_cmd_dict[cmd_name].get('start', 0)
                code_end = ipmi_cmd_dict[cmd_name].get('end', -1)
                ipmi_cmd_dict[cmd_name]['code'] = ''.join(lines[code_start: code_end + 1])

    return ipmi_cmd_dict


def sep_ipmi_message_cmds(ipmi_json_filename: str, ipmi_message_filename: str, output_dir: str, project_name: str,
                          lua_format: str):
    """ 分离集中在ipmi_message.lua的命令到单独的文件 """
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    else:
        shutil.rmtree(output_dir)
        os.mkdir(output_dir)

    package_name = get_package_name(ipmi_json_filename)
    cmd_names = get_cmd_names(ipmi_json_filename)
    lines = []

    # 读取ipmi_message文件到ipmi_cmd_dict(cmd_name -> {start: int, end: int, code: str}) 
    with os.fdopen(os.open(ipmi_message_filename, os.O_RDONLY, stat.S_IRUSR), "r") as input_f:
        lines = input_f.readlines()
    ipmi_cmd_dict = get_ipmi_cmd_dict(lines, cmd_names, package_name)

    copyright_comments = get_copyright_comments(lines)

    requires = filter_out_cmds_requires(lines, package_name)

    file_list = save_cmds_to(output_dir, ipmi_cmd_dict, package_name, requires, copyright_comments)

    # 修改ipmi_message文件，引用分离开的单独的命令
    modify_ipmi_message_lines(lines, ipmi_cmd_dict, package_name, project_name)
    os.chmod(ipmi_message_filename, 0o666)
    with os.fdopen(os.open(ipmi_message_filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                           stat.S_IWUSR | stat.S_IRUSR), 'w') as output_f:
        output_f.write(''.join(lines))
    file_list.append(ipmi_message_filename)
    for file_path in file_list:
        if os.path.exists(lua_format):
            tools.run_command(["python3", lua_format, file_path], command_echo=False)
        os.chmod(file_path, 0o444)


def usage():
    """ 输出脚本使用示例 """
    logging.info("sep_ipmi_message.py <ipmi.json path> <ipmi_message.lua path> <output directory> <lua_format path>")


def main(args: List[str]):
    if len(args) < 5:
        usage()
        return

    ipmi_json_filename = args[0]
    ipmi_message_filename = args[1]
    output_dir = args[2]
    project_name = args[3]
    lua_format = args[4]

    sep_ipmi_message_cmds(ipmi_json_filename, ipmi_message_filename, output_dir, project_name, lua_format)


if __name__ == "__main__":
    main(sys.argv[1:])
