#!/usr/bin/env python3
# encoding=utf-8
# 描述：组件维护工具
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
import argparse
import json
import time
from multiprocessing import Process
import pysftp
import requests
import yaml
import urllib3
from bmcgo.misc import CommandInfo
from bmcgo.utils.tools import Tools
from bmcgo.bmcgo_config import BmcgoConfig

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

tool = Tools("deploy")
log = tool.log
command_info: CommandInfo = CommandInfo(
    group="Misc commands",
    name="deploy",
    description=["产品包部署"],
    hidden=True
)


def if_available(bconfig: BmcgoConfig):
    # 只在二级流水线有效
    return bconfig.component is None


class BmcHostException(Exception):
    def __init__(self, *args, **kwargs):
        super(BmcHostException, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(BmcHostException, self).__str__()


class RestApiException(Exception):
    def __init__(self, *args, **kwargs):
        super(RestApiException, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(RestApiException, self).__str__()


class UpgradeTask(Process):
    def __init__(self, config, cfg_file, filename):
        super().__init__()
        self.host = config.get("ip")
        self.port = config.get("port")
        self.username = config.get("username")
        self.password = config.get("password")
        self.filename = filename
        if self.host is None:
            raise BmcHostException(f"配置文件{cfg_file}缺少ip配置项.")
        if self.port is None:
            self.port = 443
        else:
            self.port = int(self.port)
        if self.username is None:
            raise BmcHostException(f"配置文件{cfg_file}缺少username配置项.")
        if self.host is None:
            raise BmcHostException(f"配置文件{cfg_file}缺少password配置项.")
        if self.port != 443:
            self.base_url = "https://" + self.host + ":" + str(self.port)
        else:
            self.base_url = "https://" + self.host
        self.session = None
        self.request_header = None

    def run(self):
        if self.session is None:
            self._login()
        try:
            self._upload(self.filename)
            if self.filename.endswith(".hpm"):
                self._upgrade(self.filename)
            else:
                log.warning(f"{self.filename}文件名不是以.hpm结尾, 不支持升级.")
        except Exception as e:
            self._logout()
            log.error("部署失败，错误信息:" + str(e))
            return -1
        self._logout()
        return 0

    def _login(self):
        url = f"{self.base_url}/UI/Rest/Login"
        log.info(f"{self.host} >> 登录")
        payload = {
            "UserName": self.username,
            "Password": self.password,
            "Domain": "LocaliBMC",
            "Type": "Local"
        }
        resp = requests.post(url, data=payload, verify=False, timeout=10)
        if resp.status_code != 200:
            raise RestApiException(f"登录失败，登录接口返回状态码 {resp.status_code}.")
        cookies = resp.cookies
        body = json.loads(resp.content)
        scsrf_token = body.get("XCSRFToken")
        self.session = body.get("Session")
        self.request_header = {
            "X-Csrf-Token": scsrf_token,
            "Cookie": "SessionId=" + cookies.get("SessionId")
        }

    def _upload_by_sftp(self, filename):
        log.info(f"{self.host} >> 尝试使用sftp接口上传文件")
        with pysftp.Connection(self.host, username=self.username, password=self.password) as sftp:
            sftp.makedirs('/tmp/web')
            with sftp.cd('/tmp/web'):
                sftp.put(filename)

    def _upload(self, filename):
        log.info(f"{self.host} >> 上传文件 {filename} 至 /tmp/web/{os.path.basename(filename)}")
        url = f"{self.base_url}/UI/Rest/FirmwareInventory"
        files = {
            "imgfile": open(filename, 'rb')
        }
        resp = requests.post(url, files=files, headers=self.request_header, verify=False, timeout=300)
        if resp.status_code == 200:
            return
        log.warning(f"{self.host} >> 使用Rest接口上传{filename}失败，返回状态码 {resp.status_code}.")
        self._upload_by_sftp(filename)

    def _upgrade(self, filename):
        log.info(f"{self.host} >> 调用接口启动升级")
        url = f"{self.base_url}/UI/Rest/BMCSettings/UpdateService/FirmwareUpdate"
        payload = {
            "FilePath": os.path.join("/tmp/web/", os.path.basename(filename))
        }
        resp = requests.post(url, data=payload, headers=self.request_header, verify=False, timeout=10)
        if resp.status_code != 200:
            raise BmcHostException(f"升级{self.host}失败，Rest接口返回状态码 {resp.status_code}, 响应: {resp.content.decode()}.")
        body = json.loads(resp.content)
        url = self.base_url + body.get("url")
        log.info(f"{self.host} >> 启动升级成功，开始检测升级状态")
        sleep_sec = 1
        progress = 0
        while True:
            time.sleep(sleep_sec)
            resp = requests.get(url, headers=self.request_header, verify=False)
            if resp.status_code != 200:
                log.warning(f"{self.host} >> 轮询升级状态失败，Rest接口返回状态码 {resp.status_code}，升级可能失败，请自检.")
                break
            body = json.loads(resp.content)
            state = body.get("state")
            if state in ["Exception", "Suspended", "Interrupted", "Pending", "Killed", "Cancelled"]:
                raise BmcHostException(f"{self.host} >> 升级状态接口返回状态异常{state}，升级失败")
            if state == "Completed":
                log.info(f"{self.host} >> 升级状态接口返回Completed状态")
                return
            if state not in ["Starting", "New", "Running"]:
                raise BmcHostException(f"{self.host} >> 升级状态接口返回未知的{state}状态，升级可能失败，请自检.")
            new_progress = int(body.get("prepare_progress"))
            if new_progress != progress:
                log.info(f"{self.host} >> 升级进度：{new_progress}")
                progress = new_progress
            if sleep_sec <= 2:
                sleep_sec += 0.1

    def _logout(self):
        log.info(f"{self.host} >> 退出登录")
        session_id = self.session.get("SessionID")
        url = f"{self.base_url}/UI/Rest/Sessions/" + session_id
        resp = requests.delete(url, headers=self.request_header, verify=False, timeout=10)
        if resp.status_code != 200:
            log.error(f"{self.host} >> 退出登录失败, status code {resp.status_code}")


class BmcgoCommand:
    def __init__(self, bconfig: BmcgoConfig, *args):
        self.bconfig = bconfig
        parser = argparse.ArgumentParser(prog="bingo deploy", description="BMC产品包部署升级，待部署主机配置由bmcgo config命令管理",
                                         add_help=True, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-f", "--filename", help="待部署的文件", required=True)
        parsed_args = parser.parse_args(*args)
        self.filename = os.path.realpath(parsed_args.filename)
        if not os.path.isfile(self.filename):
            raise argparse.ArgumentError(f"file {parsed_args.filename} not exist")

    @staticmethod
    def _calc_checksum():
        pass

    def run(self):
        tasks = self._read_hosts()
        if len(tasks) == 0:
            log.warning("未找到可用的部署配置")
            return
        if len(tasks) == 1:
            tasks[0].run()
            return
        for task in tasks:
            task.start()
        while len(tasks) > 0:
            time.sleep(1)
            for task in tasks:
                if task.is_alive():
                    continue
                if task.exitcode is not None and task.exitcode != 0:
                    log.error(f"{task.host} >> 升级失败")
                else:
                    log.success(f"{task.host} >> 升级完成")
                tasks.remove(task)
        log.warning("部署过程受账号、网络、会话、代理、存储、设备状态等多方面影响，失败问题需要使用者自己定位，构建工程不提供直接支持。")

    def _read_hosts(self):
        tasks: list[UpgradeTask] = []
        tasks = self._read_yml_hosts()
        if tasks:
            return tasks
        tasks = self._read_config_hosts()
        return tasks

    def _read_yml_hosts(self):
        tasks: list[UpgradeTask] = []
        cur_dir = os.getcwd()
        log.info("从当前路径开始向上递归查找.openUBMC_config.yml文件")
        while cur_dir != "/":
            cfg_file = os.path.join(cur_dir, ".openUBMC_config.yml")
            if not os.path.isfile(cfg_file):
                cur_dir = os.path.dirname(cur_dir)
                continue
            log.info(f"读取配置文件 {cfg_file}")
            with open(cfg_file, "r") as fp:
                config = yaml.safe_load(fp)
            hosts = config.get("hosts", None)
            if hosts is None:
                log.warning(f"配置文件 {cfg_file} 未配置hosts对象")
                continue
            if isinstance(hosts, list):
                for conf in hosts:
                    tasks.append(UpgradeTask(conf, cfg_file, self.filename))
            elif isinstance(hosts, object):
                tasks.append(UpgradeTask(hosts, cfg_file, self.filename))
            return tasks
        return []

    def _read_config_hosts(self):
        tasks: list[UpgradeTask] = []
        for item in filter(lambda x: x.startswith("deploy-"), self.bconfig.bmcgo_config_list.keys()):
            cfg_file = item
            conf = {}
            conf["ip"] = item.split('-')[1]
            for k, v in self.bconfig.bmcgo_config_list[item].items():
                conf[k] = v
            tasks.append(UpgradeTask(conf, cfg_file, self.filename))
        return tasks
