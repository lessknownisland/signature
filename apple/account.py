from django.test import TestCase
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from control.middleware.config      import RET_DATA
from apple.middleware.common import AppStoreConnectApi
from apple.middleware.config import csr
from apple.models import AppleAccountTb, AppleDeviceTb
from detect.telegram                import SendTelegram
from signature                      import settings
from control.middleware.user        import User, login_required_layui, is_authenticated_to_request
from control.middleware.config      import RET_DATA, MESSAGE_TEST
from control.middleware.common      import IsSomeType

import json
import logging

logger = logging.getLogger('django')

@csrf_exempt
# @login_required_layui
def create_crt(request):
    '''
        创建苹果证书，及一些关联操作:

        1. 判断账号是否已经入库
        2. 在进行创建证书前，先关闭此账号的签名请求
        3. 删除数据库中已记录的设备记录
        4. 获取开发者账号上的已注册设备，并写入数据库
        5. 删除 apple 上的 IOS_DISTRIBUTION 证书
        6. 创建新的证书，并更新账号信息

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

            # # 获取开发者账号上的已注册设备
            # ret_data = asca.get_devices()
            
            # # 先删除数据库中已记录的设备记录
            # AppleDeviceTb.objects.filter(apple_id=apple_id).delete()

            # if ret_data['code'] == 0: # 如果是成功的，则执行其他操作
            #     devices = ret_data['data']['data']
            #     for device in devices: # 将设备信息写入库
            #         d = AppleDeviceTb()
            #         d.udid = device['attributes']['udid']
            #         d.apple_id = apple_id
            #         d.device_id = device['id']
            #         d.device_name = device['attributes']['name']
            #         d.device_model = device['attributes']['model']
            #         d.save()

            #     return HttpResponse(json.dumps(ret_data))
            # else:
            #     return HttpResponse(json.dumps(ret_data))

            # 获取并删除 apple 账号上的 "certificateType": "IOS_DISTRIBUTION" 证书
            ret_data = asca.get_cer()
            if ret_data['code'] == 0: # 如果是成功的，则执行其他操作
                for cer in ret_data['data']['data']:
                    return asca.delete_cer(cer['id'])
            else:
                return HttpResponse(json.dumps(ret_data))

            # # 创建证书，获取返回
            # ret_data = asca.create_cer(csr)

            # if ret_data['code'] == 0: # 如果创建证书是成功的，则执行其他操作
            #     cer_data = ret_data['data']['data']
            #     apple_account.cer_id = cer_data['id']
            #     apple_account.cer_content = str(cer_data)
            #     apple_account.save()

        return HttpResponse(json.dumps(ret_data))

