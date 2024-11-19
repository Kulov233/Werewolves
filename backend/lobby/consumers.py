# lobby/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.exceptions import DenyConnection
from channels.db import database_sync_to_async
from django.core.cache import caches
import uuid

class LobbyConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lobby_cache = caches["lobby_cache"]

    # 连接时触发
    async def connect(self):
        if self.scope["user"].is_anonymous:
            # 如果用户未认证，拒绝连接
            await self.close()
        else:
            # 接受连接并将用户加入组
            await self.channel_layer.group_add("lobby", self.channel_name)
            await self.accept()
            # 发送房间列表
            rooms = await self.get_room_list()
            await self.send(text_data=json.dumps({
                "type": "room_list",
                "rooms": rooms
            }))

    async def disconnect(self, close_code):
        # 从 "lobby" 组移除用户
        # TODO: 检查用户是否在房间中，如果在房间中则移除用户
        await self.channel_layer.group_discard("lobby", self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # 仅允许认证用户发送消息
        if not self.scope["user"].is_authenticated:
            raise DenyConnection("没有权限。")

        data = json.loads(text_data)
        action = data.get("action")

        # 处理客户端发送的消息
        # 下面是客户端可以进行的操作

        # 创建房间
        if action == "create_room":
            # TODO: 检验是否已存在房间
            rooms = await self.get_room_list()
            for room in rooms:
                if room["owner"] == self.scope["user"].id:
                    await self.send(text_data=json.dumps({
                        "type": "error",
                        "message": "您已经创建了一个房间。"
                    }))
                    return

            room_id = str(uuid.uuid4())
            room_data = {
                # TODO: 确定房间数据的格式
                "id": room_id,
                "title": data.get("title", "未命名的房间"),
                "description": data.get("description", "房主没有填写简介~"),
                "owner": self.scope["user"].id,
                "players": [self.scope["user"].id],
                "game_mode": data.get("game_mode", "default")
            }
            await self.create_room(room_id, room_data)
            await self.add_room_id(room_id)  # 添加房间 ID 到列表
            await self.broadcast_room_update("room_created", room_data)

        # 移除房间
        elif action == "remove_room":
            # 验证房主身份
            room_id = data.get("room_id")
            room_data = self.lobby_cache.get(f"room:{room_id}")
            if room_data and room_data["owner"] == self.scope["user"].id:
                # 移除房间内的所有玩家
                for player_id in room_data["players"]:
                    # TODO: 在前端处理玩家离开房间的情况
                    await self.channel_layer.group_discard(f"room_{room_id}", f"player_{player_id}")
                await self.lobby_cache.delete(f"room:{room_id}")
                await self.remove_room_id(room_id)
                await self.broadcast_room_update("room_removed", {"id": room_id})
            else:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "您不是房主，无法删除房间。"
                }))

    async def broadcast_room_update(self, event_type, room_data):
        # 将房间更新广播给 "lobby" 组的所有连接
        await self.channel_layer.group_send(
            "lobby",
            {
                "type": "lobby_message",
                "event": event_type,
                "room": room_data
            }
        )

    async def lobby_message(self, event):
        # 将广播的消息发送到客户端
        await self.send(text_data=json.dumps({
            "type": event["event"],
            "room": event["room"]
        }))

    @database_sync_to_async
    def create_room(self, room_id, room_data):
        # 创建房间并保存到缓存或数据库中（此处使用缓存）
        self.lobby_cache.set(f"room:{room_id}", room_data, timeout=3600) # TODO: 考虑timeout

    # 添加房间 ID 列表到缓存中
    @database_sync_to_async
    def add_room_id(self, room_id):
        room_list = self.lobby_cache.get("room_list", [])
        room_list.append(room_id)
        self.lobby_cache.set("room_list", room_list, timeout=3600)

    # 移除房间 ID
    @database_sync_to_async
    def remove_room_id(self, room_id):
        room_list = self.lobby_cache.get("room_list", [])
        if room_id in room_list:
            room_list.remove(room_id)
        self.lobby_cache.set("room_list", room_list, timeout=3600)

    # 获取房间列表
    @database_sync_to_async
    def get_room_list(self):
        room_list = self.lobby_cache.get("room_list", [])
        rooms = [self.lobby_cache.get(f"room:{room_id}") for room_id in room_list]
        return rooms

