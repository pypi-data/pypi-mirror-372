#!/usr/bin/env python3
# encoding=utf-8
# 描述：CSR构建出包
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
import json
import re
import argparse
import shutil
import gzip
import io
import stat
import binascii
import hashlib
import tempfile
import subprocess
from enum import Enum
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone, timedelta
import ecdsa
import json5
import requests
from bmcgo import misc
from bmcgo import errors
from bmcgo.misc import CommandInfo
from bmcgo.utils.tools import Tools
from bmcgo.utils.buffer import Buffer
from bmcgo.utils.merge_csr import Merger
from bmcgo.bmcgo_config import BmcgoConfig
from bmcgo.functional.simple_sign import BmcgoCommand as SimpleSign


tool = Tools("csr_build")
log = tool.log
cwd = os.getcwd()

SR_UPGRADE = "SRUpgrade"
TIANCHI = "bmc.dev.Board.TianChi"
HPM_PACK_PATH = "/usr/share/bmcgo/csr_packet"
EEPROM_SIZE_LIMIT_CONFIG = "/usr/share/bmcgo/schema/eepromSizeLimit.json"

JSON_DATA_FORMAT = 0x01
SR_UID_MAX_LENGTH = 24
DEFAULT_EEPROM_SIZE_LIMIT = 32

# 需要兼容的组件UID列表
LEGACY_UIDS = [
    "00000001050302023924", "00000001030302023925", "00000001040302023945",
    "00000001040302023947", "00000001030302024340", "00000001030302023936",
    "00000001030302023938", "00000001100302023955", "00000001100302023956", 
    "00000001040302052957", "00000001100302025549", "00000001030302023934"
]


class SignatureTypeEnum(Enum):
    SERVER_SIGN = "server_sign"
    SELF_SIGN = "self_sign"
    DEFAULT = "default"


class SignInfo:
    def __init__(self, sign_data: bytearray):
        # 哈希SHA256算法码
        self.sign_hash_code = 0x00
        # ECC签名算法码
        self.sign_algorithm_code = 0x00
        # ECC签名算法曲线ID
        self.sign_curve_id = 415
        self.sign_length = len(sign_data)
        self.sign_content = sign_data


class CsrHeader:
    def __init__(self, csr_head_len, csr_bytes_arr):
        self.csr_max_count = 4
        self.csr_ver = 0x01
        self.padding = 0x0000
        self.csr_count = 0
        self.csr_offset = Buffer(self.csr_max_count * 2)
        self.offset = csr_head_len // 8

        for i in range(self.csr_max_count):
            csr_bytes = csr_bytes_arr[i]
            if csr_bytes:
                self.csr_offset.put_uint16(self.offset)
                self.offset += len(csr_bytes) // 8
                self.csr_count += 1
            else:
                self.csr_offset.put_uint16(0x00)


class SrMakeOptions:
    def __init__(self, comp_name: str, sr_json: dict, oem_data: bytearray):
        self.comp_name = comp_name
        self.sr_json = sr_json
        self.oem_data = oem_data
        self.uid = self.get_uid(sr_json)
        self.binary_names = [self.uid]

    def find_uid_from_object(self, parent, key, obj):
        if key == TIANCHI:
            if "UID" in obj:
                return obj["UID"]
            if "UID" in parent:
                return parent["UID"]
        for obj_key, value in obj.items():
            if isinstance(value, dict):
                ret = self.find_uid_from_object(obj, obj_key, value)
                if ret:
                    return ret
        return ""

    def get_uid(self, sr_json):
        component_id = ""
        if "Objects" not in sr_json:
            raise Exception(f"'Objects' not found in sr file")
        objects = sr_json["Objects"]
        for key in objects:
            if re.fullmatch(r"SRUpgrade_\d", key):
                if "UID" in objects[key]:
                    component_id = objects[key]["UID"]
                break
        if not component_id:
            for key in objects:
                ret = self.find_uid_from_object(objects, key, objects[key])
                if ret:
                    component_id = ret
                    break
        if not component_id:
            raise Exception(f"未在{self.comp_name}文件中找到UID，没有UID的文件不支持出包。")
        if len(component_id) > SR_UID_MAX_LENGTH:
            raise Exception(f"{self.comp_name}文件UID超过最大长度，无法出包。")
        return component_id


def if_available(bconfig: BmcgoConfig):
    return (
        bconfig.component is None and bconfig.conan_index is None and
        bconfig.manifest is None
    )

command_info: CommandInfo = CommandInfo(
    group=misc.GRP_MISC,
    name="build",
    description=["CSR构建出包"],
    hidden=False
)


