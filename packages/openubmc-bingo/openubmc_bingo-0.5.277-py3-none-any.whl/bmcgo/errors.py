#!/usr/bin/python3
# coding: utf-8
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.


class BmcGoException(Exception):
    """
         Generic bmcgo exception
    """
    def __init__(self, *args, **kwargs):
        super(BmcGoException, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(BmcGoException, self).__str__()


class ExitOk(Exception):
    """
         触发bmcgo退出
    """
    def __init__(self, *args, **kwargs):
        super(ExitOk, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(ExitOk, self).__str__()


class EnvironmentException(Exception):
    """
         环境异常，包括路径不正确，配置错误等
    """
    def __init__(self, *args, **kwargs):
        super(EnvironmentException, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(EnvironmentException, self).__str__()


class NotFoundException(BmcGoException):  # 404
    """
        404 error
    """

    def __init__(self, *args, **kwargs):
        super(NotFoundException, self).__init__(*args, **kwargs)


class ParameterException(BmcGoException):  # 404
    """
        参数错误异常
    """

    def __init__(self, *args, **kwargs):
        super(ParameterException, self).__init__(*args, **kwargs)


class DepAnalysisConfigException(BmcGoException):  # 404
    """
        依赖分析配置错误
    """

    def __init__(self, *args, **kwargs):
        super(DepAnalysisConfigException, self).__init__(*args, **kwargs)


class DepAnalysisException(BmcGoException):  # 404
    """
        依赖分析错误
    """

    def __init__(self, *args, **kwargs):
        super(DepAnalysisException, self).__init__(*args, **kwargs)


class NotIntegrateException(BmcGoException):  # 404
    """
        非集成环境 error
    """

    def __init__(self, *args, **kwargs):
        super(NotIntegrateException, self).__init__(*args, **kwargs)


class CommandNotFoundException(BmcGoException):  # 404
    """
        非集成环境 error
    """

    def __init__(self, *args, **kwargs):
        super(CommandNotFoundException, self).__init__(*args, **kwargs)


class XmlErrorException(BmcGoException):  # 404
    """
        404 error
    """

    def __init__(self, *args, **kwargs):
        super(NotFoundException, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(BmcGoException, self).__str__()


class ConfigException(BmcGoException):
    """
        配置错误 error
    """

    def __init__(self, *args, **kwargs):
        super(ConfigException, self).__init__(*args, **kwargs)
