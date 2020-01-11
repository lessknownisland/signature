"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

from channels.auth    import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from signature.routing   import channel_routing

application = ProtocolTypeRouter({
    # (http->django views is added by default) 
    # 普通的HTTP请求不需要我们手动在这里添加，框架会自动加载过来
    'websocket': AuthMiddlewareStack(
        URLRouter(
            channel_routing
        )
    ),
})