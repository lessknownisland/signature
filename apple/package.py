from django.test import TestCase
from django.http                    import HttpResponse
from django.shortcuts               import redirect
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from control.middleware.config      import RET_DATA
from control.middleware.common      import get_random_s
from apple.middleware.api           import AppStoreConnectApi
from apple.middleware.get_model_object import get_apple_account
from apple.models  import AppleAccountTb, AppleDeviceTb, PackageTb
from alioss.models import AliossBucketTb
from customer.models import CustomerTb
from detect.telegram                import SendTelegram
from signature                      import settings
from control.middleware.user        import User, login_required_layui, is_authenticated_to_request
from control.middleware.config      import RET_DATA, MESSAGE_TEST, csr, xml, udid_url
from control.middleware.common      import IsSomeType
from alioss.middleware.api          import get_bucket, AliOssApi, get_bucket_fromurl

import re
import os
import json
import logging
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
            return ret_bucket
        
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
        sh_dir = f"{settings.BASE_DIR}/apple/shell"
        mc_tmpname = "".join(random.sample(string.ascii_letters + string.digits, 32)) + ".mobileconfig"
        mc_name = "".join(random.sample(string.ascii_letters + string.digits, 32)) + ".mobileconfig"
        mc_tmpstr = xml.format(udid_url=udid_url, id=package.id, random_s="".join(random.sample(string.ascii_letters + string.digits, 32)))        
        with open(f"{sh_dir}/tmp/{mc_tmpname}", 'w') as f:
            f.write(mc_tmpstr)
        
        # 执行mobileconfig 脚本
        shell = f"openssl smime -sign -in {sh_dir}/tmp/{mc_tmpname} -out {sh_dir}/tmp/{mc_name} -signer {sh_dir}/InnovCertificates.pem -certfile {sh_dir}/root.crt.pem -outform der -nodetach"
        logger.info(f"执行脚本: {shell}")
        status, result = subprocess.getstatusoutput(shell)
        if status != 0: # 如果脚本执行失败，返回错误
            ret_data['code'] = 500
            ret_data['msg'] = f"mobiconfig 脚本执行错误: {result}"
            logger.error(ret_data['msg'])
            return HttpResponse(json.dumps(ret_data))

        # 上传 mobileconfig
        ret_mobileconfig = aoa.upload_localfile('mobileconfig', f"{sh_dir}/tmp/{mc_name}")
        if ret_mobileconfig['code'] != 0:
            return HttpResponse(json.dumps(ret_mobileconfig))
        os.remove(f"{sh_dir}/tmp/{mc_tmpname}")
        os.remove(f"{sh_dir}/tmp/{mc_name}")

        package.mobileconfig = ret_mobileconfig['data']
        package.save()

        return HttpResponse(json.dumps(ret_data))


def ret_error(ret_data):
    logger.error(ret_data['msg'])
    response = HttpResponse(ret_data['msg'])
    response.status_code = ret_data['code']
    return response

@csrf_exempt
# @login_required_layui
# @is_authenticated_to_request
def package_get(request):
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
            package = PackageTb.objects.get(id=package_id)

        except PackageTb.DoesNotExist as e:
            ret_data['msg'] = f"package: {package_id} 不存在"
            ret_data['code'] = 500
            return ret_error(ret_data)

        # 获取业主
        try:
            customer_id = package.customer
            customer = CustomerTb.objects.get(id=customer_id)

        except CustomerTb.DoesNotExist as e:
            ret_data['msg'] = f"customer: {customer_id} 不存在"
            ret_data['code'] = 500
            return ret_error(ret_data)

        # 获取苹果开发者账号
        ret_data = get_apple_account(customer, udid)
        if ret_data['code'] != 0:
            return ret_error(ret_data)
        apple_account = ret_data['data']['apple_account']
        logger.info(f"获取到可用的开发者账号: {apple_account.account}")
        device_id = ret_data['data']['device_id']
        cer_id = apple_account.cer_id
        bundleIds = apple_account.bundleIds

        # 创建 profile
        # 引入asca 类
        asca = AppStoreConnectApi(apple_account.account, apple_account.p8, apple_account.iss, apple_account.kid)
        ret_data = asca.create_profile(bundleIds, cer_id, device_id)
        if ret_data['code'] != 0: # 如果profile 创建失败
            return ret_error(ret_data)

        logger.info(ret_data['data'])


        return HttpResponse("111")

        ### 下载 p12 ###
        p12 = apple_account.p12
        remote_p12 = p12.split('/')[-1]
        # local_p12  = f"{sh_dir}/tmp/{get_random_s}"
        local_p12  = get_random_s + '.p12'

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
        # local_ipa  = f"{sh_dir}/tmp/{get_random_s}"
        local_ipa  = get_random_s + '.ipa'

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

        shell = f"{ausign} --sign $1 -c $2 -m $3 -p 'a123w456'"
        logger.info(f"执行脚本: {shell}")
        status, result = subprocess.getstatusoutput(shell)
        if status != 0: # 如果脚本执行失败，返回错误
            ret_data['code'] = 500
            ret_data['msg'] = f"mobiconfig 脚本执行错误: {result}"
            logger.error(ret_data['msg'])
            return HttpResponse(json.dumps(ret_data))



        return HttpResponse("111")
        # return redirect('https://www.baidu.com/')