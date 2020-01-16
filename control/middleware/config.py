#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from signature                         import settings

import re
import json
import logging
import requests

logger = logging.getLogger('django')

# models 中启用与禁用参数
choices_s = ((1, '启用'), (0, '禁用'),)

choices_proj = (
        ('other',      '其他[other]'), 
        ('appleqp',    '苹果棋牌'), 
        ('caipiao',    '彩票[caipiao]'), 
        ('zhuanyepan', '专业盘[zyp]'), 
        ('sport',      '体育[sport]'),
        ('houtai',     '后台[houtai]'),
        ('pay',        '支付[pay]'),
        ('ggz',        '广告站[ggz]'),
        ('image',      '图片[image]'),
        ('vpn',        'vpn'),
        ('httpdns',    'httpdns'),
    )

choices_permission = (
        ('read',    u'读权限'), 
        ('change',  u'改权限'),
        ('delete',  u'删权限'),
        ('add',     u'增权限'),
        ('execute', u'执行权限'),
    )

# 初始化返回给前端的数据
# 1001: 登陆失效；0: 获取成功；403: 没有权限；400: 非法请求；500: 内部服务错误
RET_DATA = {'code': 1001, 'msg': '请重新登陆'}

# telegram api
TELEGRAM_API = {
    'api':{
        'AuraAlertBot'  : '471691674:AAFx1MQ3VwXdWUYyh4CaErzwoUNswG9XDsU',
        'sa_monitor_bot': '422793714:AAE8A-sLU1Usms2bJxiKWc3tUWaWYP98bSU',
        'KeepMessageBot': '906727223:AAFytrPY0kuZLpkY5-SQKmF9P790sPEiH8U',
    },

    'url':{
        'AuraAlertBot'  : 'https://api.telegram.org/bot471691674:AAFx1MQ3VwXdWUYyh4CaErzwoUNswG9XDsU/',
        'sa_monitor_bot': 'https://api.telegram.org/bot422793714:AAE8A-sLU1Usms2bJxiKWc3tUWaWYP98bSU/',
        'KeepMessageBot': 'https://api.telegram.org/bot906727223:AAFytrPY0kuZLpkY5-SQKmF9P790sPEiH8U/',
    },
}

# telegram 参数
MESSAGE_TEST = {
    'doc': False,
    'bot': "sa_monitor_bot", #AuraAlertBot: 大魔王
    'text': "",
    'group': "arno_test2",
    'parse_mode': "HTML",
    'doc_file': "message.txt",
}

MESSAGE_ONLINE = {
    'doc': False,
    'bot': "sa_monitor_bot", #AuraAlertBot: 大魔王
    'text': "",
    'group': "kindergarten",
    'parse_mode': "HTML",
    'doc_file': "message.txt",
}

#cloudflare api
CF_URL = 'https://api.cloudflare.com/client/v4/zones'

#dnspod api
DNSPOD_URL = 'https://dnsapi.cn/'