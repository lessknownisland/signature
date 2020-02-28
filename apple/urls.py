#-_- coding: utf-8 -_-
from django.conf.urls          import url, include
from django.views.generic.base import RedirectView
from . import views
from apple.tests import *
from apple.account import cer_create, account_get, account_delete, account_edit, p12_upload, csr_get, account_test_connect, account_deploycustomer
from apple.package import package_upload, mobileconfig_create, package_install, package_install_andios, packages_get, package_edit

urlpatterns = [
    # APPLE
    url('^cer/create$', cer_create, name='CerCreate'), # 创建苹果证书
    url('^p12/upload$', p12_upload, name='P12Upload'), # 上传p12 文件
    url('^account/get$', account_get, name='AccountGet'), # 获取苹果个人账号
    url('^account/testconnect$', account_test_connect, name='AccountTestConnect'), # 账号测试连接
    url('^account/delete$', account_delete, name='AccountDelete'), # 删除苹果个人账号
    url('^csr/get$', csr_get, name='CsrGet'), # 获取csr证书
    url('^account/edit$', account_edit, name='AccountEdit'), # 修改苹果个人账号
    url('^account/deploycustomer$', account_deploycustomer, name='AccountDeploycustomer'), # 分配业主

    # package
    url('^package/upload$', package_upload, name='PackageUpload'), # 上传 IPA 文件
    url('^package/mobileconfig/create$', mobileconfig_create, name='MobileconfigCreate'), # 手动请求，生成mobileconfig
    url('^package/install$', package_install, name='PackageInstall'), # 获取 签名过后的IPA 文件，用于用户下载安装
    url('^package/install/andios$', package_install_andios, name='PackageInstallAndIos'), # 区分安卓和IOS，用于用户下载安装
    url('^package/edit$', package_edit, name='PackageEdit'), # 修改 package
    url('^packages/get$', packages_get, name='PackagesGet'), # 获取 packages

    # 测试
    url('^test$', test, name='Test'),
    url('^testalioss$', test_alioss, name='TestAlioss'),
    
    # 用户权限及信息
    # url('menu$', views.menu, name='Menu'),
    # url('user/session$', views.userSession, name='userSession'),
]
