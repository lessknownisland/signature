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

choices_customer = ( 
            (29, u'公共客户[pub]'),

            #凤凰彩票
            (1, u'阿里[ali]'), 
            (2, u'光大[guangda]'), 
            (34, u'恒达[hengda]'), 
            (121001, u'恒信[hengxin]'), 
            (3, u'乐盈|熊猫[leying]'), 
            (4, u'彩投[caitou]'), 
            (5, u'天天[tiantian]'), 
            (6, u'三德|富豪|668[sande]'), 
            (7, u'uc彩票[uc]'), 
            (10, u'ag彩[agcai]'), 
            #(20, u'福利彩[fulicai]'), 
            #(22, u'亿人[yrcai]'), 
            (23, u'亿腾[yiteng]'),
            #(24, u'永利会[yonglihui]'), 
            #(25, u'618彩[618cai]'), 
            #(28, u'乐天[letian]'),
            (11, u'万游[klc]'),
            #(17, u'yy娱乐城[yy]'),
            #(18, u'永发[yongfa]'),
            (39, u'68彩[68bet]'),
            (40, u'567彩[567bet]'),
            (41, u'专业盘彩票[zyp]'),
            (42, u'飞信[feixin]'),
            (43, u'世彩堂[sct]'),

            #凤凰体育彩票
            (8, u'谷歌[9393cp]'), 
            (9, u'苹果[188cp|3535]'), 
            (19, u'芒果[1717cp]'), 
            (21, u'乐都城[ldc]'), 
            (36, u'瑞银[ruiyin|UBS]'),
            (37, u'勇士[warrior]'),
            (38, u'体彩[tc]'),
            (121002, u'565sport[565体育]'), 
            (121003, u'newregal[新富豪]'), 
            #凤凰体育
            (13, u'钻石[le7|diamond]'),
            #(14, u'大象6668[dx_6668]'),
            #(15, u'大象70887[dx_70887]'),
            #(30, u'大象[daxiang]'),

            #凤凰圆角分
            (32, u'世德[shide]'),
            (33, u'图腾[tuteng]'),

            #Java
            (31, u'恒隆[henglong]'),
            (35, u'迪拜吧[dibaiba]'),

            #越众棋牌
            (101001, u'BB棋牌'),
            (101002, u'汪汪棋牌'),
            )

choices_product = ( 
            (0, u'公共产品[pub]'),
            (12, u'凤凰[fenghuang]'),
            (16, u'勇士[warrior]'),
            (27, u'瑞银[ruiyin|UBS]'),
            (26, u'JAVA'),
            (101, u'越众棋牌'),
            )


# 初始化返回给前端的数据
RET_DATA = {'code': 1001, 'msg': '请重新登陆'}

# telegram api
TELEGRAM_API = {
    'api':{
        'AuraAlertBot'  : '471691674:AAFx1MQ3VwXdWUYyh4CaErzwoUNswG9XDsU',
        'sa_monitor_bot': '422793714:AAE8A-sLU1Usms2bJxiKWc3tUWaWYP98bSU',
    },

    'url':{
        'AuraAlertBot'  : 'https://api.telegram.org/bot471691674:AAFx1MQ3VwXdWUYyh4CaErzwoUNswG9XDsU/',
        'sa_monitor_bot': 'https://api.telegram.org/bot422793714:AAE8A-sLU1Usms2bJxiKWc3tUWaWYP98bSU/',
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