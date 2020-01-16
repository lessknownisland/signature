# coding: utf8
from django.db import models
from control.middleware.config  import choices_s
from django.utils import timezone

class AppleAccountTb(models.Model):
    '''
        苹果个人开发者账号 表
    '''
    account  = models.CharField(verbose_name="账号邮箱", max_length=64, null=False, unique=True)
    count    = models.IntegerField(verbose_name="账号签名所剩设备数", null=False)
    p8       = models.TextField(verbose_name="p8 证书", null=False)
    iss      = models.CharField(verbose_name="issue ID", max_length=128, null=False)
    kid      = models.CharField(verbose_name="key ID", max_length=128, null=False)
    cer_id   = models.CharField(verbose_name="证书 ID", max_length=64, null=False, default="null")
    cer_content = models.TextField(verbose_name="证书 详情", null=True)
    bundleid = models.CharField(verbose_name="bundle ID", max_length=64, null=False, default="null")
    p12      = models.CharField(verbose_name="p12 文件名", max_length=128, null=False, default="null")
    # csr      = models.TextField(verbose_name="csr 证书", null=False)
    create_time = models.DateTimeField("生成的日期", default=timezone.now)
    status   = models.IntegerField(verbose_name="是否启用", choices=choices_s, default=0)

    def __str__(self):
        return f"账号: {self.account} ; 所剩次数 {self.count} ; 状态: {self.get_status_display()} "

class AppleDeviceTb(models.Model):
    '''
        苹果设备udid 表
    '''
    udid  = models.CharField(verbose_name="设备 udid", max_length=128, null=False)
    apple_id = models.IntegerField(verbose_name="关联的苹果账号 id", null=False)
    device_id = models.CharField(verbose_name="设备注册 ID", max_length=64, null=False)
    device_name = models.CharField(verbose_name="设备名", max_length=64, null=True)
    device_model = models.CharField(verbose_name="设备型号", max_length=64, null=True)
    create_time = models.DateTimeField("生成的日期", default=timezone.now)
    status   = models.IntegerField(verbose_name="是否启用", choices=choices_s, default=1)
