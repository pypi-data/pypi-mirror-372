#!/usr/bin/env python
# coding: utf-8
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
import os
import sys
import copy
import hashlib
import stat
import shutil
import argparse
import subprocess
import logging
import time
import struct
import functools
import hashlib
import configparser
from multiprocessing import Lock

import jsonschema
import yaml

from bmcgo.utils.tools import Tools
from bmcgo.logger import Logger
from bmcgo import errors, misc
from bmcgo.bmcgo_config import BmcgoConfig

tools = Tools("config")
log = Logger("config")
VERSION = "Version"
BUILD_NUMBER = "BuildNum"
VERSION_LEN = 5


class Config:
    # RTOS版本号
    rtos_version = None
    rtos_kernel = None
    arm_dic = {"V3": "arm", "V5": "arm", "V6": "arm64"}
    sdk_path = None
    hpm_build_dir = None
    gpp_build_dir = None
    buildimg_dir = None
    inner_path = None
    component_list_file = None
    asan = None
    enable_qemu = False
    pull_up_qemu = False
    version = ""
    chip = "1711"
    _rtos_offering = None
    enable_luajit = False
    _profile = ""
    conan_index_options = []
    _manifest_data = {}
    schema_file = f"{misc.SCHEMA_FILE_PATH}/manifest.schema.json"
    schema_need_validate = False # 由frame.py或target文件配置是否启用
    enable_debug_model = False # # 是否启用调测模式，默认为false，个人构建启用

    def __init__(self, bconfig: BmcgoConfig, board_name="openUBMC", target="target_personal"):
        self.bconfig = bconfig

        # 单板名
        self.board_name = board_name
        # 构建目标的文件名，不包含py尾缀，文件存储在application/build/target目录
        self.target = target
        self.from_source = False
        self.local = ""
        # step???
        self.step = "ultimate"
        # 编译选项，默认值为 False，可用方法 set_enable_arm_gcov 设置
        self.enable_arm_gcov = False
        # 是否需要进行签名
        self.sign = ""
        self.init_path()
        self.doc_file = "Open Source Software Notice.docx"

        self.download_0502 = f"{self.temp_path}/download_0502"
        os.makedirs(self.download_0502, exist_ok=True)
        # 存储0502编码
        self.manufacture_code = None
        # 存储tosupporte编码
        self.tosupporte_code = None
        self.build_type = "debug"
        self.stage = misc.StageEnum.STAGE_DEV.value
        self.set_common_params()
        # 构建日志临时目录
        self.log_path = os.path.join(self.temp_path, 'log')
        if os.path.isdir(self.log_path):
            shutil.rmtree(self.log_path)
        os.makedirs(self.log_path)
        os.makedirs(self.output_path, 0o755, exist_ok=True)
        # MR门禁编译标志位，由prepare任务根据MR配置修改
        self.update_mr_info()
        os.environ['CONAN_REVISIONS_ENABLED'] = "1"
        self.publish_version = ""
        self.verbose = False
        self.update_conan_cache = False
        self.source_mode = os.getenv('SOURCE_MODE')
        self.partner_path = f'{os.path.expanduser("~")}/partner_path'
        self.container_tag = "v3:v3_partner"
        self.partner_docker_home = f"{self.code_root}/dev_tools/partner_docker"
        self.partner_workspace = f"{self.temp_path}/archive_to_cmc"
        self.docker_component_home = f"{self.temp_path}/docker_component_home"
        self.conan_parallel_lock = Lock()
        self.archive_conf = None
        self.archive_path = None
        self.partner_docker = False
        # 版本号拆分
        self.major_ver = ""
        self.miner_ver = ""
        self.release_ver = ""
        self.patch_ver = ""
        self.build_ver = ""
        self.date = None
        self.show_version = ""
        # Docker相关
        self.upload_docker = False
        self.partner_name = None
        self.docker_tag = None
        # 伙伴/开源远端相关
        self.open_remote = None

    @property
    def partner_mode(self):
        """是否是伙伴模式"""
        return self.bconfig.partner_mode

    @property
    def sysroot(self):
        return f"/opt/{self.rtos_offering}/{self.rtos_version}/arm64le_{self.rtos_kernel}/sdk"

    @property
    def self_sign(self):
        self_sign_config = self.get_manufacture_config("base/signature/simple_signer_server")
        if not self_sign_config:
            self_sign_config = self.get_manufacture_config("base/signature/certificates")
        if not self_sign_config:
            self_sign_config = self.bconfig.hpm_server_sign
        if not self_sign_config:
            self_sign_config = self.bconfig.hpm_self_sign

        return self_sign_config is not None

    @property
    def rootca_der(self):
        """签名根公钥"""
        output = self.get_manufacture_config("base/signature/certificates/rootca_der")
        if not os.path.isfile(output):
            raise errors.BmcGoException("base/signature/certificates/rootca_der 配置的根证书不存在")
        return output

    @property
    def rootca_crl(self):
        """签名根公钥"""
        output = self.get_manufacture_config("base/signature/certificates/rootca_crl")
        if not os.path.isfile(output):
            raise errors.BmcGoException("base/signature/certificates/rootca_crl 配置的证书吊销列表文件不存在")
        return output

    @property
    def signer_pem(self):
        """签名证书私钥"""
        output = self.get_manufacture_config("base/signature/certificates/signer_pem")
        if not os.path.isfile(output):
            raise errors.BmcGoException("base/signature/certificates/signer_pem 配置的签名私钥文件不存在")
        return output

    @property
    def ts_signer_pem(self):
        """时间戳签名证书私钥"""
        output = self.get_manufacture_config("base/signature/certificates/timestamp_signer_pem")
        if not os.path.isfile(output):
            raise errors.BmcGoException("base/signature/certificates/timestamp_signer_pem 配置的时间戳签名私钥文件不存在")
        return output

    @property
    def ts_signer_cnf(self):
        """时间戳签名配置"""
        output = self.get_manufacture_config("base/signature/certificates/timestamp_signer_cnf")
        if not os.path.isfile(output):
            raise errors.BmcGoException("base/signature/certificates/timestamp_signer_cnf 配置的时间戳配置文件不存在")
        return output

    @property
    def profile(self):
        return Tools.get_conan_profile(self._profile, self.build_type, self.enable_luajit)

    @property
    def subsys_dir(self):
        subsys = os.path.join(self.code_path, "subsys")
        if self.stage == misc.StageEnum.STAGE_STABLE.value:
            subsys = os.path.join(subsys, misc.StageEnum.STAGE_STABLE.value)
        else:
            subsys = os.path.join(subsys, misc.StageEnum.STAGE_RC.value)
        return subsys

    @staticmethod
    def argparser(code_path, partner_mode=False):
        parser = argparse.ArgumentParser(description="构建openUBMC", formatter_class=argparse.RawTextHelpFormatter)
        boards = Config.get_all_board(code_path)
        help_txt = "单板包，可选值为build/product/<Kunpeng|...>/下的目录名\n默认：openUBMC"
        help_txt += "\n支持的单板列表："
        for board, _ in boards.items():
            help_txt += "\n" + board
        parser.add_argument("-b", "--board_name", help=help_txt, default="openUBMC")
        parser.add_argument("-bt", "--build_type", 
                            help="构建类型，可选：debug（调试包）, release（正式包）, dt（开发者测试包）", default="debug")
        parser.add_argument(
            "-s",
            "--from_source",
            help=argparse.SUPPRESS if partner_mode else "使能全量源码构建",
            action=misc.STORE_TRUE,
        )
        parser.add_argument("--stage", help="包类型，可选值为: dev(调试包), rc（预发布包）, stable（发布包）\n默认：dev", 
                            default='dev')
        parser.add_argument("--verbose", help="使能conan构建详细日志打印", action=misc.STORE_TRUE)
        parser.add_argument("-ucc", "--update_conan_cache", help="全量更新本地conan缓存", action=misc.STORE_TRUE)
        parser.add_argument("-r", "--remote", help=f"conan仓别名，请检查conan remote list查看已配置的conan仓")
        parser.add_argument("-z", "--zip_code",
                            help=(
                                argparse.SUPPRESS
                                if partner_mode
                                else "0502编码，可选值参考单板manifest/manufacture，示例: 05023UDK"
                            ), default=None)
        parser.add_argument("-sc", "--supporte_code", 
                            help="待发布的SupportE编码，可选值参考单板manifest.yml/tosupporte\n默认：default",
                            default="default")
        parser.add_argument("-q", "--enable_qemu", help=argparse.SUPPRESS, action=misc.STORE_TRUE)
        parser.add_argument("-qi", "--qemu_in", help=argparse.SUPPRESS, action=misc.STORE_TRUE)
        parser.add_argument("-cov", "--coverage", help=argparse.SUPPRESS if partner_mode else "使能覆盖率统计功能", 
                            action=misc.STORE_TRUE)
        parser.add_argument("-as", "--asan", help=argparse.SUPPRESS if partner_mode else "Enable address sanitizer", 
                            action=misc.STORE_TRUE)
        parser.add_argument("-pr", "--profile",
                            help=argparse.SUPPRESS if partner_mode else Tools.get_profile_arg_help(), default="")
        parser.add_argument("-jit", "--enable_luajit", help=argparse.SUPPRESS if partner_mode else "Enable luajit",
                            action=misc.STORE_FALSE if partner_mode else misc.STORE_TRUE)
        return parser

    # 从product/productline查找所有单板
    @staticmethod
    def get_all_board(code_path):
        product_path = os.path.join(code_path, "product")
        boards = {}
        for productline in os.listdir(product_path):
            path = os.path.join(product_path, productline)
            if not os.path.isdir(path):
                continue
            for board in os.listdir(path):
                board_path = os.path.join(path, board)
                manifest = os.path.join(board_path, "manifest.yml")
                if not os.path.isfile(manifest):
                    continue
                boards[board] = board_path
        return boards

    @staticmethod
    def log_init():
        """在manifest仓未删除frame.py及works前保留"""
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        loglevel = os.environ.get("LOG")
        if loglevel is not None:
            formatter = logging.Formatter(fmt='[{asctime} {levelname} {filename}:{lineno} {funcName:4}] {message}',
                style='{')
            if loglevel == "debug":
                logger.setLevel(logging.DEBUG)
            elif loglevel == "warn":
                logger.setLevel(logging.WARNING)
            elif loglevel == "error":
                logger.setLevel(logging.ERROR)
            else:
                logger.setLevel(logging.INFO)
        else:
            formatter = logging.Formatter(fmt='[{levelname} {filename}:{lineno} {funcName:4}] {message}',
                style='{')
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.handlers = []
        logger.addHandler(handler)

    @staticmethod
    def set_conf(conf_file, scheme: dict):
        """设置.ini文件
        参数:
            scheme (dict): 需设置的ini文件的节与参数,
            e.g.
                ```
                {
                    "Section A": { "key1": "val1", "key2": "val2" },
                    "Section B": { "key3": "val3" },
                    "Section C": {}
                }
                ```
        """
        conf = configparser.ConfigParser()
        if os.path.isfile(conf_file):
            conf.read(conf_file)
        for section, entries in scheme.items():
            try:
                sec = conf[section]
            except Exception as e:
                conf[section] = {}
                sec = conf[section]
            for key, val in entries.items():
                sec[key] = str(val)
        with os.fdopen(os.open(conf_file, flags=os.O_WRONLY | os.O_CREAT | os.O_TRUNC, \
                mode=stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH), "w") as conf_fd:
            conf.write(conf_fd)
            conf_fd.close()

    @staticmethod
    def _calc_manifest_data_sha256(filename, template):
        sha256 = Tools.sha256sum(filename)
        template_str = json.dumps(template)
        template_hash = hashlib.sha256()
        template_hash.update(template_str.encode())
        template_sha256 = template_hash.hexdigest()
        return sha256 + template_sha256

    @functools.cached_property
    def rtos_offering(self):
        return self.get_manufacture_config("base/rtos_offering", "RTOS")

    @functools.cached_property
    def skynet_config(self):
        deps = self.get_manufacture_config('dependencies', [])
        for dep in deps:
            conan = dep.get(misc.CONAN)
            name = conan.split("/")[0]
            if name == 'skynet':
                return dep
        return {'conan': 'skynet'}

    @functools.cached_property
    def conan_remotes(self):
        """conan remotes列表"""
        cmd = 'conan remote list -raw'
        _, data = subprocess.getstatusoutput(cmd)
        remotes_list = [{remote.split()[0]: remote.split()[1]} for remote in data.split('\n')]
        return remotes_list

    # 从manifest中获取属性值
    def get_manufacture_config(self, key: str, default_val=None):
        """获取manifest.yml当中的配置
        参数:
            key (str): 要获取的配置，采用路径类似格式，比如'manufacture/05023VAY'
        返回值:
            None: 未找到配置
            str: 配置的值
        """
        manifest_conf = self.load_manifest_yml()
        splits = key.split("/")
        processed = ""
        for split in splits:
            if processed == "":
                processed = split
            else:
                processed = processed + "/" + split
            manifest_conf = manifest_conf.get(split)
            if manifest_conf is None:
                log.info('不能从 yaml 文件中获取到键值 {}, 没有相关配置'.format(processed))
                return default_val
        return manifest_conf

    def get_origin_manufacture_config(self, key: str, default_val=None):
        """获取origin manifest.yml当中的配置
        参数:
            key (str): 要获取的配置，采用路径类似格式，比如'manufacture/05023VAY'
        返回值:
            None: 未找到配置
            str: 配置的值
        """
        manifest_file = os.path.join(self.board_path, "manifest.yml")
        with open(manifest_file, "r", encoding="utf-8") as fp:
            manifest_conf = yaml.safe_load(fp)
        splits = key.split("/")
        processed = ""
        for split in splits:
            if processed == "":
                processed = split
            else:
                processed = processed + "/" + split
            manifest_conf = manifest_conf.get(split)
            if manifest_conf is None:
                log.info('不能从 yaml 文件中获取到键值 {}, 没有相关配置'.format(processed))
                return default_val
        return manifest_conf

    def get_manufacture_version(self) -> str:
        """调整version的值，特殊场景要求装备版本号要在正常版修订号加1

        返回值:
            str: 新的修正后的版本号
        """
        if self.version == "":
            return self.version
        version = self.version.rsplit(".", 1)[0] if "B" in self.version else self.version
        correction_version = str(int(version.rsplit(".", 1)[-1]) + 1)
        version = "{}.{}".format(version.rsplit(".", 1)[0], correction_version.zfill(2))
        return version

    def read_m4i_template(self):
        file = os.path.join(self.work_out, "m4i_template.m4i")
        if os.path.isfile(file):
            with open(file) as fp:
                return fp.read()
        return None

    # 模板化，manifest.yml替换时使用
    def get_template(self) -> dict:
        version = self.version.rsplit(".", 1)[0] if "B" in self.version else self.version
        template = {
            "code_root": self.code_root,
            "product": f"{self.code_path}/product",
            "manufacture": f"{self.code_path}/manufacture",
            "hpm_build_dir": self.hpm_build_dir,
            "board_path": self.board_path,
            "ori_board_path": self.ori_board_path,
            "download_0502": self.download_0502,
            "version": version,
            "manufacture_version": self.get_manufacture_version(),
            "manufacture_code": self.manufacture_code,
            "tosupporte_code": self.tosupporte_code,
            "board_name": self.board_name,
            "work_out": self.work_out,
            "output_path": self.output_path,
            "m4i_template": self.read_m4i_template(),
            "doc_file": self.doc_file,
            "sdk_path": self.sdk_path,
            "partner_path": self.partner_path,
            "major_ver": self.major_ver,
            "minor_ver": self.miner_ver,
            "release_ver": self.release_ver,
            "patch_ver": self.patch_ver,
            "build_ver": self.build_ver,
            "show_version": self.show_version,
            "package_folder": self.temp_platform_dir_name
        }
        return template

    def init_path(self):
        # 编译 debug 或者 release 或者 装备分离 版本的app包
        self.build_path = ""
        self.rootfs_path = ""
        self.cache_path = ""
        self.work_out = ""
        self.work_config = ""
        # build/board/<board_name>路径
        self.board_path = ""
        # 关键路径定义
        # build目录
        self.code_path = os.path.join(self.bconfig.manifest.folder, "build")
        # 代码根目录
        self.code_root = self.bconfig.manifest.folder
        self.temp_path = os.path.join(self.code_root, 'temp')
        os.makedirs(self.temp_path, exist_ok=True)
        # 定义自研构建工具目录并添加到环境变量
        self.tools_path = os.path.realpath(os.path.join(self.temp_path, "tools"))
        os.makedirs(self.tools_path, exist_ok=True)
        os.makedirs(os.path.join(self.tools_path, "build_tools"), exist_ok=True)
        os.environ['PATH'] = os.environ["PATH"] + ":" + os.path.join(self.tools_path, "build_tools")
        # CI工程上库路径
        self.output_path = os.path.join(self.code_root, 'output')

    def init_conan_profile(self, profile: str):
        manifest_profile = self.get_manufacture_config("base/profile")
        if manifest_profile:
            log.warning(f"根据当前产品manifest.yml中的profile配置为{manifest_profile}，忽略命令行指定的-pr参数")
            self._profile = manifest_profile
        else:
            self._profile = profile

    def update_mr_info(self):
        self.src_git = ""
        self.src_branch = ""
        self.tgt_git = ""
        self.tgt_branch = ""
        mr_config = f"{self.code_root}/../mr_config.json"
        if not os.path.isfile(mr_config):
            return

        with open(mr_config, "r") as json_file:
            cfg = json.load(json_file)
            self.src_git = cfg["src_git"]
            self.src_branch = cfg["src_branch"]
            self.tgt_git = cfg["tgt_git"]
            self.tgt_branch = cfg["tgt_branch"]

    def set_from_source(self, from_source):
        self.from_source = from_source

    # 设置0502编码
    def set_manufacture_code(self, code):
        self.manufacture_code = code

    def set_tosupporte_code(self, code):
        self.tosupporte_code = code

    def set_step(self, arg_step):
        '''
        参数：arg_step 可选值："build"/"ultimate"/"standard"/""
        '''
        self.step = arg_step

    def set_enable_arm_gcov(self, is_enable):
        '''
        是否添加编译选项 -DGCOV=ON
        参数：is_enable 是否添加-DGCOV=ON 可选值：True;False
        '''
        # 实现 gcov 功能以后, 请将 False 改为 is_enable
        self.enable_arm_gcov = False
        self.set_enable_qemu(is_enable)

    def set_sign(self, arg_sign):
        '''
        是否需要签名
        '''
        self.sign = arg_sign

    def update_path(self):
        self.build_path = os.path.join(self.temp_path, f"build_{self.board_name}_{self.build_type}_{self.stage}")
        self.board_path = os.path.join(self.temp_path, f"board_{self.board_name}")
        self.rootfs_path = os.path.join(self.build_path, 'tmp_root')
        self.work_out = os.path.join(self.build_path, 'output')
        self.cache_path = os.path.join(self.build_path, 'cache')
        self.sdk_path = os.path.join(self.build_path, 'sdk')
        # 单板打包路径
        self.hpm_build_dir = f"{self.build_path}/hpm_build_dir"
        self.gpp_build_dir = f"{self.build_path}/gpp_build_dir"
        self.buildimg_dir = f"{self.build_path}/buildimg"
        self.inner_path = os.path.join(self.output_path, "packet/inner", self.build_type)
        os.makedirs(self.build_path, 0o755, exist_ok=True)
        os.makedirs(self.work_out, 0o755, exist_ok=True)
        os.makedirs(self.rootfs_path, 0o755, exist_ok=True)
        os.makedirs(self.cache_path, 0o755, exist_ok=True)
        os.makedirs(self.hpm_build_dir, 0o755, exist_ok=True)
        os.makedirs(self.gpp_build_dir, 0o755, exist_ok=True)
        os.makedirs(self.buildimg_dir, 0o755, exist_ok=True)
        os.makedirs(self.inner_path, 0o755, exist_ok=True)
        self.component_list_file = f"{self.board_path}/component.list"

    def set_build_type(self, arg_build_type="debug"):
        '''
        这只编译app的cmake编译选项
        参数：arg_build_type 可选值："debug";"release";"dt"
        '''
        # 可以编译的版本
        build_type_turple = ("debug", "release", "dt")
        if arg_build_type not in build_type_turple:
            log.info("不支持的构建类型, 请从以下构建类型中输入: [debug release dt]")
            return

        self.build_type = arg_build_type
        # 为了支持组件定制化脚本获取定制类型，在此处设置环境变量
        os.environ["BUILD_TYPE"] = self.build_type
        # 构建过程文件存储在以下目录
        self.set_enable_luajit(self.enable_luajit)

    def deal_conf(self, config_dict):
        if not config_dict:
            return
        for conf in config_dict:
            try:
                method = getattr(self, f"set_{conf}")
                method(config_dict.get(conf))
            except Exception as e:
                raise Exception(f"目标 config 无效配置: {conf}") from e

    def print_config(self):
        header = 30
        log.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>  根据目标开始配置  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        log.info("board name:".ljust(header) + self.board_name)
        log.info("from source:".ljust(header) + str(self.from_source))
        log.info("build type:".ljust(header) + str(self.build_type))
        log.info("target:".ljust(header) + str(self.target))
        log.info("qemu:".ljust(header) + str(self.enable_qemu))
        log.info("partner mode:".ljust(header) + str(self.partner_mode))
        log.info("build path:".ljust(header) + str(self.build_path))
        log.info("rootfs path:".ljust(header) + str(self.rootfs_path))
        log.info("cache path:".ljust(header) + str(self.cache_path))
        log.info("work out:".ljust(header) + str(self.work_out))
        log.info("board path:".ljust(header) + str(self.board_path))
        log.info("temp path:".ljust(header) + str(self.temp_path))
        log.info("manufacture_code:".ljust(header) + str(self.manufacture_code))
        log.info("tosupporte_code:".ljust(header) + str(self.tosupporte_code))
        log.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  根据目标配置结束  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    def set_common_params(self):
        # conan仓
        self.remote = None
        self.remote_list = []
        self.temp_platform_dir_name = f"temp/board_{self.board_name}_platform"
        self.temp_platform_build_dir = os.path.join(self.code_path, self.temp_platform_dir_name)
        self.board_version = "V6"
        self.cross_prefix = "aarch64-target-linux-gnu"
        self.cross_host = "aarch64-linux-gnu"
        self.cross_host_alias = "aarch64-linux-gnu"
        self.cross_build_dir = "aarch64-unknown-linux-gnu"
        self.cross_compile = "aarch64-unknown-linux-gnu-"
        self.cross_compile_install_path = "/opt/hcc_arm64le"
        self.cpu = "arm64le"
        self.platform = "platform_v6"
        self.strip = f"{self.cross_prefix}-strip"
        self.gcc = f"{self.cross_prefix}-gcc"
        self.gxx = f"{self.cross_prefix}-g++"
        # build.py 构建app的全局变量，原方式从参数传递
        self.arch = self.arm_dic.get(self.board_version)
        # 单板配置路径
        self.ori_board_path = ""
        self.productline = ""
        self.version = "5.01.00.01.B001"

    def set_board_name(self, board_name):
        if self.board_name != board_name:
            log.info("设置单板名为: {}".format(board_name))
        # 设置单板板名和基本属性
        self.board_name = board_name
        self.temp_platform_dir_name = f"temp/board_{self.board_name}_platform"
        self.temp_platform_build_dir = os.path.join(self.code_path, self.temp_platform_dir_name)
        boards = self.get_all_board(self.code_path)
        # 单板配置路径
        self.ori_board_path = boards.get(self.board_name)
        log.info(f"单板源配置路径: {self.ori_board_path}")
        # openUBMC get Kunpeng
        self.productline = os.path.abspath(self.ori_board_path).split('/')[-2]
        board_files = ["manifest.yml", "update_ext4.cfg", "version.xml", "archive.ini"]
        for f in board_files:
            file = os.path.join(self.ori_board_path, f)
            if not os.path.isfile(file):
                raise errors.ConfigException("未发现单板配置文件({}), 请检查单板配置文件".format(file))
        self.update_path()
        log.info("复制单板的 manifest 目录从 {} 到 {}".format(self.ori_board_path, self.board_path))
        tools.run_command(f"rm -rf {self.board_path}")
        tools.run_command(f"cp -rf {self.ori_board_path} {self.board_path}")

    def set_enable_luajit(self, enable):
        if self.build_type == "Dt":
            self.enable_luajit = False
        self.enable_luajit = enable

    def set_schema_need_validate(self, enable):
        self.schema_need_validate = enable

    def set_enable_debug_model(self, enable):
        self.enable_debug_model = enable

    def set_conan_index_options(self, options):
        if options is not None:
            self.conan_index_options = options
        else:
            self.conan_index_options = []

    def set_pull_up_qemu(self, pull_up_qemu):
        self.pull_up_qemu = pull_up_qemu
        # 如果要拉起qemu，那么qemu包必须存在，打开出qemu包的开关
        self.enable_qemu = True if pull_up_qemu is True else self.enable_qemu

    def set_enable_qemu(self, enable_qemu):
        self.enable_qemu = True if enable_qemu is True else self.enable_qemu

    def set_stage(self, stage: str):
        in_stage = [member.value for member in misc.StageEnum if member is not misc.StageEnum.STAGE_PRE]
        if stage not in in_stage:
            raise errors.ConfigException(f"stage 参数错误, 可用选项为: {in_stage}, 请检查参数")
        self.stage = stage

    def set_show_version(self):
        self.show_version = self.get_manufacture_config("base/show_version", "")
        if self.manufacture_code is not None:
            self.show_version = self.get_manufacture_config(f"manufacture/{self.manufacture_code}/show_version",
                                                            self.show_version)
        elif self.tosupporte_code is not None:
            self.show_version = self.get_manufacture_config(f"tosupporte/{self.tosupporte_code}/show_version",
                                                            self.show_version)

    def set_version(self, version):
        self.version = version
        if self.version == "":
            self.update_version()
        else:
            self.update_version(True)

    def set_target(self, target):
        self.target = target

    def set_docker_info(self, docker_flags):
        self.upload_docker = docker_flags.upload_docker
        self.partner_name = docker_flags.partner_name
        self.docker_tag = docker_flags.docker_tag + '_' + self.board_name

    def set_kunpeng_publish_info(self, kunpeng_publish_flags):
        self.open_remote = kunpeng_publish_flags.open_conan_remote

    # 预处理manifest
    def pre_cook_manifest(self):
        manifest_file = os.path.join(self.board_path, "manifest.yml")
        template = {
            "product": f"{self.code_path}/product"
        }
        mani = self.load_manifest_yml(template=template)

        self.merge_platform_manifest(mani)
        self.complement_components(mani)

        if mani.get("include"):
            del mani["include"]
        if mani.get("platform"):
            del mani["platform"]
        dumps = yaml.safe_dump(mani, sort_keys=False)
        with os.fdopen(os.open(manifest_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w+', encoding="utf-8") as file_handler:
            file_handler.write(f"# yaml-language-server: $schema={self.schema_file}\n")
            file_handler.write(dumps)
    
    #补全组件版本号
    def complement_components(self, mani):
        subsys_comps = self.get_subsys_coms()
        # 补全基本的dependencies
        self.merge_dependencies(mani.get("dependencies", []), subsys_comps, [])
        deps = mani.get("dependencies", [])
        if self.manufacture_code:
            manufature_deps = mani["manufacture"][self.manufacture_code].get("dependencies", [])
            self.merge_dependencies(manufature_deps, subsys_comps, deps)
        elif self.tosupporte_code:
            supporte_deps = mani["tosupporte"][self.tosupporte_code].get("dependencies", [])
            self.merge_dependencies(supporte_deps, subsys_comps, deps)

    def merge_dependencies(self, dependencies, subsys_comps, base_deps):
        for com_package in dependencies:
            com_package_split = com_package.get(misc.CONAN).split("/")
            if len(com_package_split) > 2:
                continue
            pkg_name = com_package_split[0]
            for sub_name in base_deps:
                sub_pkg_name = sub_name.get(misc.CONAN).split("/")[0]
                # 上下层具有相同组件名的组件
                if pkg_name == sub_pkg_name:
                    self.fix_com_package(com_package, misc.CONAN, sub_name.get(misc.CONAN))
                    break
            for sub_name in subsys_comps:
                sub_pkg_name = sub_name.split("/")[0]
                # 上下层具有相同组件名的组件
                if pkg_name == sub_pkg_name:
                    self.fix_com_package(com_package, misc.CONAN, sub_name)
                    break
            self.fix_com_package(com_package, misc.CONAN, pkg_name)

    def fix_com_package(self, com_package, index, sub_name):
        com_package_split = com_package[index].split("/")
        if len(com_package_split) == 1:
            com_package[index] = sub_name
        elif len(com_package_split) == 2:
            stage = self.stage
            if stage != misc.StageEnum.STAGE_STABLE.value:
                stage = misc.StageEnum.STAGE_RC.value
            user_channel = f"@{tools.conan_user}/{stage}"
            com_package[index] += user_channel

    def get_subsys_coms(self):
        comps = []
        for f in os.listdir(self.subsys_dir):
            with open(os.path.join(self.subsys_dir, f)) as fp:
                yml = yaml.safe_load(fp)
            deps = yml.get('dependencies')
            for dep in deps:
                conan = dep.get(misc.CONAN)
                if conan:
                    comps.append(conan)
        return comps

    def load_platform_manifest(self, package):
        package_conan_dir = tools.install_platform(package, self.stage, self.remote)
        if os.path.isdir(self.temp_platform_build_dir):
            shutil.rmtree(self.temp_platform_build_dir)
        os.makedirs(os.path.join(self.code_path, "temp"), exist_ok=True)
        tools.run_command(f"cp -rf {package_conan_dir} {self.temp_platform_build_dir}")
        self.copy_rtos_sdk(package_conan_dir)
        platform_manifest_path = os.path.join(
            self.temp_platform_build_dir, "manifest.yml"
        )
        platform_mani = self.load_manifest_yml(filename=platform_manifest_path, template={})
        return platform_mani

    def copy_rtos_sdk(self, package_conan_dir):
        if self.source_mode is not None:
            rtos_sdk_dir = os.path.join(self.code_path, "rtos_sdk")
            rtos_sdk_src_dir = os.path.join(package_conan_dir, "rtos_sdk")
            if os.path.isdir(rtos_sdk_dir):
                shutil.rmtree(rtos_sdk_dir)
            tools.run_command(f"cp -rf {rtos_sdk_src_dir} {rtos_sdk_dir}")

    # 合并platform manifest.yml
    def merge_platform_manifest(self, mani):
        platform_package = self.get_manufacture_config("platform", {})
        if platform_package:
            platform_mani = self.load_platform_manifest(platform_package)
            tools.check_product_dependencies(mani, platform_mani)
            if self.manufacture_code:
                tools.check_product_dependencies(mani["manufacture"][self.manufacture_code], platform_mani)
            elif self.tosupporte_code:
                tools.check_product_dependencies(mani["tosupporte"][self.tosupporte_code], platform_mani)
            self.merge_manifest_yml(mani, platform_mani, "")
        else:
            shutil.rmtree(self.temp_platform_build_dir, ignore_errors=True)

    def merge_manifest_yml(self, top, base, prev_path):
        self._merge_manifest_yaml_easy(top, base, prev_path)
        self._merge_manifest_yaml_easy(base, top, prev_path)
        top_val = copy.deepcopy(top)
        for key, value in top_val.items():
            base_value = base.get(key)
            top_value = top.get(key)
            # 上层有，下层没有的，忽略
            next_path = prev_path + key + "/"
            if next_path == "tosupporte/" or next_path == "manufacture/":
                continue
            if isinstance(top_value, dict):
                self.merge_manifest_yml(top_value, base_value, next_path)
            # 正式出包由上层决定,忽略下层的
            if next_path == "base/customization/":
                if isinstance(base_value, str) and base_value != value:
                    top[key] = [base_value, value]
                elif isinstance(base_value, list) and value not in value:
                    top[key].insert(0, value)
                else:
                    top[key] = base_value
            elif isinstance(value, list):
                # 如果key为dependencies需要特殊处理
                if key in ("dependencies", "dt_dependencies", "debug_dependencies", "platform"):
                    top[key] = tools.merge_dependencies(value, base_value)

    def load_manifest_yml(self, filename=None, template=None):
        top_manifest = False
        if not filename:
            filename = os.path.join(self.board_path, "manifest.yml")
            top_manifest = True
        # 注意：这里一定要判断template is None，不能使用if not template
        if template is None:
            template = self.get_template()
        mani = self._load_manifest_with_template(filename, template)
        inc_filename = mani.get("include")
        if not inc_filename:
            return mani
        inc_filename = os.path.realpath(inc_filename)
        boards = self.get_all_board(self.code_path)
        for board, dir_path in boards.items():
            manifest_yml = os.path.join(dir_path, "manifest.yml")
            if manifest_yml == inc_filename:
                template["ori_board_path"] = dir_path
                template["board_name"] = board
                break

        mani_inc = self.load_manifest_yml(inc_filename, template)
        self.merge_manifest_yml(mani, mani_inc, "")
        if top_manifest and self.schema_need_validate:
            schema_file = mani.get("schema", self.schema_file)
            if not schema_file:
                schema_file = misc.get_decleared_schema_file(filename)
                # 获取产品配置的schema，已通过schema校验，必然存在
            if schema_file is None:
                raise errors.BmcGoException("未找到应该遵循的manifest规范，无法校验manifest.yml文件正确性，" +
                                            "请检查配置项yaml-language-server或schema配置项是否正确")
            if not os.path.isfile(schema_file):
                raise errors.BmcGoException(f"产品配置了一个不存在的manifest规范文件{schema_file}，" +
                                            "无法校验manifest.yml文件正确性，请检查bingo是否正确安装")
            self.schema_file = schema_file
            with open(self.schema_file, "rb") as fp:
                schema = json.load(fp)
            log.debug(f"使用规范配置文件{self.schema_file}校验{filename}配置项")
            jsonschema.validate(mani, schema)
        return mani

    def get_archive(self):
        self.archive_conf = self.get_manufacture_config("archive")
        self.archive_path = self.get_manufacture_config("archive/archive_path")
        if self.target == "docker_build":
            self.archive_path = "openUBMC/ToCommunity"
        self.partner_docker = self.get_manufacture_config("archive/partner_docker")

    def version_split(self):
        if isinstance(self.version, str):
            if len(self.version.split('.')) == VERSION_LEN:
                self.major_ver, self.miner_ver, self.release_ver, patch_ver, self.build_ver = self.version.split(".")
            else:
                self.major_ver, self.miner_ver, self.release_ver, patch_ver = self.version.split(".")
            self.patch_ver = struct.pack('>i', int(patch_ver)).hex()
        else:
            raise ArithmeticError("版本号设置错误, 非 4 段 或 5 段样式")
        # 填充构建日期
        with open(f"{self.temp_path}/date/date.txt", "r") as date_fp:
            date = date_fp.read().strip("\n")
            self.date = time.strptime(date, "%H:%M:%S %b %d %Y")

    def update_version(self, configured=False):
        """ 更新版本号，并将manifest.yml文件版本号更新
            版本号使用优先级：zip包fix_version > 传入的参数 > manifest.yml > version.yml
        """
        self.rtos_version = self.get_manufacture_config("base/rtos_version")
        self.rtos_kernel = self.get_manufacture_config("base/rtos_kernel")

        # 参数从frame.py获取，如果为空(默认值)，则未传入参数，从文件读取
        if configured is False:
            self.version = self.get_manufacture_config("base/version")
            if self.version is None:
                with open(f"{self.code_path}/version.yml", "r") as fp:
                    version_data = yaml.safe_load(fp)
                self.version = f"{str(version_data[VERSION])}.{str(version_data[BUILD_NUMBER])}"

        manifest_file = os.path.join(self.board_path, "manifest.yml")
        with open(manifest_file, "r", encoding="utf-8") as fp:
            mani = yaml.safe_load(fp)
        mani["base"]["version"] = self.version
        schema_file = misc.get_decleared_schema_file(manifest_file)
        with os.fdopen(os.open(manifest_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w+') as file_handler:
            if schema_file != "":
                file_handler.write(f"# yaml-language-server: $schema={schema_file}\n")
            file_handler.write(yaml.safe_dump(mani))
        self.version_split()

        # 如果有包配置，则检查包里面的fix_version
        fixed_version = None
        if self.manufacture_code is not None:
            key = f"manufacture/{self.manufacture_code}/fixed_version"
            fixed_version = self.get_manufacture_config(key)

        if fixed_version is not None:
            log.warning(f"版本号因参数 {self.manufacture_code} 编码已变更为 {fixed_version}")
            self.build_ver = self.version.rsplit(".")[-1]
            self.version = fixed_version

    # 将manifest格式化后的内容写入board_path的real_manifest.yml
    def dump_manifest(self):
        real_manifest_file = os.path.join(self.board_path, "real_manifest.yml")
        mani = self.load_manifest_yml()
        dumps = yaml.safe_dump(mani, sort_keys=False)
        with os.fdopen(os.open(real_manifest_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w+', encoding="utf-8") as file_handler:
            file_handler.write(f"# yaml-language-server: $schema={self.schema_file}\n")
            file_handler.write(dumps)

    def version_conf(self, dest_file):
        # 根据要打的包，确定版本号来源
        version_data_source = "manufacture" if self.manufacture_code is not None else "tosupporte"
        package_code = self.manufacture_code if self.manufacture_code is not None else self.tosupporte_code
        package_name = self.get_origin_manufacture_config(f"{version_data_source}/{package_code}/package_name")
        fixed_version = self.get_manufacture_config(f"{version_data_source}/{package_code}/fixed_version")
        version = self.get_manufacture_config("base/version")

        with open(dest_file, "r") as dst:
            ver_dst_data = json.load(dst)
            # 大版本字段为空，自动填充
            if ver_dst_data[VERSION] == "":
                real_version = ""
                if fixed_version is not None:
                    real_version = fixed_version
                else:
                    real_version = version
                ver_dst_data[VERSION] = real_version.rsplit(".", 1)[0] if "B" in real_version else real_version
                # 如果包名中有manufacture字段，则自动加1
                if "manufacture" in package_name:
                    version_list = ver_dst_data[VERSION].rsplit(".", 1)
                    ver_dst_data[VERSION] = f"{version_list[0]}.{str(int(version_list[1]) + 1).zfill(2)}"

            # 小版本为空，则填充
            if ver_dst_data[BUILD_NUMBER] == "":
                if fixed_version is not None and "B" in fixed_version:
                    ver_dst_data[BUILD_NUMBER] = fixed_version.rsplit(".", 1)[1].strip("B")
                else:
                    ver_dst_data[BUILD_NUMBER] = version.rsplit(".", 1)[1].strip("B")

            # 填充构建日期
            if ver_dst_data['ReleaseDate'] == "":
                with open(f"{self.temp_path}/date/date.txt", "r") as date_fp:
                    date = date_fp.read()
                ver_dst_data['ReleaseDate'] = date.strip('\n')
            dst.close()

            # 写入到dest_file文件中
            with os.fdopen(os.open(dest_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                    stat.S_IWUSR | stat.S_IRUSR), 'w+') as file_handler:
                json.dump(ver_dst_data, file_handler)
                file_handler.close()

            log.info(f"版本 json 配置: {ver_dst_data}")

    def show_version_conf(self, dst_file):
        """ 更新 json 文件, 并添加 ShowVersion 字段

        Args:
            dst_file (_type_): 要修改的 json 文件
        """
        with open(dst_file, "r") as js_fp:
            ver_dst_data = json.load(js_fp)
        if self.show_version != "":
            ver_dst_data["ShowVersion"] = self.show_version
            # 写入到dst_file文件中
            with os.fdopen(os.open(dst_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                    stat.S_IWUSR | stat.S_IRUSR), 'w+') as file_handler:
                json.dump(ver_dst_data, file_handler)
                file_handler.close()
        else:
            log.warning("未配置 show_version 字段")

    def parse_args(self, args=None):
        parser = self.argparser(self.code_path)
        args, _ = parser.parse_known_args(args)
        if args.zip_code and args.supporte_code != "default":
            raise errors.ConfigException("manufacture 编码和 tosupporte 编码不能同时存在")

        self.set_manufacture_code(args.zip_code)
        if not args.zip_code:
            self.set_tosupporte_code(args.supporte_code)
        self.set_from_source(args.from_source)
        self.set_build_type(args.build_type)
        self.set_stage(args.stage)
        self.set_board_name(args.board_name)
        self.asan = args.asan
        self.remote = args.remote
        self.remote_list = tools.get_conan_remote_list(self.remote)
        self.verbose = args.verbose
        if os.environ.get("LOG"):
            self.verbose = True
        self.update_conan_cache = args.update_conan_cache
        # 使能qemu放在上面，防止gcov使能的qemu包被False重置
        self.set_enable_qemu(args.enable_qemu)
        self.set_pull_up_qemu(args.qemu_in)
        # cov模式下，qemu包必定打出
        self.set_enable_arm_gcov(args.coverage)
        self.set_enable_luajit(args.enable_luajit)
        self.set_show_version()
        self.get_archive()
        self.init_conan_profile(args.profile)

        # 构建阶段检查
        bt = ["dt", "debug", "release"]
        if args.build_type not in bt:
            raise errors.ConfigException("构建类型 build_type 错误, 可用选项为: [debug, release, dt], 请检查参数")

        hpm_encrypt = self.bconfig.hpm_encrypt
        if hpm_encrypt and hpm_encrypt.need_encrypt:
            if not shutil.which("crypto_tool"):
                raise errors.BmcGoException(f"开启了hpm加密配置, 在环境中未找到 'crypto_tool', 请确认环境配置是否正确.")
            os.environ["HPM_ENCRYPT"] = "true"

    def _load_manifest_with_template(self, filename, template):
        try:
            real_sha256 = Config._calc_manifest_data_sha256(filename, template)
            cfg = self._manifest_data.get(real_sha256)
            if cfg:
                return copy.deepcopy(cfg)
            cfg = tools.yaml_load_template(filename, template, self.schema_need_validate)
            self._manifest_data[real_sha256] = cfg
        except Exception as e:
            raise OSError('加载 {} 时失败\n       {}'.format(filename, str(e))) from e
        return copy.deepcopy(cfg)

    def _merge_manifest_yaml_easy(self, top, base, prev_path):
        base_val = copy.deepcopy(base)
        for key, base_value in base_val.items():
            next_path = prev_path + key + "/"
            # 由上层决定出包逻辑
            if next_path == "tosupporte/" or next_path == "manufacture/":
                continue
            top_value = top.get(key)
            if top_value is None:
                top[key] = base_value
                continue
            if isinstance(base_value, dict):
                self._merge_manifest_yaml_easy(top_value, base_value, next_path)
