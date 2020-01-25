from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from control.middleware.config      import RET_DATA, logger
from apple.middleware.api           import AppStoreConnectApi
from alioss.models                  import AliossBucketTb
from detect.telegram                import SendTelegram
from signature                      import settings
from control.middleware.user        import User, login_required_layui, is_authenticated_to_request
from control.middleware.config      import RET_DATA, MESSAGE_TEST
from control.middleware.common      import IsSomeType
from alioss.middleware.api          import get_bucket, AliOssApi

import json

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def oss_bucket_get(request):
    '''
        获取OSS Bucket信息
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '获取OSS Bucket信息'
    ret_data['data'] = []

    try:
        if request.method == 'GET':

            oss_buckets = AliossBucketTb.objects.filter(status=1).all()

            for oss_bucket in oss_buckets:
                tmp_dict = {}
                tmp_dict['value'] = oss_bucket.id
                tmp_dict['name'] = f"{oss_bucket.bucket_name} - {oss_bucket.main_host}"

                ret_data['data'].append(tmp_dict)

    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = f"{ret_data['msg']} 失败: {str(e)}"

    else:
        ret_data['msg']  = f"{ret_data['msg']} 成功"

    return HttpResponse(json.dumps(ret_data))