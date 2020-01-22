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
from control.middleware.config      import RET_DATA, MESSAGE_TEST, xml, plist, logger
from control.middleware.common      import IsSomeType
from alioss.middleware.api          import get_bucket, AliOssApi, get_bucket_fromurl

import re
import os
import datetime
import subprocess

sh_dir = f"{settings.BASE_DIR}/apple/shell"

def mc_create(package, ret_data=RET_DATA.copy(), aoa=False):
    '''
        生成mobileconfig
    '''

    if not aoa:
        # 获取 bucket
        ret_bucket = get_bucket()
        oss_bucket = ret_bucket['data']
        if not oss_bucket: # 如果 oss_bucket 账号不存在，则退出
            return ret_bucket
        
        # 获取上传的接口
        aoa = AliOssApi(oss_bucket)

    try:
        customer = CustomerTb.objects.get(id=package.customer, status=1)
    except CustomerTb.DoesNotExist as e:
        ret_data['msg'] = f"customer: {package.customer} 不存在或已禁用"
        ret_data['code'] = 500
        return ret_data

    ### 生成 mobileconfig 并上传 ###
    udid_url = customer.udid_url
    mc_tmpname = get_random_s(32) + ".mobileconfig"
    mc_name = get_random_s(32) + ".mobileconfig"
    mc_tmpstr = xml.format(udid_url=udid_url, id=package.id, random_s=get_random_s(32))        
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
        return ret_data

    # 上传 mobileconfig
    ret_mobileconfig = aoa.upload_localfile('mobileconfig', f"{sh_dir}/tmp/{mc_name}")
    if ret_mobileconfig['code'] != 0:
        return HttpResponse(json.dumps(ret_mobileconfig))
    os.remove(f"{sh_dir}/tmp/{mc_tmpname}")
    os.remove(f"{sh_dir}/tmp/{mc_name}")

    package.mobileconfig = ret_mobileconfig['data']
    package.save()

    return ret_data