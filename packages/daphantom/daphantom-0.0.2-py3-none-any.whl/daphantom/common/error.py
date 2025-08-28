# -*- coding: utf-8 -*-
"""异常组件库"""
import json

class Error(Exception):
    """通用错误类型"""
    def __init__(self, message):
        try:
            if not isinstance(message, str):
                message = json.dumps(message, ensure_ascii=False, separators=(',', ':'))
        except:
            message = str(message)
        self.message = message
        super().__init__(message)