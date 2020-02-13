from django.test import TestCase
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from control.middleware.config      import RET_DATA
from apple.middleware.api           import AppStoreConnectApi
from apple.models  import AppleAccountTb, AppleDeviceTb, CsrTb
from alioss.models import AliossBucketTb
from customer.models import CustomerTb
from detect.telegram                import SendTelegram
from signature                      import settings
from control.middleware.user        import User, login_required_layui, is_authenticated_to_request
from control.middleware.config      import RET_DATA, MESSAGE_TEST
from control.middleware.common      import IsSomeType
from alioss.middleware.api          import get_bucket, AliOssApi

import json
import logging
import datetime
import random
import string
import oss2

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
        4. 更新 bundleIDs
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

        csr = data['csr']

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

            ### 创建 bundleIds ###
            bundleId = apple_account.bundleId
            ret_data = asca.get_bundleIds()
            if ret_data['code'] != 0: # 如果获取bundleIds 失败
                return HttpResponse(json.dumps(ret_data))
            
            for bi in ret_data['data']['data']:
                if bi['attributes']['identifier'] == apple_account.bundleId: # 删除指定 bundleId
                    ret_tmp = asca.delete_bundleIds(bi['id'])
                    if ret_tmp['code'] != 0: # 如果删除bundleIds出现错误，不再执行
                        return HttpResponse(json.dumps(ret_tmp))
            
            # bundleIds删除后，需要重新生成
            apple_account.bundleIds = None
            apple_account.save()

            ret_data = asca.create_bundleIds(bundleId)
            if ret_data['code'] != 0: # 如果创建bundleIds 失败
                return HttpResponse(json.dumps(ret_data))

            # bundleIds 创建成功后，更新入库
            apple_account.bundleIds = ret_data['data']['data']['id']
            apple_account.save()

            # 获取并删除 apple 账号上的 "certificateType": "IOS_DISTRIBUTION" 证书
            ret_data = asca.get_cer()
            # return HttpResponse(json.dumps(ret_data)) # 代码测试
            
            if ret_data['code'] == 0: # 如果是成功的，则执行其他操作
                for cer in ret_data['data']['data']:
                    if cer['attributes']['certificateType'] == 'IOS_DISTRIBUTION': # 删除指定类型的证书
                        ret_tmp = asca.delete_cer(cer['id'])
                        if ret_tmp['code'] != 0: # 如果删除证书出现错误，不再执行创建证书
                            return HttpResponse(json.dumps(ret_tmp))
                        else:
                            apple_account.p12 = None # 证书删除后，需要将新证书重新生成p12
                            apple_account.save()
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
            if 'customer' not in data or not data['customer']:
                accounts = AppleAccountTb.objects.filter(account__icontains=data['account'], status__in=data['status']).order_by('-id')

                for account in accounts:
                    tmp_dict = {}
                    tmp_dict['id'] = account.id
                    tmp_dict['account'] = account.account
                    tmp_dict['count']   = account.count
                    tmp_dict['p12']     = account.p12
                    tmp_dict['cer_id']  = account.cer_id
                    tmp_dict['bundleId']   = account.bundleId
                    tmp_dict['bundleIds']   = account.bundleIds
                    tmp_dict['cer_content'] = account.cer_content
                    tmp_dict['customer'] = ','.join([ customer.name for customer in account.customertb_set.all() ])
                    tmp_dict['status']  = account.status

                    ret_data['data'].append(tmp_dict)
            else:
                customers = CustomerTb.objects.filter(id__in=data['customer']).all()
                for customer in customers:
                    for account in customer.apple_account.filter(account__icontains=data['account'], status__in=data['status']).order_by('-id').all():
                        tmp_dict = {}
                        tmp_dict['id'] = account.id
                        tmp_dict['account'] = account.account
                        tmp_dict['count']   = account.count
                        tmp_dict['p12']     = account.p12
                        tmp_dict['cer_id']  = account.cer_id
                        tmp_dict['bundleId']   = account.bundleId
                        tmp_dict['bundleIds']   = account.bundleIds
                        tmp_dict['cer_content'] = account.cer_content
                        tmp_dict['customer'] = customer.name
                        tmp_dict['status']  = account.status

                        ret_data['data'].append(tmp_dict)

    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = f"{ret_data['msg']} 失败: {str(e)}"

    else:
        ret_data['msg']  = f"{ret_data['msg']} 成功"

    return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def csr_get(request):
    '''
        获取 csr 证书
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '获取csr证书'
    ret_data['data'] = []

    try:
        if request.method == 'GET':
            csrs = CsrTb.objects.filter(status=1).all()

            for csr in csrs:
                tmp_dict = {}
                tmp_dict['id'] = csr.id
                tmp_dict['name'] = csr.name
                tmp_dict['csr_content'] = csr.csr_content

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

    else:
        ret_data['msg']  = f"{ret_data['msg']} 成功"

    return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def account_deploycustomer(request):
    '''
        分配业主
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '分配业主'
    ret_data['data'] = []

    try:
        if request.method == 'POST':
            data = json.loads(request.body)

            logger.info(data)

            account = AppleAccountTb.objects.get(id=data['id']) 

            if data['deploy'] == 'add':
                for customer in CustomerTb.objects.filter(id__in=data['customer']).all():
                    customer.apple_account.add(account)
            elif data['deploy'] == 'delete':
                ret_data['msg']  = '删除业主'
                customer = CustomerTb.objects.get(name=data['customer'])
                customer.apple_account.remove(account)

    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = f"{ret_data['msg']} 失败: {str(e)}"

    else:
        ret_data['msg']  = f"{ret_data['msg']} 成功"

    return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def account_test_connect(request):
    '''
        账号测试连接
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '账号测试连接'
    ret_data['data'] = []

    if request.method == 'POST':
        data = request.POST

        logger.info(data)
        # return HttpResponse(json.dumps(ret_data))

        apple_account = AppleAccountTb.objects.get(id=data['id']) 

        # 引入asca 类
        asca = AppStoreConnectApi(apple_account.account, apple_account.p8, apple_account.iss, apple_account.kid)
        ret_data = asca.test_connect()

        return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def account_delete(request):
    '''
        账号删除
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '账号删除'
    ret_data['data'] = []

    if request.method == 'POST':
        data = request.POST

        # 检查账号ID是否为空
        if 'id' not in data or not IsSomeType(data['id']).is_int(): 
            ret_data['msg'] = '传入的账号id 不正确'
            ret_data['code'] = 500
            logger.error(ret_data['msg'])
            return HttpResponse(json.dumps(ret_data))
        else:
            apple_id = int(data['id'])

        logger.info(data)

        try:
            account = AppleAccountTb.objects.get(id=int(data['id']))
            
            # 删除关联的设备
            AppleDeviceTb.objects.filter(apple_id=account.id).delete()

            # 删除账号
            account.delete()

        except Exception as e:
            logger.error(str(e))
            ret_data['code'] = 500
            ret_data['msg']  = f"{ret_data['msg']} 失败: {str(e)}"

        else:
            ret_data['msg']  = f"{ret_data['msg']} 成功"

        return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def p12_upload(request):
    '''
        上传 p12 文件
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '上传 p12 文件'
    ret_data['data'] = []

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

        if 'oss_bucket_id' not in data or not IsSomeType(data['oss_bucket_id']).is_int(): 
            ret_data['msg'] = '传入的oss_bucket_id 不正确'
            ret_data['code'] = 500
            logger.error(ret_data['msg'])
            return HttpResponse(json.dumps(ret_data))
        else:
            oss_bucket_id = int(data['oss_bucket_id'])

        # 生成一个 p12 随机名称
        random_s = "".join(random.sample(string.ascii_letters + string.digits, 32))

        p12_file = request.FILES.get('file',None) # 获取上传的文件

        if not p12_file: # 判断文件是否存在
            ret_data['msg'] = '未获取到上传的文件'
            ret_data['code'] = 500
            logger.error(ret_data['msg'])
            return HttpResponse(json.dumps(ret_data))

        ### 开始上传 ###
        ret_bucket = get_bucket(id=oss_bucket_id) 
        oss_bucket = ret_bucket['data']
        if not oss_bucket: # 如果 oss_bucket 账号不存在，则退出
            return ret_bucket

        aoa = AliOssApi(oss_bucket)

        apple_account = AppleAccountTb.objects.get(id=data['id']) # 获取苹果账号

        ret_data = aoa.upload_stream('p12', p12_file) # 上传 p12 文件
        if ret_data['code'] != 0:
            return HttpResponse(json.dumps(ret_data))

        apple_account.p12 = ret_data['data'] # 将新上传的p12 地址更新入库
        apple_account.save()

        return HttpResponse(json.dumps(ret_data))
