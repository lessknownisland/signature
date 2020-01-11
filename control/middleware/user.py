#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from signature                         import settings
from control.middleware.config      import RET_DATA
from control.models                 import UserPermissionsTb

# 装饰器
from functools import wraps

import re
import json
import logging
import requests

logger = logging.getLogger('django')

# Create your views here.
class User(object):
    '''
        用于获取用户信息
    '''
    def __init__(self, request):
        self.__request = request

    def get_default_values(self):
        '''
            返回 用户名，用户角色，以及IP
        '''

        username = self.__request.user.username
        try:
            role = self.__request.user.userprofile.role
        except:
            role = 'none'
        if 'HTTP_X_FORWARDED_FOR' in self.__request.META:
            clientip = self.__request.META['HTTP_X_FORWARDED_FOR']
        else:
            clientip = self.__request.META['REMOTE_ADDR']
        logger.info('user: %s, %s is requesting %s.' %(username, clientip, self.__request.get_full_path()))

        return username, role, clientip

    # def Getcsrftoken(self):


    def get_post_data(self):
        '''
            获取post的json 数据
        '''
        try:
            data = json.loads(self.__request.POST)
        except Exception as e:
            logger.error(str(e))
            data = {}

        return data
        
def login_required_layui(func):
    """
        装饰器：用户请求接口前，判断是否登陆
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        # 判断 websocket 请求
        if request.scope and 'user' in request.scope:
            if not request.scope['user'].is_authenticated: 
                request.send(text_data=json.dumps(RET_DATA))
                request.close()
            else:
                return func(request, *args, **kwargs)

        # 判断 http 请求
        if not request.user.is_authenticated: 
            return HttpResponse(json.dumps(RET_DATA))
        else:
            return func(request, *args, **kwargs)
    return wrapper

def return_req(socket, request, ret_data):
    if socket:
        request.send(text_data=json.dumps(ret_data))
        request.close()
    else:
        return HttpResponse(json.dumps(ret_data))

def is_authenticated_to_request(func):
    """
        装饰器：用户请求接口前，判断是否有权限
    """

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 403 # 没有权限
    ret_data['msg']  = '您没有权限请求此接口'

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        socket = False
        # 判断 是否是 websocket 请求
        if request.scope and 'user' in request.scope:
            socket = True
            user = request.scope['user']
            path = request.scope['path']
        else:
            user = request.user
            path = request.path

        if user.is_superuser: # 超级用户拥有所有权限
            return func(request, *args, **kwargs)
        
        try:
            user_web_uri_p = UserPermissionsTb.objects.get(user=user)
            uri_list = [ per.uri.strip() for per in user_web_uri_p.weburi_p.filter(status=1).all() ] # 获取单独用户的权限

            for group in user_web_uri_p.usergroup_p.filter(status=1).all(): # 循环将组权限 分配给用户
                for per in group.weburi_p.filter(status=1).all():
                    if per.uri.strip() not in uri_list: uri_list.append(per.uri.strip())

            if path not in uri_list: # 判断是否有权限
                return return_req(socket, request, ret_data)
            else:
                return func(request, *args, **kwargs)
                
        except Exception as e:
            logger.error(str(e))
            return return_req(socket, request, ret_data)

    return wrapper
