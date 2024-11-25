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
            rooms = await self.get_room_list_from_cache()
            await self.send(text_data=json.dumps({
                "type": "room_list",
                "rooms": rooms
            }))

    async def disconnect(self, close_code):
        # 从 "lobby" 组移除用户
        # TODO: 检查用户是否在房间中，如果在房间中则移除用户
        await self.channel_layer.group_discard("lobby", self.channel_name)
        room_id = await self.get_user_room_from_cache(self.scope["user"].id)
        if room_id:
            await self.remove_player_from_room(room_id, self.scope["user"].id)
            await self.clear_user_room_in_cache(self.scope["user"].id)

    async def receive(self, text_data=None, bytes_data=None):
        # 仅允许认证用户发送消息
        # if not self.scope["user"].is_authenticated:
        #     raise DenyConnection("没有权限。")

        data = json.loads(text_data)
        action = data.get("action")

        # 处理客户端发送的消息
        # 下面是客户端可以进行的操作

        # 创建房间
        if action == "create_room":
            await self.create_room(data)
        # 移除房间
        elif action == "remove_room":
            await self.remove_room(data)
        # 加入房间
        elif action == "join_room":
            pass
            # await self.join_room(data)
        # 离开房间
        elif action == "leave_room":
            pass
            # await self.leave_room(data)

    """
    下面是自定义的房间相关方法，考虑将它们模块化？
    """

    async def create_room(self, data):
        """
        创建房间
        :param data: 客户端发送的text_data
        :return: 没有返回值，但是会向客户端发送消息
        """
        # TODO: 检验是否已存在房间
        rooms = await self.get_room_list_from_cache()
        for room in rooms or []:
            if room:
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

        # TODO: 校验房间数据
        if not room_data["title"]:
            room_data["title"] = "未命名的房间"
        if not room_data["description"]:
            room_data["description"] = "房主没有填写简介~"

        await self.update_room_in_cache(room_id, room_data)
        await self.add_room_id_to_cache(room_id)  # 添加房间 ID 到列表
        await self.set_user_room_in_cache(self.scope["user"].id, room_id)
        await self.broadcast_room_update("room_created", room_data)

    async def remove_room(self, data):
        """
        删除房间
        :param data: 客户端发送的text_data
        :return: 不会返回值，但是会向客户端发送消息
        """
        # 验证房主身份
        room_id = data.get("room_id")
        room_data = await self.get_room_data_from_cache(room_id)
        if room_data and room_data["owner"] == self.scope["user"].id:
            await self.remove_room_from_cache(room_id)
            await self.remove_room_id_from_cache(room_id)
            # TODO: 前端在收到 "room_removed" 事件后，如果用户在房间中，应该自动退出房间
            await self.broadcast_room_update("room_removed", {"id": room_id})

            for player in room_data["players"]:
                await self.clear_user_room_in_cache(player)
        else:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "无法删除房间。房间可能不存在，或者您不是房主。"
            }))

    async def remove_player_from_room(self, room_id, user_id):
        room_data = await self.get_room_data_from_cache(room_id)
        if room_data:
            if user_id in room_data["players"]:
                room_data["players"].remove(user_id)
                await self.update_room_in_cache(room_id, room_data)
                await self.broadcast_room_update("player_left", room_data)

    async def lobby_message(self, event):
        # 从 event 中获取广播数据
        event_type = event.get("event")
        room_data = event.get("room")

        # 将广播的消息发送到客户端
        await self.send(text_data=json.dumps({
            "type": event_type,
            "room": room_data
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

    # 添加房间 ID 列表到缓存中
    @database_sync_to_async
    def add_room_id_to_cache(self, room_id):
        room_list = self.lobby_cache.get("room_list", [])
        room_list.append(room_id)
        self.lobby_cache.set("room_list", room_list, timeout=None)

    # 移除房间 ID
    @database_sync_to_async
    def remove_room_id_from_cache(self, room_id):
        room_list = self.lobby_cache.get("room_list", [])
        if room_id in room_list:
            room_list.remove(room_id)
        self.lobby_cache.set("room_list", room_list, timeout=None)

    # 获取房间列表
    @database_sync_to_async
    def get_room_list_from_cache(self):
        room_list = self.lobby_cache.get("room_list", [])
        rooms = [self.lobby_cache.get(f"room:{room_id}") for room_id in room_list]
        return rooms

    # 创建房间并保存到缓存或数据库中（此处使用缓存）
    @database_sync_to_async
    def update_room_in_cache(self, room_id, room_data):
        self.lobby_cache.set(f"room:{room_id}", room_data, timeout=3600) # TODO: 考虑timeout

    # 删除房间
    @database_sync_to_async
    def remove_room_from_cache(self, room_id):
        self.lobby_cache.delete(f"room:{room_id}")

    # 获取房间数据
    @database_sync_to_async
    def get_room_data_from_cache(self, room_id):
        return self.lobby_cache.get(f"room:{room_id}")

    # 记录用户所在房间
    @database_sync_to_async
    def set_user_room_in_cache(self, user_id, room_id):
        self.lobby_cache.set(f"user_room:{user_id}", room_id, timeout=None)

    # 获取用户所在房间
    @database_sync_to_async
    def get_user_room_from_cache(self, user_id):
        # 直接从缓存获取用户所在的房间 ID
        return self.lobby_cache.get(f"user_room:{user_id}")

    # 移除用户所在房间
    @database_sync_to_async
    def clear_user_room_in_cache(self, user_id):
        # 删除用户的房间绑定记录
        self.lobby_cache.delete(f"user_room:{user_id}")

