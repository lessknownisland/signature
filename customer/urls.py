#-_- coding: utf-8 -_-
from django.conf.urls          import url, include
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    # customer
    url('^account/get$', views.account_get, name='CustomerAccountGet'), # 获取业主账号
]
