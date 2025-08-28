#!/usr/bin/python3
# coding: utf-8
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import sys
import os
import re
import json
from html.parser import HTMLParser
import argparse
import functools
import fnmatch

from bmcgo.utils.tools import Tools

DOC_STRING = """
PURPOSE:
Calculate incremental coverage of git commits

USAGE:
./incremental_cov.py <since>..<until> <monitor_c_files> <lcov_dir> <thresholdold>
example: 
./incremental_cov.py "227b032..79196ba" '["src/file"]' "coverage" 0.6    LTX--

WORK PROCESS:
get changed file list between <since> and <until> , filter by <monitor_c_files> options;
get changed lines per changed file;
based on <lcov_dir>, search .gcov.html per file, and get uncover lines;
create report file:ut_incremental_check_report.html and check <thresholdold> (cover lines/new lines).

coverage_exclude.json example:
{
    "xxx": {
        "LUA_EXCLUDED": [],
        "C_EXCLUDED": []
    }
}
"""

tools = Tools()
log = tools.log

OUTPUT_DATA = "dt_result.json"

# 组件里需要解析mds获取component名字
FILE_WHITE_LIST = ["src"]


def open_file(file_name, mode="r", encoding=None, **kwargs):
    # 尝试用不同编码方式解码该文件内容并打开
    with open(file_name, "rb") as f:
        context = f.read()
        for encoding_item in ["UTF-8", "GBK", "ISO-8859-1", "GB2312"]:
            try:
                context.decode(encoding=encoding_item)
                encoding = encoding_item
                return open(file_name, mode=mode, encoding=encoding, **kwargs)
            except UnicodeDecodeError as e:
                pass
    return open(file_name, mode=mode, encoding=encoding, **kwargs)


def num_to_percentage(num):
    percentage = num * 100
    return f"{percentage:.1f}%"


class GcovHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.uncovers = []
        self.covers = []
        self.is_line_num = False
        self.line_num = 0

    def handle_starttag(self, tag, attrs):
        if tag == "span":
            for a in attrs:
                if a == ("class", "lineNum"):
                    self.is_line_num = True
                if a == ("class", "lineNoCov"):
                    self.uncovers.append(self.line_num)
                if a == ("class", "lineCov"):
                    self.covers.append(self.line_num)

    def handle_data(self, data):
        if self.is_line_num:
            try:
                self.line_num = int(data)
            except Exception as e:
                self.line_num = -1

    def handle_endtag(self, tag):
        if tag == "span":
            self.is_line_num = False


