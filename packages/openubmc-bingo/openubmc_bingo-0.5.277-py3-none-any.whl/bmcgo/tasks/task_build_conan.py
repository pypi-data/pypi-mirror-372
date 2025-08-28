#!/usr/bin/env python
# coding=utf-8
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

"""
文件名：work_build_conan.py
功能：编译产品依赖包
版权信息：华为技术有限公司，版本所有(C) 2019-2020
"""

import os
import shutil
import shlex
import stat
import json
import time
import subprocess
import random
import pathlib
from multiprocessing import Process, Queue
from copy import deepcopy

import yaml
from colorama import Fore, Back, Style
from conans.model.profile import Profile

from bmcgo.tasks.task import Task
from bmcgo.utils.config import Config
from bmcgo.utils.component_post import ComponentPost
from bmcgo.utils.component_version_check import ComponentVersionCheck
from bmcgo import errors, misc
from bmcgo.utils.tools import Tools
from bmcgo.errors import BmcGoException
from bmcgo.component.component_helper import ComponentHelper

IBMC_LOCK_FILE = "openubmc.lock"
SDK_ROOT = "/opt/hi1711sdk"
SDK_ROOT_MODULE_SYMVERS = os.path.join(SDK_ROOT, "Module.symvers")
PERSIST_TYPES = {
    "TemporaryPer": "TemporaryPer",
    "TemporaryPerRetain": "TemporaryPer",
    "ResetPer": "ResetPer",
    "ResetPerRetain": "ResetPer",
    "PoweroffPer": "PoweroffPer",
    "PoweroffPerRetain": "PoweroffPer",
    "PermanentPer": "PermanentPer"
}
PRIMARY_KEYS = "PrimaryKeys"
tools = Tools()


class CopyComponent(Process):
    def __init__(self, work: Task, comp: str, profile: Profile):
        super().__init__()
        self.work = work
        self.config = self.work.config
        self.comp = comp
        self.profile = profile

    def link_recursive_deal(self, file_name, ownership):
        self.work.run_command(f"chown -h {ownership} {file_name}", sudo=True)
        if os.path.islink(os.readlink(file_name)):
            self.link_recursive_deal(os.readlink(file_name), ownership)

    def run(self):
        self.work.work_name = self.comp
        # 复制组件文件到rootfs中
        # rc.sysinit脚本只允许使用rootfs_user仓库的
        rc_sysinit_path = os.path.join(self.comp, "etc/rc.d/rc.sysinit")
        if self.comp != "rootfs_user" and os.path.isfile(rc_sysinit_path):
            shutil.rmtree(rc_sysinit_path, ignore_errors=True)
        # 由于复制时有很多同名路径，cp命令有概率失败，10次复制尝试
        self._copy_files()

        # 执行权限控制逻辑
        per_cfg = os.path.join(self.comp, "permissions.ini")
        if not os.path.isfile(per_cfg):
            self.work.warning("权限文件 {} 不存在, 所以无法设置组件 {} 的权限".format(per_cfg, self.comp))
            return
        self.work.info("依据配置文件: {}, 修改权限".format(per_cfg))
        # NOTE 这里的配置时间, 偶发复制未完成, 就开始修改权限
        with open(per_cfg, "r") as fp:
            for line in fp:
                line = line.strip()
                if len(line) == 0:
                    continue
                if line.startswith("#"):
                    continue
                self.proc_permissions_line(line)

    def proc_permissions_line(self, line):
        chk = line.split()
        if len(chk) not in (5, 6):
            raise errors.BmcGoException("格式错误行: {}, 固定格式为: name type mode uid gid [os1,os2]".format(line))
        file = os.path.join(self.config.rootfs_path, chk[0])
        if len(chk) == 6:
            host_os = self.profile.settings.get("os")
            is_supported_by_os = host_os in (chk[5].split(","))
            if not is_supported_by_os:
                return

        if chk[1] == 'f' or chk[1] == "d":
            self.work.run_command("chmod {} {}".format(chk[2], file), sudo=True, command_echo=False,
                                  command_key=self.comp)
            self.work.run_command("chown {}:{} {}".format(chk[3], chk[4], file), sudo=True, command_echo=False,
                                  command_key=self.comp)
            if os.path.islink(file):
                self.link_recursive_deal(file, f"{chk[3]}:{chk[4]}")
        elif chk[1] == "r":
            self.work.pipe_command(["sudo find {} -type f ".format(file), " sudo xargs -P 0 -i. chmod {} ."
                                    .format(chk[2])], command_echo=False)
            self.work.pipe_command(["sudo find {} -type f ".format(file), " sudo xargs -P 0 -i. chown {}:{} ."
                                    .format(chk[3], chk[4])], command_echo=False)
        elif chk[1] == "rd":
            self.work.pipe_command(["sudo find {} -type d ".format(file), " sudo xargs -P 0 -i. chmod {} ."
                                    .format(chk[2])], command_echo=False)
            self.work.pipe_command(["sudo find {} -type d ".format(file), " sudo xargs -P 0 -i. chown {}:{} ."
                                    .format(chk[3], chk[4])], command_echo=False)
        elif chk[1] == "l":
            self.work.run_command("chown -h {}:{} {}".format(chk[3], chk[4], file), sudo=True,
                                    command_key=self.comp)

    def _copy_files(self):
        # 由于复制时有很多同名路径，cp命令有概率失败，10次复制尝试
        cmd = "sudo cp -dfr {}/. {}".format(self.comp, self.config.rootfs_path)
        for _ in range(0, 10):
            try:
                # 尝试复制到目标目录，成功则break退出循环
                ret = self.work.run_command(cmd, command_echo=True, ignore_error=True)
                if ret.returncode is not None and ret.returncode == 0:
                    return
            except Exception:
                # 失败了打印告警信息，等待后继续尝试
                self.work.run_command("pwd", show_log=True)
                self.work.warning("执行命令 {} 失败, 即将重试".format(cmd))
                time.sleep(0.5 + random.random())
        else:
            # 如果10次都失败了，则报错，并退出
            raise errors.BmcGoException(f"复制 {self.comp} 失败 !!!")


