#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
'''
功    能：构建框架
修改记录：2021-10-11 创建
'''
import os
import time
import sys
import argparse
import signal
import shutil
import stat

from bmcgo import misc
from bmcgo import errors
from bmcgo.utils.perf_analysis import PerfAnalysis
from bmcgo.utils.tools import Tools
from bmcgo.bmcgo_config import BmcgoConfig
from bmcgo.functional.deploy import BmcgoCommand as Deploy
from bmcgo.worker import WorkStatusServer, create_target_scheduler, q

tool = Tools(__name__)
log = tool.log


class Frame(object):
    def __init__(self, bconfig: BmcgoConfig, config):
        self.bconfig = bconfig
        https_proxy = os.environ.get("https_proxy")
        if https_proxy is not None and https_proxy != "":
            log.warning("检测到环境设置了https_proxy代理，可能导致网络资源访问失败.")
            log.warning("  如需关闭代理，请执行命令: export https_proxy=")
            log.warning("  如需关闭特定域名或IP的代理，可以设置no_proxy环境变量，也可将no_proxy设置到/etc/profile中.")
            log.warning("  no_proxy配置示例: export no_proxy=localhost,127.0.0.0/8,.huawei.com,.inhuawei.com")
        self.perf = PerfAnalysis(os.path.join(bconfig.manifest.folder, "output"))
        self.code_path = os.path.join(bconfig.manifest.folder, "build")
        sys.path.append(self.code_path)
        os.makedirs(misc.CACHE_DIR, exist_ok=True)
        self.ws_server = None
        self.config = config
        self.config.log_init()
        self.need_deploy = False
        self.args = None
        self.conan_args = None
        self.targets = {}

    def record_build_time(self):
        date_file = f"{self.config.temp_path}/date/date.txt"
        os.makedirs(os.path.dirname(date_file), exist_ok=True)
        with os.fdopen(os.open(date_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as file_handler:
            now = time.strftime("%H:%M:%S %b %-d %Y", time.localtime())
            file_handler.write(now)
            file_handler.close()

    def get_all_target(self, ex_target_dir=""):
        targets = {}
        bingo_install_path = os.path.dirname(os.path.abspath(__file__))
        dirname = os.path.join(bingo_install_path, "target")
        for file in os.listdir(dirname):
            if not file.endswith(".yml"):
                continue
            tgt_file = os.path.join(dirname, file)
            targets[file.split(".")[0]] = tgt_file
        if not os.path.isdir(ex_target_dir):
            return targets
        for file in os.listdir(ex_target_dir):
            if not file.endswith(".yml"):
                continue
            tgt_file = os.path.join(ex_target_dir, file)
            targets[file.split(".")[0]] = tgt_file
        return targets

    def cmc_open_parse(self, args, unknown_args):
        if args.target != "cmc_open" and args.target != "docker_build":
            return None, unknown_args
        parser = argparse.ArgumentParser(description="cmc_open info")
        parser.add_argument("-ud", "--upload_docker", help="是否上传docker镜像", action=misc.STORE_TRUE)
        parser.add_argument("-pn", "--partner_name", help="伙伴名称")
        local_time = time.strftime("%y%m%d%H%M", time.localtime())
        default_tag = f'v3_partner_{local_time}_{self.bconfig.current_branch}'
        parser.add_argument("-dtag", "--docker_tag", help="上传docker镜像tag", default=default_tag)
        docker_args, unknown_args = parser.parse_known_args(unknown_args)
        if docker_args.upload_docker and docker_args.partner_name is None:
            raise errors.BmcGoException("伙伴名称为空, 无法完成上传, 请指定伙伴名称!")
        return docker_args, unknown_args

    def kunpeng_publish_parse(self, args, unknown_args):
        if args.target != "cmc_open" and args.target != "kunpeng_publish":
            return None, unknown_args
        os.environ['NOT_CLEAN_CONAN_CACHE'] = "True"
        parser = argparse.ArgumentParser(description="open_source conan repo info")
        parser.add_argument("-opr", "--open_conan_remote", help="开源/伙伴仓远端(场内远端)")
        kunpeng_publish_args, unknown_args = parser.parse_known_args(unknown_args)
        return kunpeng_publish_args, unknown_args

    def parse(self, argv=None, ex_target_dir=""):
        parser = argparse.ArgumentParser(description="构建openUBMC",
            parents=[self.config.argparser(self.code_path, self.bconfig.partner_mode)],
            add_help=False,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        help_info = "构建目标，请查看build/target目录, 支持的目标："
        self.targets = self.get_all_target(ex_target_dir)
        for tgt, _ in self.targets.items():
            help_info += "\n" + tgt

        parser.add_argument("-d", "--debug_frame", help=argparse.SUPPRESS, const="debug", action="store_const")
        if log.is_debug:
            parser.add_argument("--debug_task", help="调试任务，与目标描述文件的klass完全相同，如：bmcgo.tasks.task_download_buildtools",
                                default=None)
        else:
            parser.add_argument("--debug_task", help=argparse.SUPPRESS, default=None)

        parser.add_argument("-v", "--version", help="构建版本号，不指定时从manifest.yml读取", default="")
        parser.add_argument("-t", "--target", help=help_info, default="personal")
        parser.add_argument("--deploy", help="将hpm包部署至bmc设备", action=misc.STORE_TRUE)
        args, unknown_args = parser.parse_known_args(argv)
        if args.target.startswith("target_"):
            args.target = args.target[7:]
        log.info(f'已知参数: {argv}')
        log.info(f"调试框架: {args.debug_frame}, 构建参数: {args}")
        conan_index_options = []
        if args.target == "dependencies":
            parser = argparse.ArgumentParser(description="build target")
            parser.add_argument("-cp", "--conan_package", help="软件包名, 示例: kmc/21.1.2.B001", default="")
            parser.add_argument("-uci", "--upload_package", help="是否上传软件包", action=misc.STORE_TRUE)
            parser.add_argument("-o", "--options", help="组件特性配置, 示例: -o skynet:enable_luajit=True",
                                action='append')
            self.conan_args, unknown_args = parser.parse_known_args(unknown_args)
            if self.conan_args is None or self.conan_args.conan_package == "":
                raise errors.BmcGoException("软件包选项为空, 请输入软件包选项!")
            conan_index_options = self.conan_args.options
        docker_args, unknown_args = self.cmc_open_parse(args, unknown_args)
        kunpeng_publish_args, unknown_args = self.kunpeng_publish_parse(args, unknown_args)
        self.config.parse_args(argv)
        self.config.pre_cook_manifest()
        self.record_build_time()
        self.config.set_version(args.version)
        self.config.set_target(args.target)
        self.config.set_conan_index_options(conan_index_options)
        if docker_args:
            self.config.set_docker_info(docker_args)
        if kunpeng_publish_args:
            self.config.set_kunpeng_publish_info(kunpeng_publish_args)
        self.need_deploy = args.deploy
        # 开启schema校验，也可参考personal目标配置禁用校验
        self.config.set_schema_need_validate(True)
        self.args = args

    def sigint_handler(self, _, __):
        log.debug('关闭全局状态管理器，所有任务都将因与状态管理器通信失败而退出!')
        self.ws_server.kill()
        signal.raise_signal(signal.SIGKILL)

    def sigterm_handler(self, _, __):
        log.debug('接收到终止信号!, 退出!')
        signal.raise_signal(signal.SIGINT)

    def run(self):
        self._prepare()
        # 启动全局状态服务
        signal.signal(signal.SIGINT, self.sigint_handler)
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        self.ws_server = WorkStatusServer()
        self.ws_server.start()
        succ = True
        args = self.args
        conan_args = self.conan_args
        # 初始化性能数据收集功能
        try:
            # 等待sever起来
            q.get()
            succ = create_target_scheduler(
                args.target,
                args.target,
                self.perf,
                self.config,
                args,
                conan_args,
                self.targets[args.target],
            )
        except Exception as e:
            log.error(str(e))
            log.error(f"Error: 构建目标({args.target})失败，请参考“构建检查”和下载“全量构建日志（右上角-日志-全量构建日志）”检查错误！！！！！！！！")
            succ = False

        self.ws_server.kill()
        if os.environ.get("PERF") is not None:
            self.perf.render(args.target)
        if succ:
            log.success(f"任务 {args.target} 执行成功")
            hpm_path = os.path.join(self.config.output_path, f"rootfs_{self.config.board_name}.hpm")
            if self.need_deploy and os.path.isfile(hpm_path):
                deploy = Deploy(self.bconfig, ["-f", hpm_path])
                deploy.run()
            time.sleep(0.5)
        else:
            # 等待2秒给各子任务同步状态
            time.sleep(2)
            raise errors.BmcGoException(f"任务 {args.target} 执行失败")
        return 0

    def _prepare(self):
        tool.sudo_passwd_check()
        shutil.rmtree(misc.CACHE_DIR)
        os.makedirs(misc.CACHE_DIR)
        os.chmod(misc.CACHE_DIR, 0o777)
        if shutil.which(misc.CONAN) is not None:
            tool.run_command("conan remove --locks")
