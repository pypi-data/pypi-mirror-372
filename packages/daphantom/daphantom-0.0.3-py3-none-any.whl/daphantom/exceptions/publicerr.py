# -*- coding: utf-8 -*-
'''公共组件库的异常'''
from daphantom.common.error import Error

class PublicErrorOther(Error):
    """其他未知错误"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class PublicErrorType(Error):
    """类型错误"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class PublicErrorParameter(Error):
    """参数错误"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class PublicErrorQuery(Error):
    """查询失败"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


