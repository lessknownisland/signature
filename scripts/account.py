#!/usr/bin/env python
#-_- coding:utf-8 -_-
#author: Arno

import os
import sys

#将上层目录加入环境变量，用于引用其他模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

#设置django环境
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'signature.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "signature.settings")
django.setup() #启动django

from customer.models import CustomerTb
from apple.middleware.api import AppStoreConnectApi
from scripts.middleware.logger import logger
from scripts.config import remind_count, message
from control.middleware.config import RET_DATA
from detect.telegram import SendTelegram

# 获取所有业主
customers = CustomerTb.objects.filter(status=1).all()

for customer in customers:

    message['text'] = f"超级签 账号检测异常\r\n业主: {customer.name}\r\n"

    logger.info(f"#"*100)
    logger.info(f"开始操作 业主: {customer.name}")

    apple_accounts = customer.apple_account.filter(status=1).all()
    for apple_account in apple_accounts:
        asca = AppStoreConnectApi(apple_account.account, apple_account.p8, apple_account.iss, apple_account.kid)
        ret_data = asca.test_connect()
        if ret_data['code'] != 0:
            logger.error(ret_data['data'])
            message['text'] += f"{apple_account.account}: {ret_data['data']}\n"

    # 发送预警信息
    message['group'] = "arno_test2"
    message['doc'] = False

    if len(message['text']) >= 1024:
        message['doc'] = True

    if "errors" in message['text']:
        message['group'] = "arno_test2"
        SendTelegram(message).send()
        message['group'] = "yunwei"
        SendTelegram(message).send()
