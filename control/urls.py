#-_- coding: utf-8 -_-
from django.conf.urls          import url, include
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    # 主页入口
    url('^$', views.index, name='Index'),

    # 用户登入登出
    url('login$', views.Login, name='Login'),
    url('logout$', views.Logout, name='Logout'),

    # 用户权限及信息
    url('menu$', views.menu, name='Menu'),
    url('user/session$', views.userSession, name='userSession'),
]
