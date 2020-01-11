#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from django.contrib.auth.forms      import AuthenticationForm
from signature                         import settings
from control.middleware.user        import User, login_required_layui
from control.middleware.config      import RET_DATA
from control.models					import UserPermissionsTb, WebUriFirstLevelTb, WebUriSecondLevelTb, WebUriThirdLevelTb

import re
import json
import time
import logging
import requests

# 获取django 自带的登入登出机制
from django.contrib.auth import (
                                REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
                                logout as auth_logout, update_session_auth_hash,
                            )

logger = logging.getLogger('django')

# Create your views here.
@csrf_exempt
# @login_required_layui
def index(request):
    '''
        主页入口
    '''
    username, role, clientip = User(request).get_default_values()

    return render(request, 'home.html',)

@csrf_exempt
def Login(request, authentication_form=AuthenticationForm):
    '''
        控制登陆
    '''
    username, role, clientip = User(request).get_default_values()

    data = request.POST

    # # 判断是否登入
    # if request.user.is_authenticated:
    #     return HttpResponseRedirect('/')

    # 校验登陆
    form = authentication_form(request, data=data)
    if form.is_valid():
        auth_login(request, form.get_user())

        # 返回新的token
        logger.info('%s login' %username)
        return HttpResponse(json.dumps({
                  "code": 0,
                  "msg": "登陆成功了",
                  "data": {
                    "csrftoken": "c262e61cd13ad99fc650e6908c7e5e65b63d2f32185ecfed6b801ee3fbdd5c0a"
                  }
                })
            )
    else:
        return HttpResponse(json.dumps({
                  "code": 1001,
                  "msg": "账号密码错误",
                })
            )

@csrf_exempt
def Logout(request):
    '''
        控制登出
    '''
    username, role, clientip = User(request).get_default_values()

    data = request.POST

    # 登出
    logger.info('%s logout' %username)
    ret_data = {"code": 1001, "msg": "您已登出"}
    auth_logout(request)
    return HttpResponse(json.dumps(ret_data))

@csrf_exempt
# @login_required
def userSession(request):
    '''
        返回用户信息
    '''
    username, role, clientip = User(request).get_default_values()

    data = request.POST

    # 判断是否登入
    if not request.user.is_authenticated:
        ret_data = {"code": 1001, "msg": "请重新登陆"}
        return HttpResponse(json.dumps(ret_data))

    # 返回新的token
    logger.info('%s login' %username)
    return HttpResponse(json.dumps({
              "code": 0,
              "msg": "获取用户信息成功",
              "data": {
                'username': username,
                'is_superuser': request.user.is_superuser,
                'is_staff': request.user.is_staff
              }
            })
        )

@csrf_exempt
@login_required_layui
def menu(request):
    '''
        获取 前端导航栏
    '''
    username, role, clientip = User(request).get_default_values()
    
    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '获取导航栏路由'
    ret_data['data'] = []

    # 获取用户对路由的权限
    try:
        if request.user.is_superuser: # 超级用户拥有所有权限
            first_level_list  = WebUriFirstLevelTb.objects.filter(status=1).all()
            second_level_list = WebUriSecondLevelTb.objects.filter(status=1).all()
            third_level_list  = WebUriThirdLevelTb.objects.filter(status=1).all()
        else:
            user_web_uri_p = UserPermissionsTb.objects.get(user=request.user)
            first_level_list  = [ per for per in user_web_uri_p.weburifirst_l.filter(status=1).all()]
            second_level_list = [ per for per in user_web_uri_p.weburisecond_l.filter(status=1).all()]
            third_level_list  = [ per for per in user_web_uri_p.weburithird_l.filter(status=1).all()]
            for group in user_web_uri_p.usergroup_p.filter(status=1).all(): # 循环将组权限 分配给用户
                for first_level in group.weburifirst_l.filter(status=1).all():
                    if first_level not in first_level_list:
                        first_level_list.append(first_level)
                for second_level in group.weburisecond_l.filter(status=1).all():
                    if second_level not in second_level_list:
                        second_level_list.append(second_level)
                for third_level in group.weburithird_l.filter(status=1).all():
                    if third_level not in third_level_list:
                        third_level_list.append(third_level)

    except Exception as e:
        logger.error(str(e))
        return HttpResponse(json.dumps(ret_data))
    
    # 将权限 格式化成合法的数据
    for first_level in first_level_list:
        first_level_dict = { # 获取第一层导航路由
            'title': first_level.title,
            'name':  first_level.name,
            'jump':  first_level.jump,
            'icon':  first_level.icon,
            'list':  []
        }
        for second_level in first_level.next_l.filter(status=1).all():
            if second_level in second_level_list:
                second_level_dict = { # 获取第二层导航路由
                    'title': second_level.title,
                    'name':  second_level.name,
                    'jump':  second_level.jump,
                    'icon':  second_level.icon,
                    'list':  []
                }
                for third_level in second_level.next_l.filter(status=1).all():
                    if third_level in third_level_list:
                        third_level_dict = { # 获取第三层导航路由
                            'title': third_level.title,
                            'name':  third_level.name,
                            'jump':  third_level.jump,
                            'icon':  third_level.icon,
                            'list':  []
                        }
                        second_level_dict['list'].append(third_level_dict)
                first_level_dict['list'].append(second_level_dict)
        ret_data['data'].append(first_level_dict)

    return HttpResponse(json.dumps(ret_data))