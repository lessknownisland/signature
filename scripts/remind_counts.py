#!/usr/bin/env python
#-_- coding:utf-8 -_-
#author: Arno
#introduciton:
#    发送telegram 信息，提醒各家超级签所剩的名额
#version: 2019/04/30  实现基本功能

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

    if customer.name == "默认": continue

    message['text'] = f"超级签\r\n业主: {customer.name}\r\n"

    logger.info(f"#"*100)
    logger.info(f"开始操作 业主: {customer.name}")

    # 循环数据，筛选得到所剩名额
    remain_all = 0

    apple_accounts = customer.apple_account.filter(status=1).all()
    for apple_account in apple_accounts:
        message['text'] += f"{apple_account.account}: {apple_account.count}\r\n"
        logger.info(f"{apple_account.account}: {apple_account.count}")
        remain_all += apple_account.count

    logger.info(f"所剩名额总数: {remain_all}")
    message['text'] += "\r\n".join([
            "所剩名额总数: %s" %remain_all,
            # "%s: %s" %(department.department, ", ".join(name)),
        ])

    # 发送预警信息
    message['group'] = "arno_test2"
    message['doc'] = False
    if remain_all <= remind_count:
        message['group'] = "yunwei"
    
    if len(message['text']) >= 1024:
        message['doc'] = True

    SendTelegram(message).send()
