#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
'''
功    能：任务调度框架
修改记录：2025-5-20 创建
'''
import json
import importlib
import os
import time
import threading
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from multiprocessing import Process, Queue

import yaml

from bmcgo import errors
from bmcgo.utils.perf_analysis import PerfAnalysis
from bmcgo.utils.tools import Tools

# 注意端口号需要与V3的配置不同
WORK_SERVER_PORT = 62345
# 任务失败状态
TASK_STATUS_FAILED = "Failed"
# 用于通知主程序 server已经启动
q = Queue(1)
tool = Tools(__name__)
log = tool.log


class WsServerCommException(errors.BmcGoException):
    """
        与状态服务通信失败
    """

    def __init__(self, *arg, **kwarg):
        super(WsServerCommException, self).__init__(*arg, **kwarg)


class WorkStatusServer(Process):
    """
    全局任务状态管理器
    """
    def __init__(self):
        super().__init__()
        self.task_status_dict = {}
        self.start_time = time.time()
        self.fd = socket(AF_INET, SOCK_STREAM)
        self.fd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        address = ("", WORK_SERVER_PORT)
        try:
            self.fd.bind(address)
            self.fd.listen(10)
            # 向主进程发送准备好的消息
            q.put(1)
        except Exception as e:
            log.error(f"任务状态错误: {e}")
            raise Exception(f"请手动运行此命令(sudo fuser -k {WORK_SERVER_PORT}/tcp), 若命令不存在执行apt install psmisc安装") from e
        self.has_work_failed = False

    def run(self):
        while True:
            self._accept()

    def _accept(self):
        cur_time = time.time()
        if int(cur_time - self.start_time) / 60 > 60:
            self.start_time = time.time()
            log.warning(f"任务状态字典为: {self.task_status_dict}")
            log.warning("构建时长已超 60 分钟")

        cli_fd, _ = self.fd.accept()
        recv = cli_fd.recv(1024)
        recv_json = recv.decode()
        msg = json.loads(recv_json)
        act = msg["action"]
        resp = ""
        wn = msg["work_name"]
        if act == "set_if_not_exist":
            st = msg["work_status"]
            resp = "False"
            status = self.task_status_dict.get(wn)
            if status is None:
                self.task_status_dict[wn] = st
                resp = "True"
        elif act == "set":
            st = msg["work_status"]
            self.task_status_dict[wn] = st
            if st == TASK_STATUS_FAILED:
                self.has_work_failed = True
            resp = "True"
        elif act == "get":
            if self.has_work_failed:
                resp = TASK_STATUS_FAILED
            else:
                st = self.task_status_dict.get(wn)
                resp = "None" if st is None else st

        cli_fd.send(resp.encode())
        cli_fd.close()


class WorkStatusClient():
    """
    全局任务状态管理器
    """
    def __init__(self):
        super().__init__()
        self.task_status_dict = {}

    @staticmethod
    def __comm(msg, ignore_error):
        fd = socket(AF_INET, SOCK_STREAM)
        fd.settimeout(2)
        while True:
            try:
                fd.connect(("", WORK_SERVER_PORT))
                fd.send(msg.encode())
                msg = fd.recv(1024)
                fd.close()
                return msg.decode()
            except Exception as e:
                if ignore_error:
                    log.info(str(e))
                    return None
                else:
                    raise WsServerCommException("与任务状态服务器通信失败") from e

    # 获取任务状态
    def get(self, target_name, work_name, ignore_error=False):
        return self.__comm("{\"action\":\"get\", \"work_name\":\"%s/%s\"}" % (target_name, work_name), ignore_error)

    # 任务不存在时创建任务状态，否则返回False
    def set_if_not_exist(self, target_name, work_name, status, ignore_error=False):
        return self.__comm("{\"action\":\"set_if_not_exist\", \"work_name\":\"%s/%s\", \"work_status\":\"%s\"}" %
                           (target_name, work_name, status), ignore_error)

    # 设置任务状态
    def set(self, target_name, work_name, status, ignore_error=False):
        self.__comm("{\"action\":\"set\", \"work_name\":\"%s/%s\", \"work_status\":\"%s\"}" %
                    (target_name, work_name, status), ignore_error)


ws_client = WorkStatusClient()


