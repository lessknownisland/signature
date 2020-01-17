#-_- coding: utf-8 -_-
from django.conf.urls          import url, include
from django.views.generic.base import RedirectView
from . import views
from apple.tests import *
from apple.account import cer_create, account_get, account_edit

urlpatterns = [
    # APPLE
    url('^cer/create$', cer_create, name='CerCreate'), # 创建苹果证书
    url('^account/get$', account_get, name='AccountGet'), # 获取苹果个人账号
    url('^account/edit$', account_edit, name='AccountEdit'), # 修改苹果个人账号

    # 测试
    url('^test$', test, name='Test'),
    url('^testalioss$', test_alioss, name='TestAlioss'),
    
    # 用户权限及信息
    # url('menu$', views.menu, name='Menu'),
    # url('user/session$', views.userSession, name='userSession'),
]
