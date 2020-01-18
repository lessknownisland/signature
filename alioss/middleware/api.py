#-_- coding: utf-8 -_-
from signature                 import settings
from control.middleware.config import RET_DATA
from alioss.models             import AliossBucketTb

import re
import json
import logging
import datetime
import requests
import random
import string
import time
import oss2

logger = logging.getLogger('django')

class AliOssApi(object):
    '''
        阿里云OSS 接口
    '''
    def __init__(self, oss_bucket):
        '''
            生成oss auth
        '''
        self.__oss_bucket = oss_bucket
        self.__access_keyid = oss_bucket.access_keyid
        self.__access_keysecret = oss_bucket.access_keysecret
        self.__auth = oss2.Auth(self.__access_keyid, self.__access_keysecret)
        self.__bucket = oss2.Bucket(self.__auth, self.__oss_bucket.main_host, self.__oss_bucket.bucket_name)
        self.__ret_data = RET_DATA.copy()

        self.__req_id = 'bucket_' + ''.join(str(random.choice(range(10))) for _ in range(10)) # 对每一次bucket 操作，指定一个随机的10位数

    def upload_stream(self, file_ext, file_stream):
        '''
            上传文件流
        '''
        # 生成一个 32 位随机名称
        random_s = "".join(random.sample(string.ascii_letters + string.digits, 32))
        self.__file_name = f"{random_s}.{file_ext}"

        self.__ret_data['code'] = 0
        self.__ret_data['msg'] = f"req_id: {self.__req_id} : {self.__file_name} 文件上传"

        ret = self.__bucket.put_object(self.__file_name, file_stream)

        if ret.status == 200:
            self.__ret_data['msg']  = f"{self.__ret_data['msg']} 成功"
            self.__ret_data['data'] = f"{self.__oss_bucket.main_host}/{self.__file_name}".replace("https://", f"https://{self.__oss_bucket.bucket_name}.")
            logger.info(self.__ret_data['msg'])

        else:
            self.__ret_data['code'] = 500
            self.__ret_data['msg']  = f"{self.__ret_data['msg']} 失败"
            logger.error(self.__ret_data['msg'])

        return self.__ret_data['msg']


def get_bucket():
    '''
        获取可用的阿里云OSS
        ret_data: {
            'code': 404, # 说明无可用的bucket
            'msg': "",
            'data': bucket
        }
    '''
    __ret_data = RET_DATA.copy()
    __ret_data['data'] = None

    buckets = AliossBucketTb.objects.filter(status=1).all()
    for bucket in buckets:
        __ret_data = {
            'code': 0,
            'msg': "bucket 获取成功",
            'data': bucket
        }
        break
    
    if not __ret_data['data']:
        __ret_data = {
            'code': 404,
            'msg': "bucket 获取失败",
            'data': bucket
        }

    return __ret_data