def wait_finish(target_name, wait_list, prev_work_name):
    if not wait_list:
        return True
    start_time = time.time()
    cnt = 0
    while True:
        finish = True
        time.sleep(0.1)
        for work_name in wait_list:
            cur_time = time.time()
            status = ws_client.get(target_name, work_name, ignore_error=True)
            if status is None:
                log.debug(f"任务{target_name}/{prev_work_name}执行失败，原因是未能获取到任务{target_name}/{work_name}的状态")
                ws_client.set(target_name, prev_work_name, TASK_STATUS_FAILED, ignore_error=True)
                return False
            if status == "Done":
                continue
            if status == TASK_STATUS_FAILED:
                log.debug(f"任务{target_name}/{prev_work_name}执行失败，原因其等待的任务{target_name}/{work_name}失败")
                ws_client.set(target_name, prev_work_name, TASK_STATUS_FAILED, ignore_error=True)
                return False
            finish = False
            # 每等待60s打印一次日志
            if int(cur_time - start_time) >= 60:
                start_time = time.time()
                cnt += 60
                log.info("目标 {} 正在等待任务: {}, 当前已等待 {} 秒".format(target_name, work_name, cnt))
            break
        if finish:
            return True


class WorkerScheduler(Process):
    '''
    '''
    def __init__(self, target_name, work, perf: PerfAnalysis, config, args):
        super().__init__()
        self.work = work
        self.target_name = target_name
        self.work_name = self.work["name"]
        self.klass = self.work.get("klass", "")
        self.perf = perf
        self.config = config
        self.args = args

    def load_class(self):
        if self.klass == "":
            return None
        # bmcgo的任务类名固定为TaskClass
        if self.klass.startswith("bmcgo"):
            work_path = self.klass
            class_name = "TaskClass"
        else:
            split = self.klass.split(".", -1)
            work_path = ".".join(split[:-1])
            class_name = split[-1]
        log.debug("工作路径: {}, 类名: {}".format(work_path, class_name))
        try:
            work_py_file = importlib.import_module(work_path)
            return getattr(work_py_file, class_name)
        except ModuleNotFoundError as e:
            ignore = self.work.get("ignore_not_exist", False)
            if ignore:
                log.warning(f"{self.klass} 已配置 ignore_not_exist 且为真, 跳过执行")
                return None
            else:
                raise e

    def run(self):
        ret = -1
        try:
            ret = self._run(self.config, self.args)
            if ret != 0:
                ws_client.set(self.target_name, self.work_name, TASK_STATUS_FAILED, ignore_error=True)
        except WsServerCommException as exc:
            msg = str(exc)
            log.debug(msg)
            ret = -1
        except Exception as exc:
            if os.environ.get("LOG"):
                import traceback
                log.info(traceback.format_exc())
            msg = str(exc)
            log.error(msg)
            ws_client.set(self.target_name, self.work_name, TASK_STATUS_FAILED, ignore_error=True)
            ret = -1
        if ret != 0:
            log.debug(f"任务名: {self.work_name}, 类名: {self.klass} 退出状态错误")
        return ret

    def _run(self, config, args):
        '''
        功能描述：执行work
        '''
        work_name = self.work_name
        log.debug(f"任务名: {self.work_name}, 类: {self.klass}) 已就绪")
        ret = wait_finish(self.target_name, self.work.get("wait"), work_name)
        if not ret:
            log.debug(f"等待任务 {self.work_name} 类 {self.klass} 发生错误")
            return -1
        try:
            log.success(f"任务 {work_name} 开始")
            target_config = self.work.get("target_config")
            config.deal_conf(target_config)
            # bmcgo的任务类名固定为TaskClass
            work_class = self.load_class()
            # 如果未指定类时，不需要执行
            if work_class is not None:
                work_x = work_class(config, work_name)
                # work配置项和target配置项
                work_config = self.work.get("work_config")
                work_x.deal_conf(work_config)
                ret = ws_client.set_if_not_exist(self.target_name, work_name, "Running")
                self.perf.add_data(work_name, "running")
                if not args.debug_frame and ret:
                    # 创建进程并且等待完成或超时
                    ret = work_x.run()
                    if ret is not None and ret != 0:
                        return -1
                elif not args.debug_frame and not ret:
                    # 不需要创建进程，等待任务执行完成即可
                    wait_list = []
                    wait_list.append(work_name)
                    ret = wait_finish(self.target_name, wait_list, work_name)
                    if not ret:
                        log.debug(f"等待任务 {self.work_name} 类 {self.klass} 发生错误")
                        return -1

                log.debug(f"任务 {work_name} 开始安装步骤")
                if not args.debug_frame:
                    ret = work_x.install()
                    if ret is not None and ret != 0:
                        return -1
                self.perf.add_data(work_name, "finish")

            # 创建子任务
            ret = exec_works(self.target_name, self.work.get("subworks"), work_name, self.perf, self.config, self.args)
            if not ret:
                ws_client.set(self.target_name, self.work_name, TASK_STATUS_FAILED, ignore_error=True)
                log.error(f"运行子任务 {self.work_name} 类 {self.klass}失败")
                return -1
            # 创建include_target子任务
            target_include = self.work.get("target_include")
            if target_include:
                ret = create_target_scheduler(work_name, target_include, self.perf, self.config, self.args)
                if not ret:
                    ws_client.set(self.target_name, self.work_name, TASK_STATUS_FAILED, ignore_error=True)
                    log.error(f"创建计划表 {target_include} 失败")
                    return -1
            log.success(f"任务 {work_name} 完成")
            ws_client.set(self.target_name, self.work_name, "Done")
            return 0
        except Exception as exc:
            log.error(f"任务 {work_name} 执行失败, {str(exc)}")
            raise errors.BmcGoException(f"任务 {work_name} 执行失败") from exc


