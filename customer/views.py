from django.shortcuts import render
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt
from control.middleware.config      import RET_DATA, logger
from control.middleware.user        import User, login_required_layui, is_authenticated_to_request
from customer.models import CustomerTb

import json

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def account_get(request):
    '''
        获取业主账号
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '获取业主账号'
    ret_data['data'] = []

    try:
        if request.method == 'GET':
            accounts = CustomerTb.objects.filter(status=1).all()

            for account in accounts:
                tmp_dict = {}
                tmp_dict['value'] = account.id
                tmp_dict['name'] = account.name

                ret_data['data'].append(tmp_dict)

    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = f"{ret_data['msg']} 失败: {str(e)}"
        logger.error(ret_data['msg'])

    ret_data['msg']  = f"{ret_data['msg']} 成功"
    logger.info(ret_data['msg'])

    return HttpResponse(json.dumps(ret_data))