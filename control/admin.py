from django.contrib import admin
from control.models import WebUriTb, WebUriFirstLevelTb, WebUriSecondLevelTb, WebUriThirdLevelTb
from control.models import UserPermissionsTb, UserGroupPermissionsTb

admin.site.register(WebUriTb)
admin.site.register(WebUriFirstLevelTb)
admin.site.register(WebUriSecondLevelTb)
admin.site.register(WebUriThirdLevelTb)
admin.site.register(UserPermissionsTb)
admin.site.register(UserGroupPermissionsTb)
