# -*- coding: utf-8 -*-
# 这是一个令牌生产机器
import json
import time
import random
from daphantom.common.requests4 import requests4, headers4
from daphantom.common.components import Components
from typing import Union, Dict, Literal, List, Tuple, TypedDict, Optional, Any

components = Components()

class Alibaba1688Token:
    def __init__(self):
        pass

    @staticmethod
    def sign1(keyword: str):
        """
        api: hamlet/async/v1.json
        起始日期：2025-08-27
        更新日期：2025-08-27
        `keyword` : 搜索值
        """
        # 13位时间戳 + 1位随机值 = 14位字符串
        salt = str(int(time.time() * 1000)) + str(random.randint(1, 9))
        sign = Components.hash_encrypt(f'pcsem{keyword}{salt}csb44T%34CiKj&FyRbCBJ', 'md5')
        return {
            "sign": sign,
            "salt": salt,
        }

    def test(self, keyword: str):
        """测试 keyword 查询的内容"""
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://www.1688.com",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "Referer": "https://www.1688.com/",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Sec-Gpc": "1",
            **headers4()
        }
        url = "https://p4psearch.1688.com/hamlet/async/v1.json"
        sign = self.sign1(keyword=keyword)
        params = {
            "beginpage": "1",
            "asyncreq": "6",
            "keywords": "",
            "keyword": keyword,
            "sortType": "",
            "descendOrder": "",
            "province": "",
            "city": "",
            "priceStart": "",
            "priceEnd": "",
            "dis": "",
            "ptid": "",
            "exp": "pcSemFumian:C;pcDacuIconExp:A;pcCpxGuessExp:B;pcCpxCpsExp:B;qztf:E;wysiwyg:B;hotBangdanExp:B;pcSemWwClick:A;asst:E;pcSemDownloadPlugin:A",
            "cosite": "baidujj_pz",
            "salt": sign['salt'],
            "sign": sign['sign'],
            "hmaTid": "3",
            "hmaQuery": "graphDataQuery",
            "pidClass": "pc_list_336",
            "cpx": "cpc,free,nature",
            "api": "pcSearch",
            "pv_id": ""
        }
        response = requests4(method='GET', url=url, headers=headers, params=params)
        return self._filter(response.json())

    def _filter(self, data):
        data_list = data.get('module', {}).get('offer', {}).get('list', [])
        assert data_list, '没有获取到数据'
        return [
            {
                "标题": item.get('subject', ''),
                "价格": item.get('price', ''),
                "商品链接": item.get('odUrl', ''),
                "公司": item.get('company', ''),
                "主图": item.get('imgUrl', ''),
                "副图": item.get('imgUrlList', []),
                "销售量": item.get('saleVolume', '0') + item.get('unit', ''),
                "商品id": item.get('offerId', '')
            } for item in data_list
        ]

    @staticmethod
    def sign2(token='', appKey='12574478', data: Union[dict, str] = None):
        """
        api: h5/mtop.1688.trade.service.mtoprateservice.querydsrratedatav2/1.0/
        起始日期：2025-08-27
        更新日期：2025-08-27
        """
        return components.sign_hmac_standard(token=token, t=str(int(time.time() * 1000)), appKey=appKey, data=data)


    def _m_h5_tk(self):
        """
        获取临时的 _m_h5_tk_enc 和 _m_h5_tk 令牌
        起始日期：2025-08-27
        更新日期：2025-08-27
        """
        headers = {
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://detail.1688.com",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "Referer": "https://detail.1688.com/",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Sec-Gpc": "1",
            **headers4()
        }
        url = "https://h5api.m.1688.com/h5/mtop.1688.trade.service.mtoprateservice.querydsrratedatav2/1.0/"
        sign = self.sign2(token='', appKey='12574478', data={})
        params = {
            "jsv": "2.7.2",
            "appKey": sign['appKey'],
            "t": sign['t'],
            "sign": sign['sign'],
            "api": "mtop.1688.trade.service.MtopRateService.queryDsrRateDataV2",
            "v": "1.0",
            "dataType": "jsonp",
            "type": "originaljson",
            "timeout": "20000"
        }
        data = sign['data']
        response = requests4(method='POST', url=url, headers=headers, params=params, data=data)
        cookies = response.cookies.get_dict()
        return cookies

    def text2(self):
        headers = {
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://detail.1688.com",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "Referer": "https://detail.1688.com/",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Sec-Gpc": "1",
            **headers4()
        }
        cookies = self._m_h5_tk()
        # cookies = {"_m_h5_tk_enc":"0d5a49b05e27a74aaf710898bb0333a8","_m_h5_tk":"ee90c4a73e69b98d22449256211b0f2c_1756315670354"}
        url = "https://h5api.m.1688.com/h5/mtop.1688.trade.service.mtoprateservice.querydsrratedatav2/1.0/"
        sign = self.sign2(token=cookies['_m_h5_tk'].split('_')[0], appKey='12574478', data={"loginId":"中国迅奇","scene":"shop"})
        params = {
            "jsv": "2.7.2",
            "appKey": sign['appKey'],
            "t": sign['t'],
            "sign": sign['sign'],
            "api": "mtop.1688.trade.service.MtopRateService.queryDsrRateDataV2",
            "v": "1.0",
            "dataType": "jsonp",
            "type": "originaljson",
            "timeout": "20000"
        }
        data = {'data': sign['data']}
        response = requests4(method='POST', url=url, headers=headers, cookies=cookies, params=params, data=data)
        res_data = response.json()
        return res_data


if __name__ == '__main__':
    alibaba = Alibaba1688Token()
    print(alibaba.test(keyword="上衣 短袖 男士"))

    # print(alibaba.text2())

