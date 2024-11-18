# lobby/routing.py
from django.urls import path
from .consumers import LobbyConsumer

websocket_urlpatterns = [
    path("ws/lobby/", LobbyConsumer.as_asgi()),  # 大厅 WebSocket 路由
]
