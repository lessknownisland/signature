# coding: utf8
from django.db import models
from django.contrib.auth.models import User
from control.middleware.config  import choices_s
# from domainns.models            import CfAccountTb, DnspodAccountTb, CdnAccountTb


class WebUriTb(models.Model):
    '''
        接口信息表
    '''
    name      = models.CharField(verbose_name="接口名称", max_length=32, null=False, unique=True)
    uri       = models.CharField(verbose_name="接口路径", default="", max_length=128, blank=True)
    status    = models.IntegerField(verbose_name="是否启用", choices=choices_s, default=1)

    def __str__(self):
        return " | ".join([self.uri, self.name, self.get_status_display()])

class WebUriThirdLevelTb(models.Model):
    '''
        前端WEB 导航栏第三级路由
    '''
    title     = models.CharField(verbose_name="html title", max_length=32, null=False)
    name      = models.CharField(verbose_name="第三级路由名", max_length=32, null=False, unique=True)
    jump      = models.CharField(verbose_name="跳转路由", default="", max_length=128, blank=True)
    icon      = models.CharField(verbose_name="layui图标", default="", max_length=32, blank=True)
    status    = models.IntegerField(verbose_name="是否启用", choices=choices_s, default=1)

    def __str__(self):
        return " | ".join([self.title, self.name, self.jump, self.get_status_display()])

class WebUriSecondLevelTb(models.Model):
    '''
        前端WEB 导航栏第二级路由
    '''
    title     = models.CharField(verbose_name="html title", max_length=32, null=False)
    name      = models.CharField(verbose_name="第二级路由名", max_length=32, null=False, unique=True)
    jump      = models.CharField(verbose_name="跳转路由", default="", max_length=128, blank=True)
    icon      = models.CharField(verbose_name="layui图标", default="", max_length=32, blank=True)
    next_l    = models.ManyToManyField(WebUriThirdLevelTb, verbose_name="下一层路由", blank=True, db_constraint=False)
    status    = models.IntegerField(verbose_name="是否启用", choices=choices_s, default=1)

    def __str__(self):
        return " | ".join([self.title, self.name, self.jump, self.get_status_display()])

class WebUriFirstLevelTb(models.Model):
    '''
        前端WEB 导航栏第一级路由
    '''
    title     = models.CharField(verbose_name="html title", max_length=32, null=False)
    name      = models.CharField(verbose_name="第一级路由名", max_length=32, null=False, unique=True)
    jump      = models.CharField(verbose_name="跳转路由", default="", max_length=128, blank=True)
    icon      = models.CharField(verbose_name="layui图标", default="", max_length=32, blank=True)
    next_l    = models.ManyToManyField(WebUriSecondLevelTb, verbose_name="下一层路由", blank=True, db_constraint=False)
    status    = models.IntegerField(verbose_name="是否启用", choices=choices_s, default=1)

    def __str__(self):
        return " | ".join([self.title, self.name, self.jump, self.get_status_display()])

class UserGroupPermissionsTb(models.Model):
    '''
        每个用户组，拥有的权限
    '''
    name           = models.CharField(verbose_name="组名", max_length=32, null=False)
    # users          = models.ManyToManyField(User, verbose_name="用户", blank=True)
    # 导航路由权限
    weburifirst_l  = models.ManyToManyField(WebUriFirstLevelTb, verbose_name="第一级路由权限", blank=True)
    weburisecond_l = models.ManyToManyField(WebUriSecondLevelTb, verbose_name="第二级路由权限", blank=True)
    weburithird_l  = models.ManyToManyField(WebUriThirdLevelTb, verbose_name="第三级路由权限", blank=True)

    # 接口权限
    weburi_p = models.ManyToManyField(WebUriTb, verbose_name="接口权限", blank=True)

    # # domainns CF和dnspod 账号权限
    # cf_account_p     = models.ManyToManyField(CfAccountTb, verbose_name="CloudFlare账号 权限", blank=True)
    # dnspod_account_p = models.ManyToManyField(DnspodAccountTb, verbose_name="DnsPod账号 权限", blank=True)

    # # domainns cdn 账号权限
    # cdn_account_p    = models.ManyToManyField(CdnAccountTb, verbose_name="cdn账号 权限", blank=True)

    status = models.IntegerField(verbose_name="是否启用", choices=choices_s, default=1)

    def __str__(self):
        return self.name

class UserPermissionsTb(models.Model):
    '''
        每个用户，单独拥有的权限
    '''
    user        = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False)

    # 用户组权限
    usergroup_p = models.ManyToManyField(UserGroupPermissionsTb, verbose_name="路由组权限", blank=True)

    # 导航路由权限
    weburifirst_l  = models.ManyToManyField(WebUriFirstLevelTb, verbose_name="第一级路由权限", blank=True)
    weburisecond_l = models.ManyToManyField(WebUriSecondLevelTb, verbose_name="第二级路由权限", blank=True)
    weburithird_l  = models.ManyToManyField(WebUriThirdLevelTb, verbose_name="第三级路由权限", blank=True)

    # 接口权限
    weburi_p = models.ManyToManyField(WebUriTb, verbose_name="接口权限", blank=True)

    # # domainns CF和dnspod 账号权限
    # cf_account_p     = models.ManyToManyField(CfAccountTb, verbose_name="CloudFlare账号 权限", blank=True)
    # dnspod_account_p = models.ManyToManyField(DnspodAccountTb, verbose_name="DnsPod账号 权限", blank=True)

    # # domainns cdn 账号权限
    # cdn_account_p    = models.ManyToManyField(CdnAccountTb, verbose_name="cdn账号 权限", blank=True)

    def __str__(self):
        return self.user.username