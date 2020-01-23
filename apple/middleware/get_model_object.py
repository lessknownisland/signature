#-_- coding: utf-8 -_-
from signature                 import settings
from control.middleware.config import RET_DATA, apple_url, logger
from apple.models              import AppleAccountTb, AppleDeviceTb
from customer.models           import CustomerTb
from apple.middleware.api      import AppStoreConnectApi

import json
import datetime
import random
import time


def get_apple_account(customer, udid):
    '''
        通过设备的udid 分配开发者账号:
        1. 通过业主查询，是否已有注册的记录
        2. 没有已注册记录，分配新的开发者账号
    '''
    ret_data = RET_DATA.copy()
    ret_data['msg'] = f"customer: {customer.name} 开发者账号获取成功。"
    ret_data['code'] = 0
    ret_data['data'] = {
        'apple_account': None,
        'is_first_install': 1 # 1 代表是需要新注册的设备
    }

    # 获取苹果开发者账号
    # try:
    #     devices = AppleDeviceTb.objects.get(udid=udid)
    #     apple_account_id = device.apple_id

    # except AppleDeviceTb.DoesNotExist as e:
    #     logger.info(f"device udid: {udid} 不存在。开始分配新账号...")

    #     ret_data = get_available_aa(customer, udid)
    #     ret_data['data']['is_first_install'] = 1

    # else:
    #     apple_accounts = customer.apple_account.filter(status=1, id=apple_account_id)
    #     if len(apple_accounts) == 0:
    #         ret_data = get_available_aa(customer, udid)
    #         ret_data['data']['is_first_install'] = 1
    #     else:
    #         ret_data['data']['apple_account'] = apple_accounts[0]
    #         ret_data['data']['device_id'] = device.device_id
    #         ret_data['data']['is_first_install'] = 0

    devices = AppleDeviceTb.objects.filter(udid=udid, status=1).all()
    for device in devices:
        apple_account_id = device.apple_id
        apple_accounts = customer.apple_account.filter(status=1, id=apple_account_id)
        if len(apple_accounts) != 0:
            ret_data['data']['apple_account'] = apple_accounts[0]
            ret_data['data']['device'] = device
            ret_data['data']['is_first_install'] = 0
            break

    if not ret_data['data']['apple_account']:
        ret_data = get_available_aa(customer, udid)
        ret_data['data']['is_first_install'] = 1


    return ret_data

def get_available_aa(customer, udid):
    '''
        获取可用的目前剩余下载次数最多的一个账号
    '''
    ret_data = RET_DATA.copy()
    ret_data['msg'] = f"customer: {customer.name} 开发者账号获取成功。"
    ret_data['code'] = 0
    ret_data['data'] = {}
    apple_accounts = customer.apple_account.filter(status=1, count__gt=0).order_by('-count')
    if len(apple_accounts) > 0:
        apple_account = apple_accounts[0]
        ret_data['data']['apple_account'] = apple_account

        # 为新设备在账号上进行注册
        # 引入asca 类
        asca = AppStoreConnectApi(apple_account.account, apple_account.p8, apple_account.iss, apple_account.kid)
        ret_tmp = asca.create_devices(udid)
        if ret_tmp['code'] != 0:
            return ret_tmp
        else:
            device_id = ret_tmp['data']['data']['id']
            
            # 更新账号剩余签名次数
            apple_account.count -= 1
            apple_account.save()

            # 将新注册的设备信息写入库
            device = AppleDeviceTb()
            device.apple_id = apple_account.id
            device.device_id = device_id
            device.udid = udid
            device.device_name = ret_tmp['data']['data']['attributes']['name']
            device.device_model = ret_tmp['data']['data']['attributes']['model']
            device.save()
        
            ret_data['data']['device'] = device

    else:
        ret_data['msg'] = f"customer: {customer.name} 已无可用的开发者账号。"
        ret_data['code'] = 500
        
    return ret_data
