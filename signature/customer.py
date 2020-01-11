# coding: utf8
from channels.generic.websocket import WebsocketConsumer, AsyncJsonWebsocketConsumer, AsyncWebsocketConsumer
from control.middleware.user    import User

import json, logging

logger = logging.getLogger('django')

class DefConsumer(WebsocketConsumer):
    def connection_groups(self, **kwargs):
        """
        Called to return the list of groups to automatically add/remove
        this connection to/from.
        """
        return ["test"]

    def connect(self):
        """
            在连接阶段accept: self.accept()，close: self.close()
        """
        self._ret_data = {
            'code': 0, # 0 代表正常返回，1001 代表登陆失效
            'step_all': 0,
            'step_finished': 0,
            'msg': ""
        }

        # 判断账号是否登陆
        # if not self.scope['user'].is_authenticated: 
        #     self._ret_data['code'] = 1001
        #     # self.send(text_data=json.dumps(self._ret_data))
        #     self.close(code=self._ret_data['code'])
        #     return False

        # 接受全部
        self.accept()

        # 获取账号基本信息
        self.username = self.scope['user'].username
        try:
            self.role = self.scope['user'].userprofile.role
        except:
            self.role = 'none'
        self.clientip = self.scope['client'][0]
        logger.info('user: %s | [websocket]%s is requesting. %s' %(self.username, self.clientip, self.scope['path']))

    def args(self):
        return self

    def receive(self, text=None, bytes=None, **kwargs):
        """
        Called when a message is received with either text or bytes
        filled out.
        """
        pass
        
    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        pass