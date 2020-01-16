from django.test import TestCase
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from control.middleware.user        import User, login_required_layui
from control.middleware.config      import RET_DATA
from apple.middleware.common import AppStoreConnectApi
from apple.middleware.config import csr
from apple.models import AppleAccountTb

import json

@csrf_exempt
@login_required_layui
def test(request):
    '''
        测试
    '''
    username, role, clientip = User(request).get_default_values()

    ret_data = RET_DATA.copy()

    # apple_account = AppleAccountTb.objects.get(id=2)

    # asca = AppStoreConnectApi(apple_account.account, apple_account.p8, apple_account.iss, apple_account.kid)

    # ret_data = asca.create_crt(csr)
    return HttpResponse(json.dumps(ret_data))
