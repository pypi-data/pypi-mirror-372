# -*- coding: utf-8 -*-
'''mysql的异常'''
from daphantom.common.error import Error



class MysqlErrorOther(Error):
    """其他未知错误"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class MysqlErrorType(Error):
    """类型错误"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class MysqlErrorParameter(Error):
    """参数错误"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

