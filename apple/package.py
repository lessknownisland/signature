from django.test import TestCase
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from control.middleware.config      import RET_DATA
from apple.middleware.api           import AppStoreConnectApi
from apple.models  import AppleAccountTb, AppleDeviceTb
from alioss.models import AliossBucketTb
from detect.telegram                import SendTelegram
from signature                      import settings
from control.middleware.user        import User, login_required_layui, is_authenticated_to_request
from control.middleware.config      import RET_DATA, MESSAGE_TEST, csr
from control.middleware.common      import IsSomeType
from alioss.middleware.api          import get_bucket, AliOssApi

import re
import json
import logging
import datetime
import random
import string
import oss2
import zipfile
import plistlib

logger = logging.getLogger('django')

# 获取plist路径
def find_path(zip_file, pattern_str):
    name_list = zip_file.namelist()
    pattern = re.compile(pattern_str)
    for path in name_list:
        m = pattern.match(path)
        if m is not None:
            return m.group()

# 获取ipa信息
def get_ipa_info(plist_info):
    print('软件名称: %s' % str(plist_info['CFBundleDisplayName']))
    print('软件标识: %s' % str(plist_info['CFBundleIdentifier']))
    print('软件版本: %s' % str(plist_info['CFBundleShortVersionString']))
    print('支持版本: %s' % str(plist_info['MinimumOSVersion']))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def package_upload(request):
    '''
        上传 IPA 文件
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '上传 ipa 文件'
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

        ipa_file_t = zipfile.ZipFile(ipa_file) # 解压到临时文件

        # 获取 bucket
        ret_bucket = get_bucket()
        oss_bucket = ret_bucket['data']
        if not oss_bucket: # 如果 oss_bucket 账号不存在，则退出
            return ret_bucket

        ### 开始上传 IPA 和 ICON ###
        aoa = AliOssApi(oss_bucket)

        ret_ipa = aoa.upload_stream('ipa', ipa_file) # 上传 IPA 文件
        if ret_ipa['code'] != 0:
            return ret_ipa

        # 上传 IPA 成功后执行
        plist_path = find_path(ipa_file_t, 'Payload/[^/]*.app/Info.plist')

        # 读取plist内容
        plist_data = ipa_file_t.read(plist_path)

        # 解析plist内容
        plist_detail_info = plistlib.loads(plist_data)
        logger.info(plist_detail_info)
        
        device = AppleDeviceTb() # 将 package 信息写入库
        device.name = plist_detail_info['CFBundleName']
        device.version = plist_detail_info['CFBundleShortVersionString']
        device.build_version = plist_detail_info['CFBundleVersion']
        device.mini_version = plist_detail_info['MinimumOSVersion']
        device.ipa = ret_ipa['data']
        device.mobileconfig = "null"

        return HttpResponse(json.dumps(ret_data))
