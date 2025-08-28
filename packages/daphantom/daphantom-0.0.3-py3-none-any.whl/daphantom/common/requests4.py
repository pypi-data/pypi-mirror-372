# -*- coding: utf-8 -*-
"""requests请求器轮子"""
import requests
import random
from typing import Union, Dict, Literal, List, Tuple, TypedDict, Optional, Any
from daphantom.common.decorate import retry

def requests4(*,
         method: Literal['GET', 'POST', 'HEAD'] = None,
         url='',
         params=None,
         data=None,
         json=None,
         cookies=None,
         headers=None,
         files=None,
         auth=None,
         timeout=None,
         allow_redirects=True,   # 302重定向 默认开启
         proxies=None,
         hooks=None,
         stream=None,
         verify=None,
         cert=None,
         max_retries: int = 3,
         delay: int = 1,
         exceptions: Tuple[Exception, ...] = (Exception,)
         ) -> requests.models.Response:
    params = {
         'url': url,
         'params': params,
         'data': data,
         'json': json,
         'cookies': cookies,
         'headers': headers,
         'files': files,
         'auth': auth,
         'timeout': timeout,
         'allow_redirects': allow_redirects,
         'proxies': proxies,
         'hooks': hooks,
         'stream': stream,
         'verify': verify,
         'cert': cert,
     }
    @retry(max_retries=max_retries, delay=delay, exceptions=exceptions)
    def _req() -> requests.models.Response:
        assert method in ['GET', 'POST', 'HEAD'], 'method参数错误'
        _request = getattr(requests, method.lower())
        return _request(**params)
    return _req()


def headers4(capitalize: bool=False):
    """
    `capitalize` True 每个单词首字母大写  False使用默认
    """
    v1 = random.randint(557, 600)
    v2 = random.randrange(110, 160, 2)
    v3 = 36 or random.randrange(6, 50, 2)  # 常见36
    v4 = random.choice([6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36])
    sec_ch_ua = random.choice([
        f"\"Not)A;Brand\";v=\"{v4}\", \"Chromium\";v=\"{v2}\", \"Brave\";v=\"{v2}\"",
        f"\"Chromium\";v=\"{v2}\", \"Not A(Brand\";v=\"{v4}\", \"Google Chrome\";v=\"{v2}\"",
        f"\"Not?A_Brand\";v=\"{v4}\", \"Chromium\";v=\"{v2}\"",
        f"\"Chromium\";v=\"{v2}\", \"Not_A Brand\";v=\"{v4}\"",
                 ])
    """
    `User-Agent`: 
            含义：标识浏览器和版本信息。
            浏览器作用：服务器会根据 UA 判断是否兼容，比如返回移动端页面、PC 页面。
            爬虫意义：最常用的反爬参数，很多网站会封禁默认 UA（如 python-requests/2.x）。
            反反爬：✅ 必须随机化或模拟真实浏览器 UA。
    `Accept`:
            含义：客户端可接受的数据类型（MIME types）。
            浏览器作用：决定返回什么格式的数据（html/json/image等）。
            爬虫意义：模拟浏览器时，保持和真实浏览器一致，避免服务端识别为爬虫。
            反反爬：✅ 很有用，特别是一些反爬站点会检查 Accept 和 User-Agent 是否匹配。
    `Accept-Language`:
            含义：客户端可接受的语言和优先级。
            浏览器作用：服务器可能根据这个字段返回对应语言版本。
            爬虫意义：伪装地区/语言，比如设置成 en-US 更像海外用户。
            反反爬：✅ 常见的识别点（中国 IP + en-US UA → 可疑）。
    `Connection`:
            含义：是否保持连接，常见 keep-alive 或 close。
            浏览器作用：提升性能，减少重复 TCP 握手。
            爬虫意义：没什么大用，基本保持默认即可。
            反反爬：❌ 几乎不用来反爬
    `Referer`:
            含义：表示请求的来源页面。
            浏览器作用：安全和流量来源统计。
            爬虫意义：模拟点击路径，比如从 google.com 点进来。
            反反爬：✅ 很常见，如果缺失/伪造错误，容易触发 403。
    `sec-ch-ua`:
            含义：User-Agent Client Hints，Chrome 提出的 UA 拆解字段。
            浏览器作用：告诉服务器具体浏览器内核和版本。
            爬虫意义：必须和 UA 对应，否则会被识别为爬虫。
            反反爬：✅ 高级反爬点。比如 UA 显示 Chrome 110，但 sec-ch-ua 却是 Chromium 130 → 可疑。
    `sec-ch-ua-mobile`:
            含义：是否是移动端，?0=PC，?1=Mobile。
            爬虫意义：控制是否返回 H5 页面。
            反反爬：✅ 重要，UA 是 iPhone 却传 ?0 → 矛盾。
    `sec-ch-ua-platform`:
            含义：操作系统平台，比如 "Windows" / "macOS" / "Android"`。
            反反爬：✅ UA 和 platform 对不上会被识别。
    `Sec-Fetch-*`:
            字段：
                Sec-Fetch-Dest: 资源类型（document、image、script）
                Sec-Fetch-Mode: 请求模式（navigate、cors、no-cors）
                Sec-Fetch-Site: 请求来源站点关系（same-origin、cross-site）
                Sec-Fetch-User: 是否是用户触发的导航（?1 表示是）
            浏览器作用：提供上下文，帮助 CSP（内容安全策略）。
            反反爬：✅ 很有用。比如请求图片却传 document，立刻暴露爬虫。
    `Sec-GPC`:
            含义：Global Privacy Control，隐私相关字段。
            浏览器作用：告诉网站不要追踪用户（欧盟/加州法案要求）。
            爬虫意义：很少被检查。
            反反爬：❌ 几乎没影响。
    `Cache-Control / Pragma`:
            含义：控制缓存策略。
            爬虫意义：一般没什么大作用，但模拟时最好保留。
            反反爬：❌ 不是重点。
    `Origin`:
            含义：跨域请求时，标明来源站点。
            反反爬：✅ 跨站 API 常检查 origin，否则 403。
    `Content-Type`:
            含义：请求体的数据类型，比如 application/json。
            反反爬：✅ POST 请求时必须正确，否则服务端解析失败。
    `Priority`:
            含义：HTTP/2 的优先级设置。
            爬虫意义：可模拟真实浏览器请求顺序。
            反反爬：⚠️ 部分高级反爬会用。
    """

    headers = {
        "sec-ch-ua": sec_ch_ua,
        "user-agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{v1}.{v3} (KHTML, like Gecko) Chrome/{v2}.0.0.0 Safari/{v1}.{v3}"
    }
    if capitalize: headers = {k.title(): v for k, v in headers.items()}
    return headers
