# game/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import caches

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        pass

    async def disconnect(self, close_code):
        pass