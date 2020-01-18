from django.db import models
from control.middleware.config  import choices_s
from apple.models import AppleAccountTb
from django.utils import timezone

class CustomerTb(models.Model):
    '''
        业主 表
    '''
    name  = models.CharField(verbose_name="业主 名称", max_length=64, null=False, unique=True)
    apple_account = models.ManyToManyField(AppleAccountTb, verbose_name="苹果账号", blank=True)
    create_time = models.DateTimeField("生成的日期", default=timezone.now)
    status = models.IntegerField(verbose_name="是否启用", choices=choices_s, default=0)
    
    def __str__(self):
    	return f"业主: {self.name}"