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

import logging
import re
import os
import inspect
from colorama import Fore, Back, Style


class CustomFormatter(logging.Formatter):
    def custformat(self, log_level):
        # CI 不打印格式化字符串
        if os.getenv("CLOUD_BUILD_RECORD_ID") is not None:
            formatter = "{message}"
            formats = {
                logging.DEBUG: formatter,
                logging.INFO: formatter,
                logging.WARNING: "WARN: " + formatter,
                logging.ERROR: "ERROR: " + formatter,
                logging.CRITICAL: "CRITICAL: " + formatter
            }
        # 本地未设置打印级别
        elif os.getenv("LOG") is None:
            formatter = "{message}"
            formats = {
                logging.DEBUG: formatter,
                logging.INFO: formatter,
                logging.WARNING: Fore.YELLOW + "WARN: " + formatter + Style.RESET_ALL,
                logging.ERROR: Fore.RED + "ERROR: " + formatter + Style.RESET_ALL,
                logging.CRITICAL: Fore.RED + "CRITICAL: " + formatter + Style.RESET_ALL
            }
        # 本地设置打印级别
        else:
            # 自定义格式化
            formatter = "[{asctime} {levelname}] {message}"
            formats = {
                logging.DEBUG: formatter,
                logging.INFO: formatter,
                logging.WARNING: Fore.YELLOW + formatter + Style.RESET_ALL,
                logging.ERROR: Fore.RED + formatter + Style.RESET_ALL,
                logging.CRITICAL: Fore.RED + formatter + Style.RESET_ALL
            }
        return formats.get(log_level)

    # 格式化重写
    def format(self, record):
        log_fmt = self.custformat(record.levelno)
        formatter = logging.Formatter(log_fmt, style='{')
        return formatter.format(record)


class Logger(logging.Logger):
    def __init__(self, name="bmcgo", level=logging.INFO, log_file=None):
        """初始化一个日志记录器

        Args:
            name (str): 记录器的名字
            level (int): 记录器日志级别

        Returns:
            logger: 返回日志记录器对象
        """
        super().__init__(name)
        self.log_level_env = os.environ.get("LOG")
        self.ci_env = os.getenv("CLOUD_BUILD_RECORD_ID")
        formatter = CustomFormatter()
        if log_file:
            ch = logging.FileHandler(filename=log_file)
            ch.setFormatter(formatter)
            self.addHandler(ch)
        self.is_debug = True
        if self.log_level_env == "info":
            self.setLevel(logging.INFO)
        elif self.log_level_env == "warn":
            self.setLevel(logging.WARNING)
        elif self.log_level_env == "error":
            self.setLevel(logging.ERROR)
        elif self.log_level_env == "debug":
            self.setLevel(logging.DEBUG)
        else:
            self.is_debug = False
            self.setLevel(level)
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.addHandler(ch)
        # 匹配关键字
        self.tip_msg = "|".join(["error", "failed", "unknown", "unable", "couldn't",
        "invalid", "unexpected", "TypeError"])
        # 判断是否包含关键字，且前后不能紧跟单词下划线和换行,或者前后紧跟换行但不匹配换行符,或以关键词开头结尾
        self.error_pattern = re.compile((f'((?:^|(?<=\n)|.*[^\w\n])(?:{self.tip_msg})(?:[^\w\n].*|(?=\n)|$))'), re.I)

    def error(self, msg, *args, **kwargs):
        uptrace = kwargs.get("uptrace", None)
        if uptrace is None:
            uptrace = 1
        else:
            uptrace += 1
            del kwargs["uptrace"]
        msg = self._format_msg(msg, uptrace)
        return super().error(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        uptrace = kwargs.get("uptrace", None)
        if uptrace is None:
            uptrace = 1
        else:
            uptrace += 1
            del kwargs["uptrace"]
        msg = str(msg)
        match = re.findall(self.error_pattern, msg)
        if match:
            msg = self.set_tip_msg(msg)
        msg = self._format_msg(msg, uptrace)
        return super().info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        uptrace = kwargs.get("uptrace", None)
        if uptrace is None:
            uptrace = 1
        else:
            uptrace += 1
            del kwargs["uptrace"]
        msg = self._format_msg(msg, uptrace)
        return super().debug(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        uptrace = kwargs.get("uptrace", None)
        if uptrace is None:
            uptrace = 1
        else:
            uptrace += 1
            del kwargs["uptrace"]
        msg = self._format_msg(msg, uptrace)
        return super().warning(msg, *args, **kwargs)

    def success(self, msg, *args, **kwargs):
        uptrace = kwargs.get("uptrace", None)
        if uptrace is None:
            uptrace = 1
        else:
            uptrace += 1
            del kwargs["uptrace"]
        if self.log_level_env is not None or self.ci_env is None:
            msg = Fore.GREEN + self._format_msg(msg, uptrace) + Style.RESET_ALL
        else:
            msg = self._format_msg(msg, uptrace)
        return super().info(msg, *args, **kwargs)

    def set_tip_msg(self, msg):
        msgs = re.split(self.error_pattern, msg)
        tip_msg = ""
        # 循环正则切割后的内容，在有关键词的内容添加背景色
        for item in msgs:
            if re.findall(self.error_pattern, item):
                tip_msg = f"{tip_msg}{Back.YELLOW}{item}{Style.RESET_ALL}"
            else:
                tip_msg = f"{tip_msg}{item}"
        return tip_msg

    def _format_msg(self, msg, uptrace):
        if self.is_debug:
            stack = inspect.stack()[uptrace + 1]
            filename = os.path.basename(stack.filename)
            return f"{filename}:{stack.lineno} {msg}"
        return msg
