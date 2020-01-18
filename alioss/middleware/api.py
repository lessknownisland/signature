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
import time
import oss2

logger = logging.getLogger('django')

class AliOssApi(object):
    '''
        阿里云OSS 接口
    '''
    def __init__(self, access_keyid, access_keysecret):
        '''
            生成oss auth
        '''
        self.__access_keyid = access_keyid
        self.__access_keysecret = access_keysecret
        self.__auth = oss2.Auth(access_keyid, access_keysecret)

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