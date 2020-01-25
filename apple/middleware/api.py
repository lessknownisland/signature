#-_- coding: utf-8 -_-
from signature                 import settings
from control.middleware.config import RET_DATA, apple_url
from control.middleware.common import get_random_s

import re
import json
import logging
import datetime
import requests
import random
import time
import jwt

logger = logging.getLogger('django')

class AppStoreConnectApi(object):
    '''
        苹果开发者商店 接口
    '''
    def __init__(self, account, p8, iss, kid):
        '''
            初始化 个人开发者账号信息
        '''
        self.__account = account
        self.__p8 = p8
        self.__iss = iss
        self.__kid = kid
        self.__ret_data = RET_DATA.copy()
        self.__timeout  = 15
        self.__verify   = False
        self.__token    = self._get_token()

    def _get_token(self):
        '''
            利用 jwt 获取token
        '''
        # 苹果采用的 ES256 编码方式，key是需要分段(\n)的，密钥头尾的"—BEGIN PRIVATE KEY—"也是必须的。之前我一直直接复制privatekey以文本的形式输入，在HS256下正常但是ES256会报错ValueError: Could not deserialize key data。
        private_key = "-----BEGIN PRIVATE KEY-----" + self.__p8.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "").replace(" ", "\n") + "-----END PRIVATE KEY-----"

        # payload
        token_dict = {
            "exp": time.time() + 20*60,  # 时间戳, token 有效时间 20分钟
            "iss": self.__iss,
            "aud": "appstoreconnect-v1"
        }

        # headers
        headers = {
            "alg": "ES256",  # 声明所使用的算法。
            "kid": self.__kid,
            "typ": "JWT",
        }
        
        try:
            # 使用jwt 获取苹果开发者 接口token
            jwt_token = jwt.encode(token_dict, private_key, algorithm="ES256", headers=headers)
            token = str(jwt_token, encoding='utf-8')
            logger.info(f"{self.__account} : {token}")
            return token
        except Exception as e:
            logger.error(f"获取苹果开发者 {self.__account} 接口token 错误: {str(e)}")
            return None

    def create_profile(self, bundleIds, cer_id, device_id):
        '''
            创建profile
        '''
        # 初始化 req 参数
        self.__content = "创建profile"
        self.__method = "POST"
        self.__url    = f"{apple_url}/profiles"
        self.__data   = {
            "data": {
                "type": "profiles", 
                "attributes": {
                    "name": get_random_s(16),
                    "profileType": "IOS_APP_ADHOC"
                },
                "relationships": {
                    "bundleId": { 
                        "data": {
                            "id": bundleIds,
                            "type": "bundleIds"
                        }
                    },
                    "certificates": {
                        "data": [{
                            "id": cer_id,
                            "type": "certificates"
                        }]
                    },
                    "devices": {
                        "data": [{
                            "id": device_id,
                            "type": "devices"
                        }]
                    }
                }
            }
        }
        self.__headers = {"Content-Type": "application/json"}

        # 获取接口结果
        return self._send_req()

    def create_devices(self, udid):
        '''
            创建devices
        '''
        # 初始化 req 参数
        self.__content = "创建devices"
        self.__method = "POST"
        self.__url    = f"{apple_url}/devices"
        self.__data   = {
            "data": {
                "type": "devices", 
                "attributes": {
                    "udid": udid,
                    "name": udid,
                    "platform": "IOS",
                }
            }
        }
        self.__headers = {"Content-Type": "application/json"}

        # 获取接口结果
        return self._send_req()

    def create_bundleIds(self, bundleId):
        '''
            创建bundleIds:
        '''
        # 初始化 req 参数
        self.__content = "创建bundleIds"
        self.__method = "POST"
        self.__url    = f"{apple_url}/bundleIds"
        self.__data   = {
            "data": {
                "type": "bundleIds", 
                "attributes": {
                    "identifier": bundleId,
                    "name": "AppBundleId",
                    "platform": "IOS",
                }
            }
        }
        self.__headers = {"Content-Type": "application/json"}

        # 获取接口结果
        return self._send_req()

    def delete_bundleIds(self, bundleIds):
        '''
            删除bundleIds
        '''
        # 初始化 req 参数
        self.__content = "删除bundleIds"
        self.__method = "DELETE"
        self.__url    = f"{apple_url}/bundleIds/{bundleIds}"
        self.__data   = {}
        self.__headers = {"Content-Type": "application/json"}

        # 获取接口结果
        return self._send_req()

    def get_bundleIds(self):
        '''
            获取bundleIds
        '''
        # 初始化 req 参数
        self.__content = "获取bundleIds"
        self.__method = "GET"
        self.__url    = f"{apple_url}/bundleIds?limit=200"
        self.__data   = {
            "platform": "IOS"
        }
        self.__headers = {"Content-Type": "application/json"}

        # 获取接口结果
        return self._send_req()

    def create_cer(self, csr):
        '''
            创建证书:
            {
                "certificateType": "IOS_DISTRIBUTION"
            }
        '''
        # 初始化 req 参数
        self.__content = "创建证书"
        self.__method = "POST"
        self.__url    = f"{apple_url}/certificates"
        self.__data   = {
            "data": {
                "type": "certificates", 
                "attributes": {
                    "csrContent": csr,
                    "certificateType": "IOS_DISTRIBUTION"
                }
            }
        }
        self.__headers = {"Content-Type": "application/json"}

        # 获取接口结果
        return self._send_req()

    def delete_cer(self, cer_id):
        '''
            删除证书:
            {
                "certificateType": "IOS_DISTRIBUTION"
            }
        '''
        # 初始化 req 参数
        self.__content = "删除证书"
        self.__method = "DELETE"
        self.__url    = f"{apple_url}/certificates/{cer_id}"
        self.__data   = {}
        self.__headers = {"Content-Type": "application/json"}

        # 获取接口结果
        return self._send_req()

    def get_cer(self):
        '''
            获取证书:
            {
                "certificateType": "IOS_DISTRIBUTION"
            }
        '''
        # 初始化 req 参数
        self.__content = "获取证书"
        self.__method = "GET"
        self.__url    = f"{apple_url}/certificates?limit=200"
        self.__data   = {
            "certificateType": "IOS_DISTRIBUTION"
        }
        self.__headers = {"Content-Type": "application/json"}

        # 获取接口结果
        return self._send_req()

    def get_devices(self):
        '''
            获取开发者账号上的已注册设备
            GET https://api.appstoreconnect.apple.com/v1/devices
        '''
        # 初始化 req 参数
        self.__content = "获取已注册设备信息"
        self.__method = "GET"
        self.__url    = f"{apple_url}/devices?limit=200"
        self.__data   = {}
        self.__headers = {"Content-Type": "application/json"}

        # 获取接口结果
        return self._send_req()

    def _send_req(self):
        '''
            发送 requests 请求
        '''
        token = self.__token
        if not token: # 获取token 失败
            self.__ret_data['msg']  = "获取 苹果账号token 失败"
            self.__ret_data['code'] = 500
            return self.__ret_data

        self.__headers["Authorization"] = f"Bearer {token}"

        self.__req_id = ''.join(str(random.choice(range(10))) for _ in range(10)) # 对每一次请求，指定一个随机的10位数
        logger.info(f"""{self.__content}: # 记录请求参数
            req_id: {self.__req_id}
            method: {self.__method}
            url: {self.__url}
            data: {self.__data}
            headers: {self.__headers}
        """)

        s = requests.Session()
        req = requests.Request(self.__method, self.__url,
            data=json.dumps(self.__data),
            headers=self.__headers
        )
        prepped = s.prepare_request(req)
        try:
            ret = s.send(prepped, verify=self.__verify, timeout=self.__timeout) # 发起请求
            
            self.__ret_data['code'] = 0
            if ret.status_code == 204: # 状态码 204，返回内容为空，例如 DELETE 证书的请求
                self.__ret_data['data'] = f"{self.__account}: {self.__content} 成功"
                logger.info(f"req_id: {self.__req_id} {self.__ret_data['data']}")

            else:
                app_ret = ret.json()
                self.__ret_data['data'] = app_ret
                self.__ret_data['msg']  = f"{self.__account}: {self.__content} 成功"

                if "errors" in app_ret.keys():
                    self.__ret_data['msg']  = f"{self.__account}: {self.__content} 失败"
                    self.__ret_data['code'] = 500
                    logger.error(f"req_id: {self.__req_id} {self.__ret_data['msg']}: {self.__url} :{str(app_ret)}")

                else:
                    logger.info(f"req_id: {self.__req_id} {self.__ret_data['msg']}: {self.__url} :{str(app_ret)}")
        
        except Exception as e:
            self.__ret_data['msg'] = f"{self.__account}: {self.__content} 失败: {ret.text}"
            self.__ret_data['code'] = 500
            logger.error(f"req_id: {self.__req_id} {self.__account}: {self.__content} 失败: {self.__url} : {str(e)}。返回错误: {ret.text}")

        return self.__ret_data

    def test_connect(self):
        '''
            测试账号能够正常通过 苹果API 来连接
        '''
        # 初始化 req 参数
        self.__content = "测试连接"
        self.__method = "GET"
        self.__url    = f"{apple_url}/apps"
        self.__data   = {}
        self.__headers = {"Content-Type": "application/json"}

        # 获取接口结果
        return self._send_req()
