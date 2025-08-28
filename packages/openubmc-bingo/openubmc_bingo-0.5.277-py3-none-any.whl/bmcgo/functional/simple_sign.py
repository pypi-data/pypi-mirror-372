#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR
import argparse
import os
import json
from http import HTTPStatus

import requests

from bmcgo.utils.tools import Tools
from bmcgo.bmcgo_config import BmcgoConfig
from bmcgo import misc
from bmcgo.errors import BmcGoException, NotFoundException

tools = Tools()
log = tools.log

command_info: misc.CommandInfo = misc.CommandInfo(
    group="Misc commands",
    name="simple_sign",
    description=["使用简易https签名服务器进行文件签名"],
    hidden=True
)


def if_available(_: BmcgoConfig):
    return True


class BmcgoCommand:
    def __init__(self, bconfig: BmcgoConfig, *args):
        self.bconfig = bconfig
        parser = argparse.ArgumentParser(
            prog="bingo simple_sign",
            description="使用简易签名服务器(返回包含signed.cms和rootca.crl的zip包)进行签名",
            add_help=True,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser.add_argument("-i", "--input", help="待签名文件", required=True)
        parser.add_argument("-s", "--signer_id", help="签名证书ID", required=True)
        parser.add_argument("-u", "--url", help="签名服务器签名POST接口url", required=True)
        parser.add_argument("-v", "--verify", help="是否验证HTTPS证书有效性", action=misc.STORE_TRUE)
        parsed_args, _ = parser.parse_known_args(*args)
        self.input = os.path.realpath(os.path.join(os.getcwd(), parsed_args.input))
        self.signer_id = parsed_args.signer_id
        self.url = parsed_args.url
        self.verify = parsed_args.verify
        if not os.path.isfile(self.input):
            raise NotFoundException(f"待签名文件{self.input}不存在")

    def run(self):
        signed_zip = self.sign_file()
        tools.run_command(f"unzip -o {signed_zip}")
        if not os.path.isfile("rootca.crl") or not os.path.isfile("signed.cms"):
            raise NotFoundException("签名服务器返回的zip包中rootca.crl或signed.cms文件不存在。")

    def get_sign_metadata(self):
        token = os.environ.get("SIGN_TOKEN", "")
        metadata = {
            "FileName": os.path.basename(self.input),
            "FileSha256": tools.sha256sum(self.input),
            "CertId": self.signer_id,
            "Token": token,
            "Version": "0",
        }
        return metadata

    def sign_file(self):
        # 组装待签名文件
        files = {"file": ("signed", open(self.input, "rb"), "text/plain")}
        metadata = self.get_sign_metadata()
        data = {"metadata": json.dumps(metadata)}
        # 发起POST请求
        try:
            log.info({"metadata": json.dumps(metadata)})
            response = requests.post(self.url, files=files, data=data, verify=self.verify)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise BmcGoException(f"签名服务器返回错误, 文件 {self.input} 签名失败") from e

        # 接收文件
        if response.status_code == HTTPStatus.OK:
            log.info("签名服务接口返回成功, 正在保存文件...")
            outfile = "signed.zip"
            with open(outfile, "wb") as f:
                f.write(response.content)
            log.info(f"签名结果已保存为：{outfile}")
            return outfile
        else:
            raise BmcGoException(f"签名POST请求失败, 文件 {self.input} 签名失败, 状态码：", response.status_code)


if __name__ == "__main__":
    bconfig = BmcgoConfig()
    sign = BmcgoCommand(bconfig=bconfig)
    sign.run()
