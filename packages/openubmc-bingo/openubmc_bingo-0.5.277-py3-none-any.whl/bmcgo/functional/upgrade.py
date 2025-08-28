#!/usr/bin/env python3
# encoding=utf-8
# 描述：bingo 升级工具
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

import re
import argparse
from pathlib import Path
from bmcgo import misc
from bmcgo.logger import Logger
from bmcgo.bmcgo_config import BmcgoConfig
from bmcgo.utils.tools import Tools
from bmcgo.utils.install_manager import InstallManager
from bmcgo.utils.installations import install_consts

tools = Tools("bingo_upgrade")
log = Logger()

command_info: misc.CommandInfo = misc.CommandInfo(
    group=misc.GRP_MISC,
    name="upgrade",
    description=["升级 bingo 版本"],
    hidden=False
)


def if_available(bconfig: BmcgoConfig):
    return True


_DESCRIPTION = """
bingo 升级工具
"""


class BmcgoCommand:
    VERSION_PATTERN = re.compile(
        r"^([a-zA-Z0-9_-]+)\s*([<>]=?|[!~]?=)?\s*([a-zA-Z0-9._+-]*|"
        rf"{install_consts.INSTALL_LATEST})$"
    )

    def __init__(self, bconfig: BmcgoConfig, *args):
        parser = argparse.ArgumentParser(
            prog="bingo upgrade",
            description=_DESCRIPTION,
            add_help=True,
            formatter_class=argparse.RawTextHelpFormatter
        )
        parser.add_argument(
            "-v",
            "--version",
            default=install_consts.INSTALL_DEFAULT,
            help="列出所有配置"
        )
        parser.add_argument(
            "-f",
            "--force",
            action=misc.STORE_TRUE,
            help="跳过确认，直接安装"
        )
        parser.add_argument(
            "-l",
            "--list",
            action=misc.STORE_TRUE,
            help="列出可安装版本"
        )

        args, _ = parser.parse_known_args()

        self.version = args.version
        self.force = args.force
        self.list = args.list

        self.installer = InstallManager()
        self.plugin_path = Path(bconfig.bmcgo_config_list.get(misc.CUSTOM_PLUGINS, misc.DEFAULT_PLUGINS_PATH))

    def run(self):
        app, opt, ver = self._parse_version()
        self.installer.init(app, opt, ver, self.plugin_path)

        if self.list:
            self._list_all_versions()
            return 0

        self.installer.pre_install()
        self.installer.install(self.force)
        self.installer.post_install()

        log.info(f"安装{self.version}已完成！")
        return 0

    def _list_all_versions(self):
        self.installer.show_versions()

    def _parse_version(self):
        match = re.search(self.VERSION_PATTERN, self.version)
        if match:
            return match.groups()
        self.version = install_consts.INSTALL_DEFAULT
        return self._parse_version()