class Worker():
    """
    任务执行器
    """
    work_name = ""
    target_name = ""

    def __init__(self, config, args):
        self.config = config
        self.args = args

    def exec_work(self, target_name, work, perf: PerfAnalysis):
        try:
            return self._exec_work(target_name, work, perf)
        except Exception as exc:
            msg = str(exc)
            log.debug(msg)
            return -1

    def run(self, target_name, work, perf: PerfAnalysis):
        self.work_name = work["name"]
        self.target_name = target_name
        t = threading.Thread(target=self.exec_work, args=(target_name, work, perf))
        t.start()

    def _exec_work(self, target_name, work, perf: PerfAnalysis):
        ws = WorkerScheduler(target_name, work, perf, self.config, self.args)
        ws.start()
        try_cnt = 0
        while ws.is_alive():
            try_cnt += 1
            time.sleep(0.1)

            # 每个任务的超时时间为70分钟(42000次循环)，如果超时则失败
            if try_cnt > 42000:
                log.error(f"任务{self.target_name}/{self.work_name}执行超时(>70min)，强制退出")
                ws.kill()
                return -1
        if ws.exitcode is not None and ws.exitcode == 0:
            return 0
        return -1


def exec_works(target_name, work_list, prev_work_name, perf: PerfAnalysis, config, args):
    if not work_list:
        return True
    # 创建任务并等待完成
    wait_list = []
    for work in work_list:
        worker = Worker(config, args)
        worker.run(target_name, work, perf)
        wait_list.append(work["name"])
    return wait_finish(target_name, wait_list, prev_work_name)


def read_config(file_path: str, conan_args):
    '''
    功能描述：读取json内容
    '''
    if not os.path.exists(file_path):
        raise errors.NotFoundException(f"{file_path} 路径不存在")

    # conan专用处理
    with open(file_path, "r") as fp:
        data = fp.read()
        if conan_args:
            if conan_args.upload_package:
                data = data.replace('${upload}', "true")
            else:
                data = data.replace('${upload}', "false")
            data = data.replace('${conan_package}', conan_args.conan_package)
        return yaml.safe_load(data)


def create_target_scheduler(target_alias, target_name, perf: PerfAnalysis, config, args, conan_args, target):
    log.info(f"创建新目标 {target_name} 构建计划表")
    if args.debug_task is None:
        if os.path.isfile(target):
            target_file = target
        else:
            raise Exception(f"构建目标文件 [target_]{target_name}.yml 不存在")
        # 创建配置

        work_list = read_config(target_file, conan_args)
    else:
        work_list = [
            {
                "name": "test_task",
                "klass": args.debug_task
            }
        ]
    if isinstance(work_list, dict):
        target_cfg = work_list.get("target_config", {})
        config.deal_conf(target_cfg)
        environments = work_list.get("environment", {})
        for key, value in environments.items():
            log.success(f"配置环境变量 {key}: {value}")
            os.environ[key] = value
    # 打印配置
    config.print_config()
    # 打印任务清单
    log.debug(f"任务列表:{work_list}")
    # 创建任务调度器
    if isinstance(work_list, dict):
        subworks = work_list.get("subworks")
        if not subworks or not isinstance(subworks, list):
            raise errors.BmcGoException(f"target文件{target_file}缺少subworks配置")
        return exec_works(target_alias, subworks, "TOP", perf, config, args)
    else:
        return exec_works(target_alias, work_list, "TOP", perf, config, args)
