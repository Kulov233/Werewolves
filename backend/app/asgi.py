"""
ASGI config for app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from lobby.routing import websocket_urlpatterns as lobby_websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

from django.core.asgi import get_asgi_application
from middlewares.middlewares import JWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            lobby_websocket_urlpatterns
        )
    ),
})
