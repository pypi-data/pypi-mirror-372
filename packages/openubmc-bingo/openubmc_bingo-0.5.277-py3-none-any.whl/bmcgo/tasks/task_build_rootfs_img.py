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
"""
功 能：buildimg_ext4脚本，该脚本 make ext4 image
版权信息：华为技术有限公司，版本所有(C) 2019-2020
"""

import os
import shutil
import json
import stat
import time
import subprocess
import tempfile
from multiprocessing import Process

from git import Repo

from bmcgo.tasks.task import Task
from bmcgo.utils.config import Config
from bmcgo.utils.combine_json_schemas import CombineJsonSchemas
from bmcgo.utils.mapping_config_patch import MappingConfigPatch
from bmcgo import errors, misc


class MakeZeroImageProcess(Process):
    def __init__(self, work, bs_count, img_path):
        super().__init__()
        self.work = work
        self.bs_count = bs_count
        self.img_path = img_path

    def run(self):
        self.work.work_name = os.path.basename(self.img_path)
        cmd = f"dd if=/dev/zero of={self.img_path} bs=4096 count={self.bs_count}"
        self.work.run_command(cmd)


class TaskClass(Task):
    def __init__(self, config: Config, work_name=""):
        super(TaskClass, self).__init__(config, work_name)
        self.rootfs_img_process = None
        self.datafs_img_process = None
        self.buildimg_dir = None
        self.rtos_rootfs = None
        self.rtos_datafs = None
        self.mnt_datafs = None
        self.rootfs_img_path = f"{self.config.work_out}/rootfs_BMC.img"
        self.datafs_img_path = f"{self.config.hpm_build_dir}/datafs_{self.config.board_name}.img"

    def set_evn(self):
        self.buildimg_dir = self.config.buildimg_dir
        self.tools.check_path(self.buildimg_dir)
        shutil.rmtree(f"{self.buildimg_dir}/rtos_with_driver", ignore_errors=True)
        # rootfs解压目录
        self.rtos_rootfs = f"{self.buildimg_dir}/rtos_with_driver/rootfs"
        self.rtos_datafs = f"{self.rtos_rootfs}/data"
        # 镜像挂载点
        self.mnt_datafs = f"{self.buildimg_dir}/mnt_datafs"
        self.run_command(f"rm -rf {self.mnt_datafs}", sudo=True)
        self.run_command(f"mkdir {self.mnt_datafs}", sudo=True)
        self.tools.check_path(self.rtos_rootfs)

    def component_cust_conf(self):
        self.chdir(self.rtos_rootfs)
        self._component_cust_action("post_rootfs")
        self.run_command(f"rm -rf {self.rtos_rootfs}/include", sudo=True, command_echo=False)
        self.run_command(f"rm -rf {self.rtos_rootfs}/usr/include", sudo=True, command_echo=False)

    def component_swbom(self):
        os.chdir(self.rtos_rootfs)
        swbom = f"{self.buildimg_dir}/swbom"
        with os.fdopen(os.open(swbom, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as fp:
            if self.config.build_type == "debug":
                fp.write("rootfs_rw\n")
            elif self.config.build_type == "release":
                fp.write("rootfs_ro\n")
            fp.close()
        self.run_command(f"cp -df {swbom} etc/swbom", sudo=True)
        self.run_command(f"rm -rf {swbom}", sudo=True)

    def prepare_config_for_luacov(self):
        """
        整包覆盖率统计: 将luacov路径增加到config.cfg, 同时将preload指定为打桩的app_preloader_luacov.lua
        """
        self.info("准备 config.cfg 配置文件, 配置 luacov 路径")
        test_config = os.path.join(self.rtos_rootfs, "opt/bmc/libmc/config.cfg")

        with open(test_config, "r") as f:
            # 插入luacov搜索路径
            search_str = '    self:add_lua_path(self.apps_root .. "?/init.lua")\n'
            insert_str = '    self:add_lua_path(self.bmc_root .. "lualib/luacov/?.lua")\n'
            lines = f.readlines()
            if insert_str in lines:
                return
            insert_index = lines.index(search_str)
            lines.insert(insert_index + 1, insert_str)
            # 让preload引用打桩的app_preloader_luacov.lua
            search_str = '    preload = self.preload or (self.libmc_root .. "lualib/mc/app_preloader.lua")\n'
            replace_str = '    preload = self.preload or (self.libmc_root .. "lualib/mc/app_preloader_luacov.lua")\n'
            lines = [replace_str if line == search_str else line for line in lines]
            write_str = "".join(lines)
        with os.fdopen(os.open(test_config, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as f:
            f.write(write_str)

    def prepare_preloader_for_luacov(self):
        """
        整包覆盖率统计: 通过app_preloader使得所有组件引用luacov
        """
        self.info("预加载 luacov")
        app_preloader_luacov = os.path.join(self.rtos_rootfs, "opt/bmc/libmc/lualib/mc/app_preloader_luacov.lua")

        with os.fdopen(os.open(app_preloader_luacov, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as fp:
            write_str = "require 'mc.app_preloader'\nrequire 'luacov'\n "
            fp.write(write_str)

    def prepare_coverage_config(self):
        """
        整包覆盖率统计: 修改luacov覆盖率配置文件
        """
        self.info("准备覆盖率配置")
        coverage_config = os.path.join(self.rtos_rootfs, "opt/bmc/lualib/luacov/luacov/defaults.lua")
        coverage_path = os.path.join("/", "data/")
        with open(coverage_config, "r") as f:
            lines = f.readlines()
            # 修改输出数据路径
            search_str = '  statsfile = "luacov.stats.out",\n'
            replace_str = f'  statsfile = "{coverage_path}luacov.stats.out",\n'
            lines = [replace_str if line == search_str else line for line in lines]
            # 使能HTML形式报告
            search_str = '  reportfile = "luacov.report.out",\n'
            replace_str = f'  reportfile = "{coverage_path}luacov.report.html",\n'
            insert_str = '  reporter   = "html",\n'
            lines = [replace_str if line == search_str else line for line in lines]
            insert_index = lines.index(replace_str)
            lines.insert(insert_index + 1, insert_str)
            # 使能统计未运行到的代码
            search_str = '  includeuntestedfiles = false,\n'
            replace_str = '  includeuntestedfiles = true,\n'
            lines = [replace_str if line == search_str else line for line in lines]
            write_str = "".join(lines)
        with os.fdopen(os.open(coverage_config, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as fp:
            fp.write(write_str)

    def modify_maca_check_for_luacov(self):
        """
        保证服务正常：luacov工具会降低各组件服务运行速度，需要修改maca启动检查和健康检查避免服务重启
        """
        self.info("修改 maca 检查配置文件")
        maca_startup_path = os.path.join(self.rtos_rootfs, "opt/bmc/apps/maca/lualib/app_mgmt/monitor/startup/init.lua")
        with open(maca_startup_path, "r") as f:
            lines = f.readlines()
            # 延长maca启动检查事件
            search_str1 = 'local STARTUP_CHECK_TIMEOUT<const> = 2\n'
            replace_str1 = 'local STARTUP_CHECK_TIMEOUT<const> = 30\n'
            lines = [replace_str1 if line == search_str1 else line for line in lines]
            search_str2 = 'local MAX_STARTUP_CHECK_TIMES<const> = 6\n'
            replace_str2 = 'local MAX_STARTUP_CHECK_TIMES<const> = 200\n'
            lines = [replace_str2 if line == search_str2 else line for line in lines]
            search_str3 = 'local MAX_ABNORMAL_RESET_TIMES<const> = 10\n'
            replace_str3 = 'local MAX_ABNORMAL_RESET_TIMES<const> = 200\n'
            lines = [replace_str3 if line == search_str3 else line for line in lines]
            write_str = "".join(lines)
        with os.fdopen(os.open(maca_startup_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as fp:
            fp.write(write_str)

        maca_health_path = os.path.join(self.rtos_rootfs, "opt/bmc/apps/maca/lualib/app_mgmt/monitor/health/init.lua")
        with open(maca_health_path, "r") as f:
            lines = f.readlines()
            # 取消maca健康检查
            search_str = '        self:check_components_health()\n'
            replace_str = '        -- self:check_components_health()\n'
            lines = [replace_str if line == search_str else line for line in lines]
            write_str = "".join(lines)
        with os.fdopen(os.open(maca_health_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as fp:
            fp.write(write_str)

    # 支持配置导入导出schema文件根据产品不同配置进行定制化
    def schema_custom(self):
        self.info("开始自定义模式")
        schema_path = os.path.join(self.rtos_rootfs, "opt/bmc/profile_schema")
        # 产品差异化shcema路径，由vpd仓打包到指定路径下
        product_schema_path = os.path.join(self.rtos_rootfs, "opt/bmc/profile_schema/product")
        # 整合schema, 生成默认配置
        combine_schemas = CombineJsonSchemas(self.config, schema_path)
        combine_schemas.gen_default_settings()
        # 差异化处理完schema文件之后已完成schema整合，不在需要产品schema目录(强制删除时即使不存在也不会出错)
        self.run_command(f"rm -rf {product_schema_path}", sudo=True)

    # 支持映射配置文件根据产品差异进行打补丁
    def mapping_config_patch(self):
        self.info("开始根据配置映射打补丁")
        for item in ["redfish", "web_backend", misc.CLI, "snmp"]:
            config_path = os.path.join(self.rtos_rootfs, "opt/bmc/apps", item, "interface_config")
            if not os.path.isdir(config_path):
                continue
            patch_work = MappingConfigPatch(self.config, config_path=config_path)
            patch_work.run()

    def scan_mds_dir(self, mds_dir):
        for mds_file in os.scandir(mds_dir):
            if not mds_file.is_file() or not mds_file.name.endswith(".json"):
                continue
            mds_file_permission = self.tools.get_file_permission(mds_file.path)
            self.run_command(f"chmod 777 {mds_file.path}", sudo=True, command_echo=False)
            self.remove_space_in_json_file(mds_file.path)
            self.run_command(f"chmod {mds_file_permission} {mds_file.path}", sudo=True, command_echo=False)

    def remove_space_in_json_file(self, file_path):
        try:
            with open(file_path, "r") as fp:
                content = json.load(fp)
            with os.fdopen(os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                stat.S_IWUSR | stat.S_IRUSR), 'w') as fp:
                json.dump(content, fp, separators=(',', ':'))
        except Exception as e:
            raise Exception(f"{file_path} 文件解析失败: {e}") from e

    def trim_mds_and_sr_json(self):
        self.info("移除 mds 文件和 sr 文件中的空格")
        apps_dir = os.path.join(self.rtos_rootfs, "opt/bmc/apps")
        if os.path.isdir(apps_dir):
            apps_dir_permission = self.tools.get_file_permission(apps_dir)
            self.run_command(f"chmod 777 {apps_dir}", sudo=True, command_echo=False)
            for app_dir in os.scandir(apps_dir):
                mds_dir = os.path.join(app_dir.path, "mds")
                if not app_dir.is_dir() or not os.path.isdir(mds_dir):
                    continue
                mds_dir_permission = self.tools.get_file_permission(mds_dir)
                self.run_command(f"chmod 777 {mds_dir}", sudo=True, command_echo=False)
                self.scan_mds_dir(mds_dir)
                self.run_command(f"chmod {mds_dir_permission} {mds_dir}", sudo=True, command_echo=False)
            self.run_command(f"chmod {apps_dir_permission} {apps_dir}", sudo=True, command_echo=False)

        sr_dir = os.path.join(self.rtos_rootfs, "opt/bmc/sr")
        if not os.path.isdir(sr_dir):
            return
        sr_dir_permission = self.tools.get_file_permission(sr_dir)
        self.run_command(f"chmod 777 {sr_dir}", sudo=True, command_echo=False)
        for sr_file in os.scandir(sr_dir):
            if not sr_file.is_file() or not sr_file.name.endswith(".sr"):
                continue
            sr_file_permission = self.tools.get_file_permission(sr_file.path)
            self.run_command(f"chmod 777 {sr_file.path}", sudo=True, command_echo=False)
            self.remove_space_in_json_file(sr_file.path)
            self.run_command(f"chmod {sr_file_permission} {sr_file.path}", sudo=True, command_echo=False)
        self.run_command(f"chmod {sr_dir_permission} {sr_dir}", sudo=True, command_echo=False)

    def merge_and_converge_process(self, sr_dir, sr_file, csr_version):
        try:
            sr_file_base_name, _ = os.path.splitext(sr_file.name)
            with open(sr_file.path, "r") as fp:
                sr_data = json.load(fp)
            csr_version[sr_file_base_name] = {
                "FormatVersion": str(sr_data["FormatVersion"]),
                "DataVersion": str(sr_data["DataVersion"]),
                "Merged": True
            }
        except Exception as e:
            raise Exception(f"{sr_file.path} 获取sr文件版本号失败: {e}") from e
        try:
            soft_sr_file_name = sr_file_base_name + '_soft.sr'
            soft_sr_file_path = os.path.join(sr_dir, soft_sr_file_name)
            if not os.path.exists(soft_sr_file_path):
                return
            soft_sr_file_permission = self.tools.get_file_permission(soft_sr_file_path)
            self.run_command(f"chmod 777 {soft_sr_file_path}", sudo=True, command_echo=False)
            with open(soft_sr_file_path, "r") as fp:
                soft_sr_data = json.load(fp)
        except Exception as e:
            raise Exception(f"{soft_sr_file_path} soft sr文件解析失败: {e}") from e
        try:
            for key, value in sr_data['Objects'].items():
                if key in soft_sr_data['Objects']:
                    sr_data['Objects'][key] = {**value, **soft_sr_data['Objects'][key]}
            sr_data['Objects'] = {**soft_sr_data['Objects'], **sr_data['Objects']}
            self.run_command(f"chmod {soft_sr_file_permission} {soft_sr_file_path}", sudo=True, command_echo=False)
        except Exception as e:
            raise Exception(f"{sr_file.path} 文件合并失败: {e}") from e
        try:
            with os.fdopen(os.open(sr_file.path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                stat.S_IWUSR | stat.S_IRUSR), 'w') as fp:
                json.dump(sr_data, fp, separators=(',', ':'))
        except Exception as e:
            raise Exception(f"{sr_file.path} 文件覆盖失败: {e}") from e

    def merge_sr_and_converge_version(self, csr_version):
        self.info("合并 sr 和 soft sr, 汇聚 sr 文件中的版本号")
        sr_dir = os.path.join(self.rtos_rootfs, "opt/bmc/sr")
        if not os.path.isdir(sr_dir):
            return
        sr_dir_permission = self.tools.get_file_permission(sr_dir)
        self.run_command(f"chmod 777 {sr_dir}", sudo=True, command_echo=False)
        for sr_file in os.scandir(sr_dir):
            if not sr_file.is_file() or not sr_file.name.endswith(".sr") or sr_file.name.endswith("_soft.sr"):
                continue
            sr_file_permission = self.tools.get_file_permission(sr_file.path)
            self.run_command(f"chmod 777 {sr_file.path}", sudo=True, command_echo=False)
            self.merge_and_converge_process(sr_dir, sr_file, csr_version)
            self.run_command(f"chmod {sr_file_permission} {sr_file.path}", sudo=True, command_echo=False)
        self.run_command(f"chmod {sr_dir_permission} {sr_dir}", sudo=True, command_echo=False)

    def create_csr_version_file(self, csr_version):
        self.info("生成 csr_version.json 文件")
        csr_version = sorted(csr_version.items(), key=lambda item: item[0])
        csr_version = dict(csr_version)
        sr_dir = os.path.join(self.rtos_rootfs, "opt/bmc/sr")
        if not os.path.isdir(sr_dir):
            return
        sr_dir_permission = self.tools.get_file_permission(sr_dir)
        self.run_command(f"chmod 777 {sr_dir}", sudo=True, command_echo=False)
        csr_version_file_path = os.path.join(sr_dir, "csr_version.json")
        try:
            with os.fdopen(os.open(csr_version_file_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                stat.S_IWUSR | stat.S_IRUSR), 'w') as fp:
                json.dump(csr_version, fp, separators=(',', ':'))
        except Exception as e:
            raise Exception(f"{csr_version_file_path} 文件生成失败: {e}") from e
        self.run_command(f"chmod {sr_dir_permission} {sr_dir}", sudo=True, command_echo=False)
        self.run_command(f"chmod 440 {csr_version_file_path}", sudo=True, command_echo=False)

    def make_strip_cmd(self, file_list):
        work_path = os.getcwd()
        relative_path = os.path.relpath(work_path, self.rtos_rootfs)
        base = ["sudo find {} -type f ".format(relative_path)]
        base.append("grep -v \"/share/\"")
        base.append("grep -v \".json$\"")
        base.append("grep -v \"\.lua$\"")
        base.append("grep -v \".sh$\"")
        base.append("grep -v \".png$\"")
        base.append("grep -v \".jpg$\"")
        base.append("grep -v \".jpeg$\"")
        base.append("grep -v \".html$\"")
        base.append("grep -v \".js$\"")
        base.append("grep -v \".css$\"")
        base.append("grep -v \".svg$\"")
        base.append("grep -v \".sr$\"")
        base.append("grep -v \".conf$\"")
        base.append("grep -v \".service$\"")
        base.append("grep -v \".cfg$\"")
        base.append("grep -v \".gif$\"")
        base.append("grep -v \".ttf$\"")
        base.append("grep -v \".target$\"")
        if self.config.build_type == "debug":
            # so库一般带有版本号，此处不能注明具体的版本号，否则可能导致版本变更时不能正确strip
            not_striped_list = ["rootfs/opt/bmc", "libclp_common.so", "libclp_private_cmd.so", "libcutils.so"]
            not_striped_list += ["libfilehook.so", "liblogging.so", "liblua.so", "libmctp.so", "libnsm_kmc.so"]
            not_striped_list += ["libplatform.so", "libsnmp.so", "libsoc_adapter.so", "libuip.so"]
            for file in not_striped_list:
                base.append("grep -v \"{}\"".format(file))
        base.append("sudo xargs -P 0 -I {{}} file {{}}".format(file_list))
        base.append("grep 'not stripped'")
        base.append("awk -F: '{{print $1}}'")
        base.append("grep -v '.ko$'")
        return base

    def build_common_fs(self):
        """
        构建rootfs根文件系统，文件存在self.buildimg_dir目录下
        """
        self.chdir(self.buildimg_dir)
        self.info("开始构建 rootfs ...")

        rtos_tar = os.path.join(self.config.sdk_path, "rtos.tar.gz")
        sdk_tar = os.path.join(self.config.sdk_path, "hi1711sdk.tar.gz")
        # 解压SDK
        self.run_command(f"rm -rf {self.rtos_rootfs}", sudo=True)
        self.run_command(f"tar --xattrs --xattrs-include=* -xf {rtos_tar}", sudo=True)
        self.run_command(f"sudo chown -R 0:0 {self.rtos_rootfs}", sudo=True)
        self.info("拷贝RTOS提供的mke2fs.conf配置文件覆盖本地环境中的/etc/mke2fs.conf文件, 确保mkfs.ext4使用该配置文件")
        self.run_command(f"cp -f {self.rtos_rootfs}/etc/mke2fs.conf /etc/mke2fs.conf", sudo=True)
        self.run_command(f"rm -rf {self.rtos_rootfs}/etc/ssh", sudo=True)
        self.run_command(f"rm -rf {self.rtos_rootfs}/usr/share/doc/openubmc", sudo=True)

        # 记录代码分支和提交节点
        self.create_bmc_release()

        # 解压SDK并复制到指定位置
        sdk_path = os.path.join(self.buildimg_dir, "sdk")
        self.run_command(f"rm -rf {sdk_path}", sudo=True)
        self.run_command(f"mkdir -p {sdk_path}", sudo=True)
        self.run_command("tar -xf {} -C {}".format(sdk_tar, sdk_path), sudo=True)
        ko_path = f"{self.rtos_rootfs}/lib/modules/"
        self.run_command("cp -dfr {}/. {}".format(sdk_path, ko_path), sudo=True)

        self.chdir(self.config.work_out)
        self.copy_rtos_modules()

        for cus in self.customization:
            cus.rootfs_cust(self.rtos_rootfs)
        # strip非ko文件
        file_list = os.path.join(self.buildimg_dir, "no_striped.filelist")
        base = self.make_strip_cmd(file_list)
        strip = os.path.join(self.config.cross_compile_install_path, "bin", self.config.strip)
        self.pipe_command(base, file_list)
        if os.path.isfile(file_list) and not self.config.enable_arm_gcov:
            cmd = ["cat {}".format(file_list), "sudo xargs -P 0 -I {{}} {} -R .comment {{}}".format(strip)]
            self.pipe_command(cmd)
            cmd = ["cat {}".format(file_list), "sudo xargs -P 0 -I {{}} {} {{}}".format(strip)]
            self.pipe_command(cmd)
        # 删除.a文件
        cmd = ["sudo find {} -type f -name *.a".format(self.rtos_rootfs), "sudo xargs -P 0 -i{{}} rm {{}}"]
        self.pipe_command(cmd)
        self.build_cfg_fs()
        # 使能覆盖率统计
        if self.config.enable_arm_gcov:
            self.modify_maca_check_for_luacov()
            self.prepare_config_for_luacov()
            self.prepare_preloader_for_luacov()
            self.prepare_coverage_config()

    def create_bmc_release(self):
        bmc_release_path = f"{self.rtos_rootfs}/etc/bmc-release"
        temp_bmc_release_file = tempfile.NamedTemporaryFile()
        repo = Repo(self.config.code_root)
        current_commit = repo.head.commit
        commit_content_item = f"COMMIT={current_commit.hexsha}\nCOMMIT_DATE={current_commit.committed_datetime}\n"
        try:
            commit_head = f'BRANCH={repo.active_branch.name}'
        except Exception as e:
            # 获取当前提交的所有标签
            tags = repo.tags
            # 查找与当前提交匹配的标签
            current_commit_tag = ""
            for tag in tags:
                if tag.commit == current_commit:
                    current_commit_tag = tag
                    break
            commit_head = f'TAG={current_commit_tag}'
        commit_content = f"{commit_head}\n{commit_content_item}"
        with os.fdopen(os.open(temp_bmc_release_file.name, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IWUSR |
                                stat.S_IRUSR | stat.S_IWGRP | stat.S_IRGRP | stat.S_IWOTH | stat.S_IROTH),
                                'w') as file:
            file.write(commit_content)
        self.run_command(f"cp {temp_bmc_release_file.name} {bmc_release_path}", sudo=True, command_echo=False)
        self.run_command(f"chmod 644 {bmc_release_path}", sudo=True)

    def copy_rtos_modules(self):
        self.run_command("cp -af {}/. {}".format(self.config.rootfs_path, self.rtos_rootfs), sudo=True)
        cp_cmd = "cp -df {} {}"
        self.run_command(cp_cmd.format("/opt/hcc_arm64le/aarch64-target-linux-gnu/lib64/libgcc_s.so.1",
                                               f"{self.rtos_rootfs}/lib64/libgcc_s.so.1"), sudo=True)
        self.run_command(cp_cmd.format("/opt/hcc_arm64le/aarch64-target-linux-gnu/lib64/libstdc++.so.6",
                                               f"{self.rtos_rootfs}/lib64/libstdc++.so.6"), sudo=True)
        self.run_command("mkdir -p {}".format(f"{self.rtos_rootfs}/opt/pme/upgrade"), sudo=True)
        self.run_command(cp_cmd.format(f"{self.config.code_path}/manufacture/misc/pme_profile_en.dat",
                                               f"{self.rtos_rootfs}/opt/pme/upgrade/pme_profile_en"), sudo=True)
        self.run_command(cp_cmd.format(f"{self.config.code_path}/manufacture/misc/datatocheck_upgrade.dat",
                                               f"{self.rtos_rootfs}/opt/pme/upgrade/datatocheck_upgrade.dat"),
                                               sudo=True)
        self.run_command("chmod 755 {}".format(f"{self.rtos_rootfs}/lib64/libgcc_s.so.1"), sudo=True)
        self.run_command("chmod 755 {}".format(f"{self.rtos_rootfs}/lib64/libstdc++.so.6"), sudo=True)
        self.run_command("chmod 400 {}".format(f"{self.rtos_rootfs}/opt/pme/upgrade/pme_profile_en"), sudo=True)
        self.run_command("chmod 400 {}".format(f"{self.rtos_rootfs}/opt/pme/upgrade/datatocheck_upgrade.dat"),
                          sudo=True)

    def make_datafs_img(self):
        tar_path = f"{self.rtos_rootfs}/usr/upgrade/datafs.tar.gz"
        self.run_command(f"mkdir -p {self.rtos_datafs}", sudo=True)
        self.run_command(f"mkdir -p {os.path.dirname(tar_path)}", sudo=True)

        # 自定义配置
        for cus in self.customization:
            cus.datafs_cust(self.rtos_datafs)

        # 打包datafs.tar.gz
        self.chdir(self.rtos_rootfs)

        # ! 制作datafs img镜像，供work_buildpkg_ext4.py使用
        datafs_mount_path = f"{self.config.build_path}/mnt_datafs/"
        self.run_command(f"rm -rf {datafs_mount_path}", sudo=True)
        self.run_command(f"mkdir -p {datafs_mount_path}", sudo=True)

        # 复制所有文件到挂载目录
        self.run_command(f"cp -a {self.rtos_datafs}/. {datafs_mount_path}", ignore_error=True, sudo=True)
        self.run_command(f"chown 0:0 {datafs_mount_path}", sudo=True)
        self.tools.make_img(self.datafs_img_path, datafs_mount_path, "1024")
        self.run_command(f"rm -rf {datafs_mount_path}", sudo=True)

        subprocess.run(f"LD_PRELOAD= sudo LD_PRELOAD=${{LD_PRELOAD}} -E\
            /usr/bin/tar --format=gnu -czvf {tar_path} ./data/", shell=True, check=True)
        self.run_command(f"chmod 440 {tar_path}", sudo=True)
        self.run_command(f"chown 0:0 {tar_path}", sudo=True)
        return

    def make_rootfs_img(self):
        self.make_datafs_img()

        self.component_cust_conf()

        # 差异化处理装备定制化schema文件
        self.schema_custom()

        # 映射配置机型差异补丁
        self.mapping_config_patch()

        # 合并sr和soft sr，汇聚csr version
        csr_version = {}
        self.merge_sr_and_converge_version(csr_version)

        # 生成csr_version文件
        self.create_csr_version_file(csr_version)

        # 去除mds和sr文件中的空格和换行，节省空间和内存
        self.trim_mds_and_sr_json()

        self.component_swbom()
        self.run_command(f"sudo cp -a {self.rtos_rootfs}/. {self.mnt_datafs}/")
        if self.config.build_type == 'debug':
            for cus in self.customization:
                cus.rootfs_debug_cust(self.mnt_datafs)
        elif self.config.build_type == 'release':
            for cus in self.customization:
                cus.rootfs_release_cust(self.mnt_datafs)

        for cus in self.customization:
            cus.rootfs_common(self.mnt_datafs)
        self.chdir(self.config.work_out)
        self.tools.make_img(self.rootfs_img_path, self.mnt_datafs, "376")

        self.run_command(f"zerofree -v {self.rootfs_img_path}")
        self.run_command(f"get_img_parma_area.sh {self.rootfs_img_path}")

    def build_cfg_fs(self):
        self.chdir(self.rtos_rootfs)
        self.info(f"开始制作 {self.config.board_name} cfgfs ...")

        self.run_command(f"chmod o+w {self.rtos_rootfs}/etc/profile", sudo=True)
        ps1_replace = 'PS1="\\\\\[\\\\033[32m\\\\\]~ \\\\w\\\[\\\\033[m\\\\\] \\\\\\\\\$ "'
        self.run_command(f"sed -i 's/^PS1=.*$/{ps1_replace}/' {self.rtos_rootfs}/etc/profile", sudo=True)

        f = open(f"{self.rtos_rootfs}/etc/profile", mode='a+')
        f.write((
            'LD_LIBRARY_PATH=/opt/bmc/lib:/usr/local/lib:/lib:/opt/pme/lib:/opt/pme/plugins/chip:'
            '/opt/bmc/lib:/lib/systemd\n'
            'if [ ! -d /dev/shm/dbus ]; then\n'
            '    mkdir -p /dev/shm/dbus\n'
            'fi\n'
            'if [ ! -f /dev/shm/dbus/.dbus ]; then\n'
            '    dbus-launch >/dev/shm/dbus/.dbus\n'
            'fi\n'
            'sleep 1\n'
            'export $(cat /dev/shm/dbus/.dbus)\n'
        ))
        f.close()
        self.run_command(f"chmod o-w {self.rtos_rootfs}/etc/profile", sudo=True)

    def change_own(self):
        user_group = f"{os.getuid()}:{os.getgid()}"
        self.run_command(f"chown -R {user_group} {self.buildimg_dir}")
        self.run_command(f"chown -R {user_group} {self.buildimg_dir}")
        return

    def run(self):
        self.set_evn()
        self.build_common_fs()
        self.make_rootfs_img()
