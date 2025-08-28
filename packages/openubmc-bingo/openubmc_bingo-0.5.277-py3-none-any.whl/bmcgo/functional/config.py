#!/usr/bin/env python3
# encoding=utf-8
# 描述：bingo 配置默认参数功能
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import os
import stat
import re
import argparse
from pathlib import Path

from bmcgo import misc
from bmcgo.utils.tools import Tools
from bmcgo.bmcgo_config import BmcgoConfig


tool = Tools("config")
log = tool.log

command_info: misc.CommandInfo = misc.CommandInfo(
    group=misc.GRP_MISC,
    name="config",
    description=["bingo参数配置"],
    hidden=False
)


def if_available(bconfig: BmcgoConfig):
    return True


_CONFIGS = {
    misc.ENV_CONST: {
        misc.HTTP_PROXY_CONST: {
            misc.DESCRIPTION: "bingo 使用的 http_proxy 环境变量",
            misc.PATTERN: r"^((https?://)?[a-zA-Z0-9.]+:[0-9]+)?$"
        },
        misc.HTTPS_PROXY_CONST: {
            misc.DESCRIPTION: "bingo 使用的 https_proxy 环境变量",
            misc.PATTERN: r"^((https?://)?[a-zA-Z0-9.]+:[0-9]+)?$"
        },
        misc.FTP_PROXY_CONST: {
            misc.DESCRIPTION: "bingo 使用的 ftp_proxy 环境变量",
            misc.PATTERN: r"^((https?://)?[a-zA-Z0-9.]+:[0-9]+)?$"
        },
        misc.NO_PROXY_CONST: {
            misc.DESCRIPTION: "bingo 使用的 no_proxy 环境变量"
        },
        misc.TIMESTAMP_SIGN_SERVER: {
            misc.DESCRIPTION: "用于 jar 文件签名的时间戳签名服务器环境变量",
            misc.PATTERN: r"^https?://[^ ]+"
        },
        misc.JARSIGNER_HTTP_PROXY: {
            misc.DESCRIPTION: "",
            misc.PATTERN: r"^((https?://)?[a-zA-Z0-9.]+:[0-9]+)?$"
        },
        misc.JSON_CHECKER: {
            misc.DESCRIPTION: "检查 json 文件的工具"
        },
        misc.CUSTOM_PLUGINS: {
            misc.DESCRIPTION: f"设置插件地址，默认 {Path(misc.DEFAULT_PLUGINS_PATH).resolve()}"
        }
    },
    misc.DEPLOY_HOST_CONST: {
        misc.PORT_CONST: {
            misc.DESCRIPTION: "https 端口号，默认 443",
            misc.PATTERN: r"^\d+$"
        },
        misc.USERNAME_CONST: {
            misc.DESCRIPTION: "用户名"
        },
        misc.PASSWORD_CONST: {
            misc.DESCRIPTION: "密码"
        }
    }
}


def gen_conf_str():
    conf_str = ["可用配置:"]
    for group, secs in _CONFIGS.items():
        for sec, info in secs.items():
            desc = info[misc.DESCRIPTION]
            conf_str.append(f"\t{group}.{sec} : {desc}")
    return "\n".join(conf_str)


_DESCRIPTION = f"""
配置文件类型:
1. 系统级配置文件：{misc.GLOBAL_CFG_FILE}（只读）
2. 全局配置文件: ~/.bmcgo/config
3. 本地配置文件: .bmcgo/config
{gen_conf_str()}
- 通过 bingo config 设置的环境变量(env.x)会写入到环境变量配置文件中。
指令参考:
1. 配置全局参数:
    bingo config env.{misc.HTTP_PROXY_CONST}=http://proxy.example.com:8080
2. 配置本地参数:
    bingo config --local env.{misc.HTTP_PROXY_CONST}=http://proxy.example.com:8080
3. 查看生效配置:
    bingo config -l
4. 取消全局参数配置:
    bingo config --unset env.{misc.HTTP_PROXY_CONST}
5. 取消本地参数配置:
    bingo config --local --unset env.{misc.HTTP_PROXY_CONST}
6. 设置时间戳签名服务器:
    bingo config env.{misc.TIMESTAMP_SIGN_SERVER}=http://url.example.com
7. 设置 JarSigner HTTP 代理主机:
    bingo config env.{misc.JARSIGNER_HTTP_PROXY}=http://proxy.example.com:8080
8. 设置部署配置: 
    格式: bingo config deploy-<host>.<port|username|password>=<value>. host 既可以是主机名也可以是域名或 IP
    bingo config deploy-192.168.1.1.port=443
    bingo config deploy-192.168.1.1.username=UserName
    bingo config deploy-192.168.1.1.password=Password
"""


def save_config_file(config, config_path):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with os.fdopen(
        os.open(config_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH), 
        "w"
    ) as f:
        config.write(f)


