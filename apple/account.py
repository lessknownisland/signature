from django.test import TestCase
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from control.middleware.config      import RET_DATA
from apple.middleware.api           import AppStoreConnectApi
from apple.models import AppleAccountTb, AppleDeviceTb
from detect.telegram                import SendTelegram
from signature                      import settings
from control.middleware.user        import User, login_required_layui, is_authenticated_to_request
from control.middleware.config      import RET_DATA, MESSAGE_TEST, csr
from control.middleware.common      import IsSomeType

import json
import logging
import datetime

logger = logging.getLogger('django')

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def cer_create(request):
    '''
        创建苹果证书，及一些关联操作:

        1. 检查账号ID是否为空
        2. 在进行创建证书前，先关闭此账号的签名请求
        3. 更新数据库中的设备信息
        4. 删除 apple 上的 IOS_DISTRIBUTION 证书
        5. 创建新的证书，并更新账号信息

    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 500 # 请求异常，返回 500
    ret_data['msg']  = '创建证书 失败'

    # 初始化 telegram 信息
    message = MESSAGE_TEST.copy()

    if request.method == 'POST':
        # 获取 POST 数据
        data = request.POST

        # 检查账号ID是否为空
        if 'id' not in data or not IsSomeType(data['id']).is_int(): 
            ret_data['msg'] = '传入的账号id 不正确'
            ret_data['code'] = 500
            logger.error(ret_data['msg'])
            return HttpResponse(json.dumps(ret_data))
        else:
            apple_id = int(data['id'])

        apple_account = AppleAccountTb.objects.get(id=apple_id)
        apple_account.status = 0 # 在进行创建证书前，先关闭此账号的签名请求
        apple_account.save()

        if apple_account:
            # 引入asca 类
            asca = AppStoreConnectApi(apple_account.account, apple_account.p8, apple_account.iss, apple_account.kid)

            # 获取开发者账号上的已注册设备
            ret_data = asca.get_devices()
            
            # 更新数据库中的设备信息
            # AppleDeviceTb.objects.filter(apple_id=apple_id).delete() # 代码测试，删除当前记录的设备信息
            if ret_data['code'] == 0: # 如果是成功的，则执行其他操作
                device_select = AppleDeviceTb.objects.filter(apple_id=apple_id)
                devices = ret_data['data']['data']

                # 更新 apple 表中的剩余签名数量
                apple_account.count = 100 - ret_data['data']['meta']['paging']['total']
                apple_account.save()

                for device in devices: # 将设备信息写入库
                    d = device_select.filter(udid=device['attributes']['udid'])
                    if not d:
                        d = AppleDeviceTb()
                        d.udid = device['attributes']['udid']
                        d.apple_id  = apple_id
                        d.device_id = device['id']
                        d.device_name  = device['attributes']['name']
                        d.device_model = device['attributes']['model']
                        # 苹果返回的是UTC 时间，格式是 "2020-01-13T13:00:46.000+0000"，即 "%Y-%m-%dT%H:%M:%S.%f%z"，所以换成北京时间，应加 8 小时
                        d.create_time  = datetime.datetime.strptime(device['attributes']['addedDate'], '%Y-%m-%dT%H:%M:%S.%f%z')
                        d.save()
                        logger.info(f"udid: {device['attributes']['udid']}, name: {device['attributes']['name']}, device: {device['attributes']['model']} 写入数据库成功。")
                    else:
                        # d = device_select.get(udid=device['attributes']['udid']) # 修正数据库中的 设备创建时间
                        # d.create_time = datetime.datetime.strptime(device['attributes']['addedDate'], '%Y-%m-%dT%H:%M:%S.%f%z')
                        # d.save()
                        logger.info(f"udid: {device['attributes']['udid']}, name: {device['attributes']['name']}, device: {device['attributes']['model']} 在数据库已有记录")

                # return HttpResponse(json.dumps(ret_data)) # 代码测试
            else:
                return HttpResponse(json.dumps(ret_data))

            # 获取并删除 apple 账号上的 "certificateType": "IOS_DISTRIBUTION" 证书
            ret_data = asca.get_cer()
            # return HttpResponse(json.dumps(ret_data)) # 代码测试
            
            if ret_data['code'] == 0: # 如果是成功的，则执行其他操作
                for cer in ret_data['data']['data']:
                    ret_data = asca.delete_cer(cer['id'])
                    if ret_data['code'] != 0: # 如果删除证书出现错误，不再执行创建证书
                        return HttpResponse(json.dumps(ret_data))
            else:
                return HttpResponse(json.dumps(ret_data))

            # 创建证书，获取返回
            ret_data = asca.create_cer(csr)

            if ret_data['code'] == 0: # 如果创建证书是成功的，则执行其他操作
                cer_data = ret_data['data']['data']
                apple_account.cer_id = cer_data['id']
                apple_account.cer_content = cer_data['attributes']['certificateContent']
                apple_account.save()

        return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def account_get(request):
    '''
        获取苹果个人账号
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '获取苹果个人账号'
    ret_data['data'] = []

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            accounts = AppleAccountTb.objects.filter(account__icontains=data['account'], status__in=data['status'])
            logger.info(data)

            for account in accounts:
                tmp_dict = {}
                tmp_dict['id'] = account.id
                tmp_dict['account'] = account.account
                tmp_dict['count']   = account.count
                tmp_dict['p12']     = account.p12
                tmp_dict['cer_content'] = account.cer_content
                tmp_dict['status']  = account.status

                ret_data['data'].append(tmp_dict)

    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = f"{ret_data['msg']} 失败: {str(e)}"

    ret_data['msg']  = f"{ret_data['msg']} 成功"

    return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def account_edit(request):
    '''
        账号修改
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '账号修改'
    ret_data['data'] = []

    try:
        if request.method == 'POST':
            data = json.loads(request.body)

            logger.info(data)
            # return HttpResponse(json.dumps(ret_data))

            account = AppleAccountTb.objects.get(id=data['id']) 

            account.status = int(data['status'])
            account.save()

    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = f"{ret_data['msg']} 失败: {str(e)}"

    ret_data['msg']  = f"{ret_data['msg']} 成功"

    return HttpResponse(json.dumps(ret_data))
