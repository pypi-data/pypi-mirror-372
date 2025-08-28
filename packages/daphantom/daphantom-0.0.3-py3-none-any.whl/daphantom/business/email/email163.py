# -*- coding: utf-8 -*-
"""
起始日期：2025-03-02
更新日期：2025-08-27
"""
import random
import time
import json5
import json
import uuid
import re
from datetime import datetime
from urllib.parse import quote
from daphantom.common.requests4 import requests4, headers4
from daphantom.common.components import Components
from typing import Union, Dict, Literal, List, Tuple, TypedDict, Optional, Any

class Email163:
    def __init__(self, cookie: dict ='', deviceId: str = '', platform:str=None):
        # self._cookie = Components.cookie_turn_dict(cookie.strip())
        self._cookie = cookie
        self.platform = platform and platform.lower()  # 平台
        self.mid = ''  # 占位
        self._deviceId = deviceId or str(uuid.uuid4()).replace('-', '') + '_v1'
        self._header = headers4(capitalize=True)
        self._status = False
        self._time = 0
        self.Mailbox = {}
        self._get_user()
        self._Coremail()

    def __repr__(self):
        return self._status and '<success.connect>' or '<error.connect>'

    @property
    def status(self) -> bool:
        return self._status

    def _Coremail(self) -> dict:
        """获取关键临时访问sid 和 Coremail 有效期仅3分钟左右"""
        if self._cookie.get('Coremail') and self._time > int(time.time()):
            return self._cookie
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Priority": "u=0, i",
            "Referer": "https://mail.163.com/",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Gpc": "1",
            "Upgrade-Insecure-Requests": "1",
            **self._header
        }
        url = "https://mail.163.com/entry/cgi/ntesdoor"
        params = {
            "lightweight": "1",
            "verifycookie": "1",
            "from": "web",
            "df": "mail163_letter",
            "allssl": "true",
            "sdid": self._sdid()['sdid'],
            "deviceId": self._deviceId,
            "style": "-1"
        }
        response = requests4(method='HEAD',
                             url=url,
                             headers=headers,
                             cookies={"NTES_SESS": self._cookie['NTES_SESS'],**({"smslogin_trust": self._cookie['smslogin_trust']} if 'smslogin_trust' in self._cookie else {})},
                             params=params,
                             allow_redirects=False)
        response_cookies = response.cookies.get_dict()
        _header = response.headers
        assert 'bizVerifyInf' not in _header.get('Location', ''), "需要手机号验证 或 添加 smslogin_trust cookie也可使用"
        # print({"NTES_SESS": self._cookie['NTES_SESS'],**({"smslogin_trust": self._cookie['smslogin_trust']} if 'smslogin_trust' in self._cookie else {})})
        # print(response_cookies)
        Coremail = response_cookies.get('Coremail', '')
        sid = (re.findall('%(.*?)%', Coremail) + [''])[0]
        self._cookie['Coremail'] = Coremail
        self._cookie['sid'] = sid
        if sid and Coremail:
            self._status = True
            self._time = int(time.time()) + 180
        return self._cookie

    def _stats_session_id(self) -> dict:
        """
        请求ip 获取 stats_session_id
        """
        if self._cookie.get('stats_session_id'): return self._cookie
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "Referer": "https://mail.163.com/",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            **self._header
        }
        url = "https://mail.163.com/fgw/mailsrv-ipdetail/detail"
        response = requests4(method='GET', url=url, headers=headers)
        cookie = response.cookies.get_dict()
        stats_session_id = cookie.get('stats_session_id')
        self._cookie['stats_session_id'] = stats_session_id
        return self._cookie

    def _sdid(self):
        """指纹授权并获取 sdid"""
        if self._cookie.get('sdid'): return self._cookie
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "Content-Length": "71",
            "Referer": "https://mail.163.com/",
            "Origin": "https://mail.163.com",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            **self._header
        }
        cookies = {
            "starttime": "",
            "stats_session_id": self._stats_session_id()['stats_session_id']
        }
        url = "https://mail.163.com/fgw/mailsrv-device-idmapping/webapp/init"
        data = {
            "deviceId": self._deviceId,
            "appVersion": "1.0.0"
        }
        self._cookie['deviceId'] = data['deviceId']
        data = json.dumps(data, separators=(',', ':'))
        response = requests4(method='POST', url=url, headers=headers, cookies=cookies, data=data)
        data_dict = response.json()
        sdid = data_dict.get('result', {}).get('sdid')
        self._cookie['sdid'] = sdid
        return self._cookie

    def read_inbox_emails(self, limit: int=30) -> dict:
        """查询邮件 limit 最多可查20000，但这不是上限，上限需要自测"""
        self._Coremail()
        headers = {
            "Accept": "text/javascript",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Priority": "u=0, i",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Gpc": "1",
            "Upgrade-Insecure-Requests": "1",
            "content-type": "application/x-www-form-urlencoded",
            "Origin": "https://mail.163.com",
            "Referer": f"https://mail.163.com/js6/main.jsp?sid={self._cookie['sid']}&df=mail163_letter",
            **self._header
        }
        cookies = {
            "Coremail": self._cookie['Coremail'],
            "Coremail.sid": self._cookie['sid']
        }
        url = f"https://mail.163.com/js6/s?sid={self._cookie['sid']}&func=mbox:listMessages"
        data = {
            'var': f'<?xml version="1.0"?><object><int name="fid">1</int><string name="order">date</string><boolean name="desc">true</boolean><int name="limit">{limit}</int></object>',
        }
        response = requests4(method='POST', url=url, headers=headers, cookies=cookies, data=data)
        data = json5.loads(self.date_change_str_time(response.text, 1))
        if data.get('code') != 'S_OK': raise Exception('邮件查询失败！！！')
        self.Mailbox = data
        return data

    @staticmethod
    def date_change_str_time(text: str, month_add: int = 0) -> str:
        """
        处理js的时间格式
        `text`: 要处理的文本内容
        `month_add`: 月份添加 专门针对 js 的 new Date,js默认是少一个月份的
        处理文本内容，将文本内的 new Date(2025,3,3,10,17,46) 替换为正常的时间 2025-04-02 10:41:50
        """

        # 将字符串转换为时间对象
        def parse_time(time_str: str, month_add: int = 0) -> str:
            """
            `time_str`: 日期 例如：2025-2-19-11-9-52 或 2025-2-19
            `month_add`: 0或1，代表的是 是否将月份+1
            """
            # 针对 new Date(2025,3,3,10,17,46)
            if time_str.count('-') == 5:
                year, month, day, hour, minute, second = map(int, time_str.split("-"))
                return str(datetime(year, month + month_add, day, hour, minute, second))
            elif time_str.count('-') == 2:
                year, month, day = map(int, time_str.split("-"))
                return str(datetime(year, month + month_add, day))
            raise ValueError('[mail 163]时间格式错误')
        text = re.sub(r'new Date\(\d+,\d+,\d+,\d+,\d+,\d+\)', lambda x: '"' + parse_time(
            '-'.join(re.findall(r'\((.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\)', x.group(0))[0]), 1) + '"',
                      text)
        text = re.sub(r'new Date\(\d+,\d+,\d+\)',
                      lambda x: '"' + parse_time('-'.join(re.findall(r'\((.*?),(.*?),(.*?)\)', x.group(0))[0]),
                                                 1) + '"', text)
        return text

    @property
    def platform_mapping(self):
        '''多平台映射表'''
        return {
            'tiktok': {
                'subject': ['TikTok Shop商家验证码', 'is your verification code', 'TikTok Shop Verification Code'],
                're': '(?=您正在进行邮箱验证，请在验证码输入框中输入|To verify your account, enter this code in TikTok Shop).*?<span class="code">(.*?)<' + '|' + 'color: rgb\(22,24,35\);font-weight: bold;">(.*?)<'
            },
            'shopee': {
                'subject': ['Your Email OTP Verification Code'],
                're': 'line-height: 40px;"> {1,40}<b>(.*?)</b>'
            },
            'shein': {
                'subject': ['您正在登录[SHEIN]系统'],
                're': '登录验证码：(.*?)，'
            },
            'lazada': {
                'subject': ['【重要】请完成验证'],
                're': 'margin-left: -1\.25rem; line-height: 1;"></a>&nbsp;(.*?)<'
            }
        }

    def email_screening_platform(self, time_diff: int=600) -> str:
        """筛选邮件平台 time_diff 秒 """
        if self.mid: return self.mid
        self._Coremail()
        if 'var' not in self.Mailbox:
            self.read_inbox_emails()
        if 'var' not in self.Mailbox:
            raise Exception('查询邮件未执行或查询失败无法进行执行获取邮箱验证码！！')
        # mid占位
        mid_dict = {}
        # 从 几封邮件中筛选出10分钟内最新的邮件并且是官方的邮件，并返回字典数据邮件mid
        for data_dict in self.Mailbox['var']:
            # 将字典内的时间字符串转换为 datetime 对象
            target_time = datetime.strptime(data_dict['receivedDate'], "%Y-%m-%d %H:%M:%S")
            # 计算邮件收到的时间和当前时间误差是多少秒（以秒为单位）
            time_difference = int((datetime.now() - target_time).total_seconds())
            # 1、判断 subject 标题是否一致
            # 2、判断邮件是否是10分钟内的  600秒，可自定义修改
            _ = any(keyword in data_dict['subject'] for keyword in self.platform_mapping[self.platform]['subject'])
            if _ and time_difference <= time_diff:
                # 存储字典为空的情况下，直接把当前合格的字典存储起来。如果有另一封合格邮件，则对比时间，取最新的邮件进行存储
                if (not mid_dict) or ( mid_dict and target_time > datetime.strptime(mid_dict['receivedDate'],
                                                                         "%Y-%m-%d %H:%M:%S")):
                    mid_dict = {
                        'id': data_dict['id'],
                        'receivedDate': data_dict['receivedDate']
                    }
        if not mid_dict:
            raise Exception(f'未检测到{time_diff // 60}分钟内此平台发送的验证码 - {self.platform}')
        self.mid = mid_dict['id']
        return self.mid

    def get_email_by_mid(self, time_diff:int = 600):
        """通过mid读取邮件内容 并提取验证码"""
        if self.platform not in self.platform_mapping:
            raise Exception('platform 参数错误')
        self._Coremail()
        cookies = {
            'Coremail': self._cookie['Coremail'],
            "Coremail.sid": self._cookie['sid']
        }
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Priority": "u=0, i",
            "Referer": f"https://mail.163.com/js6/main.jsp?sid={self._cookie['sid']}&df=mail163_letter",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "iframe",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            **self._header
        }
        response = requests4(method='GET',
                               url=f'https://mail.163.com/js6/read/readhtml.jsp?mid={self.email_screening_platform(time_diff=time_diff)}&userType=ud&font=15&color=3370FF',
                               cookies=cookies, headers=headers)
        req_data = str(response.text).replace('\n', '').replace('\n', '').replace('\t', '').replace('\r', '').replace('\f', '')
        # 提取验证码
        Verification = re.findall(self.platform_mapping[self.platform]['re'], req_data) + ['']
        Verification = (lambda x: x[0] if isinstance(x[0], str) else next((x[0] or x[1] for x in x), None))(
            Verification)
        Verification = Verification.strip()
        # 邮箱验证码： RW4Y8N
        assert Verification, f'验证码捕获失败，正则需修改 - {self.platform}'
        return Verification

    # 官方接口 获取所有已删除的邮件mid
    def get_all_del_js6_s(self):
        '''获取所有已删除的邮件mid'''
        assert self._status, '无法执行'
        headers = {
            "Accept": "text/javascript",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Gpc": "1",
            **self._header
        }
        cookies = {
            'Coremail': self._cookie['Coremail']
        }
        # 一次性获取28000个，方便删除 这个固定不要修改，都是经过严格测试的
        data = {
            'var': f'<?xml version="1.0"?><object><int name="fid">4</int><string name="order">date</string><boolean name="desc">true</boolean><int name="limit">28000</int><int name="start">0</int><boolean name="skipLockedFolders">false</boolean><boolean name="returnTag">true</boolean><boolean name="returnTotal">true</boolean><string name="mrcid">{self._deviceId}</string></object>',
        }
        response = requests4(method='POST',
                               url=f"https://mail.163.com/js6/s?sid={self._cookie['sid']}&func=mbox:listMessages",
                               cookies=cookies, headers=headers, json=data)
        Components.print('[请求结果][get_all_del_js6_s]|[状态码]', response.status_code)
        mid_list = re.findall("'id':'(.*?)'", response.text)
        # 去重
        mid_list = list(set(mid_list))
        Components.print('[获取所有已删除的邮件mid][get_all_del_js6_s]|[数量|数据]', len(mid_list), mid_list[:200])
        # 将列表数据分批，每次最多498条，避免一次性删除太多支撑不住
        mid_list = [mid_list[i:i + 498] for i in range(0, len(mid_list), 498)]
        Components.print('[分批删除][get_all_del_js6_s]', mid_list)
        # 转html并存储到列表内
        data_list = ['<string>' + ('</string><string>'.join(i) + '</string>') for i in mid_list]
        self.mid_list = data_list

        # 执行【删除所有已删除的邮件，彻底删除】
        self.del_all_deleted_emails_js6_s()

    # 官方接口 获取临时彻底删除邮件的权限token 此token为会话级，只能作为临时使用，有效期预估为1天左右，不适合存储
    def get_temporary_del_token(self) -> Union[dict, str]:
        '''
        获取临时彻底删除邮件的权限token
        注意：如果此token获取不到，则说明邮箱有异常，需要验证身份才能进行删除邮件，但不影响查看邮件和读取邮件内的验证码
        '''
        headers = {
            "Accept": "text/javascript",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Gpc": "1",
            "Origin": "https://mail.163.com",
            "Referer": "https://mail.163.com/js6/main.jsp?sid",
            **self._header
        }
        cookies = {
            "Coremail": self._cookie['Coremail']
        }
        data = {
            "actionId": "eec599711e6041238d",  # 固定的id    b1c13ae21986484e86 这个是修改个人信息的id
            "environment": json.dumps({"mrcid": self._deviceId, "mrecp": {}, "mrvar": quote(
                f'<?xml version="1.0"?><object><array name="ids"></array><string name="mrcid">{self._deviceId}</string></object>'),
                                       "hl": "zh_CN"})
        }
        response = requests4(method='POST',
                               url=f"https://mail.163.com/fgw/mailserv-risk-control/risk/action/token?{int(time.time()*1000)}=",
                               cookies=cookies, headers=headers, data=data)
        __hid = Components.hash_encrypt(self.email, 'md5')[:4].upper()
        response_cookies = response.cookies.get_dict()
        MAIL_RISK_CTRL = response_cookies.get(f'MAIL_RISK_CTRL_{__hid}', '')
        assert MAIL_RISK_CTRL, '[get_temporary_del_token] 获取临时删除邮件权限令牌失败'
        return {f'MAIL_RISK_CTRL_{__hid}': MAIL_RISK_CTRL}

    # 官方接口 删除所有已删除的邮件，彻底删除
    def del_all_deleted_emails_js6_s(self):
        '''删除所有已删除的邮件，彻底删除 此步骤执行预估消耗时间：2秒可用删除498封，28000封预估需要1分20秒左右'''
        headers = {
            "Accept": "text/javascript",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Gpc": "1",
            "Origin": "https://mail.163.com",
            "Referer": "https://mail.163.com/js6/main.jsp?sid",
            **self._header
        }
        cookies = {
            'Coremail': self._cookie['Coremail'],
            **self.get_temporary_del_token()
            # 获取删除【彻底删除权限】的token，这个token如果获取不了，说明邮箱是异常的，需要手机验证，还有一种情况是邮箱检测可能有盗号的风险，也是无法删除的
        }
        if len(cookies) < 2:
            return ''
        # 删除28000封邮件预估1分20秒内
        # 循环遍历删除，删除【已删除的邮件】每次最多只能删除498个，所以只能遍历删除
        for mid_str in self.mid_list:
            data = {
                'var': f'<?xml version="1.0"?><object><array name="ids">{mid_str}</array><string name="mrcid">{self._deviceId}</string></object>',
            }
            response = requests4(method='POST',
                                   url=f"https://mail.163.com/js6/s?sid={self._cookie['sid']}&func=mbox:deleteMessages",
                                   cookies=cookies, headers=headers, data=data)
            Components.print('[请求结果][del_all_deleted_emails_js6_s]|[状态码]', response.status_code)
            print(f'[彻底删除{mid_str.count("<string>")}] ->', json5.loads(response.text))
            time.sleep(round(random.uniform(0, 1), 2) or 1)

    def _get_user(self):
        """获取邮箱的用户信息 检测当前令牌是否有效"""
        headers = {
            "Accept": "text/javascript",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Gpc": "1",
            "Referer": "https://mail.163.com",
            **self._header
        }
        cookies = {
            "MAIL_SESS": self._cookie['NTES_SESS']
        }
        url = "https://mail.163.com/fgw/mailsrv-storage-control/fapi/storage"
        params = { str(int(time.time()*1000)): "" }
        response = requests4(method='GET', url=url, headers=headers, cookies=cookies, params=params)
        data_dict = response.json()
        if not (data_dict.get('code') == 200 and data_dict.get('result')):
            raise Exception('令牌错误或已失效！！！！')
        result = data_dict['result']
        self.email = result['uid']

if __name__ == '__main__':
    Email163 = Email163(
        cookie={
            "NTES_SESS": "czbLB6s0OQL7bBuUv",
            "smslogin_trust": '"f0jgsrcS"'
        }
    )
    # -----获取邮件验证码
    # Email163.platform = 'tiktok'   # 设置要获取验证码的平台
    # print(Email163.get_email_by_mid(time_diff=600))  # 获取验证码，默认是获取600秒内的邮件

    # -----执行清空邮件
    # Email163.get_all_del_js6_s()

    # -----获取邮箱号
    # print(Email163.email)

