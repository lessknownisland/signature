from django.contrib import admin
from detect.models import TelegramChatGroupTb, TelegramUserIdTb, DepartmentUserTb

admin.site.register(TelegramChatGroupTb)
admin.site.register(TelegramUserIdTb)
admin.site.register(DepartmentUserTb)