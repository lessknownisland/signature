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

from urllib.parse import urlparse

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
        self.__bucket_name = self.__oss_bucket.bucket_name
        self.__main_host = self.__oss_bucket.main_host
        self.__auth = oss2.Auth(self.__access_keyid, self.__access_keysecret)
        self.__bucket = oss2.Bucket(self.__auth, self.__main_host, self.__bucket_name)
        self.__ret_data = RET_DATA.copy()

        self.__req_id = 'bucket_' + ''.join(str(random.choice(range(10))) for _ in range(10)) # 对每一次bucket 操作，指定一个随机的10位数
        # self.__ret_data['msg'] = f"req_id: {self.__req_id}"
        self.__headers = {'Content-Type': 'application/octet-stream'}

        # 将当前 bucket 信息写入日志
        logger.info(f"bucket: {self.__bucket_name}")
        logger.info(f"bucket_host: {self.__main_host}")
        logger.info(f"req_id: {self.__req_id}")

    def upload_stream(self, file_ext, file_stream, headers={'Content-Type': 'application/octet-stream'}):
        '''
            上传文件流
        '''
        # 生成一个 32 位随机名称
        random_s = "".join(random.sample(string.ascii_letters + string.digits, 32))
        self.__file_name = f"{random_s}.{file_ext}" # 上传到 OSS 的文件名

        ret_data = RET_DATA.copy()
        ret_data['code'] = 0
        ret_data['msg'] = f"req_id: {self.__req_id} : {self.__file_name} 文件上传"

        ret = self.__bucket.put_object(self.__file_name, file_stream, headers=headers)

        if ret.status == 200:
            ret_data['msg']  += " 成功"
            ret_data['data'] = f"{self.__oss_bucket.main_host}/{self.__file_name}".replace("https://", f"https://{self.__oss_bucket.bucket_name}.")
            logger.info(ret_data['msg'])

        else:
            ret_data['code'] = 500
            ret_data['msg']  += " 失败"
            logger.error(ret_data['msg'])

        return ret_data

    def upload_localfile(self, file_ext, file_local, headers={'Content-Type': 'application/octet-stream'}):
        '''
            上传文件流
        '''
        # 生成一个 32 位随机名称
        random_s = "".join(random.sample(string.ascii_letters + string.digits, 32))
        self.__file_name = f"{random_s}.{file_ext}" # 上传到 OSS 的文件名

        ret_data = RET_DATA.copy()
        ret_data['code'] = 0
        ret_data['msg'] = f"req_id: {self.__req_id} : {self.__file_name} 文件上传"

        ret = self.__bucket.put_object_from_file(self.__file_name, file_local, headers=headers)

        if ret.status == 200:
            ret_data['msg']  += " 成功"
            ret_data['data'] = f"{self.__oss_bucket.main_host}/{self.__file_name}".replace("https://", f"https://{self.__oss_bucket.bucket_name}.")
            logger.info(ret_data['msg'])

        else:
            ret_data['code'] = 500
            ret_data['msg']  += " 失败"
            logger.error(ret_data['msg'])

        return ret_data

    def download_file(self, file_remote, file_local):
        '''
            下载文件
        '''
        ret_data = RET_DATA.copy()
        ret_data['code'] = 0
        ret_data['msg'] = f"req_id: {self.__req_id} : {file_remote} ---> {file_local} 文件下载"
        ret = self.__bucket.get_object_to_file(file_remote, file_local)

        if ret.status == 200:
            ret_data['msg']  += " 成功"
            logger.info(ret_data['msg'])

        else:
            ret_data['code'] = 500
            ret_data['msg']  += " 失败"
            logger.error(ret_data['msg'])

        return ret_data

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

def get_bucket_fromurl(url):
    '''
        从url 中提取 bucket_name 和 main_host，筛选得到 bucket object
    '''
    ret_data = RET_DATA.copy()
    result = urlparse(url)
    bucket_name = result.netloc.split('.')[0]
    main_host   = url.replace(result.path, '').replace(f"{bucket_name}.", '')

    # 获取bucket
    try:
        bucket = AliossBucketTb.objects.get(bucket_name=bucket_name, main_host=main_host)
        ret_data['msg'] = f"bucket: {bucket_name} - {main_host} 获取成功"
        ret_data['code'] = 0
        ret_data['data'] = bucket
        logger.info(ret_data['msg'])

    except AliossBucketTb.DoesNotExist as e:
        ret_data['msg'] = f"bucket: {bucket_name} - {main_host} 不存在"
        ret_data['code'] = 500
        logger.error(ret_data['msg'])
        
    return ret_data


