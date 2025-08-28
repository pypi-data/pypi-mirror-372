#!/usr/bin/python
# -*- coding: utf-8 -*-
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
import re
import argparse
import concurrent.futures
from enum import auto
from pathlib import Path
from typing import Callable, List, Optional

from bmcgo.utils.tools import Tools
from bmcgo.utils.basic_enums import BaseStringEnum


tools = Tools("JSONChecker")
logger = tools.log


class JsonTypeEnum(BaseStringEnum):
    JSON = auto()
    JSON5 = auto()
    PYJSON5 = auto()


class JSONValidator:
    def __init__(self):
        self.logger = tools.log

        self.loaders = {
            JsonTypeEnum.JSON: load_json,
            JsonTypeEnum.JSON5: load_json5,
            JsonTypeEnum.PYJSON5: load_pyjson5
        }

    def validate_files(
            self,
            root_path: Path,
            extensions: List[str],
            json_type: JsonTypeEnum = JsonTypeEnum.JSON,
            max_workers: Optional[int] = None
        ):
        root_path = Path(root_path)
        files = find_files(root_path, extensions)

        if not files:
            self.logger.info(f"没有找到{extensions}后缀的文件！")
            return

        loader = self._get_loader(json_type)
        fails = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(validate, file, loader): file for file in files}

            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    error = future.result()
                    if error:
                        self.logger.debug(f"{str(file_path)}: Failed!")
                        fails[file_path] = error
                    else:
                        self.logger.debug(f"{str(file_path)}: PASS!")
                except Exception as e:
                    self.logger.error(f"{file_path} - {str(e)}")

        self._print_summary(fails)
        if fails:
            raise ValueError("JSON 格式错误！")

    def _get_loader(self, json_type: JsonTypeEnum):
        if json_type == JsonTypeEnum.JSON5:
            try:
                import json5
            except ImportError:
                self.logger.warning("json5 不可用，使用 json 检查")
                json_type = JsonTypeEnum.JSON
        elif json_type == JsonTypeEnum.PYJSON5:
            try:
                import pyjson5
            except ImportError:
                self.logger.warning("pyjson5 不可用，使用 json 检查")
                json_type = JsonTypeEnum.JSON
        else:
            json_type = JsonTypeEnum.JSON

        return self.loaders.get(json_type)


    def _print_summary(self, fails):
        if fails:
            self.logger.error("json 检查找到以下错误:")
            for path, err in fails.items():
                self.logger.error(f"{path}")
                for detail in err:
                    self.logger.error(detail)
        else:
            self.logger.info("json 检查全部通过！")


def format_error_position(content: str, message: str, position: int, window: int = 50):
    lines = content.splitlines()
    curr_pos = 0
    for ln, line in enumerate(lines, 1):
        if curr_pos + len(line) >= position:
            start = max(0, position - curr_pos - window)
            end = min(len(line), position - curr_pos + window)

            snippet = line[start:end]
            marker = " " * (position - curr_pos - start) + "↑"
            if start > 0:
                marker = " " * 3 + marker

            prefix = "..." if start > 0 else ""
            suffix = "..." if end < len(line) else ""

            return (f"Line {ln}: {message}", f"{prefix}{snippet}{suffix}", f"{marker} ({position - curr_pos + 1})")
        curr_pos += len(line) + 1
    return ""


def format_error_row_and_col(content: str, message: str, lineno: int, colno: int, window: int = 50):
    lines = content.splitlines()
    for ln, line in enumerate(lines, 1):
        if ln != lineno:
            continue

        start = max(0, colno - window)
        end = min(len(line), colno + window)

        snippet = line[start:end]
        marker = " " * (colno - start - 1) + "↑"
        if start > 0:
            marker = " " * 3 + marker

        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(line) else ""

        return (f"Line {ln}: {message}", f"{prefix}{snippet}{suffix}", f"{marker} ({colno})")
    return ""


def format_error(error: Exception, content: str, file_path: Path):
    error_msg = str(error)
    pos = getattr(error, 'pos', None)
    if pos is not None:
        return format_error_position(content, error_msg, error.pos)

    args = getattr(error, 'args')
    if args:
        msg = args[0]

        result = re.search(r"<string>:(\d+)\s+(.+?)\s+at column\s+(\d+)", msg)
        if result:
            lineno = int(result.group(1))
            colno = int(result.group(3))
            reason = result.group(2)

            return format_error_row_and_col(content, reason, lineno=lineno, colno=colno)

        result = re.search(r"near (\d+)", msg)
        if result:
            pos = int(result.group(1)) - 1
            return format_error_position(content, msg, pos)

    # 需要以 tuple 返回，和 format_error_x 返回类型一致
    return f"{error_msg}\n in {file_path}",


def validate(file_path: Path, loader: Callable):
    try:
        content = file_path.read_text(encoding='utf-8')
        loader(content)
        return None
    except Exception as e:
        return format_error(e, content, file_path)


def find_files(root_path: Path, extensions: List[str]):
    if root_path.is_dir():
        ret = list(root_path.rglob("*"))
    elif root_path.is_file():
        ret = [root_path]
    else:
        ret = []

    return [path for path in ret if path.suffix.lstrip(".").lower() in extensions]


def load_json(content: str):
    import json
    json.loads(content)


def load_json5(content: str):
    import json5
    json5.loads(content)


def load_pyjson5(content: str):
    import pyjson5
    pyjson5.loads(content)


def get_cpu_count():
    return os.cpu_count() or 1


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-p", "--path", type=Path, default=Path(".").resolve())
    parser.add_argument(
        "-e", 
        "--extensions", 
        type=lambda s: [ext.strip().lstrip('.').lower() for ext in re.split(r'\s*[，,]\s*', s) if ext],
        required=True
    )
    parser.add_argument("-j", "--json-type", choices=list(JsonTypeEnum), default=JsonTypeEnum.JSON)
    parser.add_argument("-n", "--worker-num", type=int, default=get_cpu_count() * 2)
    args = parser.parse_args()

    validator = JSONValidator()
    validator.validate_files(
        root_path=args.path,
        extensions=args.extensions,
        json_type=args.json_type,
        max_workers=args.worker_num
    )


if __name__ == "__main__":
    main()