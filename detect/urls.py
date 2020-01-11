#-_- coding: utf-8 -_-
from django.conf.urls          import url, include
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    # 发送telegram信息
    url('telegram$', views.telegram_group, name='TelegramGroup'),
    url('telegram/sendgroupmessage$', views.telegram_sendgroupmessage, name='Telegramsendgroupmessage'),
    # url('telegram/uploadimgs$', views.TelegramUploadimgs, name='TelegramUploadimgs'),

]
