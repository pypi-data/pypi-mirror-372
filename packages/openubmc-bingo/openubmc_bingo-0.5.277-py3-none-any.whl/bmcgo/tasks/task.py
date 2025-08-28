#!/usr/bin/python3
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
import os
import json
import stat
import traceback
import importlib
import shutil
import time
import tempfile
import filecmp
from string import Template
from multiprocessing import Process
from collections import OrderedDict

import yaml
from conans.model.profile import Profile
from bmcgo.utils.config import Config
from bmcgo.utils.tools import Tools
from bmcgo import errors
from bmcgo.utils.component_post import ComponentPost
from bmcgo.functional.simple_sign import BmcgoCommand as SimpleSign


class Task(Process):
    name = "WorkBase"
    timeout = 1200
    description = "基础类"
    work_name = ""
    manifest_obj = None

    def __init__(self, config: Config, work_name=""):
        super(Task, self).__init__()
        log_file = os.path.join(config.temp_path, "log", "task.log")
        self.tools: Tools = Tools(work_name, log_file=log_file)
        self.log = self.tools.log
        self.config: Config = config
        self.built_type_check()
        self.work_name = work_name

    @property
    def conan_home(self):
        return self.tools.conan_home

    @property
    def conan_profiles_dir(self):
        return self.tools.conan_profiles_dir

    @property
    def conan_data(self):
        return self.tools.conan_data

    # rootfs定制化，参考application/build/customization
    @property
    def customization(self):
        config = self.get_manufacture_config("base/customization")
        if config is None:
            return []
        # 类名
        config_file = []
        if isinstance(config, str):
            config_file = [config]
        elif isinstance(config, list):
            config_file = config
        obj = []
        for config in config_file:
            path = config.replace("/", ".")[0:-3]
            work_py_file = importlib.import_module(path, "works.work")
            work_class = getattr(work_py_file, "Customization", None)
            if not work_class:
                work_class = getattr(work_py_file, "BaseCustomization", None)
            if not work_class:
                raise errors.BmcGoException(f"定制化脚本 {config} 未找到Customization或BaseCustomization类，定制化失败")
            obj.append(work_class(self, self.config))
        return obj

    def built_type_check(self):
        if self.config.manufacture_code is None:
            return
        manufacture_build_type = self.get_manufacture_config(f"manufacture/{self.config.manufacture_code}/build_type")
        if manufacture_build_type is not None and self.config.build_type != manufacture_build_type:
            self.error("构建类型和包编码中配置的构建类型不匹配, 参数配置为: {}, 而对应包编码配置为: {}".format(\
                self.config.build_type, manufacture_build_type))
            raise Exception

    def read_json(self, json_path):
        if not os.path.exists(json_path):
            raise Exception
        with open(json_path, "r") as json_file:
            return json.load(json_file)
        raise Exception

    # 子类必须实现run方法,未实现时异常
    def run(self):
        self.info(f"{__file__} error")
        raise Exception

    # 安装函数，将各work的产出安装到config.rootfs目录中
    def install(self):
        pass

    def deal_conf(self, config_dict):
        """
        处理每个work的私有配置"work_config"，只有work类有set_xxx类方法的属性可以设置
        """
        if not config_dict:
            return
        for conf in config_dict:
            try:
                exist = getattr(self, f"set_{conf}")
                val = config_dict.get(conf)
                exist(val)
            except Exception as e:
                raise Exception(f"无效配置: {conf}, {e}, {traceback.print_exc()}") from e

    def link(self, src, dst, uptrade=1):
        if os.path.isfile(dst):
            os.unlink(dst)
        if os.path.dirname(dst) != "":
            os.makedirs(os.path.dirname(dst), exist_ok=True)
        # 直接复制文件
        self.info(f"复制 {src} 到 {dst}", uptrace=uptrade)
        shutil.copyfile(src, dst)

    def manufacture_version_check(self, filename) -> bool:
        """ 当某些包打出来的包的版本号是当前版本加1的，使用此接口来进行确认是否加1
        返回值:
            bool: 是否需要加1
        """
        with open(filename, mode="r") as fp:
            origin_config = yaml.safe_load(fp)
        # 这两个code是冲突的，只取其一，默认情况下会取第二个
        if self.config.manufacture_code is not None:
            package_name = origin_config.get("manufacture").get(self.config.manufacture_code).get("package_name")
        else:
            package_name = origin_config.get("tosupporte").get(self.config.tosupporte_code).get("package_name")

        if "manufacture_version" in package_name:
            return True
        else:
            return False

    # 依赖manifest的files复制文件
    def copy_manifest_files(self, files, exclude_files=None):
        if not files:
            return
        exclude_files = exclude_files or []
        file_list = []
        if isinstance(files, dict):
            for _, val in files.items():
                file_list.append(val)
        else:
            file_list = files
        for file in file_list:
            condition = file.get("condition")
            match = self._if_match(condition)
            if not match:
                continue
            filename = file.get("file")
            if filename is None:
                continue
            filename = time.strftime(filename, self.config.date)
            dst = file.get("dst")
            if dst is None:
                dst = os.path.basename(filename)
            if dst in exclude_files:
                self.debug(f"Skip copy {filename} because in exclude list")
                continue
            if not os.path.isfile(filename):
                raise FileNotFoundError("{} 不是一个文件或者不存在".format(filename))
            dst = time.strftime(dst, self.config.date)
            if "/" in dst:
                dst = str(Template(dst).safe_substitute(self.config.get_template()))
                dirname = os.path.dirname(dst)
                os.makedirs(dirname, exist_ok=True)
            self.info("复制文件 {} 到 {}".format(filename, dst))
            if file.get("template"):
                # 模板文件替换内容后复制
                with open(filename, "r") as fp:
                    content = fp.read()
                    fp.close()
                self.info(f"模板替换后复制{filename}到{dst}")
                content = Template(content)
                content = content.safe_substitute(self.config.get_template())
                with os.fdopen(os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                       stat.S_IWUSR | stat.S_IRUSR), 'w') as file_handler:
                    file_handler.write(content)
                    file_handler.close()
            else:
                # 非模板文件直接复制
                self.link(filename, dst)

    # 从manifest中获取属性值
    def get_manufacture_config(self, key: str, default_val=None):
        """获取manifest.yml当中的配置
        参数:
            key (str): 要获取的配置，采用路径类似格式，比如'manufacture/05023VAY'
        返回值:
            None: 未找到配置
            str: 配置的值
        """
        return self.config.get_manufacture_config(key, default_val)

    def get_profile_config(self) -> (Profile, OrderedDict):
        return self.tools.get_profile_config(self.config.profile)

    def prepare_conan(self):
        # 先删除profile文件
        self.run_command(f"rm -rf {self.conan_profiles_dir}/profile.dt.ini", ignore_error=True)
        self.run_command(f"rm -rf {self.conan_profiles_dir}/profile.ini", ignore_error=True)
        self.run_command(f"rm -rf {self.conan_profiles_dir}/profile.luajit.ini", ignore_error=True)
        profile_dt = f"{self.config.code_path}/profile.dt.ini"
        if os.path.isfile(profile_dt):
            shutil.copy2(profile_dt, f"{self.conan_profiles_dir}/profile.dt.ini")
        profile = f"{self.config.code_path}/profile.ini"
        if os.path.isfile(profile):
            shutil.copy2(profile, f"{self.conan_profiles_dir}/profile.ini")
        # 新增profile文件需要存在在manifest/build/profiles目录
        profiles = os.path.join(self.config.code_path, "profiles")
        if os.path.isdir(profiles):
            shutil.copytree(profiles, self.conan_profiles_dir, dirs_exist_ok=True)
        platform_profiles = os.path.join(self.config.temp_platform_build_dir, "profiles")
        if os.path.isdir(platform_profiles):
            shutil.copytree(platform_profiles, self.conan_profiles_dir, dirs_exist_ok=True)
        self.run_command("conan remote remove conancenter", ignore_error=True)
    
    def check_need_install(self, download_dir_path, old_sha, new_sha):
        need_install_flag = True
        # 计算sha256
        self.pipe_command([f"find {download_dir_path} -type f", "xargs sha256sum", "awk '{print $1}'", "sort"], new_sha)
        if os.path.isfile(old_sha) and filecmp.cmp(old_sha, new_sha):
            need_install_flag = False
        return need_install_flag

    def chdir(self, path):
        self.info(f"切换工作目录到: {path}", uptrace=1)
        os.chdir(path)

    def run_command(self, command, ignore_error=False, sudo=False, **kwargs):
        """
        如果ignore_error为False，命令返回码非0时则打印堆栈和日志并触发异常，中断构建
        """
        uptrace = kwargs.get("uptrace", 1)
        kwargs["uptrace"] = uptrace
        return self.tools.run_command(command, ignore_error, sudo, **kwargs)

    def pipe_command(self, commands, out_file=None, **kwargs):
        return self.tools.pipe_command(commands, out_file, **kwargs)

    def signature(self, unsigned_file, cms_output, crl_output, ca_output):
        manifest_sign_server = self.get_manufacture_config("base/signature/simple_signer_server") 
        hpm_server_sign = self.config.bconfig.hpm_server_sign
        if manifest_sign_server or hpm_server_sign:
            self._server_signature(unsigned_file, cms_output, crl_output, ca_output)
        else:
            self._local_signature(unsigned_file, cms_output, crl_output, ca_output)

    def error(self, msg, *args, **kwargs):
        uptrace = kwargs.get("uptrace", None)
        if uptrace is None:
            uptrace = 1
        else:
            uptrace += 1
        kwargs["uptrace"] = uptrace
        self.tools.log.error(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        uptrace = kwargs.get("uptrace", None)
        if uptrace is None:
            uptrace = 1
        else:
            uptrace += 1
        kwargs["uptrace"] = uptrace
        self.tools.log.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        uptrace = kwargs.get("uptrace", None)
        if uptrace is None:
            uptrace = 1
        else:
            uptrace += 1
        kwargs["uptrace"] = uptrace
        self.tools.log.debug(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        uptrace = kwargs.get("uptrace", None)
        if uptrace is None:
            uptrace = 1
        else:
            uptrace += 1
        kwargs["uptrace"] = uptrace
        self.tools.log.warning(msg, *args, **kwargs)

    def success(self, msg, *args, **kwargs):
        uptrace = kwargs.get("uptrace", None)
        if uptrace is None:
            uptrace = 1
        else:
            uptrace += 1
        kwargs["uptrace"] = uptrace
        self.tools.log.success(msg, *args, **kwargs)

    def _if_match(self, condition):
        if condition is None:
            return True
        for key, val in condition.items():
            if key == "build_type":
                if self.config.build_type != val:
                    return False
            else:
                raise OSError(f"未知条件: {key}, 请检查此种条件是否在配置内")
        return True

    def _component_cust_action(self, action: str):
        conan_install = f"{self.config.build_path}/conan_install"

        # 优先处理rootfs定制化脚本
        comps = ["rootfs"]
        for dirname in os.listdir(conan_install):
            if not os.path.isdir(f"{conan_install}/{dirname}"):
                continue
            if dirname != "rootfs" and dirname != "openubmc":
                comps.append(dirname)
        # 最后处理openubmc
        comps.append("openubmc")
        self.info(f"所有组件为: {comps}")

        profile, _ = self.get_profile_config()
        for comp in comps:
            cust = os.path.join(conan_install, comp, "include", "customization.py")
            if not os.path.isfile(cust):
                continue
            self.info(f">>>>>>>>>> 开始执行 {cust} {action} 定制化")
            self.info(f"执行脚本 {comp}/include/customization.py 开始")
            post = ComponentPost(self.config, os.path.join(conan_install, comp), profile)
            post.post_work(os.getcwd(), action)

    def _local_signature(self, unsigned_file, cms_output, crl_output, ca_output):
        """自签名方法"""
        self_sign_config = self.config.bconfig.hpm_self_sign
        unsigned_file = os.path.realpath(unsigned_file)
        cms_output = os.path.realpath(cms_output)
        tmp_dir = tempfile.TemporaryDirectory()
        cwd = os.getcwd()
        self.chdir(tmp_dir.name)
        certificates = self.get_manufacture_config("base/signature/certificates")
        if certificates:
            rootca_der = self.config.rootca_der
            rootca_crl = self.config.rootca_crl
            signer_pem = self.config.signer_pem
            ts_signer_pem = self.config.ts_signer_pem
            ts_signer_cnf = self.config.ts_signer_cnf
        else:
            rootca_der = self_sign_config.rootca_der
            rootca_crl = self_sign_config.rootca_crl
            signer_pem = self_sign_config.signer_pem
            ts_signer_pem = self_sign_config.ts_signer_pem
            ts_signer_cnf = self_sign_config.ts_signer_cnf
        self.run_command(f"openssl x509 -in {rootca_der} -inform der -outform pem -out rootca.pem")
        self.run_command(f"openssl crl -in {rootca_crl} -inform der -outform pem -out cms.crl.pem")
        cmd = f"hpm_signer -s {signer_pem} -t {ts_signer_pem} -T {ts_signer_cnf} -i {unsigned_file} -o {cms_output}"
        self.run_command(cmd)
        self.run_command(f"hpm_verify -r rootca.pem -C cms.crl.pem -c {unsigned_file} -s {cms_output}")
        self.log.info(f"使用 hpm_signer 自签名 {unsigned_file} 成功")
        self.chdir(cwd)
        self.tools.copy(rootca_crl, crl_output)
        self.tools.copy(rootca_der, ca_output)
    
    def _server_signature(self, unsigned_file, cms_output, crl_output, ca_output):
        manifest_sign_server = self.get_manufacture_config("base/signature/simple_signer_server")
        hpm_server_sign = self.config.bconfig.hpm_server_sign
        if manifest_sign_server:
            rootca_der = manifest_sign_server.get("rootca_der")
            url = manifest_sign_server.get("url")
            cert_id = manifest_sign_server.get("cert_id")
            ssl_verify = manifest_sign_server.get("ssl_verify")
        else:
            rootca_der = hpm_server_sign.rootca_der
            url = hpm_server_sign.url
            cert_id = hpm_server_sign.cert_id
            ssl_verify = hpm_server_sign.ssl_verify

        if not os.path.isfile(rootca_der):
            raise FileNotFoundError(f"签名根证书{rootca_der}不存在")
        unsigned_file = os.path.realpath(unsigned_file)
        cms_output = os.path.realpath(cms_output)
        crl_output = os.path.realpath(crl_output)
        ca_output = os.path.realpath(ca_output)
        cwd = os.getcwd()
        tmpdir = tempfile.TemporaryDirectory()
        self.chdir(tmpdir.name)
        args = ["-i", unsigned_file, "-s", cert_id, "-u", url, "-v", ssl_verify]
        cmd = SimpleSign(self.config.bconfig, args)
        cmd.run()
        # 签名工具会输出rootca.crl和signed.cms
        self.tools.copy("signed.cms", cms_output)
        self.tools.copy("rootca.crl", crl_output)
        # 签名根证书在manifest.yml中配置
        self.tools.copy(rootca_der, ca_output)
        os.chdir(cwd)