class BmcgoCommand:
    def __init__(self, bconfig: BmcgoConfig, *args):
        self.parser = argparse.ArgumentParser(
            prog="bingo参数配置",
            description=_DESCRIPTION,
            add_help=True,
            formatter_class=argparse.RawTextHelpFormatter
        )
        self.parser.add_argument(
            "-l",
            "--list",
            action=misc.STORE_TRUE,
            help="列出所有配置"
        )
        self.parser.add_argument(
            "--unset",
            action=misc.STORE_TRUE,
            help="取消配置参数"
        )
        self.parser.add_argument(
            "--local",
            action=misc.STORE_TRUE,
            help="本地配置模式"
        )

        self.bconfig = bconfig
        self.args, self.kwargs = self.parser.parse_known_args(*args)

    def run(self):
        if self.args.list:
            return self._display_configs()
        
        if self.args.unset:
            return self._unset_configs()

        if len(self.kwargs) == 1 and "=" not in self.kwargs[0]:
            return self._display_config()

        return self._set_configs()

    def _display_configs(self):
        if self.args.unset or self.args.local or len(self.kwargs) > 0:
            log.error("--list 不能和其他参数一起使用！")
            return -2

        log.info("配置参数:")
        for section, k_v_ls in self.bconfig.bmcgo_config_list.items():
            for k, v in k_v_ls.items():
                log.info(f"{section}.{k}={v}")
        return 0

    def _unset_configs(self):
        config, config_path = self._get_config_path()

        is_dirty = False
        for key in self.kwargs:
            if "." not in key:
                log.error(f"无效键值:{key}")
                return -2
            
            section, k = key.rsplit(".", 1)
            if section in config.sections():
                if not is_dirty:
                    is_dirty = True
                config.remove_option(section, k)
                if not config.options(section):
                    config.remove_section(section)

        if is_dirty:
            save_config_file(config, config_path)
        return 0

    def _display_config(self):
        key = self.kwargs[0]
        if "." not in key:
            log.error(f"无效键值:{key}")
            log.info(gen_conf_str())
            return -2
        
        section, k = key.rsplit(".", 1)
        section = section.lower()
        k = k.lower()

        if section.startswith("deploy-"):
            section = misc.DEPLOY_HOST_CONST

        info = _CONFIGS.get(section, {}).get(k, None)
        if info is None:
            log.error(f"无效键值: {key}")
            log.info(gen_conf_str())
            return -2

        v = self.bconfig.bmcgo_config_list.get(section, {}).get(k, None)
        if v is not None:
            log.info(f"{section}.{k}={v}")
        return 0

    def _set_configs(self):
        params = self._parse_arguments()
        if params is None:
            return -2
        
        if not self._check_param_valid(params):
            return -2
        
        config, config_path = self._get_config_path()

        for k, v in params.items():
            sec, key = k.rsplit(".", 1)
            sec = sec.lower()
            key = key.lower()
            
            if sec not in config.sections():
                config.add_section(sec)
            config.set(sec, key, v)

        save_config_file(config, config_path)

        return 0

    def _parse_arguments(self):
        params = {}
        index = 0
        length = len(self.kwargs)

        while index < length:
            current = self.kwargs[index]
            if current.startswith(('"', "'")):
                quote_char = current[0]
                val_parts = [current[1:]]

                index += 1
                while index < length and not self.kwargs[index].endswith(quote_char):
                    val_parts.append(self.kwargs[index])
                    index += 1

                if index >= length:
                    log.error(f"未闭合的引号: {current}")
                    return None
                
                last_part = self.kwargs[index]
                val_parts.append(last_part[:-1])
                full_value = " ".join(val_parts)

                if index == 0:
                    log.error(f"参数{full_value}缺少键值！")
                    return None
                
                params[key] = full_value
                index += 1
                continue

            if "=" in current:
                key, value = current.split("=", 1)
                params[key] = value
                index += 1
            else:
                if index + 1 >= length:
                    log.error(f"参数{current}缺少键值！")
                    return None
                
                params[current] = self.kwargs[index + 1]
                index += 2

        return params
    
    def _check_param_valid(self, params):
        if not params:
            self.parser.print_help()
            return False
            
        for k, v in params.items():
            if "." not in k:
                log.error(f"不可用配置项: {k}.")
                log.info(gen_conf_str())
                return False

            sec, key = k.rsplit(".", 1)
            sec = sec.lower()
            key = key.lower()

            if sec.startswith("deploy-"):
                sec = misc.DEPLOY_HOST_CONST

            info = _CONFIGS.get(sec, {}).get(key, None)
            if info is None:
                log.error(f"不可用配置项: {k}.")
                log.info(gen_conf_str())
                return False
            
            pattern = info.get(misc.PATTERN, None)
            if pattern:
                if not re.match(pattern, v):
                    log.error(f"{v} 不满足正则表达式: {pattern}")
                    return False
            
        return True

    def _get_config_path(self):
        if self.args.local:
            config = self.bconfig.bmcgo_local_config
            config_path = self.bconfig.bmcgo_local_config_path
        else:
            config = self.bconfig.bmcgo_global_config
            config_path = self.bconfig.bmcgo_global_config_path
        return config, config_path