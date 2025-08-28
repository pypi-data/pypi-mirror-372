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

import argparse
import shutil
import os
import stat
from subprocess import Popen, PIPE


def find_lua_format():
    lua_format = shutil.which('lua-format', mode=os.X_OK)
    if lua_format:
        return lua_format
    lua_format = os.getenv('LUA_FORMAT')
    if os.access(lua_format, os.X_OK):
        return lua_format
    raise RuntimeError('找不到工具 lua-format')


def find_config_file(file):
    parent_dir = os.path.dirname(file)
    while len(parent_dir) > 1:
        if os.path.exists(os.path.join(parent_dir, '.lua-format')):
            return os.path.join(parent_dir, '.lua-format')
        parent_dir = os.path.dirname(parent_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', metavar='FILE', type=str, nargs='+',
                        help='Source File Paths')
    options = parser.parse_args()
    files = options.files
    if len(files) == 0:
        return
    if len(files) > 1:
        raise RuntimeError('格式化文件不得超过一个')

    cmds = [find_lua_format()]
    cfg = find_config_file(__file__)
    if cfg:
        cmds += ['-c', cfg]
    cmds += files
    with Popen(cmds, stdout=PIPE) as proc:
        data, _ = proc.communicate(timeout=50)
        output = data.decode('utf-8')
    with os.fdopen(os.open(files[0], os.O_WRONLY | os.O_TRUNC, stat.S_IWUSR | stat.S_IRUSR), 'w') as out_fp:
        out_fp.write(output)


if __name__ == "__main__":
    main()
