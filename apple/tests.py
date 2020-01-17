from django.test import TestCase
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from control.middleware.user        import User, login_required_layui
from control.middleware.config      import RET_DATA, logger
from apple.middleware.api import AppStoreConnectApi
from signature     import settings
from apple.models  import AppleAccountTb
from alioss.models import AliossBucketTb

import json
import oss2

@csrf_exempt
@login_required_layui
def test(request):
    '''
        测试
    '''
    username, role, clientip = User(request).get_default_values()

    ret_data = RET_DATA.copy()

    # apple_account = AppleAccountTb.objects.get(id=2)

    # asca = AppStoreConnectApi(apple_account.account, apple_account.p8, apple_account.iss, apple_account.kid)

    # ret_data = asca.create_crt(csr)
    return HttpResponse(json.dumps(ret_data))


@csrf_exempt
# @login_required_layui
def test_alioss(request):
    '''
        测试 阿里云 OSS API
    '''
    username, role, clientip = User(request).get_default_values()

    ret_data = RET_DATA.copy()
    ret_data['code'] = 0
    ret_data['msg']  = "测试 ok"

    oss_bucket = AliossBucketTb.objects.get(id=1)
    
    ret_data['data'] = {
        'bucket': oss_bucket.bucket_name,
        'access_keyid': oss_bucket.access_keyid,
        'access_keysecret': oss_bucket.access_keysecret,
        'main_host': oss_bucket.main_host,
        'vpc_host': oss_bucket.vpc_host
    }
    
    auth = oss2.Auth(oss_bucket.access_keyid, oss_bucket.access_keysecret)
    bucket = oss2.Bucket(auth, oss_bucket.main_host, oss_bucket.bucket_name)

    file_name = "48M9233T39.p12"

    ret = bucket.put_object_from_file(file_name, f"{settings.BASE_DIR}/apple/p12/{file_name}")

    logger.info(dir(ret))
    logger.info(ret.resp)
    logger.info(ret.status)



    return HttpResponse(json.dumps(ret_data))