class ConanLockParse:
    error_str = "Error"

    def __init__(self, bundle_file_name, work: Task):
        """
        bundle_file_name: 生成的.bundle文件
        """
        self.work = work
        # 读取bundle文件生成入度字典
        with open(bundle_file_name, "r") as fp:
            self._bundle = json.load(fp)['lock_bundle']
        self._queue = Queue()
        self._degree = None
        # 防止丢包，已收到包校验
        self._received_list = []
        self._process_list = []

    def conan_install(self, cmd, com):
        real_cmd = shlex.split(cmd)
        pipe = subprocess.Popen(real_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # 超时时长1800s
        out, _ = pipe.communicate(timeout=1800)
        if pipe.returncode != 0:
            self.work.error(f"================== {com} 构建失败日志起始位置 ==================")
            self.work.info(out.decode())
            self.work.error(f"================== {com} 构建失败日志结束位置 ==================")
            self._queue.put(self.error_str)
            self._queue.put(self.error_str)
            self._queue.put(self.error_str)
            return
        self._queue.put(com)
        self._queue.put(com)
        self._queue.put(com)
        self.work.info(f"命令 {cmd} " + Fore.GREEN + "执行完成" + Style.RESET_ALL)

    def wait_task_finished(self):
        # 所有入度为0任务拉起后等待完成消息
        finished_com = self._queue.get()
        # 失败时返回Error传递到主进程
        if finished_com == self.error_str:
            for process in self._process_list:
                if process.is_alive():
                    process.terminate()
            raise errors.BmcGoException("conan 组件构建进程接收到错误")
        # 未收到过组件消息，检查收到收到的消息是否在未构建的组件依赖中，是则入度-1
        if finished_com not in self._received_list:
            self._received_list.append(finished_com)
            for b_key in self._bundle.keys():
                key_req = self._bundle[b_key].get("requires")
                if self._degree.get(b_key) is not None and key_req is not None and finished_com in key_req:
                    self._degree[b_key] = (self._degree[b_key] - 1 if self._degree[b_key] > 0
                                            else self._degree[b_key])
            return False
        return True

    def conan_parallel_build(self, cmd, log_path):
        # 日志目录不存在则新建
        log_path = f"{log_path}/com_log"
        os.makedirs(log_path, exist_ok=True)

        self._degree = {x: len(self._bundle[x].get('requires')) if self._bundle[x].get('requires') is not None else 0
                             for x in self._bundle.keys()}

        self.work.success(">>>>>>>>>>>>>>>>> 开始构建所有组件 <<<<<<<<<<<<<<<<")
        self.work.info("这些进程将要花费几分钟(2-3分钟), 请耐心等待")
        while self._degree:
            # 深拷贝入度字典，分级拉起构建
            entry_degree_temp_dict = deepcopy(self._degree)
            for com, entry_degree in entry_degree_temp_dict.items():
                if entry_degree != 0:
                    continue
                # openubmc作为一个最终组件，不推送(远端没有，直接弹出)
                if com.startswith("openubmc/"):
                    self._degree.pop(com)
                    break
                cmd_tmp = cmd.replace("com_name", f"{com}")
                t = Process(target=self.conan_install, args=(cmd_tmp, com))
                t.start()
                self._process_list.append(t)
                self.work.info(f"命令 {cmd_tmp} " + Fore.GREEN + "开始" + Style.RESET_ALL)
                # 入度为0的任务构建拉起后弹出
                self._degree.pop(com)
            else:
                while self.wait_task_finished():
                    continue

        self.work.success(">>>>>>>>>>>>>>>>> 所有组件构建成功 <<<<<<<<<<<<<<<<")
        return 0


class TaskClass(Task):
    # 当前软件包的组件依赖列表
    depdencies = []

    def __init__(self, config: Config, work_name=""):
        super(TaskClass, self).__init__(config, work_name)
        self.update_path()

    @property
    def subsys_dir(self):
        subsys = os.path.join(self.config.code_path, "subsys")
        if self.config.stage == misc.StageEnum.STAGE_STABLE.value:
            subsys = os.path.join(subsys, misc.StageEnum.STAGE_STABLE.value)
        else:
            subsys = os.path.join(subsys, misc.StageEnum.STAGE_RC.value)
        return subsys

    @staticmethod
    def match_persist_type(usage):
        for item in usage:
            if item in PERSIST_TYPES:
                return PERSIST_TYPES[item]
        return None

    def find_conan_package_and_write(self, search, comps, file_handler, stage):
        if search.find("/") < 0:
            search += "/"
        for comp in comps:
            if comp.startswith(search):
                if stage == misc.StageEnum.STAGE_STABLE.value \
                    and not comp.endswith(f"/{misc.StageEnum.STAGE_STABLE.value}"):
                    err_msg = f"组件包 {comp} user/channel 配置错误, 必须以 \"{misc.StageEnum.STAGE_STABLE.value}\" 作为结尾, 终止构建"
                    raise errors.BmcGoException(err_msg)
                if stage != misc.StageEnum.STAGE_DEV.value and comp.endswith(f"/{misc.StageEnum.STAGE_DEV.value}"):
                    err_msg = f"组件包 {comp} user/channel 配置错误, 必须以 \"{stage}\" 作为结尾, 终止构建"
                    raise errors.BmcGoException(err_msg)
                self.add_new_dependencies(comp, file_handler)
                return
        raise errors.ConfigException(f"未知组件: {search}, 请检查配置 !!!")

    def update_path(self):
        # conan source folder
        self.conan_source = os.path.join(self.config.temp_path,
                                         f"conan_source_{self.config.build_type}_{self.config.stage}/openubmc")
        # conan install folder
        self.conan_install = os.path.join(self.config.build_path, "conan_install")
        # openubmc install folder
        self.openubmc_ins_dir = os.path.join(self.conan_install, "openubmc")
        # openubmc top rootfs folder
        self.top_rootfs_dir = os.path.join(self.conan_install, "rootfs")
        self.board_option = ""
        self.skip_package = False

    def mkdir_work_path(self):
        self.run_command(f"rm -rf {self.conan_source}", sudo=True)
        os.makedirs(self.conan_source, exist_ok=True)
        self.run_command(f"rm -rf {self.conan_install}", sudo=True)
        os.makedirs(self.conan_install, exist_ok=True)
        self.run_command(f"rm -rf {self.openubmc_ins_dir}", sudo=True)
        self.run_command(f"rm -rf {self.top_rootfs_dir}", sudo=True)
        self.run_command(f"rm -rf {self.config.rootfs_path}", sudo=True)
        os.makedirs(self.config.rootfs_path)

    def set_build_type(self, build_type):
        self.config.set_build_type(build_type)
        self.update_path()

    def set_stage(self, stage):
        self.config.set_stage(stage)
        self.update_path()

    def set_from_source(self, value):
        if value:
            self.config.set_from_source(True)
        else:
            self.config.set_from_source(False)

    def set_skip_package(self, value):
        if value:
            self.skip_package = True
        else:
            self.skip_package = False

    def package_dependencies_parse(self, default_component: list):
        """解析manufacture或者tosupporte配置，不同的包设置不同组件的不同编译选项
        参数:
            default_component (list): manifest的标准配置
        返回值:
            default_component (list): 依据manufacture配置处理后配置
        """
        # 默认情况下，不配置额外的options
        if self.config.manufacture_code is None and self.config.tosupporte_code == "default":
            return default_component
        if self.config.manufacture_code is not None:
            package_dependencies = self.get_manufacture_config(
                f"manufacture/{self.config.manufacture_code}/dependencies")
        elif self.config.tosupporte_code != "default":
            package_dependencies = self.get_manufacture_config(f"tosupporte/{self.config.tosupporte_code}/dependencies")
        if package_dependencies is None:
            return default_component
        components = tools.merge_dependencies(package_dependencies, default_component)
        self.debug(f"组件处理结束后: {components}")
        return components

    def add_new_dependencies(self, conan, file_handler):
        file_handler.write("  - conan: \"{}\"\n".format(conan))
        self.success(f"获取到依赖: {conan}")
        self.depdencies.append(conan)

    def merge_manifest(self):
        comps = []
        for f in os.listdir(self.subsys_dir):
            with open(os.path.join(self.subsys_dir, f)) as fp:
                yml = yaml.safe_load(fp)
            deps = yml.get('dependencies')
            for dep in deps:
                conan = dep.get(misc.CONAN)
                if conan:
                    comps.append(conan)
        self.debug("依赖列表: {}".format(comps))
        # 重建新的依赖关系
        # 从单板目录manifest.yml，与subsys/<stage>目录下的组件合并
        new_fd = os.fdopen(os.open("manifest.yml", os.O_WRONLY | os.O_CREAT,
                            stat.S_IWUSR | stat.S_IRUSR), 'w')
        new_fd.write("base:\n")
        ver = self.get_manufacture_config("base/version")

        new_fd.write(f"  version: \"{ver}@{tools.conan_user}/{misc.StageEnum.STAGE_RC.value}\"\n")
        self.info(f"包版本号: {ver}")

        new_fd.write("dependencies:\n")
        deps = self._get_dependencies_pkg()

        # 如果是打包，依赖信息调整
        deps = self.package_dependencies_parse(deps)
        # 由于manifest.yml当中有对于此的新的配置，此处将配置读出，并重新分配
        skynet_with_enable_luajit = False
        for dep in deps:
            conan = dep.get(misc.CONAN)
            if not conan:
                continue
            if conan.find("@") > 0:
                self.add_new_dependencies(conan, new_fd)
            elif conan.find("/") > 0:
                stage = self.config.stage
                if stage != misc.StageEnum.STAGE_STABLE.value:
                    stage = misc.StageEnum.STAGE_RC.value
                conan += f"@{tools.conan_user}/{stage}"
                self.add_new_dependencies(conan, new_fd)
            else:
                self.find_conan_package_and_write(conan, comps, new_fd, self.config.stage)
            options = dep.get("options", {})
            name = conan.split("/")[0]
            for key, val in options.items():
                self.board_option = self.board_option + " -o {}:{}={}".format(name, key, val)
                # skynet特殊处理：manifest.yml指定enable_luajit特性时需要覆盖用户输入
                if name == "skynet" and key == "enable_luajit":
                    self.warning(f"根据manifest.yml配置，当前产品的enable_luajit配置为{val}，忽略命令行指定的-jit参数")
                    self.config.set_enable_luajit(val)
                    skynet_with_enable_luajit = True
        # 当使能Luajit又未向skynet传递enable_luajit配置项时需要添加使能参数
        if not skynet_with_enable_luajit and self.config.enable_luajit:
            self.board_option += f" -o skynet:enable_luajit={self.config.enable_luajit}"
        self.merge_0502_default_options()
        sha256 = Tools.sha256sum(SDK_ROOT_MODULE_SYMVERS)
        self.board_option += " -o *:module_symvers={}".format(sha256)
        new_fd.close()

    def merge_0502_default_options(self):
        if self.config.manufacture_code:
            default_options_path = f"manufacture/{self.config.manufacture_code}/default_options"
            default_options = self.get_manufacture_config(default_options_path, {})
            for key, val in default_options.items():
                self.board_option += f" -o *:{key}={val}"

    def package_info_gen(self, bundle_file, dst_file):
        with open(bundle_file, "r") as fp:
            bundle = json.load(fp)['lock_bundle']
        require_list = list(bundle.keys())
        list.sort(require_list)
        package_info_list = deepcopy(require_list)
        self.run_command(f"rm -rf {dst_file}", sudo=True)
        temp_dst_file = f"{self.config.rootfs_path}/{os.path.basename(dst_file)}"
        with os.fdopen(os.open(temp_dst_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IWUSR | stat.S_IRUSR |
                               stat.S_IWGRP | stat.S_IRGRP | stat.S_IWOTH | stat.S_IROTH), 'w') as fp:
            for package in require_list:
                if "openubmc/" not in package:
                    fp.write(f"{package.split('#')[0]}\n")
                else:
                    package_info_list.remove(package)
            fp.close()
        self.run_command(f"cp -df {temp_dst_file} {dst_file}", sudo=True)
        self.run_command(f"rm -rf {temp_dst_file}", sudo=True)

    def sensitive_data_conf_gen(self, comps, dst_file):
        self.run_command(f"rm -rf {dst_file}", sudo=True)
        temp_dst_file = f"{self.config.rootfs_path}/{os.path.basename(dst_file)}"
        output = {
            "TemporaryPer": {},
            "ResetPer": {},
            "PoweroffPer": {},
            "PermanentPer": {},
            "PrimaryKeys": {}
        }
        for comp in comps:
            try:
                output = self.proc_comp(comp, output)
            except Exception as e:
                self.warning(f"分析组件 {comp} 的 model.json 失败, 失败信息:{e}")

        with os.fdopen(os.open(temp_dst_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as fp:
            json.dump(output, fp, sort_keys=True)
        self.run_command(f"cp -df {temp_dst_file} {dst_file}", sudo=True)
        self.run_command(f"rm -rf {temp_dst_file}", sudo=True)

    def proc_sensitive(self, table_type, props, table_name, output):
        for prop_key, prop_data in props.items():
            prop_name = prop_key
            if "alias" in prop_data:
                prop_name = prop_data.get("alias")
            if prop_data.get("primaryKey"):
                output[PRIMARY_KEYS][table_name] = output[PRIMARY_KEYS].get(table_name, {})
                output[PRIMARY_KEYS][table_name][prop_name] = prop_data.get("sensitive", False)
                continue
            per_type = self.match_persist_type(prop_data.get("usage", [])) or table_type
            if not per_type:
                continue
            output[per_type][table_name] = output[per_type].get(table_name, {})
            output[per_type][table_name][prop_name] = prop_data.get("sensitive", False)
        return output

    def proc_comp(self, comp, output):
        model_file = os.path.join(self.conan_install, comp, "include", "mds", "model.json")
        if not os.path.isfile(model_file):
            return output
        with open(model_file, "r") as fp:
            content = json.load(fp)
        for class_data in content.values():
            table_type = PERSIST_TYPES.get(class_data.get("tableType", ""))
            table_name = class_data.get("tableName", "")
            if not table_name or class_data.get("tableLocation") == "Local":
                continue
            class_props = [class_data.get("properties", {})]
            for intf_data in class_data.get("interfaces", {}).values():
                class_props.append(intf_data.get("properties", {}))
            for props in class_props:
                output = self.proc_sensitive(table_type, props, table_name, output)
        return output

    def calc_options(self):
        if self.config.build_type == "dt":
            options = "-s build_type=Dt"
        else:
            if self.config.build_type == "debug":
                options = "-s build_type=Debug"
            else:
                options = "-s build_type=Release"

        if self.config.enable_arm_gcov:
            options += " -o *:gcov=True"
        return options

    def install_ibmc(self):
        profile_file = os.path.join(self.tools.conan_profiles_dir, self.config.profile)
        if not os.path.isfile(profile_file):
            raise BmcGoException(f"{profile_file} 文件不存在")

        options = self.calc_options()
        append_cmd = f"-r {self.config.remote}" if self.config.remote else ""
        # 构建前删除锁文件
        if os.path.isfile(IBMC_LOCK_FILE):
            os.unlink(IBMC_LOCK_FILE)
        # 依据选项生成openubmc.lock和openubmc.bundle文件
        cmd = f"conan lock create conanfile.py --lockfile-out=openubmc.lock -pr={self.config.profile} "
        cmd += f"-pr:b profile.dt.ini {append_cmd} {options} {self.board_option} --build"
        if self.config.from_source:
            self.run_command(cmd)
            cmd = f"conan install com_name -if={self.conan_install} --lockfile=openubmc.lock "
            cmd += f"{append_cmd} --build=com_name"
        else:
            cmd += "=missing"
            self.run_command(cmd)
            cmd = f"conan install com_name -if={self.conan_install} --lockfile=openubmc.lock --build=missing "
            cmd += f"{append_cmd}"
        self.run_command("conan lock bundle create openubmc.lock --bundle-out=openubmc.bundle")
        # 优化缓存构建时长：非源码构建时先尝试直接构建一次，失败时构建所有依赖组件
        ret = -1
        install_cmd = f"conan install conanfile.py --lockfile=openubmc.lock -if={self.conan_install} -g deploy"
        if not self.config.from_source:
            self.info(">>>>>>>>>>>>> 尝试直接安装 >>>>>>>>>>>>>>>>>>")
            ret = 0
            try:
                self.run_command(install_cmd, command_echo=True, warn_log="缓存安装失败，可能缺少某个依赖项制品，开始从源码构建缺失的软件包")
            except Exception:
                ret = -1
        if ret != 0:
            bundle_parse = ConanLockParse("openubmc.bundle", self)
            bundle_parse.conan_parallel_build(cmd, self.config.build_path)
            self.run_command(install_cmd, command_echo=True)
        shutil.copyfile(IBMC_LOCK_FILE, f"{self.conan_install}/conan.lock")
        # 检查使用到的组件是否都在单板目录 manifest.yml 中配置了
        component_check = ComponentVersionCheck(manifest_yml="manifest.yml", ibmc_lock=IBMC_LOCK_FILE)
        component_check.run()
        self.clean_luac_out()

    def deploy(self):
        src = os.path.join(self.config.code_path, "conan_index/openubmc")
        shutil.copytree(src, self.conan_source, dirs_exist_ok=True)
        openubmc_dir = os.path.join(self.conan_source, "all")
        self.chdir(openubmc_dir)
        # 复制manifest.yml文件
        self.merge_manifest()
        # 下载组件构建脚本
        ComponentHelper.download_recipes(self.depdencies, self.tools, self.config.remote_list)
        # 下载skynet
        self.install_luac_or_luajit()

        # 复制全局定制rootfs到conan install目录
        top_rootfs = os.path.join(self.config.code_path, "rootfs")
        self.info("复制 {} 到 conan 安装目录".format(top_rootfs))
        self.run_command(f"rm -rf {self.top_rootfs_dir}")
        self.run_command(f"cp -rf {top_rootfs} {self.top_rootfs_dir}")

        version_path = self.top_rootfs_dir
        # 复制单板目录下的权限配置和rootfs文件
        rootfs_dir = os.path.join(self.config.board_path, "rootfs")
        if os.path.isdir(rootfs_dir):
            self.run_command(f"rm -rf {self.openubmc_ins_dir}")
            self.run_command(f"cp -rf {rootfs_dir} {self.openubmc_ins_dir}")
        else:
            os.makedirs(self.openubmc_ins_dir)

        if os.path.isfile(f"{self.openubmc_ins_dir}/etc/version.json"):
            version_path = self.openubmc_ins_dir
        self.config.version_conf(f"{version_path}/etc/version.json")
        self.config.show_version_conf(f"{version_path}/etc/version.json")
        per_file = os.path.join(self.config.board_path, "permissions.ini")
        if os.path.isfile(per_file):
            shutil.copy(per_file, self.openubmc_ins_dir)

        self.install_ibmc()

    def clean_luac_out(self):
        # 清理冗余文件luac.out
        self.chdir(self.conan_install)
        for root, _, files in os.walk("."):
            for file in files:
                if "luac.out" == file:
                    os.remove(os.path.join(root, file))

    def link_recursive_deal(self, file_name, ownership):
        self.run_command(f"chown -h {ownership} {file_name}", sudo=True)
        if os.path.islink(os.readlink(file_name)):
            self.link_recursive_deal(os.readlink(file_name), ownership)

    def package_lock(self):
        self.chdir(self.conan_install)
        inner_path = self.config.inner_path
        os.makedirs(inner_path, exist_ok=True)
        self.run_command(f'cp -f conan.lock {os.path.join(inner_path, f"package_{self.config.board_name}.lock")}')
        self.run_command(f'cp -f conan.lock {os.path.join(self.config.output_path, f"package.lock")}')

    def copy_components(self, comps: list, profile: Profile):
        # 优先处理rootfs
        p = CopyComponent(self, "rootfs", profile)
        p.run()
        # 打印组件清单
        self.info(f"组件列表: {comps}")
        pools = []
        for comp in comps:
            p = CopyComponent(self, comp, profile)
            p.start()
            pools.append(p)

        while pools:
            time.sleep(0.01)
            for p in pools:
                if p.is_alive():
                    continue
                if p.exitcode is not None and p.exitcode != 0:
                    raise errors.BmcGoException(f"复制组件 ({p.comp}) 失败, 退出码: {p.exitcode}")
                pools.remove(p)
        # 最后处理openubmc
        p = CopyComponent(self, "openubmc", profile)
        p.run()

    def package(self):
        self.chdir(self.conan_install)
        self.run_command(f"sudo rm -rf {self.config.rootfs_path}")
        os.makedirs(self.config.rootfs_path)
        profile, _ = self.get_profile_config()
        comps = []
        for dirname in os.listdir("."):
            if not os.path.isdir(dirname):
                continue
            if dirname != "rootfs" and dirname != "openubmc":
                comps.append(dirname)
        
        self.copy_components(comps, profile)

        # 运行组件定制化文件
        for comp in comps:
            cust = os.path.join(self.conan_install, comp, "include", "customization.py")
            if not os.path.isfile(cust):
                continue
            self.info(f"开始执行 {comp}/include/customization.py")
            post = ComponentPost(self.config, os.path.join(self.conan_install, comp), profile)
            post.post_work(self.config.rootfs_path, "post_image")

        self.chdir(self.config.rootfs_path)
        self.package_info_gen(f"{self.conan_source}/all/openubmc.bundle", "etc/package_info")
        self.sensitive_data_conf_gen(comps, "opt/bmc/trust/sensitive_data.json")
        if os.path.isfile("permissions.ini"):
            os.unlink("permissions.ini")

    def prepare_luac_for_luacov(self, luac):
        """
        对luac进行打桩，统计覆盖率场景lua文件如果是字节码将无法统计到具体的行覆盖信息
        """
        luac_cov = f"{self.conan_home}/bin/luac.c"
        with os.fdopen(os.open(luac_cov, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as f:
            luac_str = "int main(int argc, char* argv[]) {return 0;}"
            f.write(luac_str)

        if os.path.isfile(luac_cov):
            self.run_command(f"gcc {luac_cov} -o {luac}", sudo=True)
            self.run_command(f"rm {luac_cov}", sudo=True)

    def install_luac_or_luajit(self):
        conan_bin = os.path.join(self.conan_home, "bin")
        if not os.path.isdir(conan_bin):
            os.makedirs(conan_bin)

        ld_library_path = conan_bin + ":" + os.environ.get("LD_LIBRARY_PATH", "")
        os.environ["LD_LIBRARY_PATH"] = ld_library_path
        path = conan_bin + ":" + os.environ.get("PATH", "")
        os.environ["PATH"] = path
        os.environ["LUA_PATH"] = f"{conan_bin}/?.lua"

        if self.config.build_type == "dt":
            return
        luajit_pkg = None
        for dep in self.depdencies:
            if dep.startswith("luajit/"):
                luajit_pkg = dep
        if luajit_pkg is None:
            raise errors.BmcGoException("luajit是必要依赖，未找到正确的luajit包，请确保manifest.yml正确配置luajit")
        luajit_flag = luajit_pkg.split("@")[0].replace("/", "_")
        luajit_flag = os.path.join(conan_bin, luajit_flag)
        luac = f"{conan_bin}/luajit"
        luac_back = f"{conan_bin}/luajit_back"

        self.config.conan_parallel_lock.acquire()
        # luajit版本一致且luac_back/luajit_back存在时赋权即可
        if os.path.isfile(luajit_flag) and os.path.isfile(luac_back):
            self.link(luac_back, luac)
        else:
            Tools.clean_conan_bin(conan_bin)
            append_cmd = f"-r {self.config.remote}" if self.config.remote else ""
            self.run_command(f"conan install {luajit_pkg} {append_cmd}" +
                             " -pr profile.dt.ini -if=temp/.deploy -g deploy")
            cmd = f"cp temp/.deploy/luajit/usr/bin/luajit {conan_bin}"
            self.run_command(cmd)
            cmd = f"cp temp/.deploy/luajit/usr/lib64/liblua.so {conan_bin}"
            self.run_command(cmd)
            cmd = f"cp -r temp/.deploy/luajit/usr/bin/jit {conan_bin}"
            self.run_command(cmd)
            self.link(luac, luac_back)
        # 仅在覆盖率使能场景下，对luac进行打桩
        if self.config.enable_arm_gcov:
            self.prepare_luac_for_luacov(luac)
        os.chmod(luac, stat.S_IRWXU)
        luajit2luac = shutil.which("luajit2luac.sh")
        cmd = f"cp {luajit2luac} {conan_bin}/luac"
        self.run_command(cmd)
        pathlib.Path(luajit_flag).touch(0o600, exist_ok=True)
        self.config.conan_parallel_lock.release()

    def run(self):
        self.mkdir_work_path()
        self.tools.clean_locks()
        self.deploy()
        self.package_lock()
        if not self.skip_package:
            self.package()

    def _get_dependencies_pkg(self):
        deps = self.get_manufacture_config('dependencies', [])
        if self.config.enable_arm_gcov:
            dt_deps = self.get_manufacture_config("dt_dependencies", [])
            for dep in dt_deps:
                deps.append(dep)
        # 只有非CI场景的个人构建支持调测包
        if self.config.enable_debug_model and "CLOUD_BUILD_RECORD_ID" not in os.environ:
            dt_deps = self.get_manufacture_config("debug_dependencies", [])
            for dep in dt_deps:
                deps.append(dep)
        return deps
