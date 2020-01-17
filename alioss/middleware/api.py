#-_- coding: utf-8 -_-
from signature                 import settings
from control.middleware.config import RET_DATA

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