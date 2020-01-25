#-_- coding: utf-8 -_-
from django.conf.urls          import url, include
from django.views.generic.base import RedirectView
from . import views
from alioss.views import oss_bucket_get

urlpatterns = [
    # 主页入口
    url('^$', views.index, name='Index'),

    # 用户登入登出
    url('login$', views.Login, name='Login'),
    url('logout$', views.Logout, name='Logout'),

    # 获取 oss 接口信息
    url('oss/bucket/get$', oss_bucket_get, name='OssBucketGet'),


    # 用户权限及信息
    url('menu$', views.menu, name='Menu'),
    url('user/session$', views.userSession, name='userSession'),
]
