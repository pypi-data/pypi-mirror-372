#!/usr/bin/python
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
import argparse
import os
import time
import fcntl
import stat
from pyecharts import options as opts
from pyecharts.charts import Bar
from bmcgo.utils.tools import Tools

tool = Tools()


class WorkData():
    def __init__(self, name):
        self.name = name
        self.prepare = 0
        self.running = 0
        self.last = 0


class PerfAnalysis():
    def __init__(self, output_dir):
        self.x_data = []
        self.wait_data = []
        self.prepare_data = []
        self.running_data = []
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.lock_file = os.path.join(output_dir, "prof.perf.lock")
        self.perf_file = os.path.join(output_dir, "openubmc.perf")
        file_handle = os.fdopen(os.open(self.lock_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                stat.S_IWUSR | stat.S_IRUSR), 'w')
        file_handle.close
        file_handle = os.fdopen(os.open(self.perf_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                stat.S_IWUSR | stat.S_IRUSR), 'w')
        file_handle.close

    def add_data(self, work_name, state):
        with open(self.lock_file, "r") as fp:
            fcntl.flock(fp.fileno(), fcntl.LOCK_EX)
            with os.fdopen(os.open(self.perf_file, os.O_WRONLY | os.O_CREAT,
                                   stat.S_IWUSR | stat.S_IRUSR), 'a+') as file_handler:
                file_handler.write("{}|{}|{}\n".format(time.time(), work_name, state))
            fcntl.flock(fp.fileno(), fcntl.LOCK_UN)

    def render(self, target="frame.py"):
        output = os.path.join(self.output_dir, "openubmc_performance.html")
        self._proc_data()
        _ = (Bar(init_opts=opts.InitOpts(width="100%", height="500px", page_title="BMC构建时序图"))
            .add_xaxis(self.x_data)
            .add_yaxis('prepare', self.prepare_data, color="#DCDCDC", stack="stack1",
                       is_show_background=True, bar_width=15, label_opts=opts.LabelOpts(is_show=False),)
            .add_yaxis('running', self.running_data, stack="stack1")
            .reversal_axis()
            .set_global_opts(title_opts=opts.TitleOpts(title="BMC构建时序图({})".format(target)))
            .render(output)
            )
        cmd = "sed -i 's@https://assets.pyecharts.org/assets/v5/echarts.min.js"
        cmd += "@https://cdnjs.cloudflare.com/ajax/libs/echarts/5.4.3/echarts.min.js@g' " + output
        tool.run_command(cmd)

    def _proc_data(self):
        start = 0.0
        points: dict[str, WorkData] = {}
        with open(self.perf_file, "r") as fp:
            lines = fp.readlines()
            for line in lines:
                line = line.strip()
                split = line.split("|", -1)
                if start == 0 or start > float(split[0]):
                    start = float(split[0])
                if points.get(split[1]) is None:
                    points[split[1]] = WorkData(split[1])

            for line in lines:
                line = line.strip()
                split = line.split("|", -1)
                if split[2] == 'running':
                    points[split[1]].prepare = float(split[0]) - start
            for line in lines:
                line = line.strip()
                split = line.split("|", -1)
                if split[2] == 'finish':
                    points[split[1]].running = float(split[0]) - start - points[split[1]].prepare
                    points[split[1]].last = float(split[0]) - start
        sorted_points = sorted(points.items(), key=lambda kv:kv[1].prepare)
        for k in sorted_points:
            data = k[1]
            self.x_data.append(k[0])
            self.prepare_data.append(int(data.prepare * 100) / 100)
            self.running_data.append(int(data.running * 100) / 100)
        self.x_data.reverse()
        self.prepare_data.reverse()
        self.running_data.reverse()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="import depencency.json")
    parser.add_argument("-f", "--pref_file", help="openubmc.pref file", default="openubmc.pref")
    args = parser.parse_args()

    bar = PerfAnalysis(args.pref_file)
    bar.render()