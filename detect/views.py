#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
# from dwebsocket                     import require_websocket, accept_websocket
from detect.models                  import DepartmentUserTb, TelegramChatGroupTb 
# from monitor.models                 import telegram_ssl_alert_t
# from accounts.limit                 import LimitAccess
from detect.telegram                import SendTelegram
from signature                         import settings
from control.middleware.user        import User, login_required_layui, is_authenticated_to_request
from control.middleware.config      import RET_DATA, MESSAGE_TEST
from control.middleware.common      import IsSomeType

import re
import json
import time
import logging
import requests

logger = logging.getLogger('django')

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
# @login_required
def telegram_group(request):
    '''
        获取telegram 群组，以及 各部门的人员
    '''
    username, role, clientip = User(request).get_default_values()

    # 判断是否登陆
    if not request.user.is_authenticated: return HttpResponse(json.dumps(ret_data))

    # 获取需要@的群组人员
    atUsers = {}
    if request.user.is_superuser:
        atUsersSelects = DepartmentUserTb.objects.filter(status=1).all()
    else:
        atUsersSelects = DepartmentUserTb.objects.filter(status=1).all()

    # 获取需要发送信息的群组
    groups = {}
    if request.user.is_superuser or username == 'test':
        groupSelects = TelegramChatGroupTb.objects.filter(status=1).all()
    elif role == "sa":
        groupSelects = TelegramChatGroupTb.objects.filter(status=1, group__in=['kindergarten', 'zhuanyepan', 'yunwei', 'sport2']).all()
    else:
        groupSelects = TelegramChatGroupTb.objects.filter(status=1, group__in=['kindergarten', 'zhuanyepan', 'sport2']).all()

    for department in atUsersSelects:
        atUsers[department.name] = {
            'id': department.id,
            'department': department.department,
            'users': [ 
                {
                    'name': user.name,
                    'user': user.user,
                    'user_id': user.user_id,
                }
                for user in department.user.filter(status=1).all() ],
            'atUsers': department.AtUsers(),
            'display': department.display().replace(' ', ''),
        }

    for group in groupSelects:
        groups[group.group] = {
            'id': group.id,
            'group': group.group,
            'name':  group.name,
            'group_id': group.group_id,
        }

    return HttpResponse(json.dumps({"code": 0, 
            "msg": "",
            'data': {
                'atUsers':  atUsers,
                'groups':   groups,
            },

        }))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
# @login_required
def telegram_sendgroupmessage(request):
    '''
        往对应群组发送信息
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '未发送任何消息'

    # 初始化 telegram 信息
    message = MESSAGE_TEST.copy()

    # time.sleep(5)

    if request.method == 'POST':
        
        data = request.POST

        # 检查群组是否为空
        if 'group' not in data or not data['group']: 
            ret_data['msg'] = 'TG群组为空，请检查！'
            return HttpResponse(json.dumps(ret_data))
        else:
            message['group'] = data['group']

        # 检查是否有图片
        if 'files[]' in request.FILES and request.FILES.getlist('files[]'):
            # request.FILES 是一个 MultiValueDict，如果传入的参数是一个数组，需要通过 getlist 方法来获取列表数据
            for img in request.FILES.getlist('files[]'):
                logger.info(img)
                # 判断文件是不是 gif
                s = SendTelegram(message)
                if str(img)[-3:] == "gif":
                    r = s.send_document(img)
                else:
                    r = s.send_document(img)
                    # r = s.send_photo(img)

                logger.info(message)

                if r:
                    ret_data['msg']  = '图片发送成功'
                else:
                    ret_data['code'] = 500
                    ret_data['msg']  = '图片发送失败'
                    return HttpResponse(json.dumps(ret_data))

        # 检查信息是否为空
        if 'text' not in data or not data['text']: 
            # ret_data['msg'] = '信息为空，请检查！'
            return HttpResponse(json.dumps(ret_data))

        # 获取需要@的部门或组
        atUsers = []
        if 'atUsers' in data and data['atUsers']: 
            atUsersDepList = [ int(id) for id in data['atUsers'].replace(' ', '').split(',') if IsSomeType(id).is_int() ]
            atUsersSelects = DepartmentUserTb.objects.filter(status=1, id__in=atUsersDepList).all()
            for department in atUsersSelects:
                atUsers.append(department.department + ': ' + ', '.join([ '@'+user.user for user in department.user.filter(status=1).all() ]))

        message['text']  = data['text'] + '\r\n\r\n' + '\r\n'.join(atUsers)
        s = SendTelegram(message)
        if s.send():
            ret_data['msg'] = '发送成功！'
        else: 
            ret_data['msg'] = 'telegram 接口错误，发送失败！'
        return HttpResponse(json.dumps(ret_data))

    else:
        ret_data['msg'] = '403'
        return HttpResponse(json.dumps(ret_data))


