from django.db import models
from control.middleware.config  import choices_s

class AliossBucketTb(models.Model):
    '''
        阿里云OSS 账号及存储桶 表
    '''
    bucket_name = models.CharField(verbose_name="存储桶 名称", max_length=64, null=False)
    access_keyid     = models.CharField(verbose_name="账号 keyid", max_length=128, null=False)
    access_keysecret = models.CharField(verbose_name="账号 keysecret", max_length=128, null=False)
    main_host   = models.CharField(verbose_name="Bucket 主域名", max_length=128, null=False)
    vpc_host    = models.CharField(verbose_name="Bucket 内网域名", max_length=128, null=True)
    status = models.IntegerField(verbose_name="是否启用", choices=choices_s, default=1)