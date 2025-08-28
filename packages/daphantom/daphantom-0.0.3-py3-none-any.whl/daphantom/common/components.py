# -*- coding: utf-8 -*-
"""组件库"""
import time
import random
import hashlib
import json
import base64
from datetime import datetime
from urllib.parse import unquote
from typing import Union, Dict, Literal, List, Tuple, TypedDict, Optional, Any
from daphantom.exceptions.publicerr import *

class Components:
    def __init__(self):
        pass

    @staticmethod
    def generate_permanent_id() -> str:
        """
        随机生成一个永远不会重复的id
        1755769016.5906160607.814
        1755769016.2206952012.487
        1755769016.0341171988.971
        1755769016.8431545742.871
        1755769016.4897476452.757
        """
        # 随机的5位字符串
        num_str = str(random.uniform(0, 0.9))[2:12]
        # 随机的3位字符串
        random_number = str(random.randint(100, 999))
        # 时间戳（秒单位）
        time_str = str(int(time.time()))
        return time_str + '.' + num_str + '.' + random_number

    @staticmethod
    def print(*args: any) -> None:
        """开发者测试专用 可代替print打印"""
        formatted_time = datetime.fromtimestamp(time.time()).strftime("%H:%M:%S.%f")[:-3]  # %Y/%m/%d %H:%M:%S.%f
        if len(args) > 1:
            label, *values = args
            type_str = "".join(f"[{type(v).__name__}]" for v in values)
            value_str = " ".join(f"[{v}]" for v in values)
            print(f'[{formatted_time}][{label}] | {type_str} -> {value_str}')
            return
        elif len(args) == 1:
            print(f'[{formatted_time}][{type(args[0]).__name__}] -> [{args[0]}]')

    @staticmethod
    def hash_encrypt(string: str,
                     algorithm: Literal['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512', 'blake2b', 'blake2s',
                                        'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
                                        'shake_128', 'shake_256'], iv: str = '') -> str:
        """
        hash哈希加密合集 整合hash哈希加密算法，支持加盐加密
        `string`: 要加密的字符串
        `algorithm`: 选择要使用的加密库（标准库）
        `iv`: 手动加盐，非标准库内置 最长支持20位长度
        """
        # 支持的算法列表
        supported_algorithms = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
                                'blake2b', 'blake2s',
                                'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
                                'shake_128', 'shake_256']

        # 检查算法是否支持
        if algorithm not in supported_algorithms:
            raise PublicErrorParameter('不支持的算法')
        # 手动加盐 不能超过20位
        if type(iv) != str or len(iv) > 20:
            raise PublicErrorParameter('iv必须位字符类型/长度不能超过20')
        if iv: string += '*&*' + iv
        try:
            hash_obj = getattr(hashlib, algorithm)()
            hash_obj.update(string.encode('utf-8'))
            return hash_obj.hexdigest()
        except Exception as e:
            raise PublicErrorOther(f'加密发生错误: {e}')
    @staticmethod
    def base64_senior(string: str, salt: Optional[str] = None,
                      algorithm: Literal['encode', 'decode'] = 'encode'):
        """
        base64编码解码标准库（支持加盐处理）支持魔改版加盐编码解码
        `string`: 要编码的明文字符数据
        `salt`: 盐值 支持数字+大小写字母，支持长度为6-32位
        `algorithm`: 选择 编码/解码：encode/decode
        """
        if algorithm == 'encode':
            # 将输入字符串编码为字节（utf-8）
            input_bytes = string.encode('utf-8')  # 将字符串转换为字节数据
            # 如果提供了盐值，则对输入字节数据进行加盐处理
            if salt:
                if 32 < len(salt) or len(salt) < 6:
                    raise PublicErrorParameter('盐值长度必须为6-32位')
                if len(string) > 10000:
                    raise PublicErrorParameter('盐只能编码明文长度为10000内的字符内容')
                # 将盐值字符串转换为字节
                salt_bytes = salt.encode('utf-8')
                # 将字节数据转换为可变的字节数组（bytearray）以便修改
                input_bytes = bytearray(input_bytes)  # bytearray 是可变的，可以修改其中的字节
                # 遍历字节数据，对每个字节进行 XOR 操作，增加盐值的影响
                for i in range(len(input_bytes)):
                    # 使用盐值与字节数据进行 XOR（异或）操作，混合数据和盐
                    input_bytes[i] ^= salt_bytes[i % len(salt_bytes)] ^ len(salt)  # XOR 操作，通过盐值改变数据
            # 对可能被加盐后的字节数据进行 Base64 编码
            encoded_bytes = base64.b64encode(input_bytes)
            # 将编码后的字节数据转为字符串并返回
            # 返回 base64 编码后的字符串
            return encoded_bytes.decode('utf-8')
        elif algorithm == 'decode':
            # 将输入的 base64 编码字符串转换为字节数据
            encoded_bytes = string.encode('utf-8')
            # 对 base64 编码的数据进行解码，得到原始字节数据
            decoded_bytes = base64.b64decode(encoded_bytes)
            # 如果提供了盐值，则对解码后的字节数据进行解盐处理
            if salt:
                if 32 < len(salt) or len(salt) < 6:
                    raise PublicErrorParameter('盐值长度必须为6-32位')
                # 将盐值字符串转换为字节
                salt_bytes = salt.encode('utf-8')
                # 将字节数据转换为可变的字节数组
                decoded_bytes = bytearray(decoded_bytes)
                # 遍历字节数据，对每个字节进行反向 XOR 操作，恢复原始数据
                for i in range(len(decoded_bytes)):
                    # 使用盐值与字节数据进行 XOR 操作，移除加盐效果
                    decoded_bytes[i] ^= salt_bytes[i % len(salt_bytes)] ^ len(salt)  # XOR 操作，解盐
            # 将解码后的字节数据转换为字符串并返回
            # 返回解码后的字符串（即原始字符串）
            return decoded_bytes.decode('utf-8')
        else:
            raise PublicErrorParameter('缺少algorithm字段内容或输入错误')

    def sign_hmac_standard(self, *, token, t=str(int(time.time() * 1000)), appKey='', data=''):
        """
        sign HMAC标准签名 13位的时间戳
        `token`: token 通常是cookie里的_m_h5_tk键里获取
        `t`: 一个13位的时间戳（默认），也可能是10位
        `appKey`: 一个key, 不同网站用的不一样
        `data`: 要载荷的data数据，也是要签名的数据
        """
        if not isinstance(data, str):
            data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        sign = self.hash_encrypt(string=str(token) + "&" + str(t) + "&" + str(appKey) + "&" + data, algorithm='md5')
        return {
            'sign': sign,
            't': t,
            'appKey': appKey,
            'data': data
        }

    @staticmethod
    def cookie_turn_dict(cookies: str, decode_start: bool = False) -> dict:
        """
        Cookie字符串转字典 将浏览器里的字符cookie直接转为字典，方便使用
        `cookies`: 字符cookie
        `decode_start`: False: 不解码    Ture: 将cookie进行解码
        """
        cookies = cookies.strip()
        if '=' not in cookies:
            raise PublicErrorParameter('cookies格式参数错误')
        # 存储cookie
        data_dict = {}
        for cook in cookies.split(';'):
            cook = cook.strip().split('=', 1) + ['']
            if not cook[0]:
                continue
            value = cook[1]
            # 进行解码
            if decode_start:
                value = unquote(value)
            data_dict[cook[0]] = value
        return data_dict
