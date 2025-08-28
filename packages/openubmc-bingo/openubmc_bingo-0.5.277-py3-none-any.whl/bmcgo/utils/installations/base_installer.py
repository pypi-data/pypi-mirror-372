#!/usr/bin/env python3
# encoding=utf-8
# 描述：安装工具工厂类
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import abc
import sys
import importlib.util
from pathlib import Path
from typing import Dict, List, Type
from bmcgo.utils.tools import Tools
from bmcgo.utils.installations import install_consts
from bmcgo.utils.installations.version_util import PkgVersion


class BaseInstaller(abc.ABC):
    tools = Tools("install")
    logger = tools.log
    _intallers: Dict[str, Type["BaseInstaller"]] = {}
    search_paths: List[Path] = [Path(__file__).resolve().parent / install_consts.PLUGIN_INSTALLER_PATH]
    type_name = None

    def __init__(self):
        self._pkg_name = None
        self._target_ver = None
        self._cur_ver = None

    def __init_subclass__(cls, **kwargs):
        super.__init_subclass__(**kwargs)

        key = cls.type_name or cls.__name__.lower()
        if key in cls._intallers:
            cls.logger and cls.logger.warning(f"{key}({cls._intallers[key]} 被替换为: {cls})")
        cls._intallers[key] = cls

    @property
    def target_version(self):
        return self._target_ver
    
    @property
    def current_version(self):
        return self._cur_ver
    
    @property
    def package_name(self):
        return self._pkg_name

    @classmethod
    def add_installer_dir(cls, directory: Path):
        if directory not in cls.search_paths:
            cls.search_paths.append(directory)

    @classmethod
    def discover_installers(cls):
        for path in cls.search_paths:
            if not path.exists():
                cls.logger and cls.logger.warning(f"未知安装工具路径：: {str(path)}，跳过")
                continue

            for inst in path.glob("*.py"):
                if inst.name == "__init__.py":
                    continue

                module_name = inst.stem
                spec = importlib.util.spec_from_file_location(f"installer_{module_name}", inst)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    try:
                        sys.modules[module.__name__] = module
                        spec.loader.exec_module(module)
                    except Exception as e:
                        cls.logger and cls.logger.exception(f"加载安装器 {inst} 失败: {str(e)}")
                        continue

    @classmethod
    def get_installer(cls, installer_type: str) -> "BaseInstaller":
        installer_cls = cls._intallers.get(installer_type)
        if not installer_cls:
            raise ValueError(f"未定义的安装方法：{installer_type}")
        return installer_cls()
    
    def init(self, plan, operator, version):
        self.parse_plan(plan)

        versions = self.get_versions()
        self.resolve_constraint(versions, operator, version)

        self.get_current_version()

    def pre_install(self):
        """ 安装前检查 """
        self.info("安装前检查")
    
    def post_install(self):
        """ 安装后清理 """
        self.info("安装后清理")

    def rollback(self):
        """ 回退 """
        self.info("回退")

    def parse_plan(self, plan: Dict[str, List[str]]):
        self._pkg_name = plan.get(install_consts.PLAN_PACKAGE_NAME)
        if not self._pkg_name:
            self.error(f"{install_consts.PLAN_PACKAGE_NAME} 未配置!")
            return
        self.parse_custom_plan(plan)

    def resolve_constraint(self, versions, opt, ver):
        if not versions:
            self.warning("当前没有可下载版本!")
            return

        if ver == install_consts.INSTALL_LATEST or not opt:
            self._target_ver = versions[0]
            return

        pkg_ver = PkgVersion(ver)
        for avl_ver in versions:
            v = PkgVersion(avl_ver)
            if opt == ">=" and v >= pkg_ver:
                self._target_ver = v.origin
                break
            elif opt == "<=" and v <= pkg_ver:
                self._target_ver = v.origin
                break
            elif opt == "!=" and v != pkg_ver:
                self._target_ver = v.origin
                break
            elif opt == "<" and v < pkg_ver:
                self._target_ver = v.origin
                break
            elif opt == ">" and v > pkg_ver:
                self._target_ver = v.origin
                break
            elif opt == "=" and v == pkg_ver:
                self._target_ver = v.origin
                break
        else:
            self.warning(f"没有找到匹配的版本：{self._pkg_name}{opt}{ver}")
            return
        
    def info(self, msg):
        self.logger and self.logger.info(f"[{self.type_name}] {msg}")

    def error(self, msg):
        self.logger and self.logger.error(f"[{self.type_name}] {msg}")

    def warning(self, msg):
        self.logger and self.logger.warning(f"[{self.type_name}] {msg}")

    @abc.abstractmethod
    def parse_custom_plan(self, plan: Dict[str, List[str]]):
        """ 解析 yml 配置计划 """

    @abc.abstractmethod
    def install(self, force: bool):
        """ 安装入口 """

    @abc.abstractmethod
    def get_versions(self):
        """ 可用版本 """
        
    @abc.abstractmethod
    def show_versions(self):
        """ 列出可用版本 """

    @abc.abstractmethod
    def get_current_version(self):
        """ 获取当前已安装版本 """