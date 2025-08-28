#!/usr/bin/env python3
# encoding=utf-8
# 描述：BMCGO配置管理
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
import sys
import re
import select
import shutil
import configparser
import tempfile
import functools
from configparser import NoSectionError, NoOptionError
from git import Repo
from semver import valid_range, satisfies
from bmcgo import errors
from bmcgo.utils.tools import Tools
from bmcgo import misc
from bmcgo import __version__

tools = Tools("bmcgo_config")
log = tools.log


class BmcgoComp(object):
    def __init__(self, folder, config: configparser.ConfigParser):
        self.folder = os.path.realpath(folder)
        self.config = config


class BmcgoConanIndex(object):
    def __init__(self, folder, config: configparser.ConfigParser):
        self.folder = os.path.realpath(folder)
        self.config = config


class BmcgoManifest(object):
    def __init__(self, folder, config: configparser.ConfigParser):
        self.folder = os.path.realpath(folder)
        self.config = config


class BmcgoHpmServerSign(object):
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.rootca_der = config.get(misc.HPM_SERVER_SIGN, misc.HPM_SIGN_ROOTCA_DER)
        self.cert_id = config.get(misc.HPM_SERVER_SIGN, misc.HPM_SERVER_SIGN_CERT_ID)
        self.url = config.get(misc.HPM_SERVER_SIGN, misc.HPM_SERVER_SIGN_URL)
        self.ssl_verify = config.get(misc.HPM_SERVER_SIGN, misc.HPM_SERVER_SIGN_SSL_VERYFY)


class BmcgoHpmSelfSign(object):
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.rootca_der = config.get(misc.HPM_SELF_SIGN, misc.HPM_SIGN_ROOTCA_DER)
        self.rootca_crl = config.get(misc.HPM_SELF_SIGN, misc.HPM_SELF_SIGN_ROOTCA_CRL)
        self.signer_pem = config.get(misc.HPM_SELF_SIGN, misc.HPM_SELF_SIGN_SIGNER_PEM)
        self.ts_signer_pem = config.get(misc.HPM_SELF_SIGN, misc.HPM_SELF_SIGN_TS_PEM)
        self.ts_signer_cnf = config.get(misc.HPM_SELF_SIGN, misc.HPM_SELF_SIGN_TS_CNF)


class BmcgoE2pServerSign(object):
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.url = config.get(misc.E2P_SERVER_SIGN, misc.E2P_SERVER_SIGN_URL)


class BmcgoE2pSelfSign(object):
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.pem = config.get(misc.E2P_SELF_SIGN, misc.E2P_SELF_SIGN_PEM)


class BmcgoHpmEncrypt(object):
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.need_encrypt = config.getboolean(misc.HPM_ENCRYPT, misc.HPM_ENCRYPT_ENABLE)
        self.tool_path = shutil.which(misc.HPM_ENCRYPT_TOOL)