class BmcgoCommand:
    def __init__(self, bconfig: BmcgoConfig, *args):
        self.bconfig = bconfig
        parser = argparse.ArgumentParser(
            prog="bingo build_csr",
            description="csr出包，支持单个CSR和批量CSR出包",
            add_help=True,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser.add_argument("-s", "--single", help="指定单个CSR文件出包，默认为批量出包", action=misc.STORE_TRUE, default=False)
        parser.add_argument("-p", "--path", help="单CSR出包时指定CSR文件路径，批量出包时指定CSR文件和OEM文件所在目录\n默认为当前路径", default=cwd)
        parser.add_argument("-o", "--output_path", help="构建产物（hpm包或tar.gz压缩包）路径\n默认为当前路径", default=cwd)
        parser.add_argument("--oem", help="单CSR出包携带OEM文件的路径，仅-s模式下有效", default=None)
        parser.add_argument("--hpm", help="单CSR出包生成hpm文件，仅-s模式下有效", action=misc.STORE_TRUE, default=False)
        parser.add_argument("-b", "--bin", help="单CSR出包生成bin文件，仅-s模式下有效", action=misc.STORE_TRUE, default=False)
        parser.add_argument("-u", "--uid", help="指定UID生成二进制文件，多个uid以','分隔，仅-s模式下有效", default=None)
        parser.add_argument("-f", "--frud", help="指定打包frud文件，跳过白名单校验", action=misc.STORE_TRUE, default=False)
        parser.add_argument("-a", "--all", help="快捷携带-j、-b、--hpm参数，仅-s下有效", action=misc.STORE_TRUE, default=False)
        parser.add_argument("-t", "--tar", help="指定批量出包生成tar包，携带bin和hpm文件", action=misc.STORE_TRUE, default=False)
        parser.add_argument(
            "-j",
            "--json",
            help="单CSR出包生成json文件，仅在-s模式下有效",
            action=misc.STORE_TRUE,
            default=False
        )
        parser.add_argument(
            "-m",
            "--max_config",
            help="eeprom大小限制的json配置文件路径，无配置时默认限制为32k",
            default=EEPROM_SIZE_LIMIT_CONFIG
        )
        parsed_args, _ = parser.parse_known_args(*args)
        self.csr_path = os.path.realpath(parsed_args.path)
        self.single = parsed_args.single
        self.oem_path = parsed_args.oem
        self.output_path = os.path.realpath(parsed_args.output_path)
        self.json = parsed_args.json
        self.bin = parsed_args.bin
        self.hpm = parsed_args.hpm
        self.all = parsed_args.all
        self.tar = parsed_args.tar
        self.frud = parsed_args.frud
        self.max_size_map = parsed_args.max_config
        self.uid = parsed_args.uid
        self.work_dir = None
        self.target_dir = None
        self.eeprom_sign_strategy = None
        self.hpm_sign_strategy = None
        self.tmp_dir = None
        self.merger = Merger(self.output_path)

    @staticmethod
    def get_oem_data(dir_path: str, comp_name: str):
        oem_file = f'oem_{comp_name}.bin'
        oem_file_path = os.path.join(dir_path, oem_file)
        oem_data = bytearray()
        if os.path.exists(oem_file_path):
            with open(oem_file_path, 'rb') as f:
                oem_data = bytearray(f.read())
        return oem_data
    
    @staticmethod
    def check_uid(options_list):
        bin_names = set()
        for options in options_list:
            for name in options.binary_names:
                if name in bin_names:
                    raise Exception(f"存在重复的UID: {name}， 出包失败！")
                bin_names.add(name)
    
    @staticmethod
    def is_valid_json_path(path_str):
        if path_str == EEPROM_SIZE_LIMIT_CONFIG:
            return True
        path = Path(path_str)
        basic_check = path.is_file() and path.suffix.lower() == '.json'
        if not basic_check:
            return False
        try:
            with open(path, 'r', encoding='utf-8-sig') as json_file:
                json5.load(json_file)
            return True
        except (json.JSONDecodeError, UnicodeDecodeError, IOError):
            return False

    def get_eeprom_sign_strategy(self):
        if self.bconfig.e2p_server_sign:
            eeprom_sign_strategy = SignatureTypeEnum.SERVER_SIGN
        elif self.bconfig.e2p_self_sign:
            eeprom_sign_strategy = SignatureTypeEnum.SELF_SIGN
        else:
            eeprom_sign_strategy = SignatureTypeEnum.DEFAULT
        self.eeprom_sign_strategy = eeprom_sign_strategy
        log.info(f"eeprom签名使用 {eeprom_sign_strategy.value} 方法")
    
    def get_hpm_sign_strategy(self):
        if self.bconfig.hpm_server_sign:
            hpm_sign_strategy = SignatureTypeEnum.SERVER_SIGN
        elif self.bconfig.hpm_self_sign:
            hpm_sign_strategy = SignatureTypeEnum.SELF_SIGN
        else:
            hpm_sign_strategy = SignatureTypeEnum.DEFAULT
        self.hpm_sign_strategy = hpm_sign_strategy
        log.info(f"hpm签名使用 {hpm_sign_strategy.value} 方法")
             
    def get_sign_strategy(self):
        log.info("开始获取签名策略配置信息...")
        self.get_eeprom_sign_strategy()
        self.get_hpm_sign_strategy()
    
    def make_sr_binary(self, options: SrMakeOptions, hpm_temp_dir: str, max_size: int):
        eeprom_build_controller = EepromBuild(self.bconfig, options, self.work_dir, self.eeprom_sign_strategy)
        eeprom_data = eeprom_build_controller.build_eeprom()
        if len(eeprom_data) > max_size * 1024 - 40:
            raise errors.BmcGoException(f"Eeprom二进制文件大小超过限制: {options.comp_name}")
        binary_files = []
        for name in options.binary_names:
            binary_files.append(os.path.join(hpm_temp_dir, f"{name}.bin"))
            if self.bin or self.all or self.tar:
                log.info(f"生成{name}.bin文件...")
                binary_files.append(os.path.join(self.target_dir, f"{name}.bin"))
            if self.uid:
                uid_list = str(self.uid).split(',')
                for uid in uid_list:
                    log.info(f"生成{uid}.bin文件...")
                    binary_files.append(os.path.join(hpm_temp_dir, f"{uid}.bin"))
            if name not in LEGACY_UIDS and not self.frud:
                continue
            binary_files.append(os.path.join(hpm_temp_dir, f"{name}.frud"))
            log.info(f"生成{name}.frud文件...")
            if self.bin or self.all or self.frud:
                binary_files.append(os.path.join(self.target_dir, f"{name}.frud"))
        with open(binary_files[0], 'wb') as f:
            f.write(eeprom_data)
        for binary_file in binary_files[1:]:
            shutil.copy(binary_files[0], binary_file)

    def run(self):
        self.check_args()
        tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = tmp.name
        self.merger.update_tmp_dir(self.tmp_dir)
        if not os.path.exists(self.output_path):
            raise Exception(f"输出路径{self.output_path}不存在")
        sr_make_options_list = []
        if self.single:
            sr_make_options_list = self.get_sr_file_and_oem()
        else:
            sr_make_options_list = self.get_sr_files()
            if len(sr_make_options_list) == 0:  
                log.info("目录下不存在sr文件!")
                return
            log.info("进行SR文件UID唯一性验证...")
            self.check_uid(sr_make_options_list)
        self.get_sign_strategy()
        try:
            self.work_dir = tempfile.TemporaryDirectory().name
            self.target_dir = os.path.join(self.work_dir, "target")
            os.makedirs(self.target_dir, exist_ok=True)
            hpm_temp_dir = os.path.join(self.work_dir, "hpm_temp")
            os.makedirs(hpm_temp_dir, exist_ok=True)
            self.make_eeprom(hpm_temp_dir, sr_make_options_list)
            if not self.single or self.hpm or self.all: 
                if len(sr_make_options_list) == 1:
                    hpm_file = os.path.join(self.target_dir, f"{sr_make_options_list[0].comp_name}.hpm")
                else:
                    hpm_file = os.path.join(self.target_dir, f"CSR-{get_timestamp()}.hpm")
                params = (self.bconfig, hpm_file, self.work_dir, self.hpm_sign_strategy)
                hpm_package = HpmBuild(*params)
                log.info("开始执行hpm包构建任务...")
                hpm_package.run()
            if self.single or self.frud or self.tar:
                output_file = os.path.join(self.output_path, f"bingo-{get_timestamp()}.tar.gz")
                tar_command = ['tar', '-czf', output_file, "-C", self.target_dir, "."]
                try:
                    result = subprocess.run(tar_command, check=True)
                    log.info(f"成功创建压缩包{os.path.basename(output_file)}")
                except subprocess.CalledProcessError as e:
                    log.info(f"创建压缩包时出错，错误原因：{str(e)}")
            else:
                output_hpm_file = os.path.join(self.output_path, os.path.basename(hpm_file))
                shutil.copy(hpm_file, output_hpm_file)
            log.info("构建成功!")
        finally:
            if os.path.exists(self.work_dir):
                shutil.rmtree(self.work_dir)
            if os.path.exists(self.tmp_dir):
                shutil.rmtree(self.tmp_dir)

    def check_args(self):
        has_single_need_arg = self.bin or self.json or self.hpm or self.all
        if not self.single:
            if self.oem_path or self.uid or has_single_need_arg:
                raise Exception("以下参数仅在单个CSR出包模式（-s，--single）下有效：[--oem, --hpm, -j, -b, -u, -a]，请检查命令！")
        elif not has_single_need_arg:
            raise Exception("以下参数需至少携带一个：[--bin, --json, --hpm]， 可使用--all/-a指定所有选项。 执行bingo build -h查看详细参数说明")
        if not self.is_valid_json_path(self.max_size_map):
            raise Exception(f"无效的JSON文件路径：{self.max_size_map}")

    def get_sr_file_and_oem(self):
        sr_make_options_list = []
        csr_path = self.merger.get_single_csr(self.csr_path)
        oem_path = self.oem_path
        oem_data = bytearray()
        if not os.path.exists(csr_path):
            raise FileNotFoundError(f"路径 {csr_path} 不存在")
        if not os.path.isfile(csr_path):
            raise Exception(f"{csr_path} 不是一个文件路径")
        _, csr_ext = os.path.splitext(csr_path)
        if not csr_ext == ".sr":
            raise Exception(f"{csr_path} 不是一个有效的CSR文件")
        log.info("开始执行单个CSR出包任务...")
        log.info(f"执行出包的sr文件路径：{csr_path}")
        if oem_path:
            if not os.path.exists(oem_path):
                raise FileNotFoundError(f"OEM文件路径 {oem_path} 不存在")
            if not os.path.isfile(oem_path):
                raise Exception(f"{oem_path} 不是一个文件路径")
            _, oem_ext = os.path.splitext(oem_path)
            if not oem_ext == ".bin":
                raise Exception(f"OEM文件{oem_path} 应为.bin文件")
            with open(oem_path, 'rb') as f:
                oem_data = bytearray(f.read())
        name = os.path.basename(csr_path)
        comp_name = os.path.splitext(name)[0]
        with open(csr_path, 'r') as f:
            sr_json = json5.load(f)
        sr_make_options_list.append(SrMakeOptions(comp_name, sr_json, oem_data))
        return sr_make_options_list

    def get_sr_files(self):
        dir_path = Path(self.csr_path)
        sr_files = self.merger.get_multi_files(dir_path)
        sr_num = len(sr_files)
        if sr_num == 1:
            log.info("开始执行CSR出包任务...")
        elif sr_num > 1:
            log.info(f"开始执行CSR批量出包任务...共打包{sr_num}个文件")
        sr_make_options_list = []
        for sr_file in sr_files:
            name = os.path.basename(sr_file)
            log.info(f"执行出包的sr文件：{name}")
            comp_name = os.path.splitext(name)[0]
            with open(sr_file, 'r') as f:
                sr_json = json5.load(f)
            oem_data = self.get_oem_data(dir_path, comp_name)
            sr_make_options = SrMakeOptions(comp_name, sr_json, oem_data)
            sr_make_options_list.append(sr_make_options)
        return sr_make_options_list

    def make_eeprom(self, hpm_temp_dir, sr_make_options_list):
        flag = False
        if os.path.exists(self.max_size_map):
            with open(self.max_size_map, 'r') as f:
                max_size_map = json.load(f)
        else:
            flag = True
            log.info("设定eeprom大小限制为默认值（32kb）")
        for options in sr_make_options_list:
            if self.json or self.all:
                log.info(f"生成{options.comp_name}.sr文件...")
                sr_file = os.path.join(self.target_dir, f"{options.comp_name}.sr")
                json_str = json.dumps(options.sr_json, ensure_ascii=False, indent=4)
                with open(sr_file, 'w', encoding='utf-8') as f:
                    f.write(json_str)
            if not self.do_build_eeprom():
                continue
            if flag:
                max_eeprom_size = DEFAULT_EEPROM_SIZE_LIMIT
            else:
                max_eeprom_size = max_size_map.get(options.comp_name, DEFAULT_EEPROM_SIZE_LIMIT)
                if not isinstance(max_eeprom_size, int) or max_eeprom_size <= 0:
                    msg = f"{options.comp_name}sr文件的eeprom大小限制设定值{max_eeprom_size}错误，应为大于0的整数，单位（kb）"
                    raise errors.BmcGoException(msg)
            self.make_sr_binary(options, hpm_temp_dir, max_eeprom_size)

    def do_build_eeprom(self):
        if not self.single or self.all:
            return True
        elif self.bin or self.hpm:
            return True
        else:
            return False


class EepromBuild:
    def __init__(self, bconfig, options, work_dir, strategy):
        self.bconfig = bconfig
        # eeprom签名策略
        self.strategy = strategy
        # 签名参数
        self.comp_name = options.comp_name
        # devkit数据，json结构
        self.dev_data = options.sr_json
        # eeprom 规范版本号
        self.format_version = self.get_sr_version(options.sr_json, "FormatVersion")
        # 自描述数据固件版本
        self.data_version = self.get_sr_version(options.sr_json, "DataVersion")
        # 组件唯一标识数据
        self.component_uid = options.uid
        # OEM数据
        self.oem_data = options.oem_data
        # 工作目录
        self.work_dir = work_dir
        # eeprom头部长度，128 bytes
        self.eeprom_header_len = 128
        # 预留数据长度， 73 bytes
        self.reserved_len = 73
        # 组件UID数据长度，24 bytes
        self.unique_id_len = 24
        # 电子标签域数据长度，2048 bytes
        self.elabel_len = 2048
        # 系统信息域数据长度，1024 bytes
        self.system_len = 1024
        # 签名域数据长度，128 bytes
        self.sign_len = 128
        # psr头部数据长度，16 bytes
        self.psr_header_len = 16
        # csr头部数据长度，16 bytes
        self.csr_header_len = 16
        # 组件唯一标识数据
        self.component_uid_data = bytearray()
        # elabel及system区域数据预留，填充0x00，共3072字节
        self.elabel_system_data = bytearray()
        # 内部使用域数据预留，若无上传不做填充
        self.internal_data = bytearray()
        # 整机域数据
        self.psr_data = bytearray()
        # 组件域数据
        self.csr_data = bytearray()
        # 数字签名数据
        self.sign_data = bytearray()
        # 自描述固件版本号数据，低字节在前高字节在后
        self.des_ver_data = bytearray()
        # 定制化预留数据
        self.des_reserve_data = bytearray()

    @staticmethod
    def get_sr_version(sr_json, key):
        if key not in sr_json:
            return ""
        value = sr_json[key]
        if isinstance(value, str):
            return value
        elif isinstance(value, float):
            return format(value, ".2f")
        return str(value)

    @staticmethod
    def resize_bytes_supplement(byte_arr: bytearray) -> bytearray:
        """将字节数组进行8位补齐"""
        new_size = round_up_data_size(len(byte_arr))
        if new_size == len(byte_arr):
            return byte_arr
        out_bytes = bytearray(new_size)
        out_bytes[:len(byte_arr)] = byte_arr
        return out_bytes

    @staticmethod
    def get_sha256_hash(data: bytearray):
        sha256_hash = hashlib.sha256()
        sha256_hash.update(data)
        return bytearray(sha256_hash.digest())

    @staticmethod
    def get_crc32_check_sum(data: bytearray):
        crc32_value = binascii.crc32(data)
        return crc32_value

    @staticmethod
    def zip_data(data) -> bytearray:
        if not data:
            return bytearray()
        byte_data = data.encode('utf-8')
        output_stream = io.BytesIO()
        # 创建一个压缩流并写入到内存的BytesIO对象
        with gzip.GzipFile(fileobj=output_stream, mode='wb') as f:
            f.write(byte_data)
        # 读取压缩后的字节流
        compressed_data = output_stream.getvalue()
        return compressed_data

    @staticmethod
    def sign_file(file_path, signing_key):
        with open(file_path, "rb") as fp:
            file_data = fp.read()
        signature = signing_key.sign(file_data, sigencode=ecdsa.util.sigencode_der)
        with open("signature.bin", "wb") as fp:
            fp.write(signature)

    def build_eeprom(self):
        # 1. 从自描述数据中提取版本号信息
        self.des_ver_data = self.build_description_version()
        # 2. 从自描述数据中提取产品描述信息
        self.des_reserve_data = self.build_description_reserve()
        # 3. 从自描述数据中提取组件UID描述信息
        self.component_uid_data = self.build_unique_id()
        # 4. elabel和system定制化描述区域预留
        self.elabel_system_data = self.build_elabel_system_data()
        # 5. 创建内部使用区域数据
        self.internal_data = self.build_internal_area()
        # 6. 创建csr区域数据
        self.csr_data = self.build_csr()
        # 7. 创建eeprom header数据
        eeprom_header_buf = self.build_eeprom_header()
        # 8. 填充数据域
        eeprom_buf_len = (
            self.eeprom_header_len +
            self.elabel_len +
            self.system_len +
            len(self.internal_data) +
            len(self.psr_data) +
            len(self.csr_data)
        )
        eeprom_buf = Buffer(eeprom_buf_len + self.sign_len)
        eeprom_buf.put(eeprom_header_buf)
        eeprom_buf.put(self.elabel_system_data)
        eeprom_buf.put(self.internal_data)
        eeprom_buf.put(self.psr_data)
        eeprom_buf.put(self.csr_data)
        # 9. 创建数字签名区域数据
        self.sign_data = self.sign_eeprom(eeprom_buf.array()[:eeprom_buf_len])
        eeprom_buf.put(self.sign_data)
        log.info(f"{self.comp_name}：eeprom数据写入成功")
        return eeprom_buf.array()

    # 创建固件自定义描述版本号数据
    def build_description_version(self):
        ver_array = self.data_version.split(".")
        out_bytes = bytearray(2)
        if len(ver_array) != 2 or not all(part.isdigit() for part in ver_array):
            return [0, 0]
        out_bytes[0] = int(ver_array[1])
        out_bytes[1] = int(ver_array[0])
        return out_bytes

    # 创建组件自定义描述数据
    def build_description_reserve(self):
        reserve_buf = Buffer(self.reserved_len)
        return reserve_buf.array()

    # 构建uniqueID
    def build_unique_id(self):
        unique_id_buf = Buffer(self.unique_id_len)
        array_uid = bytearray(self.component_uid, 'utf-8')
        unique_id_buf.put(array_uid)
        return unique_id_buf.array()

    # 创建elabel域和system域占位数据
    def build_elabel_system_data(self):
        return bytearray(self.elabel_len + self.system_len)

    # 根据 OEM 数据创建内部区域
    def build_internal_area(self):
        oem_data = self.oem_data
        if len(oem_data) == 0:
            return oem_data
        rounded_size = round_up_data_size(len(oem_data))
        buf = Buffer(rounded_size)
        buf.put(oem_data)
        return buf.array()

    # 创建数字签名域数据
    def sign_eeprom(self, un_sign_data: bytearray):
        if self.strategy == SignatureTypeEnum.DEFAULT:
            return self.get_eeprom_default_sign()
        elif not (self.strategy == SignatureTypeEnum.SERVER_SIGN or
                  self.strategy == SignatureTypeEnum.SELF_SIGN):
            raise errors.BmcGoException("Invalid signing strategy.")
        else:
            tmp_sign_path = os.path.join(self.work_dir, "tmp_sign")
            bin_file_path = os.path.join(tmp_sign_path, "tmpEeprom.bin")
            if os.path.exists(tmp_sign_path):
                shutil.rmtree(tmp_sign_path)
            os.makedirs(tmp_sign_path, exist_ok=True)
            with open(bin_file_path, 'wb') as f:
                f.write(un_sign_data)
            if self.strategy == SignatureTypeEnum.SELF_SIGN:
                sign_data = self.get_eeprom_self_sign(un_sign_data)
            else:
                sign_data = self.get_eeprom_server_sign(tmp_sign_path, bin_file_path)
            if os.path.exists(tmp_sign_path):
                shutil.rmtree(tmp_sign_path)
            return self.build_sign(sign_data)
    
    def get_eeprom_default_sign(self):
        return bytearray(self.sign_len)

    def get_eeprom_self_sign(self, un_sign_data):
        signing_key = self.load_key()
        signature = signing_key.sign(un_sign_data, sigencode=ecdsa.util.sigencode_der)
        return bytearray(signature)

    def get_eeprom_server_sign(self, tmp_sign_path, bin_file_path):
        os.chdir(tmp_sign_path)
        url = self.bconfig.e2p_server_sign.url
        try:
            fp = os.fdopen(os.open(bin_file_path, os.O_RDONLY, stat.S_IRUSR), 'rb')
            res = requests.post(url, files={'file': fp})
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise errors.BmcGoException(f"签名服务器返回错误，文件 {bin_file_path} 签名失败")
        return bytearray(res.content)

    def load_key(self):
        priv_pem_path = self.bconfig.e2p_self_sign.pem
        if os.path.exists(priv_pem_path):
            with open(priv_pem_path, "rb") as f:
                signing_key = ecdsa.SigningKey.from_pem(f.read(), hashfunc=sha256)
            return signing_key
        else:
            raise errors.BmcGoException("ECC私钥路径不存在！")

    def build_sign(self, sign_data: bytearray):
        sign_info = SignInfo(sign_data)
        sign_buf = Buffer(self.sign_len)
        # 1. Hash算法，1字节
        sign_buf.put_uint8(sign_info.sign_hash_code)
        # 2. 签名算法，1字节
        sign_buf.put_uint8(sign_info.sign_algorithm_code)
        # 3. 签名算法曲线ID，2字节
        sign_buf.put_uint16(sign_info.sign_curve_id)
        # 4. 签名数据长度，4字节
        sign_buf.put_uint32(sign_info.sign_length)
        sign_buf.put(bytearray(sign_info.sign_content))
        return sign_buf.array()

    # 创建组件域描述数据
    def build_csr(self):
        csr_json_str = json.dumps(self.dev_data, separators=(',', ':'))
        csr_bytes_arr = [bytearray(), bytearray(), bytearray(), bytearray()]
        csr_body = self.build_csr_body(csr_json_str)
        csr_bytes_arr[0] = csr_body
        csr_header = self.build_csr_header(csr_bytes_arr)
        csr_data = Buffer(round_up_data_size(len(csr_header) + len(csr_body)))
        csr_data.put(csr_header)
        csr_data.put(csr_body)
        return csr_data.array()

    def build_csr_body(self, csr_body_str: str):
        # 1. 处理CSR数据，获取压缩后字节
        zip_data = self.resize_bytes_supplement(self.zip_data(csr_body_str))
        # 2. 计算CSR body数据域长度
        body_size = len(zip_data) + 40
        # 3. 创建CSR body字节缓冲区
        csr_body_buf = Buffer(body_size)
        # 4. 前32位校验码最后填充
        csr_body_buf.set_position(32)
        # 5. CSR数据格式码填充，1字节
        csr_body_buf.put_uint8(JSON_DATA_FORMAT)
        # 6. 数据压缩GZIP算法码填充，1字节
        csr_body_buf.put_uint8(0x00)
        # 7. 数据长度，2字节
        csr_body_buf.put_uint16(len(zip_data) // 8)
        # 8. 8字节对齐
        csr_body_buf.set_position(csr_body_buf.position() + 4)
        # 9. CSR压缩数据填充，字节数组
        csr_body_buf.put(zip_data)
        # 10. CSR完整性校验
        csr_body_buf.set_position(0)
        csr_body_buf.put(self.get_sha256_hash(csr_body_buf.array()))
        return csr_body_buf.array()

    def build_csr_header(self, csr_bytes_arr: list) -> bytearray:
        csr_header = CsrHeader(self.csr_header_len, csr_bytes_arr)
        # 1. 初始化csr header buffer
        csr_header_buf = Buffer(self.csr_header_len)
        # 2. csr域格式版本，1字节
        csr_header_buf.put_uint8(csr_header.csr_ver)
        # 3. CSR域数量，1字节
        csr_header_buf.put_uint8(csr_header.csr_count)
        # 4. csr子域偏移量，8字节
        csr_header_buf.put(csr_header.csr_offset.array())
        # 5. 占位，填充0x00，2字节
        csr_header_buf.put_uint16(csr_header.padding)
        # 6. csr header校验，4字节
        csr_header_buf.put_uint32(self.get_crc32_check_sum(csr_header_buf.array()))
        return csr_header_buf.array()

    def build_eeprom_header(self):
        eeprom_header_buf = Buffer(self.eeprom_header_len)
        e_header = EepromHeader(len(self.psr_data), len(self.csr_data), len(self.internal_data))
        # 1. 12位天池规范校验码 12字节
        eeprom_header_buf.put(e_header.code)
        # 2. 规范版本号 1字节
        eeprom_header_buf.put_uint8(e_header.header_ver)
        # 3. 电子标签域偏移，0x00填充 2字节 16
        eeprom_header_buf.put_uint16(e_header.elabel_off)
        # 4. 系统定制化描述信息（System Description Address）偏移，0x00填充，2字节
        eeprom_header_buf.put_uint16(e_header.system_off) # 272
        # 5. 内部适用域（Internal Use Area Address）偏移，0x00填充，2字节
        eeprom_header_buf.put_uint16(e_header.internal_area_off)
        # 6. 整机描述域偏移，2字节
        eeprom_header_buf.put_uint16(e_header.psr_off)
        # 7. 组件描述域偏移，2字节
        eeprom_header_buf.put_uint16(e_header.csr_off)
        # 8. 数据签名区域偏移，2字节
        eeprom_header_buf.put_uint16(e_header.sign_off)
        # 9. 定制化预留数据填充0x00, 73字节
        eeprom_header_buf.put(self.des_reserve_data)
        # 10. 自描述固件版本号数据，低字节在前高字节在后，2字节
        eeprom_header_buf.put(self.des_ver_data)
        # 11. 组件唯一标识，24字节
        eeprom_header_buf.put(self.component_uid_data)
        # 12. CRC32 校验和（4字节）
        eeprom_header_buf.put_uint32(self.get_crc32_check_sum(eeprom_header_buf.array()))
        return eeprom_header_buf.array()   


class EepromHeader:
    def __init__(self, psr_size, csr_size, internal_size):
        self.code = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 90, 165, 90, 165])
        self.header_ver = 0x03
        self.elabel_off = 16
        self.system_off = 272
        self.internal_area_off = 0x0000
        pre_area_off = 400
        if internal_size == 0:
            self.internal_area_off = 0x0000
        else:
            self.internal_area_off = pre_area_off
        if psr_size == 0:
            self.psr_off = 0x0000
        else:
            self.psr_off = pre_area_off + (internal_size // 8)
        if csr_size == 0:
            self.csr_off = 0x0000
        else:
            self.csr_off = pre_area_off + ((internal_size + psr_size) // 8)
        self.sign_off = pre_area_off + ((internal_size + psr_size + csr_size) // 8)


class HpmBuild:
    # Description: hpm打包初始化函数
    def __init__(self, bconfig, dest_file, work_dir, strategy):
        self.bconfig = bconfig
        self.strategy = strategy
        # hpm包文件名
        self.hpm_name = "devkit.hpm"
        # 打包后结果文件存放路径
        self.dest_path = dest_file
        # 打包目录
        self.hpm_temp_dir = os.path.join(work_dir, "hpm_temp")
        # 打包路径下配置文件，存放在目录csr_packet下
        self.package_list = [
            "afteraction.sh", "beforeaction.sh", "CfgFileList.conf",
            "hpm_devkit.config", "image.filelist", "packet.sh",
            "update.cfg"
        ]
        if os.path.exists(HPM_PACK_PATH):
            shutil.copytree(HPM_PACK_PATH, self.hpm_temp_dir, dirs_exist_ok=True)
        # 打包后得到的hpm包
        self.hpm_file = os.path.join(self.hpm_temp_dir, self.hpm_name)

    @staticmethod
    def sign_hpm_default():
        cms_file = os.path.realpath("image.filelist.cms")
        tool.pipe_command([f"echo 'cms placeholder'"], out_file=cms_file)
        crl_file = os.path.realpath("crldata.crl")
        tool.pipe_command([f"echo 'crl placeholder'"], out_file=crl_file)

    # 打包路径下配置文件校验
    def check_dir(self):
        if self.strategy and self.strategy != SignatureTypeEnum.DEFAULT:
            return
        for config_file in self.package_list:
            if not os.path.exists(os.path.join(self.hpm_temp_dir, config_file)):
                raise errors.BmcGoException(f"Failed to find hpm package config file: {config_file}")
            
    # hpm包制作工具检查
    def check_hpm_tools(self):
        log.info("开始hpm包制作工具检查...")
        ret = tool.run_command("which hpmimage filesizecheck")
        if ret is None or ret.returncode != 0:
            raise errors.BmcGoException("hpm包制作工具缺失，请检查bingo是否正确安装")
        if self.bconfig.hpm_encrypt and self.bconfig.hpm_encrypt.need_encrypt \
            and not self.bconfig.hpm_encrypt.tool_path:
            raise errors.BmcGoException("配置hpm加密但加密工具不存在，请联系PAE获取")

    # 执行脚本构建hpm
    def packet_hpm(self):
        log.info("开始执行构建脚本生成hpm包...")
        packet_script = os.path.join(self.hpm_temp_dir, "packet.sh")
        os.chdir(self.hpm_temp_dir)
        need_encrypt = self.bconfig.hpm_encrypt and self.bconfig.hpm_encrypt.need_encrypt
        ret = tool.run_command(f"bash {packet_script} package {self.hpm_temp_dir} {need_encrypt}", command_echo=False)
        if ret.returncode != 0:
            raise errors.BmcGoException(f"Failed to pack the hpm, error msg: {ret}")
        elif not os.path.exists(self.hpm_file):
            raise errors.BmcGoException("Failed to pack the hpm.")

    # 对hpm包进行签名
    def sign_hpm(self):
        if self.strategy == SignatureTypeEnum.DEFAULT:
            log.info("未配置签名策略，跳过hpm包签名...")
            self.sign_hpm_default()
        elif self.strategy == SignatureTypeEnum.SELF_SIGN or\
                self.strategy == SignatureTypeEnum.SERVER_SIGN:
            # 生成.filelist文件
            tool.run_command(f"cms_sign_hpm.sh 1 {self.hpm_name}", command_echo=False)
            shutil.copy("devkit.filelist", "image.filelist")
            SignGenerator(self.bconfig, self.strategy, "image.filelist").sign_generate()
        else:
            raise errors.BmcGoException("Invalid signing strategy.")

    # 签名后使用签名结果文件重新构造hpm包
    def rebuild_hpm(self):
        log.info("签名成功，使用签名结果重新构造hpm包...")
        os.chdir(self.hpm_temp_dir)
        ret = tool.run_command(f"bash {self.hpm_temp_dir}/packet.sh rebuild {self.hpm_temp_dir}", command_echo=False)
        if ret.returncode != 0 or not os.path.exists(self.hpm_file):
            raise errors.BmcGoException(f"构造hpm包失败:{ret.stderr}.")
        shutil.move(self.hpm_file, self.dest_path)

    def run(self):
        self.check_dir()
        self.check_hpm_tools()
        self.packet_hpm()
        self.sign_hpm()
        self.rebuild_hpm()


class SignGenerator:
    def __init__(self, bconfig: BmcgoConfig, sign_strategy: str, unsigned_file: str):
        self.bconfig = bconfig
        self.sign_strategy = sign_strategy
        self.unsigned_file = unsigned_file
        self.sign_suffix = ".cms"
        self.cms_output = f"{self.unsigned_file}{self.sign_suffix}"
        self.crl_output = "crldata.crl"
        self.ca_output = "rootca.der"

    def sign_generate(self):
        if self.sign_strategy == SignatureTypeEnum.SELF_SIGN:
            self.self_sign_generate()
        elif self.sign_strategy == SignatureTypeEnum.SERVER_SIGN:
            self.server_sign_generate()
        else:
            raise errors.BmcGoException("Invalid sign strategy")

    def self_sign_generate(self):
        """使用本地签名方法"""
        unsigned_file = os.path.realpath(self.unsigned_file)
        cms_output = os.path.realpath(self.cms_output)
        crl_output = os.path.realpath(self.crl_output)
        ca_output = os.path.realpath(self.ca_output)
        tmp_dir = tempfile.TemporaryDirectory()
        t_cwd = os.getcwd()
        os.chdir(tmp_dir.name)
        rootca_der = self.bconfig.hpm_self_sign.rootca_der
        rootca_crl = self.bconfig.hpm_self_sign.rootca_crl
        signer_pem = self.bconfig.hpm_self_sign.signer_pem
        ts_signer_pem = self.bconfig.hpm_self_sign.ts_signer_pem
        ts_signer_cnf = self.bconfig.hpm_self_sign.ts_signer_cnf
        tool.run_command(f"openssl x509 -in {rootca_der} -inform der -outform pem -out rootca.pem", command_echo=False)
        tool.run_command(f"openssl crl -in {rootca_crl} -inform der -outform pem -out cms.crl.pem", command_echo=False)
        cmd = f"hpm_signer -s {signer_pem} -t {ts_signer_pem} -T {ts_signer_cnf} -i {unsigned_file} -o {cms_output}"
        tool.run_command(cmd)
        tool.run_command(f"hpm_verify -r rootca.pem -C cms.crl.pem -c {unsigned_file} -s {cms_output}")
        os.chdir(t_cwd)
        tool.copy(rootca_crl, crl_output)
        tool.copy(rootca_der, ca_output)

    def server_sign_generate(self):
        """使用简易服务器签名方法"""
        cert_id = self.bconfig.hpm_server_sign.cert_id
        url = self.bconfig.hpm_server_sign.url
        ssl_verify = self.bconfig.hpm_server_sign.ssl_verify
        rootca_der = self.bconfig.hpm_server_sign.rootca_der
        if not os.path.isfile(rootca_der):
            raise errors.BmcGoException(f"签名根证书{rootca_der}不存在")
        unsigned_file = os.path.realpath(self.unsigned_file)
        cms_output = os.path.realpath(self.cms_output)
        crl_output = os.path.realpath(self.crl_output)
        ca_output = os.path.realpath(self.ca_output)
        t_cwd = os.getcwd()
        tmpdir = tempfile.TemporaryDirectory()
        os.chdir(tmpdir.name)
        args = ["-i", unsigned_file, "-s", cert_id, "-u", url, "-v", ssl_verify]
        cmd = SimpleSign(self.bconfig, args)
        cmd.run()
        # 签名工具吐出rootca.crl和signed.cms复制到image.filelist.cms、crldata.crl
        tool.copy("signed.cms", cms_output)
        tool.copy("rootca.crl", crl_output)
        # csr出包签名根证书由开发者在bmcgo.conf中配置
        tool.copy(rootca_der, ca_output)
        os.chdir(t_cwd)


# 文件名生成时间戳
def get_timestamp():
    now = datetime.now(tz=timezone(timedelta(hours=8)))
    return now.strftime("%Y%m%d%H%M%S")


def round_up_data_size(data_size: int) -> int:
    return ((data_size + 7) // 8) * 8