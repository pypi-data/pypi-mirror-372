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
import argparse
import datetime
import json
import os
import re
import subprocess
import stat
import textwrap
import xml.etree.ElementTree as ET
import shutil
from pathlib import Path

from bmcgo import misc
from bmcgo.logger import Logger
from bmcgo.component.deploy import DeployComp
from bmcgo.component.build import BuildComp
from bmcgo.component.package_info import InfoComp
from bmcgo.component.gen import GenComp
from bmcgo.codegen.c.helper import Helper
from bmcgo.component.component_dt_version_parse import ComponentDtVersionParse
from bmcgo.component.coverage.incremental_cov import IncrementalCov
from bmcgo.bmcgo_config import BmcgoConfig
from bmcgo.utils.tools import Tools
from bmcgo.errors import BmcGoException

log = Logger("comp_test")
cwd = os.getcwd()
cwd_script = os.path.split(os.path.realpath(__file__))[0]
TOTAL_TIME = "totaltime"
HIT_LINES = "hitlines"


class TestFailedError(OSError):
    """测试失败"""


class TestComp():
    def __init__(self, bconfig: BmcgoConfig, args=None):
        self.bconfig = bconfig
        self.folder = bconfig.component.folder
        self.tools = Tools()
        os.chdir(self.folder)
        # 路径定义
        self._path_define()

        parser = self.arg_parser(True)
        # 参数检查
        dt_parser = ComponentDtVersionParse(parser=parser, args=args, serv_file=self.temp_service_json)
        dt_parser.chose_dt_mode()
        self.args, self.build_args = parser.parse_known_args(args)
        if self.args.enable_luajit:
            self.build_args.append("-jit")
        self.build_args.append("-bt")
        self.build_args.append("dt")
        self.build_args.append("-r")
        self.build_args.append(self.args.remote)
        if self.args.coverage:
            self.build_args.append("-cov")
        if self.args.asan:
            self.build_args.append("-as")

        self.info = InfoComp(self.build_args, self.temp_service_json)
        self.unit_test = self.args.unit_test
        self.integration_test = self.args.integration_test
        self.test_filter = self.args.test_filter
        self.app = self.args.app
        self.asan = self.args.asan
        self.coverage = self.args.coverage    # 根据入参配置是否显示覆盖率未
        self.without_build = self.args.without_build
        self.coverage_exclude = self.args.coverage_exclude
        self.ut_output = None
        self.it_output = None
        self.fuzz_output = None
        self.dt_result = {}
        # 存在test_package目录的组件由conan拉起DT测试
        self.test_by_conan = os.path.isdir("test_package")
        # 文件名称定义
        self.origin_cov = "luacov.stats.out"
        self.cov_filter = "luacov.stats.filter"
        self.cov_report = "luacov.report.html"
        # dt-fuzz定义
        self.fuzz_test = self.args.fuzz_test
        self.fuzz_gen = self.args.fuzz_gen
        self.fuzz_count = self.args.fuzz_count
        self.dtframe = os.path.join(self.temp_path, "dtframeforlua")

        # 构建阶段检查
        self.remote_pkg_list = []
        # prerelease默认为空

        self.srv_file = os.path.join(cwd, "mds", "service.json")

        # 获取包名，默认取deps目录下的第一个目录名
        self.package_id = ""
        log.info("===>>>包名: %s", self.info.package)

        self.current_app = self.info.name
        # 初始化DT字典
        self.init_dt_result_dict()

        # 构建和部署对象
        self.build = BuildComp(bconfig, self.build_args, service_json=self.temp_service_json)
        self.deploy = DeployComp(bconfig, self.build.info)
        self.current_app = self.build.info.name

    @staticmethod
    def arg_parser(add_help=False):
        pkg_parser = InfoComp.arg_parser()
        parser = argparse.ArgumentParser(description="Test component", parents=[pkg_parser], add_help=add_help)
        parser.add_argument("-ut", "--unit_test", help="Enable unit test", action=misc.STORE_TRUE)
        parser.add_argument("-it", "--integration_test", help="Enable integration test", action=misc.STORE_TRUE)
        parser.add_argument("-ft", "--fuzz_test", help="Enable fuzz test", action=misc.STORE_TRUE)
        parser.add_argument("-fg", "--fuzz_gen", help="Generate fuzz case", action=misc.STORE_TRUE)
        parser.add_argument("-cnt", "--fuzz_count", help="Fuzz count", required=False, type=int, default=100000)
        parser.add_argument("-f", "--test_filter", help="Run unit test with a filter", required=False, default='.')
        parser.add_argument("-a", "--app", help="App in hica", required=False, default='all')
        parser.add_argument("-wb", "--without_build", help="测试时不重新构建", action=misc.STORE_TRUE)
        parser.add_argument("--coverage_exclude", help="Specify coverage exclude file path of whitelist", 
                            required=False, default="")
        return parser

    @staticmethod
    def is_method_covered(next_line):
        pattern = re.compile("data-hits")
        match = re.search(pattern, next_line)
        if match is not None:
            return True
        else:
            return False

    @staticmethod
    def find_method(line_str):
        pattern = re.compile(":(Impl[\w]+)\(.*</span>")
        match = re.search(pattern, line_str)
        if match is not None:
            return match.group(1)
        else:
            return None

    @staticmethod
    def search_test_config(test_path):
        config_list = []
        # 遍历路径, 搜索.conf文件
        for path, _, files in os.walk(test_path):
            for file in files:
                if ".conf" in file:
                    config_file = os.path.join(path, file)
                    config_list.append(config_file)
        return config_list

    @staticmethod
    def is_common_dep(dep, dt_common_deps):
        for dt_dep in dt_common_deps:
            if dt_dep.split("/")[0] in dep:
                return True
        return False

    @staticmethod
    def reslove_gcov(html_report):
        if not os.path.exists(html_report):
            log.warning("覆盖率报告 %s 不存在, 未运行到C/C++代码, 或执行测试时未使能覆盖率功能", html_report)
            return (0, 0, 0)
        with open(html_report, "r", encoding="utf-8", errors="replace") as fp:
            html_content = fp.read()
            cov_pattern = re.compile(r'<td class="headerCovTableEntryLo">([\d.]+).*%</td>')
            coverage_match = re.search(cov_pattern, html_content)
            coverage = coverage_match.group(1) if coverage_match else 0

            # 匹配total和hits
            pattern = r'<td class="headerCovTableEntry">(\d+)</td>'
            matches = re.findall(pattern, html_content)
            if len(matches) >= 2:
                first_number = int(matches[0])
                second_number = int(matches[1])
                # 较大的数字是 total_lines
                total_lines = max(first_number, second_number)
                # 较小的数字是 hit_lines
                hit_lines = min(first_number, second_number)
            else:
                total_lines = 0
                hit_lines = 0
            missed_lines = total_lines - hit_lines
            return (f"{coverage}%", hit_lines, missed_lines)


    @staticmethod
    def _clear_result(file):
        if not os.path.isfile(file):
            return
        fp = os.fdopen(os.open(file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                     stat.S_IWUSR | stat.S_IRUSR), 'w')
        fp.close()

    @staticmethod
    def _get_c_test_results(output_xmls):
        results = []
        total = 0
        failed = 0
        duration = 0
        status_dict = {"success": "ok", "failed": "not ok"}
        ljust_width = 7
        for output_xml in output_xmls:
            tree = ET.parse(output_xml)
            for testcase_element in tree.iter(tag="testcase"):
                status_element = testcase_element.find("status")
                if status_element is None:
                    continue
                duration_element = testcase_element.find("duration")
                name = testcase_element.get("path")
                result = status_element.get("result")
                duration += float(0 if duration_element is None else duration_element.text)
                total += 1
                test_result = str(status_dict.get(result, "")).ljust(ljust_width)
                results.append(f"{test_result} {str(total).ljust(ljust_width)} {name}")
                failed += 1 if result == "failed" else 0
                error_element = testcase_element.find("error")
                if error_element is not None:
                    error = error_element.text
                    results.append(f"# {error}")
        if results:
            summary = f"# Ran {total} tests in {duration:.3f} seconds, {total - failed} successes, {failed} failures"
            results.append(summary)

        return results

    def get_excluded_files_on_key(self, lang):
        if not self.coverage_exclude:
            return []

        component_name = self.current_app
        cov_exclude_path = os.path.realpath(os.path.join(cwd, self.coverage_exclude))
        try:
            with open(cov_exclude_path, 'r') as file:
                excluded_data = json.load(file)
        except FileNotFoundError as exc:
            raise BmcGoException(f"File not found: {cov_exclude_path}") from exc
        except json.JSONDecodeError:
            log.info(f"Failed to decode JSON from file: {cov_exclude_path}")
            return []

        # 基于语言筛选白名单文件
        excluded_files = []
        if component_name in excluded_data:
            excluded_files.extend(excluded_data[component_name][lang])

        return excluded_files

    def write_commponent_deps(self, deps, dt_common_deps, mf_file, uc_code, prefix):
        # 获取组件自身配置的依赖列表
        for dep in deps:
            conan = dep.get(misc.CONAN)
            if conan is None:
                log.error("依赖格式错误, 获取到: %s", dep)
            elif not self.is_common_dep(conan, dt_common_deps):
                # 写入组件配置的非DT公共依赖
                if "@" not in conan:
                    write_dep = prefix + '"' + conan + uc_code + '"' + "\n"
                else:
                    write_dep = prefix + '"' + conan + '"' + "\n"
                mf_file.write(write_dep)

    def build_and_deploy(self):
        # 构建被测组件
        self.build.run()
        os.chdir(self.folder)
        # 部署被测组件及其依赖到temp/rootfs目录
        self.deploy.run()
        os.chdir(self.folder)

    def coverage_config(self, project_root, cov_path, app):
        log.info("配置覆盖率报告选项")
        if app is not None:
            app_path = "apps/" + app + "/"
        else:
            app_path = ""

        # 获取需要屏蔽的.lua文件
        lua_exclusion = self.get_excluded_files_on_key("LUA_EXCLUDED")
        lua_x = []
        # luacov规则，移除.lua拓展名
        for file in lua_exclusion:
            if file.endswith('.lua'):
                file = file[:-4]
                lua_x.append(file)

        # 默认屏蔽test和temp目录下的文件
        lua_exclusions = [f'"{app_path}{file}"' for file in lua_x]
        exclusions = [f'"{project_root}test/.*"', f'"{project_root}temp/.*"'] + lua_exclusions

        # 用textwrap格式化配置信息
        config_str = textwrap.dedent(f"""
            return {{
                include = {{"{app_path}src/.*"}},
                exclude = {{{', '.join(exclusions)}}},
                statsfile = "{cov_path}/{self.origin_cov}",
                coverage_filter = "{cov_path}/{self.cov_filter}",
                reporter = "html",
                reportfile = "{cov_path}/{self.cov_report}",
                includeuntestedfiles = {{"{project_root}/src"}}
            }}
        """).strip()

        if not os.path.exists(cov_path):
            os.makedirs(cov_path)
        # 重写默认的defaults.lua文件
        with os.fdopen(os.open(self.cov_config, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as file:
            file.write(config_str)

    def prepare_dlclose(self):
        stub_code = textwrap.dedent('''\
            #include <stdio.h>
            int dlclose(void *handle)
            {
                return 0;
            }
        ''')

        os.makedirs(self.asan_path, exist_ok=True)
        source_file = os.path.join(self.asan_path, "dlclose.c")
        # 创建打桩文件并编译为so
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        mode = stat.S_IRUSR | stat.S_IWUSR
        with os.fdopen(os.open(source_file, flags, mode), 'w') as f:
            f.write(stub_code)
        cmd = ["gcc", source_file, "-shared", "-fPIC", "-o", self.dlclose_path]
        subprocess.run(cmd)

    def check_asan_log(self):
        files = os.listdir(self.asan_path)
        asanlog_exist = False
        for f in files:
            if "asan.log" in f:
                asanlog_exist = True
                asan_log = os.path.join(self.asan_path, f)
                # 备份日志到coverage路径下，便于看板或门禁下载
                shutil.copy(asan_log, self.cov_path)
                log.warning("地址消毒检测到内存问题, 日志保存到 %s", asan_log)
        if asanlog_exist:
            raise OSError("检测到内存问题, 请检查地址消毒日志!")

    def clear_asan_log(self):
        files = os.listdir(self.asan_path)
        for f in files:
            if "asan.log" in f:
                os.remove(os.path.join(self.asan_path, f))

    def set_additional_env(self, test_env, project_root, project_name):
        test_env["PROJECT_DIR"] = project_root
        test_env["PROJECT_NAME"] = project_name
        if self.fuzz_test:
            test_env["LD_PRELOAD"] = self.preload_option
            test_env["ASAN_OPTIONS"] = "detect_leaks=0"
        if self.coverage:
            test_env["LUA_PATH"] = self.luacov_env
            test_env["LUA_CPATH"] = self.luafilesystem
        if self.asan:
            self.prepare_dlclose()
            self.clear_asan_log()
            test_env["LD_PRELOAD"] = self.preload_option
            test_env["ASAN_OPTIONS"] = "halt_on_error=0:detect_leaks=1:log_path={}".format(self.asan_log)

    def set_unit_test_cmd(self, test_entry):
        if self.coverage:
            ut_cmd = [self.lua_bin, "-lluacov", test_entry, "-v", "-o", "TAP", "-p", self.test_filter]
        else:
            ut_cmd = [self.lua_bin, test_entry, "-v", "-o", "TAP", "-p", self.test_filter]
        return ut_cmd

    def add_luacov_to_config(self):
        log.info("添加 luacov 路径到 %s", self.test_config)
        with open(self.test_config, "r") as file:
            search_str = '    self:add_lua_path(self.apps_root .. "?/init.lua")\n'
            insert_str = '    self:add_lua_path(self.bmc_root .. "lualib/luacov/?.lua")\n'
            lines = file.readlines()
            if insert_str in lines:
                return
            insert_index = lines.index(search_str)
            lines.insert(insert_index + 1, insert_str)
            write_str = "".join(lines)
        with os.fdopen(os.open(self.test_config, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as file:
            file.write(write_str)

    def add_luacov_to_preloader(self):
        preloader_dir = os.path.dirname(self.preloader)
        preloader_wrapper = "app_preloader_wrapper.lua"
        preloader_wrapper_path = os.path.join(preloader_dir, preloader_wrapper)
        log.info("添加 luacov 依赖到 %s", preloader_wrapper_path)
        with os.fdopen(os.open(preloader_wrapper_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as file:
            preloader_path = Path(self.preloader)
            preloader_name = preloader_path.stem
            preloader_module_name = os.path.basename(preloader_path.parent)
            # luacov 需要在最前面先加载
            file.write("require 'luacov'\n")
            file.write(f"require '{preloader_module_name}.{preloader_name}'\n")

        preloader = os.path.basename(self.preloader)
        log.info(f"{self.test_config}加载{preloader}替换为{preloader_wrapper}")
        self.tools.run_command(f"sed -i 's#{preloader}#{preloader_wrapper}#g' {self.test_config}")

    def run_cmd_and_save_result(self, cmd, env, savefile):
        # 保存当前所在工作目录信息
        where = os.getcwd()
        if os.path.exists("apps"):
            app_path = os.path.join(self.folder, "apps", self.current_app)
            output_dir = os.path.join(self.cov_path, self.current_app, "output")
            # 切换到apps目录下对应的app路径
            os.chdir(app_path)
        else:
            output_dir = os.path.join(self.cov_path, "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        try:
            file = os.fdopen(os.open(savefile, os.O_WRONLY | os.O_CREAT | os.O_APPEND,
                                     stat.S_IWUSR | stat.S_IRUSR), 'w')
            tail_p = subprocess.Popen(["/usr/bin/tail", "-f", savefile])
            process = subprocess.run(cmd, env=env, stdout=file, universal_newlines=True,
                                     encoding="utf-8", errors="replace")
        finally:
            tail_p.kill()
            file.close()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, process.args)
        # 返回到之前工作目录(主要用于hica场景，独立仓不受影响)
        os.chdir(where)

    def init_dt_result_dict(self):
        self.dt_result[self.current_app] = {}
        self.dt_result[self.current_app][HIT_LINES] = 0
        self.dt_result[self.current_app]["missedlines"] = 0
        self.dt_result[self.current_app]["linecoverage"] = ""
        self.dt_result[self.current_app]["tests"] = 0
        self.dt_result[self.current_app]["failures"] = 0
        self.dt_result[self.current_app]["successes"] = 0
        self.dt_result[self.current_app][TOTAL_TIME] = 0
        self.dt_result[self.current_app]["uttime"] = 0.0
        self.dt_result[self.current_app]["ittime"] = 0
        self.dt_result[self.current_app]["lua_hitlines"] = 0
        self.dt_result[self.current_app]["lua_missedlines"] = 0
        self.dt_result[self.current_app]["lua_linecoverage"] = ""
        self.dt_result[self.current_app]["gcov_hitlines"] = 0
        self.dt_result[self.current_app]["gcov_missedlines"] = 0
        self.dt_result[self.current_app]["gcov_linecoverage"] = ""
        self.dt_result[self.current_app]["method_coverage"] = ""
        self.dt_result[self.current_app]["total_method_count"] = 0
        self.dt_result[self.current_app]["covered_method"] = []
        self.dt_result[self.current_app]["covered_method_count"] = 0
        self.dt_result[self.current_app]["uncovered_method"] = []
        self.dt_result[self.current_app]["uncovered_method_count"] = 0

    def parse_ut_result(self):
        with open(self.ut_output) as file:
            pattern = re.compile("# Ran (.*) tests in (.*) seconds, (.*) success(?:es)?, (.*) failures")
            lines = file.readlines()
            match = re.search(pattern, lines[-1])
            if match is not None:
                self.dt_result[self.current_app]["tests"] = int(match.group(1))
                self.dt_result[self.current_app]["uttime"] = float(match.group(2))
                self.dt_result[self.current_app]["successes"] = int(match.group(3))
                self.dt_result[self.current_app]["failures"] = int(match.group(4))
            else:
                log.info("分析单元测试结果失败!")

    def save_dt_result(self, destdir):
        dt_result = os.path.join(destdir, "dt_result.json")
        if self.app != "all" and os.path.exists("apps"):
            # hica单个app运行时进行结果追加
            if os.path.exists(dt_result):
                file = open(dt_result, "r")
                current_json = json.load(file)
                file.close()
            else:
                current_json = {}
            current_json.update(self.dt_result)
            json_str = json.dumps(current_json, indent=4)
        else:
            # 独立自仓或hica运行所有app时一次写入
            json_str = json.dumps(self.dt_result, indent=4)

        with os.fdopen(os.open(dt_result, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as file:
            file.write(json_str)
        log.info("Dt 报告结果输出到 %s", dt_result)

    def start_test_by_type(self, ut_cmd, config_list, test_env):
        self.init_dt_result_dict()
        cov_path = self.cov_path if not os.path.exists("apps") else os.path.join(self.cov_path, self.current_app)
        output_dir = os.path.join(cov_path, "output")
        self.ut_output = os.path.join(output_dir, "ut_output.txt")
        self.it_output = os.path.join(output_dir, "it_output.txt")
        self.fuzz_output = os.path.join(output_dir, "fuzz_output.txt")

        # 根据测试类型启动DT测试
        if self.unit_test and not self.integration_test:
            self._clear_result(self.ut_output)
            self.run_cmd_and_save_result(ut_cmd, test_env, self.ut_output)
            self.parse_ut_result()
            self.dt_result[self.current_app][TOTAL_TIME] = self.dt_result[self.current_app]["uttime"]
        elif self.integration_test and not self.unit_test:
            self._clear_result(self.ut_output)
            # 集成测试存在多个conf文件场景
            start = datetime.datetime.utcnow()
            for config in config_list:
                log.info("集成测试配置: %s", config)
                self.run_cmd_and_save_result([self.skynet_path, config], test_env, self.it_output)
            end = datetime.datetime.utcnow()
            it_time = (end - start).seconds
            self.dt_result[self.current_app]["ittime"] = it_time
            self.dt_result[self.current_app][TOTAL_TIME] = it_time
        elif self.integration_test and self.unit_test:
            # 先运行单元测试
            self._clear_result(self.ut_output)
            self.run_cmd_and_save_result(ut_cmd, test_env, self.ut_output)
            self.parse_ut_result()
            # 再运行集成测试
            self._clear_result(self.it_output)
            log.info("================ 集成测试开始 ================")
            start = datetime.datetime.utcnow()
            for config in config_list:
                log.info("集成测试配置: %s", config)
                self.run_cmd_and_save_result([self.skynet_path, config], test_env, self.it_output)
            end = datetime.datetime.utcnow()
            it_time = (end - start).seconds
            self.dt_result[self.current_app]["ittime"] = it_time
            self.dt_result[self.current_app][TOTAL_TIME] = it_time + \
                self.dt_result[self.current_app]["uttime"]
        elif self.fuzz_test:
            self._clear_result(self.fuzz_output)
            fuzz_path = os.path.join(self.folder, "test/fuzz")
            # Fuzz场景只有一个conf文件
            fuzz_config = self.search_test_config(fuzz_path)[0]
            fuzz_cmd = [self.skynet_path, fuzz_config]
            self.run_cmd_and_save_result(fuzz_cmd, test_env, self.fuzz_output)

    def get_method_coverage(self, lines, index, covered_method, uncovered_method):
        method = self.find_method(lines[index])
        if method is None:
            return
        if self.is_method_covered(lines[index + 1]):
            covered_method.append(method)
        else:
            uncovered_method.append(method)

    def get_lua_coverage(self, lines, index):
        # 通过行偏移获取总体覆盖率数据
        coverage = lines[index + 7]
        hits = lines[index + 9]
        missed = lines[index + 10]
        pattern = re.compile("<strong>(.*)</strong>")
        match = re.search(pattern, coverage)
        coverage = match.group(1) if match is not None else None
        match = re.search(pattern, hits)
        hits = match.group(1) if match is not None else None
        match = re.search(pattern, missed)
        missed = match.group(1) if match is not None else None
        self.dt_result[self.current_app]["lua_linecoverage"] = coverage
        self.dt_result[self.current_app]["lua_hitlines"] += int(hits)
        self.dt_result[self.current_app]["lua_missedlines"] += int(missed)

    def reslove_luacov(self, html_report):
        if not os.path.exists(html_report):
            log.error("覆盖率报告 %s 不存在, 执行测试时, 请使能覆盖率功能", html_report)
            return
        covered_method = []
        uncovered_method = []
        with open(html_report, "r", encoding="utf-8", errors="replace") as file:
            lines = file.readlines()
        line_index = 0
        for line in lines:
            if '<main>' in line:
                self.get_lua_coverage(lines, line_index)
            self.get_method_coverage(lines, line_index, covered_method, uncovered_method)
            line_index += 1
        # 汇总method覆盖率信息
        method_count = len(covered_method) + len(uncovered_method)
        if method_count != 0:
            self.dt_result[self.current_app]["method_coverage"] = '%.1d' % (len(covered_method) / method_count)
        self.dt_result[self.current_app]["total_method_count"] = len(covered_method) + len(uncovered_method)
        self.dt_result[self.current_app]["covered_method"] = covered_method
        self.dt_result[self.current_app]["covered_method_count"] = len(covered_method)
        self.dt_result[self.current_app]["uncovered_method"] = uncovered_method
        self.dt_result[self.current_app]["uncovered_method_count"] = len(uncovered_method)

    def generate_luacov(self, test_env):
        subprocess.run([self.lua_bin, self.luacov_bin], env=test_env)
        self.reslove_luacov(os.path.join(self.cov_path, self.cov_report))

    def save_package_info(self):
        # 保存package信息，多次构建情况下用于确定唯一的包名
        package_path = os.path.join(self.temp_path, "package_info")
        log.info("保存包信息到 %s", package_path)
        with os.fdopen(os.open(package_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                               stat.S_IWUSR | stat.S_IRUSR), 'w') as file:
            file.write(self.info.package)

    def generate_gcov(self):
        if not self.test_by_conan:
            if not os.path.exists("src/lualib-src"):
                return
            package_path = os.path.join(self.temp_path, "package_info")
            with open(package_path, "r") as file:
                lines = file.readlines()
                package_path = lines[0].replace("@", "/")
        else:
            package_path = self.info.package.replace("@", "/")
        base_dir = "%s/.conan/data/%s" % (os.path.expanduser('~'), package_path)
        gcov_path = os.path.join(self.cov_path, "gcov")
        if not os.path.exists(gcov_path):
            os.makedirs(gcov_path)
        info_file = os.path.join(gcov_path, "gcov.info")
        self.dt_result[self.current_app]["gcov_linecoverage"] = 0
        self.dt_result[self.current_app]["gcov_hitlines"] += 0
        self.dt_result[self.current_app]["gcov_missedlines"] += 0
        # 生成gcov覆盖率数据
        cmd = [
            "lcov",
            "--base-directory",
            base_dir,
            "--directory",
            base_dir,
            "--capture",
            "--output-file",
            info_file,
            "--ignore-errors",
            "unused",
        ]
        # exclude files
        exclude = [
            "--exclude=*include*",
            "--exclude=*test*",
            "--exclude=*.h",
            "--exclude=*/service/cli/*",
            "--exclude=*/gen/interface/*"
        ]

        # 获取需要屏蔽的.c/cpp文件
        c_exclusion = self.get_excluded_files_on_key("C_EXCLUDED")
        for file in c_exclusion:
            exclude.append(f"--exclude=*{file}*")
        cmd.extend(exclude)

        ret = Helper.run(cmd, check=False)
        if ret != 0:
            return
        # 生成html覆盖率报告
        cmd = ["genhtml", "--output-directory", gcov_path, info_file]
        Helper.run(cmd, check=False)
        if ret != 0:
            return
        # resolv coverage
        ret = self.reslove_gcov(os.path.join(self.cov_path, "gcov/index.html"))
        if ret is not None:
            self.dt_result[self.current_app]["gcov_linecoverage"] = ret[0]
            self.dt_result[self.current_app]["gcov_hitlines"] += int(ret[1])
            self.dt_result[self.current_app]["gcov_missedlines"] += int(ret[2])

    def combine_coverage(self):
        # 将luacov和gcov数据汇总
        self.dt_result[self.current_app][HIT_LINES] = self.dt_result[self.current_app]["lua_hitlines"] + \
            self.dt_result[self.current_app]["gcov_hitlines"]
        self.dt_result[self.current_app]["missedlines"] = self.dt_result[self.current_app]["lua_missedlines"] + \
            self.dt_result[self.current_app]["gcov_missedlines"]
        total_lines = self.dt_result[self.current_app][HIT_LINES] + self.dt_result[self.current_app]["missedlines"]
        if total_lines != 0:
            self.dt_result[self.current_app]["linecoverage"] = "{:.1%}".format(
                self.dt_result[self.current_app][HIT_LINES] / total_lines)

    def run_independent_test(self, test_env):
        log.info("================ 测试 %s 开始 ================", self.current_app)
        # 配置额外的环境变量
        self.set_additional_env(test_env, self.folder, self.current_app)
        test_entry = os.path.join(self.folder, "test/unit/test.lua")
        itegration_path = os.path.join(self.folder, "test/integration")
        # 获取集成测试配置文件列表
        config_list = self.search_test_config(itegration_path)
        # 设置覆盖率配置文件
        if self.coverage:
            self.coverage_config(self.folder, self.cov_path, None)
        # 设置unit_test运行命令
        ut_cmd = self.set_unit_test_cmd(test_entry)
        # 集成测试场景修改config.cfg和app_preloader.lua
        if (self.integration_test or self.fuzz_test) and self.coverage:
            # config.cfg中增加luacov路径到LUA_PATH
            self.add_luacov_to_config()
            # app_preloader.lua中增加require 'luacov'
            self.add_luacov_to_preloader()
        # 启动DT测试
        self.start_test_by_type(ut_cmd, config_list, test_env)
        # 生成覆盖率报告
        if self.coverage:
            # 生成lua覆盖率报告
            self.generate_luacov(test_env)
            self.generate_gcov()
            self.combine_coverage()
            log.info("行覆盖率: %s, 命中: %s 行, 未命中: %s 行",
                         self.dt_result[self.current_app]["linecoverage"],
                         self.dt_result[self.current_app][HIT_LINES],
                         self.dt_result[self.current_app]["missedlines"])
            log.info("覆盖率报告 %s 保存到 %s", self.cov_report, self.cov_path)
        # 保存结果供jenkins工程解析
        self.save_dt_result(self.cov_path)
        # 检测是否存在asan日志
        if self.asan:
            self.check_asan_log()

    def run_hica_test(self, test_env):
        # 获取app列表
        app_list = []
        if self.app == "all":
            dirs = os.listdir("apps")
            app_list.extend(dirs)
        else:
            app_list.append(self.app)

        # 集成测试场景修改config.cfg和app_preloader.lua
        if self.integration_test and self.coverage:
            # config.cfg中增加luacov路径到LUA_PATH
            self.add_luacov_to_config()
            # app_preloader.lua中增加require 'luacov'
            self.add_luacov_to_preloader()

        hica_cov = self.cov_path
        for app in app_list:
            self.current_app = app
            banner = "单元测试: %s" % (app) if self.unit_test else "集成测试: %s" % (app)
            log.info("================ %s 开始 ================", banner)
            # 适配hica仓的app路径
            project_root = os.path.join(self.folder, "apps/" + app)
            app_cov_path = os.path.join(self.cov_path, app)
            test_entry = os.path.join(project_root, "test/unit/test.lua")
            itegration_path = os.path.join(project_root, "test/integration")
            # 获取集成测试配置文件列表
            config_list = self.search_test_config(itegration_path)
            # 配置额外的环境变量
            self.set_additional_env(test_env, project_root, self.current_app)
            # 设置覆盖率配置文件
            if self.coverage:
                self.coverage_config(project_root, app_cov_path, app)
            # 设置unit_test运行命令
            ut_cmd = self.set_unit_test_cmd(test_entry)
            # 启动DT测试
            self.start_test_by_type(ut_cmd, config_list, test_env)
            # 生成覆盖率报告
            if self.coverage:
                subprocess.run([self.lua_bin, self.luacov_bin], env=test_env)
                ret = self.reslove_luacov(os.path.join(app_cov_path, self.cov_report))
                if ret is not None:
                    self.dt_result[self.current_app]["linecoverage"] = ret[0]
                    self.dt_result[self.current_app][HIT_LINES] = int(ret[1])
                    self.dt_result[self.current_app]["missedlines"] = int(ret[2])
                    log.info("行覆盖率: %s, 命中: %s 行, 未命中: %s 行", ret[0], ret[1], ret[2])
                    log.info("覆盖率报告 %s 保存到 %s", self.cov_report, app_cov_path)
        # 保存结果供jenkins工程解析
        self.save_dt_result(hica_cov)
        # 检测是否存在asan日志
        if self.asan:
            self.check_asan_log()

    def generate_fuzz(self):
        dtframe_gen = os.path.join(self.dtframe, "auto_gen_script/fuzz_build.py")
        ipmi_source = os.path.join(self.folder, "mds", "ipmi.json")
        ipmi_template = os.path.join(self.dtframe, "templates/ipmi.mako")
        mdb_template = os.path.join(self.dtframe, "templates/mdb_interface.mako")
        model_source = os.path.join(self.folder, "mds", "model.json")
        mdb_interface_root = os.path.join(self.folder, "temp/opt/bmc/apps/mdb_interface")
        fuzz_path = os.path.join(self.folder, "test/fuzz")
        os.makedirs(fuzz_path, exist_ok=True)
        os.chdir(fuzz_path)
        Helper.run(["/usr/bin/env", "python3", dtframe_gen, "-s", ipmi_source, "-t",
                    ipmi_template, "-c", str(self.fuzz_count)])
        Helper.run(["/usr/bin/env", "python3", dtframe_gen, "-s", model_source, "-t",
                    mdb_template, "-mp", mdb_interface_root, "-c", str(self.fuzz_count)])

    def run_test(self):
        log.info("================ 开发者测试开始 ================")
        # 判断temp是否存在
        if not os.path.exists(self.temp_path):
            log.error("%s 不存在, 请先构建一次此工程", self.temp_path)
            return
        # 公共环境变量
        test_env = {
            "ROOT_DIR": self.temp_path,
            "LD_LIBRARY_PATH": self.test_lib,
            "CONFIG_FILE": self.test_config
        }
        # 适配hica仓
        if os.path.exists("apps"):
            self.run_hica_test(test_env)
        else:
            self.run_independent_test(test_env)

    def print_build_menu(self):
        log.info("================================ 构建菜单 ================================")
        ljust_width = 30
        log.info("%s %s", "单元测试(ut):".ljust(ljust_width), str(self.unit_test))
        log.info("%s %s", "集成测试(it):".ljust(ljust_width), str(self.integration_test))
        log.info("%s %s", "覆盖率:".ljust(ljust_width), str(self.coverage))
        log.info("%s %s", "地址消毒:".ljust(ljust_width), str(self.asan))
        log.info("============================================================================")

    def test_c_component(self):
        # 调用测试命令
        try:
            test_package_build_dir = os.path.join(self.folder, "test_package", "build")
            if os.path.isdir(test_package_build_dir):
                shutil.rmtree(test_package_build_dir)
            self.build.test()
        except OSError as e:
            raise TestFailedError("执行测试任务失败, 退出") from e
        finally:
            self._save_c_test_result()
            if self.ut_output:
                self.parse_ut_result()

        # C框架由构建时测试，仅需要统计覆盖率
        if self.coverage:
            self.generate_gcov()
            self.combine_coverage()
            result = self.dt_result[self.current_app]
            log.info("覆盖率: %s, 命中: %s 行, 未命中: %s 行",
                         result["linecoverage"], result[HIT_LINES], result["missedlines"])
            self.save_dt_result(self.cov_path)
            log.info("覆盖率报告 %s 保存到 %s", self.cov_report, self.cov_path)

    def check_folder(self):
        test_package_folder = os.path.join(self.folder, "test_package")
        test_folder = os.path.join(self.folder, "test")
        if os.path.isdir(test_folder) or os.path.isdir(test_package_folder):
            return True
        return False

    def incremental_cov(self):
        temp_path = os.path.join(self.folder, "temp", "coverage")
        cov_exclude_path = self.coverage_exclude
        if self.coverage_exclude:
            cov_exclude_path = os.path.realpath(os.path.join(cwd, self.coverage_exclude))
        total_coverage, c_coverage, lua_coverage = IncrementalCov(
            "HEAD~..HEAD", self.current_app, temp_path, 0.8, cov_exclude_path).calculate_cov()
        log.info("增量总覆盖：%s, c代码覆盖: %s, lua代码覆盖: %s", total_coverage, c_coverage, lua_coverage)
        log.info("增量覆盖率报告保存到 dt_result.json") 

    def run(self):
        self.print_build_menu()
        if not self.check_folder():
            log.warning("当前组件不存在开发者测试的test文件夹或test_package文件夹，开发者测试终止！")
            return

        # -gen代码自动生成逻辑
        if self.fuzz_gen:
            self.generate_fuzz()
            return
        # 构建完后单独运行DT
        has_dt_type = self.unit_test or self.integration_test or self.fuzz_test
        if not has_dt_type:
            self.unit_test = True

        # 构建被测组件
        if not self.without_build:
            self.build_and_deploy()

        ret = 0
        try:
            # 有test_package的由conan启动测试
            if self.test_by_conan:
                if self.info.language == "c":
                    args = ["-s", self.temp_service_json]
                    gen = GenComp(args)
                    gen.run()
                self.test_c_component()
                if self.coverage:
                    # 调用增量模块
                    self.incremental_cov() 
                self.print_build_menu()
            else:
                self.save_package_info()
                self.run_test()
                if self.coverage:
                    # 调用增量模块
                    self.incremental_cov() 
                self.print_build_menu()
        except Exception as exp:
            log.warning("===>>>> exception: %s", str(exp))
            ret = -1
        if ret == 0:
            log.info("===>>>> 测试: %s 完成", self.info.package)
        else:
            log.warning("===>>>> 测试: %s 失败", self.info.package)

    def _path_define(self):
        self.temp_path = os.path.join(self.folder, "temp")
        os.makedirs(self.temp_path, exist_ok=True)
        self.temp_service_json = os.path.join(self.temp_path, "service.json")
        self.tools.copy("mds/service.json", self.temp_service_json)

        self.cov_path = os.path.join(self.folder, "temp", "coverage")
        self.luacov_path = os.path.join(self.temp_path, "opt/bmc/lualib/luacov")
        self.cov_config = os.path.join(self.luacov_path, "luacov/defaults.lua")
        self.test_lib = ';'.join([os.path.join(self.temp_path, v) for v in ["lib", 'lib64', 'usr/lib', "usr/lib64"]])
        self.test_config = os.path.join(self.temp_path, "opt/bmc/libmc/lualib/test_common/test_config.cfg")
        self.preloader = os.path.join(self.temp_path, "opt/bmc/libmc/lualib/test_common/app_preloader.lua")
        self.lua_bin = os.path.join(self.temp_path, "opt/bmc/skynet/lua")
        self.skynet_path = os.path.join(self.temp_path, "opt/bmc/skynet/skynet")
        self.luacov_bin = os.path.join(self.luacov_path, "bin/luacov")
        self.luacov_env = os.path.join(self.luacov_path, "?.lua")
        self.luafilesystem = os.path.join(self.temp_path, "opt/bmc/luaclib/?.so")
        # WSL环境ASAN库路径(只用于DT场景)
        self.libasan_path = "/usr/lib/x86_64-linux-gnu/libasan.so.5"
        # 地址消毒相关文件存储路径
        self.asan_path = os.path.join(self.temp_path, "asan")
        self.asan_log = os.path.join(self.asan_path, "asan.log")
        # 打桩的dlcose库路径
        self.dlclose_path = os.path.join(self.asan_path, "dlclose.so")
        self.preload_option = "{} {}".format(self.libasan_path, self.dlclose_path)

    def _save_c_test_result(self):
        test_package_build_dir = os.path.join(self.folder, "test_package", "build")
        test_build = os.path.join(test_package_build_dir, os.listdir(test_package_build_dir)[0])
        outputs = []
        for dir_or_file in os.listdir(test_build):
            file_path = os.path.join(test_build, dir_or_file)
            if os.path.isfile(file_path) and re.match(r"gtester.*.xml", dir_or_file):
                outputs.append(file_path)

        results = self._get_c_test_results(outputs)
        if not results:
            return

        self.ut_output = os.path.join(self.cov_path, "output", "ut_output.txt")
        os.makedirs(os.path.dirname(self.ut_output), exist_ok=True)
        self._clear_result(self.ut_output)
        with os.fdopen(os.open(self.ut_output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                        stat.S_IWUSR | stat.S_IRUSR), 'w') as fp:
            for line in results:
                fp.write(f"{line}\n")
