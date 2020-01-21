#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from signature                         import settings

import re
import json
import logging
import requests

logger = logging.getLogger('django')

# models 中启用与禁用参数
choices_s = ((1, '启用'), (0, '禁用'),)

choices_permission = (
        ('read',    u'读权限'), 
        ('change',  u'改权限'),
        ('delete',  u'删权限'),
        ('add',     u'增权限'),
        ('execute', u'执行权限'),
    )

# 初始化返回给前端的数据
# 1001: 登陆失效；0: 获取成功；403: 没有权限；400: 非法请求；500: 内部服务错误
RET_DATA = {'code': 1001, 'msg': '请重新登陆'}

# telegram api
TELEGRAM_API = {
    'api':{
        'AuraAlertBot'  : '471691674:AAFx1MQ3VwXdWUYyh4CaErzwoUNswG9XDsU',
        'sa_monitor_bot': '422793714:AAE8A-sLU1Usms2bJxiKWc3tUWaWYP98bSU',
        'KeepMessageBot': '906727223:AAFytrPY0kuZLpkY5-SQKmF9P790sPEiH8U',
    },

    'url':{
        'AuraAlertBot'  : 'https://api.telegram.org/bot471691674:AAFx1MQ3VwXdWUYyh4CaErzwoUNswG9XDsU/',
        'sa_monitor_bot': 'https://api.telegram.org/bot422793714:AAE8A-sLU1Usms2bJxiKWc3tUWaWYP98bSU/',
        'KeepMessageBot': 'https://api.telegram.org/bot906727223:AAFytrPY0kuZLpkY5-SQKmF9P790sPEiH8U/',
    },
}

# telegram 参数
MESSAGE_TEST = {
    'doc': False,
    'bot': "sa_monitor_bot", #AuraAlertBot: 大魔王
    'text': "",
    'group': "arno_test2",
    'parse_mode': "HTML",
    'doc_file': "message.txt",
}

MESSAGE_ONLINE = {
    'doc': False,
    'bot': "sa_monitor_bot", #AuraAlertBot: 大魔王
    'text': "",
    'group': "kindergarten",
    'parse_mode': "HTML",
    'doc_file': "message.txt",
}

#cloudflare api
CF_URL = 'https://api.cloudflare.com/client/v4/zones'

#dnspod api
DNSPOD_URL = 'https://dnsapi.cn/'

# 苹果开发者接口URL
apple_url = "https://api.appstoreconnect.apple.com/v1"

# 苹果签名 回掉API 地址
udid_url = "https://arnotest.le079.com"

# 创建苹果证书的csr
csr = '''-----BEGIN CERTIFICATE REQUEST-----
MIICizCCAXMCAQAwRjElMCMGCSqGSIb3DQEJARYWbGV5b3VrZWppODg4QGdtYWls
LmNvbTEQMA4GA1UEAwwHbHlzdXBlcjELMAkGA1UEBhMCQ04wggEiMA0GCSqGSIb3
DQEBAQUAA4IBDwAwggEKAoIBAQC5kzD6aUCgYlNirp5/1IJYvqn+e7jcCdCsP65e
5dMc70TLUoA3nCaZlurmKiLw0Sog5LDt1+WPXU2j4T5BnH8bkXgD2DEC98+5dRDt
I4CojVln0XBW2ZCZ7HSkGEXSws7k8qqtbjDI4X44aCi3M3XyqZMkeE8IGJIygMql
7CgBFfQdWf9g9H3Prf+ef0UG20sYpF/wsZVOnwQCztz6/+iksAvQ/ATcnu9F3T7g
6MA398kXFF22TQI7Hdf5qxQSeQi3RU6bIShzsOP1Jt4Cg7mX19O+f6s9awb4/bhA
hgIQQxJMvwaki74BG2sFrSlb/7KEsYbrdXFm6wEuJg06s49lAgMBAAGgADANBgkq
hkiG9w0BAQsFAAOCAQEApWgX/FC+O3pHx9PDn1wOIrnkVsA9NRzqETOmOOoFfoFZ
wwdykLuntzDvfl8fRw7BN/hEzgfVJiiWRZH3+VL22X7EX5FB2GBpdXhY5KsPQ18x
mNvlwxtMoYLZ5hG1nwbS4MwtHzcujX0ldvHwVgMcjUXhDN/VE4PuQBrvRc3i9j8N
n7fQKtYCBfrSpGGj3i3ObNnhboGiG3SLW2W3eKc+maHkSDoNXx3Y8IfklLR1dNDL
T4q/8pTfC5BqGEBCHKaLmVXppEWJEPUJprHo4hMStd7POoQDJJ4CNmUWcz/QmRDP
tlGxNg4+tyGztlJF9hpHRCdbldBMPHU8IOl+ige4Ew==
-----END CERTIFICATE REQUEST-----'''

