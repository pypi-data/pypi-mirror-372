#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
# descritption: 解析service.json配置文件，生成不同的组件版本service.json配置文件
import os
import json
import logging
import stat
import re
import argparse

from bmcgo.component.package_info import InfoComp
from bmcgo.component.component_helper import ComponentHelper
from bmcgo.logger import Logger
from bmcgo import misc

log = Logger("ComponentDtVersionParse", logging.INFO)


class Function:
    """这边只提供功能模块，做单一解析
    """
    @classmethod
    def is_opensource(cls, version_str: str):
        """检查组件是否是开源软件

        Args:
            version_str (str): 配置的组件conan版本

        Returns:
            bool: 是开源软件返回True
        """
        version_str_list = re.split('/|@', version_str)
        # 如果没有方括号，那么则是静态或者开源
        if '[' not in version_str_list[1]:
            # 如果没有查到数字三段, 则认为为开源
            if re.fullmatch("\d+\.\d+\.\d", version_str_list[1]) is None:
                return True
            # 是三段式, 判定为自研
            else:
                return False
        # 有方括号一律认定为自研
        else:
            return False

    @classmethod
    def get_key_value(cls, search_dict: dict, key: str):
        """获取字典的键的值

        Args:
            key (str): 使用"a/b/c"形式可逐级取值, 失败则返回None

        Returns:
            _type_: 返回值为键的值
        """
        if search_dict is None:
            return search_dict
        value = search_dict
        for sub_key in key.split("/"):
            value = value.get(sub_key, None)
            if value is None:
                return value
        return value

    @classmethod
    def limit_check(cls, str_input: str):
        """检查字符串是否有上下限

        Args:
            str_input (str): 被检查字符串

        Returns:
            bool: 是否匹配上
        """
        if '<' not in str_input and '>' not in str_input:
            return True, "为静态版本或者开源软件"
        elif '<' not in str_input:
            return False, "没有上限"
        elif '>' not in str_input:
            return False, "没有下限"
        else:
            return True, "上下限均已配置"

    @classmethod
    def get_minimum_version(cls, component_conf_str: str):
        """
        获取组件最低的版本配置

        Args:
            component_conf_str (str): 组件版本配置字符串

        Returns:
            str: 组件最低版本配置字符串
        """
        if cls.is_opensource(component_conf_str) is False:
            component_conf_list = re.split('/|@', component_conf_str)
            version_conf_list = component_conf_list[1].strip('[]').split(',')
            version = []
            for version_conf in version_conf_list:
                if ">=" in version_conf:
                    # 去掉下限的范围符号, 只保留固定版本号
                    version.append(version_conf.strip(' >='))
                elif "<=" in version_conf:
                    continue
                else:
                    # 其他内容保留
                    version.append(version_conf)
            component_conf_list[1] = ','.join(version)
            # 有些除了版本, 还有其他配置的, 外面的方括号加回去
            if len(version) > 1:
                component_conf_list[1] = f"[{component_conf_list[1]}]"
            # 由于之前将所有的符号给拆了，这里将符号加上
            k = 1
            for i in range(len(component_conf_list) - 1):
                component_conf_list[i + k:i + k] = ['/', '@', '/'][i]
                k = k + 1
            component_conf_str = ''.join(component_conf_list)
        return component_conf_str

    @classmethod
    def get_version_replace(cls, component_service: str, manifest_subsys: str, use_patch_range=False):
        """使用manifest_subsys的静态组件版本 替换掉 组件配置的组件版本

        Args:
            component_service (str): 组件配置的组件版本
            manifest_subsys (str): manifest仓配置的组件版本

        Returns:
            _type_: 返回替换完成的组件版本
        """
        service_version_list = re.split('/|@', component_service)
        manifest_version = re.split('/|@', manifest_subsys)[1]

        if use_patch_range and not Function.is_opensource(manifest_subsys):
            # 三段式版本组件修改为补丁范围版本 [>=x.y.z <x.y+1.0]
            major, minor, _ = manifest_version.split(".")
            uppper_verison = f"{major}.{int(minor) + 1}.0"

            service_version_list[1] = f"[>={manifest_version} <{uppper_verison}]"
        else:
            service_version_list[1] = manifest_version
        # 由于之前将所有的符号给拆了，这里将符号加上
        k = 1
        for i in range(len(service_version_list) - 1):
            service_version_list[i + k:i + k] = ['/', '@', '/'][i]
            k = k + 1
        return ''.join(service_version_list)

    @classmethod
    def find_key(cls, key, dictionary):
        """在字典中查找相同key值并返回key值组成的列表

        Args:
            key (_type_): 要查找的key值
            dictionary (_type_): 被查找的字典

        Returns:
            _type_: key的值组成的列表
        """
        results = []
        for k, v in dictionary.items():
            if k == key:
                results.append(v)
            elif isinstance(v, dict):
                results.extend(cls.find_key(key, v))
        return results


