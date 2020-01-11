#-_- coding: utf-8 -_-
from signature                    import settings
from control.middleware.config import RET_DATA
# from domainns.models           import AlterHistoryTb

# 装饰器
from functools import wraps

import re
import json
import logging
import datetime

logger = logging.getLogger('django')

# Create your views here.
class IsSomeType(object):
    '''
        用于判断字符串是否是指定的数据类型
    '''
    def __init__(self, strToverify):
        self.__strToverify = strToverify

    def is_int(self):
        '''
            判断字符串是否是整数型
        '''
        try:
            if isinstance(int(self.__strToverify), int):
                return True
            else:
                return False
        except Exception as e:
            return False
        
# def insert_ah(clientip, username, pre_rec, now_rec, result=True, action='change'):
#     logger.info("req_ip: %s | user: %s | %s-record: { %s } ---> { %s } {result: %s}" %(clientip, username, action, pre_rec, now_rec, result))

#     insert_h = AlterHistoryTb(
#             time    = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#             req_ip  = clientip,
#             user    = username,
#             pre_rec = pre_rec,
#             now_rec = now_rec,
#             action  = action,
#             status  = result,
#         )

#     insert_h.save()