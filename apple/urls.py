#-_- coding: utf-8 -_-
from django.conf.urls          import url, include
from django.views.generic.base import RedirectView
from . import views
from apple.tests import *
from apple.account import create_crt

urlpatterns = [
    # APPLE
    url('^test$', test, name='Test'),
    url('^createcrt$', create_crt, name='CreateCrt'),

    # 用户权限及信息
    # url('menu$', views.menu, name='Menu'),
    # url('user/session$', views.userSession, name='userSession'),
]
