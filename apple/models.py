# coding: utf8
from django.db    import models
from django.utils import timezone
from control.middleware.config import choices_s

class AppleAccountTb(models.Model):
    '''
        苹果个人开发者账号 表
    '''
    # customer = models.ManyToManyField(CustomerTb, blank=True)
    account  = models.CharField(verbose_name="账号邮箱", max_length=64, null=False, unique=True)
    count    = models.IntegerField(verbose_name="账号签名所剩设备数", default=0)
    p8       = models.TextField(verbose_name="p8 证书", null=False)
    iss      = models.CharField(verbose_name="issue ID", max_length=128, null=False)
    kid      = models.CharField(verbose_name="key ID", max_length=128, null=False)
    cer_id   = models.CharField(verbose_name="证书 ID", max_length=64, blank=True, null=True)
    cer_content = models.TextField(verbose_name="证书 详情", blank=True, null=True)
    bundleId = models.CharField(verbose_name="bundleId", max_length=64, null=False, default="com.app.*")
    bundleIds = models.CharField(verbose_name="苹果 bundleIds", max_length=64, blank=True, null=True)
    p12      = models.CharField(verbose_name="p12 地址", max_length=128, blank=True, null=True)
    # csr      = models.TextField(verbose_name="csr 证书", null=False)
    create_time = models.DateTimeField("生成的日期", default=timezone.now)
    status   = models.IntegerField(verbose_name="是否启用", choices=choices_s, default=0)

    def __str__(self):
    	return f"账号: {self.account} 剩余次数: {self.count} 状态: {self.get_status_display()}"

class AppleDeviceTb(models.Model):
    '''
        苹果设备udid 表
    '''
    udid  = models.CharField(verbose_name="设备 udid", max_length=128, null=False)
    apple_id  = models.IntegerField(verbose_name="关联的苹果账号 id", null=False)
    device_id = models.CharField(verbose_name="设备注册 ID", max_length=64, null=False)
    device_name  = models.CharField(verbose_name="设备名", max_length=64, blank=True, null=True)
    device_model = models.CharField(verbose_name="设备型号", max_length=64, blank=True, null=True)
    create_time  = models.DateTimeField("生成的日期", default=timezone.now)
    status = models.IntegerField(verbose_name="是否启用", choices=choices_s, default=1)

class PackageTb(models.Model):
    '''
        苹果Ipa信息 表
    '''
    name = models.CharField(verbose_name="IOS 包名", max_length=12, null=False)
    icon = models.CharField(verbose_name="Icon 地址", max_length=128, blank=True, null=True)
    version = models.CharField(verbose_name="IOS 包版本号", max_length=8, null=False)
    build_version = models.CharField(verbose_name="创建 版本号", max_length=8, null=False)
    mini_version  = models.CharField(verbose_name="最低适配IOS版本号", max_length=8, null=False)
    bundle_identifier = models.CharField(verbose_name="BundleId", max_length=32, null=False)
    ipa = models.CharField(verbose_name="IOS 包地址", max_length=128, null=False)
    mobileconfig = models.CharField(verbose_name="mobileconfig 地址", max_length=128, null=False)
    count = models.IntegerField(verbose_name="当前下载量", null=False, default=0)
    customer = models.IntegerField(verbose_name="业主", null=False, default=1)
    create_time  = models.DateTimeField("生成的日期", default=timezone.now)
    status = models.IntegerField(verbose_name="是否启用", choices=choices_s, default=1)

    def __str__(self):
    	return f"包名: {self.name} 版本: {self.version} bundleId: {self.bundle_identifier} 状态: {self.get_status_display()}"

class PackageIstalledTb(models.Model):
    '''
        苹果Ipa安装历史记录表
    '''
    package_id = models.IntegerField(verbose_name="包ID", null=False)
    package_name = models.CharField(verbose_name="IOS包名", max_length=12, null=False)
    package_version = models.CharField(verbose_name="IOS 包版本号", max_length=8, null=False)
    device_udid = models.CharField(verbose_name="设备注册ID", max_length=64, null=False)
    device_name  = models.CharField(verbose_name="设备名", max_length=64, blank=True, null=True)
    device_model = models.CharField(verbose_name="设备型号", max_length=64, blank=True, null=True)
    customer_id = models.IntegerField(verbose_name="业主", null=False, default=1)
    customer_name = models.CharField(verbose_name="业主名称", max_length=12, null=False)
    create_time  = models.DateTimeField("生成的日期", default=timezone.now)
    is_first_install = models.IntegerField(verbose_name="是否是第一次注册安装", choices=choices_s, default=1)
    install_status = models.IntegerField(verbose_name="是否安装成功", choices=choices_s, default=1)

class CsrTb(models.Model):
    '''
        生成证书用到的 csr 证书，每台mac 电脑可独立生成不同的csr，用于解密生成的cer 来导出成 p12 证书
    '''
    name = models.CharField(verbose_name="csr 名称", max_length=12, null=False, unique=True)
    csr_content = models.TextField(verbose_name="证书 详情", null=False)
    status = models.IntegerField(verbose_name="是否启用", choices=choices_s, default=1)

    def __str__(self):
    	return f"csr 名称: {self.name} 状态: {self.get_status_display()}"
