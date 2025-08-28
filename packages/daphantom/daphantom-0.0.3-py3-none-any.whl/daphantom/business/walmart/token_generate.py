# -*- coding: utf-8 -*-
# 这是一个令牌生产机器
"""
起始日期：2024-12-19
更新日期：2025-08-27
"""
import time
import random
import re
from daphantom.common.requests4 import requests4, headers4

class WalmartToken:
    """_pxvid令牌生成 含演示代码"""
    def __init__(self, proxies=None):
        """请添加 海外代理且需要使用socks5h协议，使用代理进行DNS解析，并且海外IP必须是每次请求都更换IP，可以最大程度的减少风控"""
        # self.proxies = {
        #     "http": "socks5h://127.0.0.1:7898/",
        #     "https": "socks5h://127.0.0.1:7898/",
        # }
        self.proxies = proxies

    def get_pxvid(self):
        """
        过 CAPTCHA 行为验证，使用获取的令牌进行绕过
        起始日期：2024-12-19
        更新日期：2025-08-27
        """
        cookies = {
            "isoLoc": "CN_GD_t3",
        }
        url = "https://www.walmart.com/ip/Mikolo-Power-Rack-Cage-LAT-Pulldown-System-1200LBS-Capacity-Workout-Rack-Multi-Functional-Squat-Rack-13-Level-Adjustable-Height-J-Hooks-Dip-Bars-T-Ba/800851001"
        # athAsset = {"athcpid":"800851001","athstid":"CS020","athancid":"ItemCarousel","athrk":0.0}
        params = {
            "athAsset": "eyJhdGhjcGlkIjoiODAwODUxMDAxIiwiYXRoc3RpZCI6IkNTMDIwIiwiYXRoYW5jaWQiOiJJdGVtQ2Fyb3VzZWwiLCJhdGhyayI6MC4wfQ==",
            "athena": "true",
            "%": "%",
            self._v(): self._v(),
            self._v(): self._v()
        }
        print(params)
        response = requests4(method='HEAD',
                             url=url,
                             headers=self.header(),
                             cookies=cookies,
                             params=params,
                             proxies=self.proxies
                             )
        cookies = response.cookies.get_dict()
        assert '_pxhd' in cookies, "_pxhd 生成失败"
        _pxhd = cookies['_pxhd'].split(':')[-1]
        assert 'AID' in cookies, f"_pxhd 令牌不生效 {_pxhd}"
        print('----------成功获取_pxhd令牌 请等待10秒后使用----------')
        print(_pxhd)
        # cookie = { "_pxvid": '3ef6ae21-82bd-11f0-8035-ec6e6667b997', "isoLoc": "CN_GD_t3" }
        return _pxhd

    @staticmethod
    def _v():
        ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
        ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        ascii_letters = ascii_lowercase + ascii_uppercase + digits
        return ''.join(random.choice(ascii_letters) for _ in range(random.randrange(4, 6, 2)))
    @staticmethod
    def header():
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Brave\";v=\"134\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "sec-gpc": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            **headers4()
        }
        return headers

    def test(self):
        """测试"""
        cookies = {
            "_pxvid": self.get_pxvid(),
            "isoLoc": "CN_GD_t3",
        }
        time.sleep(11)
        params = {
            self._v(): self._v()
        }
        response = requests4(method='GET',
                             url=f'https://www.walmart.com/ip/800851001?dwqd=%dwqd%dwq',
                             headers=self.header(),
                             cookies=cookies,
                             params=params,
                             proxies=self.proxies
                             )
        # 临时存储数据测试
        data_dict_template = {}
        # 数据大致处理
        data = response.text.replace('\n', '').replace('\t', '').replace('\f', '').replace('\r', '')
        # 随便提取几个数据
        data_dict_template['price'] = (re.findall('"priceCurrency":"USD","price":(.*?),', data) + [''])[0]
        data_dict_template['title'] = (re.findall('elementtiming="ip-main-title">(.*?)<', data) + [''])[0]
        print('打印提取结果', data_dict_template)


if __name__ == '__main__':
    WalmartToken = WalmartToken()
    WalmartToken.test()



