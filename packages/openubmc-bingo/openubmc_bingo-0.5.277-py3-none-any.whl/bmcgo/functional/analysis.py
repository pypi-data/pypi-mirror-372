 #!/usr/bin/env python3
# encoding=utf-8
# 描述：组件依赖和接口分析
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
from multiprocessing import Process
import urllib3
from bmcgo.frame import Frame
from bmcgo.misc import CommandInfo
from bmcgo import misc
from bmcgo.utils.tools import Tools
from bmcgo.bmcgo_config import BmcgoConfig
from bmcgo.component.analysis.analysis import AnalysisComp
from bmcgo.component.analysis.intf_validation import InterfaceValidation
from bmcgo.component.analysis.sr_validation import SrValidate
from bmcgo.utils.config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

tool = Tools("analysis")
log = tool.log
command_info: CommandInfo = CommandInfo(
    group="Misc commands",
    name="analysis",
    description=["依赖和接口分析"],
    hidden=False
)


def if_available(bconfig: BmcgoConfig):
    return bconfig.manifest is not None or bconfig.component is not None
        

class BmcgoCommand:
    def __init__(self, bconfig: BmcgoConfig, *args):
        parser = argparse.ArgumentParser(prog="bmcgo analysis", description="BMC package analysis", add_help=True,
            formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-r", "--remote", help="指定conan远端")
        parser.add_argument("--rebuild", dest="rebuild", help="rebuild the package before analysis",
                            action=misc.STORE_TRUE)
        parser.add_argument("--out_dir", dest="out_dir", help="analysis artifacts directory")
        parser.add_argument("--lock_file", dest="lock_file", help="manifest lock file path")
        parser.add_argument("-b", "--board_name", help="find supported boards in the manifest/build/product directory",
                            default="openUBMC")
        pre_parsed_args, _ = parser.parse_known_args(*args)

        self.bconfig = bconfig
        self.remote = pre_parsed_args.remote
        self.rebuild = pre_parsed_args.rebuild
        self.out_dir = pre_parsed_args.out_dir
        self.lock_file = pre_parsed_args.lock_file
        self.board_name = pre_parsed_args.board_name
    
    def run(self):
        is_integrated, work_dir = self._is_integrated_project()
        if is_integrated:
            os.chdir(work_dir)
        else:
            os.chdir(self.bconfig.component.folder)
        # 组件级构建
        if not is_integrated:
            if not InterfaceValidation(self.remote).run() or not SrValidate(os.getcwd()).run():
                return -1
            return 0
        custom_sr_dir = None
        # 非集成环境
        if not is_integrated:
            custom_sr_dir = os.getcwd()
        elif self.rebuild:
            parsed = []
            if self.board_name:
                parsed.append("-b")
                parsed.append(self.board_name)
                config = Config(self.bconfig)
                frame = Frame(self.bconfig, config)
                frame.parse(parsed)
                frame.run()
        os.chdir(os.path.join(work_dir, misc.BUILD))
        analysis_task = AnalysisComp(self.board_name, self.out_dir, self.lock_file, custom_sr_dir)
        rc = analysis_task.run()
        if not rc:
            return -1
        log.success("BMC 构建分析成功")
        return 0
    
    def _is_integrated_project(self):
        if self.bconfig.manifest is not None:
            return True, self.bconfig.manifest.folder
        return False, None