class IncrementalCov(object):
    def __init__(self, since_until, component_name, lcov_dir, threshold, coverage_exclude):
        self.since, self.until = since_until.split("..")
        self.component_name = component_name
        self.lcov_dir = lcov_dir
        self.threshold = float(threshold)
        self.coverage_exclude = coverage_exclude
        if not os.path.exists(self.lcov_dir):
            os.makedirs(self.lcov_dir)

    @functools.cached_property
    def src_root_dir(self):
        ret = tools.run_command("git rev-parse --show-toplevel", capture_output=True, command_echo=False)
        if ret.returncode != 0:
            return os.getcwd()

        return ret.stdout.strip()

    def is_file_matched(self, file_name, suffix_list):
        # 校验传入的文件参数是否在设定的匹配路径下
        for f in FILE_WHITE_LIST:
            if file_name.startswith(f) and os.path.splitext(file_name)[1][1:] in suffix_list:
                return True
        return False

    def get_lua_cov_map(self, changes, path_list):
        # 获取lua代码的校验字典
        lua_changes = {}
        uncovers = {}
        # 如果未覆盖到lua文件则返回空字典,path_list[1]为.out文件路径
        if not os.path.exists(path_list[1]):
            return lua_changes, uncovers
        cov_lines = self.parse_data(path_list[0])
        filter_lines = self.parse_check_data(path_list[1])
        for file, change_lines in changes.items():
            temp_uncovers = []
            temp_changes = []
            filters = filter_lines[file]
            if file not in cov_lines:
                cov = []
            else:
                cov = cov_lines[file]

            for change in change_lines:
                if filters[change - 1] == 0:
                    continue
                temp_changes.append(change)
                if not cov or not cov[change - 1]:
                    temp_uncovers.append(change)
            lua_changes[file] = temp_changes
            uncovers[file] = temp_uncovers

        return lua_changes, uncovers

    def parse_data(self, file_path):
        # 解析lua覆盖率的统计文件
        lines = []
        whole_lines = {}
        with open(file_path, "r") as file:
            for line in file:
                lines.append(line.strip())
        num_calculate = 1
        file_locator = "init"
        for line in lines:
            if num_calculate % 2 == 1:
                file_start = line.find("src")
                file_locator = line[file_start:]
                num_calculate += 1
            else:
                lines_cov = [int(num) for num in line.split() if num.isdigit()]
                whole_lines[file_locator] = lines_cov
                num_calculate += 1
        return whole_lines

    def parse_check_data(self, file_path):
        # 解析lua覆盖率的过滤文件
        lines = []
        check_list = {}
        with open(file_path, "r") as file:
            for line in file:
                lines.append(line.strip())
        num_calculate = 1
        file_locator = "init"
        for line in lines:
            if num_calculate % 2 == 1:
                file_start = line.find("src")
                file_locator = line[file_start:]
                num_calculate += 1
            else:
                lines_cov = [int(num) for num in line.split() if num.isdigit()]
                check_list[file_locator] = lines_cov
                num_calculate += 1
        return check_list

    def get_excluded_files(self):
        if not os.path.isfile(self.coverage_exclude):
            return []

        try:
            with open(self.coverage_exclude, "r") as file:
                excluded_data = json.load(file)
        except json.JSONDecodeError:
            log.info(f"Failed to decode JSON from file: {self.coverage_exclude}")
            return []

        # 展平排除文件列表
        excluded_files = []
        if self.component_name in excluded_data:

            for file_list in excluded_data[self.component_name].values():
                excluded_files.extend(file_list)
        return excluded_files

    def get_src(self, suffix_list):
        # 获取节点间的变动文件
        ret = tools.run_command(
            f"git diff --name-only {self.since} {self.until}", capture_output=True, command_echo=False
        )

        if ret.returncode != 0:
            log.info(f"error: git diff failed! err={ret.stderr}")

        file_list = ret.stdout.split("\n")
        src_files = []
        for f in file_list:
            if self.is_file_matched(f, suffix_list):
                src_files.append(f)

        # 获取需要排除的文件
        excluded_list = self.get_excluded_files()

        # 过滤掉排除的文件
        filtered_files = [f for f in src_files if f not in excluded_list]

        return filtered_files

    def get_change(self, src_files):
        # self.since, self.until
        # 获取变动文件的change行
        changes = {}
        for f in src_files:
            # commit中已删除文件不做统计
            file_path = os.path.join(self.src_root_dir, f)
            if not os.path.isfile(file_path):
                continue
            output, _ = tools.pipe_command(
                [f"git log --oneline {self.since}..{self.until} {f}", "awk '{print $1}'"],
                capture_output=True,
                command_echo=False,
            )
            commits = [commit for commit in output.split("\n") if commit]

            cmds = [f"git blame -f {f}"]
            for commit in commits:
                cmds.append(f"grep -E '({commit})'")
            cmds.append("awk -F' *|)' '{print $7}'")

            # 存在文件只有删除行时, git blame -f xx | grep -E '(xx)' 匹配不到修改行, grep会返回1状态码
            output, _ = tools.pipe_command(cmds, capture_output=True, command_echo=False, ignore_error=True)
            if not output:
                continue
            changes[f] = [int(i) for i in output.split("\n") if i.isdigit()]

        return changes

    def get_ghp(self, f):
        f = os.path.basename(f)
        located_file = f + ".gcov.html"
        # 以下是为了能通过点击行号跳转到对应的代码行，为原html文件的未覆盖的代码行添加一个tag
        gcovfile = self.find_and_return_file_path(located_file)
        if not os.path.exists(gcovfile):
            log.info("*.gcov.html does not exits!")
            return None

        ghp = GcovHTMLParser()
        ghp.feed(open_file(gcovfile, "r").read())

        return ghp

    def get_lcov_data(self, changes):
        # self.lcov_dir
        uncovers = {}
        lcov_changes = {}
        for f, lines in changes.items():
            ghp = self.get_ghp(f)
            if not ghp:
                uncovers[f] = lines
                lcov_changes[f] = lines
                continue

            # set创造一个不重复的集合
            lcov_changes[f] = sorted(list(set(ghp.uncovers + ghp.covers) & set(lines)))
            uncov_lines = list(set(ghp.uncovers) & set(lines))
            if len(uncov_lines) != 0:
                uncovers[f] = sorted(uncov_lines)
            ghp.close()

        return lcov_changes, uncovers

    def get_lua_cov_data(self, changes, path):
        path_list = [
            os.path.join(path, "luacov.stats.out"),
            os.path.join(path, "luacov.stats.filter"),
        ]
        return self.get_lua_cov_map(changes, path_list)

    def find_and_return_file_path(self, filename):
        for root, _, files in os.walk(self.lcov_dir, topdown=True):
            for name in files:
                if fnmatch.fnmatch(name, filename):
                    file_path = os.path.join(root, name)
                    return file_path
        return ""

    def prepare_uncover_trs(self, path):
        if os.path.exists(path):
            s = ""
            p = re.compile(r'^<span class="lineNum">\s*(?P<num>\d+)\s*</span>')
            for line in open_file(path, "r").readlines():
                ps = p.search(line)
                if ps:
                    s += '<a name="%s">' % ps.group("num") + line + "</a>"
                else:
                    s += line
            open(path, "w").write(s)

    def create_uncover_trs(self, uncovers):
        """
        返回：tr_format格式的 html table
        通过对全量报告生成的gcov.html文件解析，生成html格式的增量覆盖率的table
        """

        tr_format = """
    <tr>
      <td class="coverFile"><a href="%(f_ref_path)s.gcov.html">%(file)s</a></td>
      <td class="coverFile">%(uncov_lines)s </td>
    </tr>
    
        """
        trs = ""
        for f, v in uncovers.items():
            f = os.path.basename(f)
            located_file = f + ".gcov.html"
            # 以下是为了能通过点击行号跳转到对应的代码行，为原html文件的未覆盖的代码行添加一个tag
            gcovfile = self.find_and_return_file_path(located_file)
            self.prepare_uncover_trs(gcovfile)

            data = {
                "file": f,
                "uncov_lines": ", ".join([f'<a href="{f}.gcov.html#{i}">{i}</a>' for i in v]),
                "f_ref_path": f,
            }
            trs += tr_format % data

        return trs

    def create_report(self, changes, uncovers, type_name):
        change_linenum, uncov_linenum = 0, 0
        for _, v in changes.items():
            change_linenum += len(v)
        for _, v in uncovers.items():
            uncov_linenum += len(v)

        cov_linenum = change_linenum - uncov_linenum
        coverage = round((cov_linenum * 1.0 / change_linenum) if change_linenum > 0 else 1, 4)
        script_dir = os.path.split(os.path.realpath(__file__))[0]
        if type_name == "c":
            template = open(os.path.join(script_dir, "c_incremental_cov_report.template"), "r").read()
            data = {
                "cov_lines": cov_linenum,
                "change_linenum": change_linenum,
                "coverage": coverage * 100,
                "uncover_trs": self.create_uncover_trs(uncovers),
            }
            with open(os.path.join(self.lcov_dir, "c_incremental_coverage_report.html"), "w+") as f:
                f.write(template % data)
        if coverage < self.threshold:
            log.info(f"{type_name} incremental coverage less than {num_to_percentage(self.threshold)}")
        return coverage, change_linenum, cov_linenum

    def calculate_cov(self):
        # main function
        result_path = os.path.join(self.lcov_dir, OUTPUT_DATA)

        c_cov_match = ["c", "cpp"]
        lua_cov_match = ["lua"]

        c_src_files = self.get_src(c_cov_match)
        lua_src_files = self.get_src(lua_cov_match)

        c_changes = self.get_change(c_src_files)
        lua_changes = self.get_change(lua_src_files)

        c_lcov_changes, c_uncovered_lines = self.get_lcov_data(c_changes)
        lua_lcov_changes, lua_uncovered_lines = self.get_lua_cov_data(lua_changes, self.lcov_dir)

        c_cov_rate, c_change_linenum, c_cov_linenum = self.create_report(c_lcov_changes, c_uncovered_lines, "c")
        lua_cov_rate, lua_change_linenum, lua_cov_linenum = self.create_report(
            lua_lcov_changes, lua_uncovered_lines, "lua"
        )

        if c_change_linenum + lua_change_linenum == 0:
            total_rate = 1
        else:
            total_rate = (c_cov_linenum + lua_cov_linenum) / (c_change_linenum + lua_change_linenum)
        coverage_data = {
            "incremental_coverage": num_to_percentage(total_rate),
            "incremental_coverage_detail": {
                "c_incremental_coverage": num_to_percentage(c_cov_rate),
                "lua_incremental_coverage": num_to_percentage(lua_cov_rate),
                "total_incremental_coverage": num_to_percentage(total_rate),
                "c_change_lines": c_lcov_changes,
                "c_uncovered_lines": c_uncovered_lines,
                "lua_change_lines": lua_lcov_changes,
                "lua_uncovered_lines": lua_uncovered_lines,
            },
        }
        with open(result_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        data[self.component_name].update(coverage_data)
        with open(result_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        return (
            num_to_percentage(total_rate),
            num_to_percentage(c_cov_rate),
            num_to_percentage(lua_cov_rate),
        )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        log.info(__doc__)
        sys.exit(0)
    parser = argparse.ArgumentParser(description="manual to this script")
    # 默认统计HEAD和HEAD~之间的增量覆盖率
    parser.add_argument("--since_until", type=str, default="HEAD~..HEAD")
    parser.add_argument("--module", type=str, default=None)
    parser.add_argument("--lcov_dir", type=str, default=None)
    parser.add_argument("--threshold", type=float, default=0.8)
    parser.add_argument("--coverage_exclude", type=str, default="coverage_exclude.json")
    args = parser.parse_args()
    log.info(f"args.since_until={args.since_until}")
    log.info(f"args.module={args.module}")
    log.info(f"args.lcov_dir={args.lcov_dir}")
    log.info(f"args.threshold={args.threshold}")
    log.info(f"args.coverage_exclude={args.coverage_exclude}")
    total_coverage, c_coverage, lua_coverage = IncrementalCov(
        args.since_until,
        args.module,
        args.lcov_dir,
        args.threshold,
        args.coverage_exclude,
    ).calculate_cov()

    log.info(f"incremental coverage is {total_coverage, c_coverage, lua_coverage}.")
