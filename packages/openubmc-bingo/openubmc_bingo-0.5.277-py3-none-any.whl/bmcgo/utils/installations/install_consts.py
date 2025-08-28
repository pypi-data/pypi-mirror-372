#!/usr/bin/env python3
# encoding=utf-8
# 描述：安装工具集常量
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

INSTALLATION_PATH = "instllations"

PLUGIN_INSTALLER_PATH = "installers"
PLUGIN_INSTALL_PLAN_PATH = "install_plans"

INSTALL_ALL = "all"
INSTALL_LATEST = "latest"
INSTALL_DEFAULT = f"{INSTALL_ALL}={INSTALL_LATEST}"

PLAN_VERSION_HOMOGENEOUS = "version_homogeneous"
PLAN_STEPS = "install_steps"
PLAN_INSTALL_TYPE = "type"
PLAN_PACKAGE_NAME = "package_name"
PLAN_MODULE_NAME = "module_name"
PLAN_REPO_URL = "url"
PLAN_GPG = "gpg"
PLAN_CONFIG_FILE = "config_file"
PLAN_PUBLIC_KEY = "public_key"
PLAN_DOC = "doc"