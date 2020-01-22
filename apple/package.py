from django.test import TestCase
from django.http                    import HttpResponse, HttpResponseRedirect
from django.shortcuts               import redirect
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from control.middleware.config      import RET_DATA
from control.middleware.common      import get_random_s
from apple.middleware.api           import AppStoreConnectApi
from apple.middleware.common        import mc_create
from apple.middleware.get_model_object import get_apple_account
from apple.models  import AppleAccountTb, AppleDeviceTb, PackageTb, PackageIstalledTb
from alioss.models import AliossBucketTb
from customer.models import CustomerTb
from detect.telegram                import SendTelegram
from signature                      import settings
from control.middleware.user        import User, login_required_layui, is_authenticated_to_request
from control.middleware.config      import RET_DATA, MESSAGE_TEST, xml, udid_url, plist
from control.middleware.common      import IsSomeType
from alioss.middleware.api          import get_bucket, AliOssApi, get_bucket_fromurl

import re
import os
import json
import logging
import base64
import datetime
import subprocess
import random
import string
import oss2
import zipfile
import plistlib
import platform

from bs4 import BeautifulSoup

logger = logging.getLogger('django')
sh_dir = f"{settings.BASE_DIR}/apple/shell"

# 获取plist路径
def find_path(zip_file, pattern_str):
    name_list = zip_file.namelist()
    pattern = re.compile(pattern_str)
    for path in name_list:
        m = pattern.match(path)
        if m is not None:
            return m.group()
    return None

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def mobileconfig_create(request):
    '''
        手动请求，生成mobileconfig
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '生成mobileconfig 成功'
    ret_data['data'] = []

    if request.method == 'POST':
        # 获取 POST 数据
        data = request.POST

        # 检查ID是否为空
        if 'id' not in data or not IsSomeType(data['id']).is_int(): 
            ret_data['msg'] = '传入的id 不正确'
            ret_data['code'] = 500
            logger.error(ret_data['msg'])
            return HttpResponse(json.dumps(ret_data))
        else:
            package_id = int(data['id'])

        # 获取package
        try:
            package = PackageTb.objects.get(id=package_id)

        except PackageTb.DoesNotExist as e:
            ret_data['msg'] = f"package: {package_id} 不存在"
            ret_data['code'] = 500

        else:
            ret_data = mc_create(package, ret_data)

        return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def package_upload(request):
    '''
        1. 上传IPA 文件
        2. 上传Icon 图片
        3. 将IOS 包的基本信息写入数据库
        4. 生成 mobileconfig 并上传
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '上传ipa文件 成功'
    ret_data['data'] = []

    if request.method == 'POST':
        # 获取 POST 数据
        data = request.POST

        ipa_file = request.FILES.get('file',None) # 获取上传的文件

        if not ipa_file: # 判断文件是否存在
            ret_data['msg'] = '未获取到上传的文件'
            ret_data['code'] = 500
            logger.error(ret_data['msg'])
            return HttpResponse(json.dumps(ret_data))

        ### 开始上传 IPA 和 ICON ###
        # 获取 bucket
        ret_bucket = get_bucket()
        oss_bucket = ret_bucket['data']
        if not oss_bucket: # 如果 oss_bucket 账号不存在，则退出
            return HttpResponse(json.dumps(ret_bucket))
        
        # 获取上传的接口
        aoa = AliOssApi(oss_bucket)

        ### 1. 上传IPA 文件 ###
        ret_ipa = aoa.upload_stream('ipa', ipa_file)
        if ret_ipa['code'] != 0:
            return HttpResponse(json.dumps(ret_ipa))

        ipa_file_t = zipfile.ZipFile(ipa_file) # IPA 解压到临时文件

        # 上传 IPA 成功后执行
        plist_path = find_path(ipa_file_t, 'Payload/[^/]*.app/Info.plist')

        # 读取plist内容
        plist_data = ipa_file_t.read(plist_path)

        # 解析plist内容
        plist_detail_info = plistlib.loads(plist_data)
        logger.info(f"plist: {plist_detail_info}")
        
        # 新建 package 字段
        package = PackageTb()

        ### 2. 上传Icon 图片 ###
        icon_list = plist_detail_info['CFBundleIcons']['CFBundlePrimaryIcon']['CFBundleIconFiles']
        icon_path = find_path(ipa_file_t, f"Payload/[^/]*.app/{icon_list[-1]}@3x.png")
        if not icon_path:
            icon_path = find_path(ipa_file_t, f"Payload/[^/]*.app/{icon_list[-1]}@2x.png")
        if icon_path:
            icon = ipa_file_t.read(icon_path)
            ret_icon = aoa.upload_stream('png', icon) # 上传 Icon 文件
            if ret_icon['code'] == 0: # 如果上传成功，写入icon 的地址
                package.icon = ret_icon['data']

        ### 3. 将IOS 包的基本信息写入数据库 ###
        
        package.name = plist_detail_info['CFBundleName']
        package.version = plist_detail_info['CFBundleShortVersionString']
        package.build_version = plist_detail_info['CFBundleVersion']
        package.mini_version = plist_detail_info['MinimumOSVersion']
        package.bundle_identifier = plist_detail_info['CFBundleIdentifier']
        package.ipa = ret_ipa['data']
        package.mobileconfig = "null"
        package.status = 0
        package.save()

        ### 4. 生成 mobileconfig 并上传 ###
        ret_data = mc_create(package, ret_data, aoa)

        return HttpResponse(json.dumps(ret_data))