class ManifestConfigParse:
    """获取 manifest 目录下的所有组件版本配置
    """
    def __init__(self, package_info_file: str):
        """初始化 package_info 仓路径

        Args:
            package_info_file (str): package_info 路径
        """
        self.package_info_file = package_info_file

    def get_version_dict(self):
        """获取主干仓的 package_info 所有组件版本配置

        Returns:
            dict: 返回所有组件配置的字典
        """
        with open(self.package_info_file, mode="r") as fp:
            package_info_list = fp.readlines()
            package_info_dict = {package.strip('\n').split('/')[0]:package.strip('\n') for package in package_info_list}
        return package_info_dict


class ComponentDtVersionParse:
    """分析组件 dt 的依赖组件版本, 实现自动配置 service.json 文件, 达成 dt 构建门禁
    """
    def __init__(self, parser=None, serv_file="mds/service.json", args=None):
        """初始化，读取配置

        Args:
            serv_file (str): 配置文件路径
        """
        if not parser:
            parser = argparse.ArgumentParser(description="component dt different version")
        parser.add_argument("--minimum", "-m", action=misc.STORE_TRUE, help="获取dt构建的最小版本")
        parser.add_argument("--package_info", "-pi", default=None, help="package_info 文件路径, 使用manifest配套版本dt构建, \
            此文件在manifest构建时会在inner目录生成")
        parsed_args, _ = parser.parse_known_args(args)
        self.minimum = parsed_args.minimum
        self.package_info = parsed_args.package_info

        # 读取service.json配置文件
        self.serv_file = serv_file
        with open(self.serv_file, "r") as mds_conf_fp:
            self.mds_conf = json.load(mds_conf_fp)
            mds_conf_fp.close()
        # 生成dt与build的依赖列表, 检查时如果发现问题, 直接报出组件名, 不分类
        conan_dt_list = Function.get_key_value(self.mds_conf, "dependencies/test") or []
        conan_build_list = Function.get_key_value(self.mds_conf, "dependencies/build") or []
        # 根据配置文件，已确定为列表，有告警，无需使用list转化，影响效率
        self.conan_list = conan_dt_list + conan_build_list

    def write_to_serv_file(self):
        """写入到对象的 service.json 文件
        """
        with os.fdopen(os.open(self.serv_file, flags=os.O_WRONLY, \
                mode=stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH), "w") as mds_conf_fp:
            mds_conf_fp.seek(0)
            mds_conf_fp.truncate()
            json.dump(self.mds_conf, mds_conf_fp, indent=4, ensure_ascii=False)
            mds_conf_fp.close()

    def component_limit_check(self):
        """上下限检查

        Args:
            check_char (str): '>'表示检查下限, '<'表示检查上限

        Raises:
            AttributeError: 配置错误
        """
        # 默认情况下, 检查通过
        log.info("开始上下限检查")
        check_result = True
        for conan in self.conan_list:
            check, msg = Function.limit_check(conan[misc.CONAN])
            if check is False:
                log.error(f"组件 {conan[misc.CONAN]} {msg}")
                check_result = False
            else:
                log.debug(f"组件 {conan[misc.CONAN]} {msg}")
        # 检查失败, 报错
        if check_result is False:
            raise AttributeError("上下限检查失败")
        else:
            log.info("上下限检查通过")

    def minimum_version_config(self):
        """获取 service.json 的最小配置版本
        """
        # 列表逐个取最小版本
        for version_conf in self.conan_list:
            version_conf[misc.CONAN] = Function.get_minimum_version(version_conf[misc.CONAN])
        self.write_to_serv_file()

    def manifest_version_revise(self, package_info_file: str, use_patch_range=False):
        """将 package_info 的组件版本配置到 service.json 文件中

        Args:
            package_info (str): package_info 路径
        """
        manifest_config_dict = ManifestConfigParse(package_info_file).get_version_dict()
        check_fail_list = []
        test_component = ["dtframeforlua", "test_data"]
        for component in self.conan_list:
            component_name = component[misc.CONAN].split('/')[0]
            component_version = component[misc.CONAN]
            if component_name in manifest_config_dict:
                component[misc.CONAN] = Function.get_version_replace(
                    component_version,
                    manifest_config_dict[component_name],
                    use_patch_range,
                )
            elif component_name in test_component:
                continue
            else:
                check_fail_list.append(component_name)
        if len(check_fail_list) > 0:
            raise AttributeError(f"组件 {check_fail_list} 不在 manifest 仓的 subsys 配置中")
        self.write_to_serv_file()

    def manifest_full_version_dt(self, comp_info: InfoComp, package_info_file: str):
        """将service.json的依赖组件的所有间接依赖组件根据package_info的组件版本也配置到service.json文件中"""
        manifest_config_dict = ManifestConfigParse(package_info_file).get_version_dict()

        def get_full_pkg_dependencies(mds_conan_list, root_dependencies):
            # 获取当前组件service.json中的组件及版本
            mds_conan_dependencies = [dep[misc.CONAN] for dep in mds_conan_list]
            mds_pkgs = [dep.split("/")[0] for dep in mds_conan_dependencies]
            # 通过当前组件的依赖组件完整路径xx/v@user/channel获取间接依赖
            all_dependencies = ComponentHelper.get_all_dependencies(root_dependencies, comp_info.remote)
            dependencies = set(root_dependencies)
            for dependency in all_dependencies:
                component_name = dependency.split("/")[0]
                comp = manifest_config_dict.get(component_name, None)
                if comp and component_name not in mds_pkgs:
                    dependencies.add(comp)

            full_pkg_dependencies = []
            for package in dependencies:
                if not (package.endswith(f"/{misc.StageEnum.STAGE_STABLE.value}") \
                        or (package in mds_conan_dependencies)):
                    package = package.split("@")[0]
                full_pkg_dependencies.append({misc.CONAN: package})
            return full_pkg_dependencies

        conan_build_list = Function.get_key_value(self.mds_conf, "dependencies/build") or []
        mds_conf_build = get_full_pkg_dependencies(conan_build_list, comp_info.build_dependencies)
        self.mds_conf["dependencies"]["build"] = mds_conf_build

        conan_test_list = Function.get_key_value(self.mds_conf, "dependencies/test") or []
        mds_conf_test = get_full_pkg_dependencies(conan_test_list, comp_info.test_dependencies)
        self.mds_conf["dependencies"]["test"] = mds_conf_test
        self.write_to_serv_file()

    def chose_dt_mode(self):
        if self.minimum is True:
            self.minimum_version_config()
        elif self.package_info is not None:
            self.manifest_version_revise(self.package_info)
            comp_info = InfoComp([], self.serv_file)
            self.manifest_full_version_dt(comp_info, self.package_info)
        else:
            log.info("没有启动组件版本分析")


if __name__ == "__main__":
    _parser = argparse.ArgumentParser()
    _parser.add_argument("--service_json")
    _parsed_args, argv = _parser.parse_known_args()
    self_test = ComponentDtVersionParse(serv_file=_parsed_args.service_json, args=argv)
    self_test.chose_dt_mode()
