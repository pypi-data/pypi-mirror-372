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

import json
import re
import os
from pathlib import Path
from bmcgo.utils.tools import Tools

tools = Tools("bmcgo_config")
log = tools.log


class Merger():
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.special_suffix = ("_basic_info", "_mgmt_model", "_version")
        self.tmp_dir = None

    @staticmethod
    def remove_json5_comments(text):
        pattern = r"""
            ("(?:\\.|[^"\\])*"
            |'(?:\\.|[^'\\])*'
            )
            |(/\*[\s\S]*?\*/
            |//[^\n]*
            )
        """

        def replacer(match):
            if match.group(1):
                return match.group(1)
            else:
                return ''
        return json.loads(re.sub(pattern, replacer, text, flags=re.VERBOSE))

    def merge_json(self, dict1, dict2, is_top_level=True, path=None):
        if path is None:
            path = []
        if not isinstance(dict1, dict) or not isinstance(dict2, dict):
            if dict1 != dict2:
                raise ValueError(f"字段冲突，路径{'/'.join(path)}的值不一致：{dict1} vs {dict2}")
            return dict1
        for key, value in dict2.items():
            if key in dict1:
                if is_top_level:
                    _ = self.merge_json(dict1[key], value, is_top_level=False, path=path + [key])
                else:
                    raise ValueError(f"字段冲突：路径 {'/'.join(path + [key])} 在多个文件中重复出现")
            else:
                dict1[key] = value
        return dict1

    def generate_csr(self, filelist, csr_path):
        log.info(f"正在创建临时csr文件")
        merged = {}
        for file_path in filelist:
            p = Path(file_path)
            if not p.exists():
                raise FileNotFoundError(f"文件不存在：{file_path}")
            with open(p, "r", encoding="utf-8") as fp:
                content = self.remove_json5_comments(fp.read())
                merged = self.merge_json(merged, content)
        with open(csr_path, "w") as f:
            json.dump(merged, f)
        log.info(f"临时文件创建成功")

    def update_tmp_dir(self, tmp_dir):
        self.tmp_dir = tmp_dir

    def get_single_csr(self, csr_path):
        if os.path.exists(csr_path):
            return csr_path
        name, ext = os.path.splitext(csr_path)
        modularize_csr = []
        for suffix in self.special_suffix:
            new_path = f"{name}{suffix}{ext}"
            if not os.path.exists(new_path):
                raise FileNotFoundError(f"路径 {new_path} 不存在")
            modularize_csr.append(new_path)
        csr_path = os.path.join(self.tmp_dir, os.path.basename(csr_path))
        self.generate_csr(modularize_csr, csr_path)
        return csr_path

    def get_multi_files(self, dir_path):
        srs = list(dir_path.glob("*.sr"))
        stem_to_path = {p.stem: p for p in srs}
        special_by_base = {}
        for p in srs:
            stem = p.stem
            for suf in self.special_suffix:
                if not stem.endswith(suf):
                    continue
                base = stem.removesuffix(suf)
                if base:
                    special_by_base.setdefault(base, {})[suf] = p
                break
        to_skip = set()
        to_create = []
        for base, mod_path in special_by_base.items():
            if base in stem_to_path:
                to_skip.update(mod_path.values())
            else:
                if not all(s in mod_path for s in self.special_suffix):
                    continue
                plain = dir_path / f"{base}.sr"
                if not plain.exists():
                    plain = os.path.join(self.tmp_dir, f"{base}.sr")
                    self.generate_csr([mod_path[s] for s in self.special_suffix], plain)
                to_create.append(plain)
                to_skip.update(mod_path.values())
        res = [p for p in srs if p not in to_skip]
        res.extend(to_create)
        log.info(res)
        return res