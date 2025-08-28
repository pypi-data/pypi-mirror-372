#!/usr/bin/env python3
# encoding=utf-8
# 描述：版本比较器
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

import re


class PkgVersion:
    _version_re = re.compile(
        r"^((?P<epoch>\d+):)?"
        r"(?P<upstream>[0-9a-zA-Z.+~-]+?)"
        r"(-(?P<debian>[0-9a-zA-Z.+~]+))?$"
    )

    _digit = re.compile(r"^\d+")
    _non_digit = re.compile(r"^\D+")

    def __init__(self, version: str):
        self.origin = version
        match = self._version_re.match(version)
        if not match:
            raise ValueError(f"版本号非法: {version}")
        
        groups = match.groupdict()
        self.epoch = int(groups["epoch"] or 0)
        self.upstream = groups["upstream"]
        self.debian = groups["debian"] or "0"

    def __lt__(self, other):
        return self.__compare(other) < 0
    
    def __eq__(self, other):
        return self.__compare(other) == 0
    
    def __le__(self, other):
        return self.__compare(other) <= 0
    
    def __ge__(self, other):
        return self.__compare(other) >= 0
    
    def __gt__(self, other):
        return self.__compare(other) > 0

    def __ne__(self, other):
        return self.__compare(other) != 0

    def __compare_chars(self, a: str, b: str) -> int:
        while a or b:
            a_part = self.__get_part(a)
            b_part = self.__get_part(b)

            if a_part.startswith("~") or b_part.startswith("~"):
                if a_part != b_part:
                    return -1 if a_part.startswith("~") else 1
                
            a_isnum = a_part and a_part[0].isdigit()
            b_isnum = b_part and b_part[0].isdigit()

            if a_isnum != b_isnum:
                return -1 if a_isnum else 1
            
            if a_isnum and b_isnum:
                a_num = int(a_part.lstrip("0") or "0")
                b_num = int(b_part.lstrip("0") or "0")

                if a_num != b_num:
                    return -1 if a_num < b_num else 1
            else:
                if a_part != b_part:
                    return -1 if a_part < b_part else 1
                
            a = a[len(a_part):]
            b = b[len(b_part):]
        return 0
    
    def __get_part(self, s: str) -> str:
        if not s:
            return ""
        if s[0].isdigit():
            return self._digit.match(s).group()
        return self._non_digit.match(s).group()
    
    def __compare(self, other):
        if self.epoch != other.epoch:
            return -1 if self.epoch < other.epoch else 1
        
        upstream_cmp = self.__compare_chars(self.upstream, other.upstream)
        if upstream_cmp != 0:
            return upstream_cmp
        
        return self.__compare_chars(self.debian, other.debian)