# mobileconfig 
xml = "".join([
    "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n",
    "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n",
    "<plist version=\"1.0\">\n",
    "    <dict>\n",
    "        <key>PayloadContent</key>\n",
    "        <dict>\n",
    "            <key>URL</key>\n",
    "            <string>{udid_url}/apple/package/install?id={id}</string> <!--接收数据的接口地址-->\n",
    "            <key>DeviceAttributes</key>\n",
    "            <array>\n",
    "                <string>SERIAL</string>\n",
    "                <string>MAC_ADDRESS_EN0</string>\n",
    "                <string>UDID</string>\n",
    "                <string>IMEI</string>\n",
    "                <string>ICCID</string>\n",
    "                <string>VERSION</string>\n",
    "                <string>PRODUCT</string>\n",
    "            </array>\n",
    "        </dict>\n",
    "        <key>PayloadOrganization</key>\n",
    "        <string>Apple Inc.</string>  <!--组织名称-->\n",
    "        <key>PayloadDisplayName</key>\n",
    "        <string>此文件仅用作获取设备UDID</string>  <!--安装时显示的标题-->\n",
    "        <key>PayloadVersion</key>\n",
    "        <integer>1</integer>\n",
    "        <key>PayloadUUID</key>\n",
    "        <string>{random_s}</string>  <!--自己随机填写的唯一字符串-->\n",
    "        <key>PayloadIdentifier</key>\n",
    "        <string>online.iizvv.profile-service</string>\n",
    "        <key>PayloadDescription</key>\n",
    "        <string>该配置文件帮助用户进行APP授权安装！</string>   <!--描述-->\n",
    "        <key>PayloadType</key>\n",
    "        <string>Profile Service</string>\n",
    "    </dict>\n",
    "</plist>",
])

plist = "".join([
    "<?xml version=\"1.0\" encoding=\"UTF-8\"?>  \n",
    "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">  \n",
    "<plist version=\"1.0\">  \n",
    "<dict>  \n",
    "    <key>items</key>  \n",
    "    <array>  \n",
    "        <dict>  \n",
    "            <key>assets</key>  \n",
    "            <array>  \n",
    "                <dict>  \n",
    "                    <key>kind</key>  \n",
    "                    <string>software-package</string>  \n",
    "                    <key>url</key>  \n",
    "                    <string>{remote_signed_ipa}</string>  \n",
    "                </dict>  \n",
    "                <dict>  \n",
    "                    <key>kind</key>  \n",
    "                    <string>display-image</string>  \n",
    "                    <key>url</key>  \n",
    "                    <string>{remote_icon}</string>  \n",
    "                </dict>  \n",
    "            </array>  \n",
    "            <key>metadata</key>  \n",
    "            <dict>  \n",
    "                <key>bundle-identifier</key>  \n",
    "                <string>{bundleId}</string>  \n",
    "                <key>bundle-version</key>  \n",
    "                <string>{version}</string>  \n",
    "                <key>kind</key>  \n",
    "                <string>software</string>  \n",
    "                <key>title</key>  \n",
    "                <string>{name}</string>  \n",
    "            </dict>  \n",
    "        </dict>  \n",
    "    </array>  \n",
    "</dict>  \n",
    "</plist> "
])