from django.contrib import admin
from apple.models   import AppleAccountTb, AppleDeviceTb, PackageTb, CsrTb, PackageInstalledTb

# AppleAccountTb admin model
class AppleAccountTbAdmin(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'account', 'count', 'create_time', 'status')

    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id', 'account', 'count', 'status')

admin.site.register(AppleAccountTb, AppleAccountTbAdmin)

# AppleDeviceTb admin model
class AppleDeviceTbAdmin(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'udid', 'apple_id', 'device_id', 'status')

    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id', 'udid', 'apple_id', 'device_id', 'status')

admin.site.register(AppleDeviceTb, AppleDeviceTbAdmin)

# PackageTb admin model
class PackageTbAdmin(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'name', 'version', 'mini_version', 'bundle_identifier', 'ipa', 'mobileconfig', 'count', 'create_time', 'status')

    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id', 'name', 'version', 'mini_version', 'bundle_identifier', 'ipa', 'mobileconfig', 'count', 'create_time', 'status')

admin.site.register(PackageTb, PackageTbAdmin)

# PackageInstalledTb admin model
class PackageInstalledTbAdmin(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'package_id', 'package_name', 'package_version', 'device_udid', 'device_name', 'device_model', 'customer_id', 'customer_name', 'is_first_install', 'install_status', 'create_time')

    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id', 'package_id', 'package_name', 'package_version', 'device_udid', 'device_name', 'device_model', 'customer_id', 'customer_name', 'is_first_install', 'install_status', 'create_time')

admin.site.register(PackageInstalledTb, PackageInstalledTbAdmin)

# CsrTb admin model
class CsrTbAdmin(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'name', 'status')

    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id', 'name', 'status')

admin.site.register(CsrTb, CsrTbAdmin)