def ret_error(ret_data):
    logger.error(ret_data['msg'])
    response = HttpResponse(ret_data['msg'])
    response.status_code = ret_data['code']
    return response

@csrf_exempt
# @login_required_layui
# @is_authenticated_to_request
def package_install(request):
    '''
        给IPA 签名并返回下载地址
    '''
    username, role, clientip = User(request).get_default_values()
    ret_data = RET_DATA.copy()

    if request.method == "POST":
        package_id = request.GET.get('id')
        if not package_id or not IsSomeType(package_id).is_int():  # 如果传入的 ID 不正确
            ret_data['msg'] = '传入的 package id 不正确'
            ret_data['code'] = 500
            return ret_error(ret_data)

        # 获取UDID
        body = str(request.body).split('<?xml')[-1].split('</plist>')[0]
        body = '<?xml{}</plist>'.format(body).replace('\\t', '').replace('\\n', '')
        soup = BeautifulSoup(body)

        xml =soup.find('dict')
        vaules = []
        for item in xml.find_all():
            if item.name == 'string':
                vaules.append(item.text)

        udid = vaules[-2]
        logger.info(f"UDID: {udid}")

        # 获取package
        try:
            package = PackageTb.objects.get(id=package_id, status=1)

        except PackageTb.DoesNotExist as e:
            ret_data['msg'] = f"package: {package_id} 不存在或已禁用"
            ret_data['code'] = 500
            return ret_error(ret_data)

        # 获取业主
        try:
            customer_id = package.customer
            customer = CustomerTb.objects.get(id=customer_id, status=1)

        except CustomerTb.DoesNotExist as e:
            ret_data['msg'] = f"customer: {customer_id} 不存在或已禁用"
            ret_data['code'] = 500
            return ret_error(ret_data)

        # 获取苹果开发者账号
        ret_data = get_apple_account(customer, udid)
        if ret_data['code'] != 0:
            return ret_error(ret_data)
        apple_account = ret_data['data']['apple_account']
        device = ret_data['data']['device']
        logger.info(f"获取到可用的开发者账号: {apple_account.account}")
        device_id = device.id
        cer_id = apple_account.cer_id
        bundleIds = apple_account.bundleIds

        # 安装信息记录历史表
        package_installed = PackageIstalledTb()
        package_installed.package_id = package.id
        package_installed.package_name = package.name
        package_installed.package_version = package.version
        package_installed.device_udid = device.udid
        package_installed.device_name = device.device_name
        package_installed.device_model = device.device_model
        package_installed.customer_id = customer.id
        package_installed.customer_name = customer.name
        package_installed.is_first_install = ret_data['data']['is_first_install']
        package_installed.install_status = 0
        package_installed.save()

        ### 创建 profile ###
        # 引入asca 类
        asca = AppStoreConnectApi(apple_account.account, apple_account.p8, apple_account.iss, apple_account.kid)
        ret_data = asca.create_profile(bundleIds, cer_id, device_id)
        if ret_data['code'] != 0: # 如果profile 创建失败
            return ret_error(ret_data)

        profile_content = ret_data['data']['data']['attributes']['profileContent']
        local_profile = f"{sh_dir}/tmp/{get_random_s(32)}.mobileprovision"
        with open(local_profile, 'wb') as f:
            f.write(base64.b64decode(profile_content))

        ### 下载 p12 ###
        p12 = apple_account.p12
        remote_p12 = p12.split('/')[-1]
        local_p12  = remote_p12 + '.p12'
        if not os.path.exists(f"{sh_dir}/tmp/{local_p12}"): # 如果本地不存在，则从OSS 下载
            # 获取 bucket
            ret_data = get_bucket_fromurl(p12)
            if ret_data['code'] != 0:
                return ret_error(ret_data)
            else:
                bucket = ret_data['data']

            aoa = AliOssApi(bucket)
            ret_data = aoa.download_file(remote_p12, f"{sh_dir}/tmp/{local_p12}")
            if ret_data['code'] != 0:
                return ret_error(ret_data)

        ### 下载 IPA ###
        ipa = package.ipa
        remote_ipa = ipa.split('/')[-1]
        local_ipa  = remote_ipa + '.ipa'
        if not os.path.exists(f"{sh_dir}/tmp/{local_ipa}"): # 如果本地不存在，则从OSS 下载
            # 获取 bucket
            ret_data = get_bucket_fromurl(ipa)
            if ret_data['code'] != 0:
                return ret_error(ret_data)
            else:
                bucket = ret_data['data']

            aoa = AliOssApi(bucket)
            ret_data = aoa.download_file(remote_ipa, f"{sh_dir}/tmp/{local_ipa}")
            if ret_data['code'] != 0:
                return ret_error(ret_data)

        ### 开始签名 ###
        pf = platform.platform()
        if 'Darwin' in pf:
            ausign = f"{sh_dir}/ausign_mac"
        elif 'Linux' in pf:
            ausign = f"{sh_dir}/ausign_linux"
        else:
            ret_data['msg'] = f"系统识别错误，既不是macos 也不是 linux"
            ret_data['code'] = 500
            return ret_error(ret_data)

        # local_ipa = "fOSor6s32lxF10TeGH8KMVWXwZ7BRz9m.ipa"
        # local_p12 = "izxQaR5D82HJvqEoI46XFKuA7bfSwtPc.p12"
        # local_profile = f"{sh_dir}/tmp/A4OX61aQYxKcUynjRDC5SMg37qdT0EWt.mobileprovision"
        signed_ipa = f"{sh_dir}/tmp/{device_id}_{cer_id}_{bundleIds}.ipa"

        shell = f"{ausign} --sign {sh_dir}/tmp/{local_ipa} -c {sh_dir}/tmp/{local_p12} -m {local_profile} -p 'a123w456' -o {signed_ipa}"
        logger.info(f"执行脚本: {shell}")
        s_time = datetime.datetime.now()
        status, result = subprocess.getstatusoutput(shell)
        e_time = datetime.datetime.now()
        if status != 0: # 如果脚本执行失败，返回错误
            ret_data['code'] = 500
            ret_data['msg'] = f"mobiconfig 脚本执行错误: {result}"
            logger.error(ret_data['msg'])
            return HttpResponse(json.dumps(ret_data))
        else:
            logger.info(f"mobiconfig 脚本执行成功: 耗时 {(e_time - s_time).total_seconds()} s")
        
        # 获取 oss bucket
        ret_data = get_bucket()
        if ret_data['code'] != 0:
            return ret_error(ret_data)
        else:
            bucket = ret_data['data']
        aoa = AliOssApi(bucket)

        # ### 上传 已签名的IPA ###
        ret_data = aoa.upload_localfile('ipa', signed_ipa)
        if ret_data['code'] != 0:
            return ret_error(ret_data)
        remote_signed_ipa = ret_data['data']

        ### 生成plist 并上传 ###
        # remote_signed_ipa = "https://banana003bucket.oss-cn-hongkong.aliyuncs.com/9v3VIP4KjnlhgZQTWz7MJrHs1OyqNBut.ipa"
        final_plist = plist.format(remote_signed_ipa=remote_signed_ipa, version=package.version, name=package.name, bundleId=package.bundle_identifier, remote_icon=package.icon)
        ret_data = aoa.upload_stream('plist', final_plist)
        if ret_data['code'] != 0:
            return ret_error(ret_data)
        remote_plist = ret_data['data']

        # 更新当前下载量
        package.count += 1
        package.save()

        # 更新安装状态
        package_installed.install_status = 1
        package_installed.save()

        # 跳转到对应的下载链接
        redirect_url = f"itms-services://?action=download-manifest&url={remote_plist}"
        response = HttpResponse(status=301, content_type="text/html;charset=UTF-8")
        response['Location'] = redirect_url

        return response

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def packages_get(request):
    '''
        获取package 信息
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '获取package 信息'
    ret_data['data'] = []

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            packages = PackageTb.objects.filter(name__icontains=data['name'], status__in=data['status'])
            logger.info(data)

            for package in packages:
                # 获取业主
                try:
                    customer_id = package.customer
                    customer = CustomerTb.objects.get(id=customer_id)

                except CustomerTb.DoesNotExist as e:
                    ret_data['msg'] = f"customer: {customer_id} 不存在"
                    ret_data['code'] = 500
                    return HttpResponse(json.dumps(ret_data))

                tmp_dict = {}
                tmp_dict['id'] = package.id
                tmp_dict['name'] = package.name
                tmp_dict['count'] = package.count
                tmp_dict['version'] = package.version
                tmp_dict['mini_version'] = package.mini_version
                tmp_dict['bundle_identifier'] = package.bundle_identifier
                tmp_dict['ipa'] = package.ipa
                tmp_dict['mobileconfig'] = package.mobileconfig
                tmp_dict['customer'] = customer.name
                tmp_dict['status'] = package.status

                ret_data['data'].append(tmp_dict)

    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = f"{ret_data['msg']} 失败: {str(e)}"

    ret_data['msg']  = f"{ret_data['msg']} 成功"

    return HttpResponse(json.dumps(ret_data))