class BmcgoConfig(object):
    def __init__(self):
        """初始化"""
        self.component = None
        self.conan_index = None
        self.manifest = None
        self.ibmc_sdk = None
        self.hpm_self_sign: BmcgoHpmSelfSign = None
        self.hpm_server_sign: BmcgoHpmServerSign = None
        self.e2p_self_sign: BmcgoE2pSelfSign = None
        self.e2p_server_sign: BmcgoE2pServerSign = None
        self.hpm_encrypt = None
        self.new_frame = False
        self.conan_blacklist = []
        self.bmcgo_path = os.path.dirname(os.path.realpath(__file__))
        self.functional_path = os.path.join(self.bmcgo_path, "functional")
        self.studio_path = os.path.join(self.functional_path, "bmc_studio")
        sys.path.append(self.functional_path)
        sys.path.append(self.studio_path)
        self.cwd = os.getcwd()
        self._bmcgo_config_init()
        self.bmcgo_system_config_path = os.path.join("/etc", "bmcgo.conf")
        self.bmcgo_system_config = configparser.ConfigParser()
        self.bmcgo_global_config_path = os.path.join(os.environ["HOME"], ".bmcgo", "config")
        self.bmcgo_global_config = configparser.ConfigParser()
        self.bmcgo_local_config_path = os.path.join(self.cwd, ".bmcgo", "config")
        self.bmcgo_local_config = configparser.ConfigParser()
        self.bmcgo_config_list = {}
        self._bmcgo_config_load()
        self.conf_path = os.path.join(self.bmcgo_path, "cli", "config.yaml")

    @functools.cached_property
    def partner_mode(self):
        """是否是伙伴模式"""
        """勿删除,用于构建伙伴模式bmcgo,return True"""
        return True

    @functools.cached_property
    def current_branch(self):
        folder = self.manifest.folder if self.manifest else self.component.folder
        repo = Repo(folder)
        return repo.active_branch.name

    def _bmcgo_config_init(self):
        """配置初始化"""
        cwd = self.cwd
        if os.path.isfile("frame.py"):
            self.manifest = BmcgoManifest(os.path.realpath(os.path.join(cwd, "..")), None)
            return
        if os.path.isfile("build/frame.py"):
            self.manifest = BmcgoManifest(cwd, None)
            return
        while cwd != "/":
            config_file = os.path.join(cwd, ".bmcgo", "config")
            if os.path.isfile(config_file):
                conf = configparser.ConfigParser()
                conf.read(config_file)
                try:
                    folder = conf.get("ibmc_sdk", misc.GLOBAL_BMCGO_CONF_FOLDER)
                    folder = os.path.join(cwd, folder)
                    self.ibmc_sdk = BmcgoConanIndex(folder, conf)
                except (NoSectionError, NoOptionError):
                    log.debug("不是一个合法的ibmc_sdk仓")
                try:
                    folder = conf.get("conan-index", misc.GLOBAL_BMCGO_CONF_FOLDER)
                    folder = os.path.join(cwd, folder)
                    self.conan_index = BmcgoConanIndex(folder, conf)
                except (NoSectionError, NoOptionError):
                    log.debug("不是一个合法的conan-index仓")
                self.new_frame = True
                try:
                    folder = conf.get("manifest", misc.GLOBAL_BMCGO_CONF_FOLDER)
                    folder = os.path.join(cwd, folder)
                    self.manifest = BmcgoManifest(folder, conf)
                except (NoSectionError, NoOptionError):
                    log.debug("不是一个合法的manifest仓")
                    self.new_frame = False
                try:
                    self.conan_blacklist = conf.get("bmcgo", "conan-blacklist", raw=True).splitlines()
                except (NoSectionError, NoOptionError):
                    log.debug("未在.bmcgo/config中找到conan-blacklist配置项，拉取全部connan")
                try:
                    folder = conf.get("component", misc.GLOBAL_BMCGO_CONF_FOLDER)
                    folder = os.path.join(cwd, folder)
                    self.component = BmcgoComp(folder, conf)
                except (NoSectionError, NoOptionError):
                    log.debug("不是一个合法的组件仓，尝试查找mds/service.json")

                self._bmcgo_signature_config_load(conf)

            config_file = os.path.join(cwd, "mds", "service.json")
            if self.manifest is None and os.path.isfile(config_file):
                self.component = BmcgoComp(cwd, None)
                return

            cwd = os.path.dirname(cwd)

    def _bmcgo_config_load(self):
        """读取配置"""
        self._bmcgo_system_config_load()
        self._bmcgo_global_config_load()
        self._bmcgo_local_config_load()
        self._bmcgo_signature_config_load(self.bmcgo_local_config)
        self._bmcgo_signature_config_load(self.bmcgo_global_config)
        self._bmcgo_signature_config_load(self.bmcgo_system_config)

    def _bmcgo_system_config_load(self):
        """读取配置"""
        if os.path.isfile(self.bmcgo_system_config_path):
            self.bmcgo_system_config.read(self.bmcgo_system_config_path)
            for section in self.bmcgo_system_config.sections():
                for k, v in self.bmcgo_system_config.items(section):
                    self._generate_bmcgo_config(section, k, v)

    def _bmcgo_global_config_load(self):
        """读取配置"""
        if os.path.isfile(self.bmcgo_global_config_path):
            self.bmcgo_global_config.read(self.bmcgo_global_config_path)
            for section in self.bmcgo_global_config.sections():
                for k, v in self.bmcgo_global_config.items(section):
                    self._generate_bmcgo_config(section, k, v)

    def _bmcgo_local_config_load(self):
        """读取配置"""
        if os.path.isfile(self.bmcgo_local_config_path):
            self.bmcgo_local_config.read(self.bmcgo_local_config_path)
            for section in self.bmcgo_local_config.sections():
                for k, v in self.bmcgo_local_config.items(section):
                    self._generate_bmcgo_config(section, k, v)

    def _bmcgo_signature_config_load(self, conf: configparser.ConfigParser):
        """解析hpm与eeprom签名加密配置，优先级如下"""
        """.bmcgo/config > local config > global config > system config"""
        try:
            if not self.hpm_self_sign:
                self.hpm_self_sign = BmcgoHpmSelfSign(conf)
        except (NoSectionError, NoOptionError):
            log.debug("未找到hpm自签名配置")

        try:
            if not self.hpm_server_sign:
                self.hpm_server_sign = BmcgoHpmServerSign(conf)
        except (NoSectionError, NoOptionError):
            log.debug("未找到hpm服务器签名配置")
        
        try:
            if not self.e2p_self_sign:
                self.e2p_self_sign = BmcgoE2pSelfSign(conf)
        except (NoSectionError, NoOptionError):
            log.debug("未找到eeprom自签名配置")
        
        try:
            if not self.e2p_server_sign:
                self.e2p_server_sign = BmcgoE2pServerSign(conf)
        except (NoSectionError, NoOptionError):
            log.debug("未找到eeprom服务器签名配置")

        try:
            if not self.hpm_encrypt:
                self.hpm_encrypt = BmcgoHpmEncrypt(conf)
        except (NoSectionError, NoOptionError):
            log.debug("未找到hpm加密配置")

    def _generate_bmcgo_config(self, section, key, value):
        """读取配置"""
        if section not in self.bmcgo_config_list:
            self.bmcgo_config_list[section] = {key: value}
        else:
            self.bmcgo_config_list[section][key] = value
