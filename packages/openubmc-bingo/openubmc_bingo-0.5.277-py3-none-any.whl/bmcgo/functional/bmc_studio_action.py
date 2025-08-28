#!/usr/bin/python3
# coding: utf-8
# 启动停止bmc studio的操作
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import os
import argparse

from bmcgo.utils.tools import Tools
from bmcgo import misc
from bmcgo.bmcgo_config import BmcgoConfig

tools = Tools("bmc_studio")
log = tools.log
ACTION_TRUE = "store_true"


command_info: misc.CommandInfo = misc.CommandInfo(
    group=misc.GRP_STUDIO,
    name="studio",
    description=["执行bmc studio启动停止操作"],
    hidden=False
)


def if_available(bconfig: BmcgoConfig):
    return True


class BmcgoCommand(object):
    def __init__(self, bconfig: BmcgoConfig, *args):
        self.bconfig = bconfig
        parser = argparse.ArgumentParser(prog="bmc studio", description="启动停止bmc studio", add_help=True,
                                        formatter_class=argparse.RawTextHelpFormatter)
        action_group = parser.add_mutually_exclusive_group()
        action_group.add_argument("-start", action=ACTION_TRUE, help="bmc studio的启动操作")
        action_group.add_argument("-stop", action=ACTION_TRUE, help="bmc studio的停止操作")
        action_group.add_argument("-restart", action=ACTION_TRUE, help="bmc studio的重启操作")
        parser.add_argument("-b", "--backend", help="指定bmc studio是前端运行还是后端运行，默认前端运行", action=ACTION_TRUE)
        parsed_args, _ = parser.parse_known_args(*args)
        self.action = self.get_action(parsed_args)
        self.backend = parsed_args.backend
        self.studio_path = tools.get_studio_path()
        self.studio_command = ""
        self.studio_script = ""
        if self.studio_path:
            self.studio_script = f"{self.studio_path}/bmc_studio.sh"
            self.studio_command = f"{self.studio_script} {self.action}"

    def get_action(self, parsed_args):
        if parsed_args.stop:
            return "stop"
        elif parsed_args.restart:
            return "restart"
        else:
            return "start"

    def run(self):
        if not self.studio_command or not os.path.isfile(self.studio_script):
            raise Exception(f"bmc studio服务不存在,请安装之后重试操作。")

        if self.action == "stop":
            self.run_stop()
            return

        self.run_start()

    def run_stop(self):
        stop_ret = tools.run_command(self.studio_command, command_echo=False,
            ignore_error=True, capture_output=True)
        stop_out = stop_ret.stdout
        if stop_ret.returncode == 0:
            log.info(stop_out)
            return

        log.warning(stop_out)

    def run_start(self):
        if not self.backend:
            tools.run_command(self.studio_command, command_echo=False, show_log=True, timeout=None)
            return

        self.studio_command = f"{self.studio_command} backend"
        start_ret = tools.run_command(self.studio_command, command_echo=False,
            ignore_error=True, capture_output=True)
        start_out = start_ret.stdout
        if start_ret.returncode == 0:
            log.info(start_out)
            return

        log.warning(start_out)
