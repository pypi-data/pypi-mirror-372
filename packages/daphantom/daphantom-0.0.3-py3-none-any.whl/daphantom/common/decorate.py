# -*- coding: utf-8 -*-
"""装饰器"""
from typing import Union, Dict, Literal, List, Tuple, TypedDict, Optional, Any
from functools import wraps
import time

def retry(*, max_retries: int=3, delay:Union[int, float]=1, exceptions: Tuple[Exception, ...]=(Exception, )):
    """
    `max_retries` 最大重试次数
    `delay` 每次重试的间隔时间(单位秒)
    `exceptions`  捕获需要重试的异常类型(Exception,ValueError,)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries >= max_retries:
                        raise e.__class__(f"操作在重试{max_retries}次后仍然失败: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

