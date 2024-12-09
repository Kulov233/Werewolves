# game/consumers.py
import json

from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.core.cache import caches

# Channel: room:{room_id}
class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_cache = caches['game_cache']
        self.lobby_cache = caches['lobby_cache']
        self.room_timeout = 3600

    # noinspection PyUnresolvedReferences
    async def connect(self):
        try:
            if self.scope["user"].is_anonymous:
                # 如果用户未认证，拒绝连接
                raise DenyConnection("用户未认证。")
            else:
                room_id = self.scope['url_route']['kwargs']['room_id']
                user_id = str(self.scope['user'].id)

                # 获取房间缓存
                room_data = await self.get_room_data_from_cache(room_id)
                if room_data is None:
                    raise DenyConnection("房间不存在。")
                if user_id not in room_data['players']:
                    raise DenyConnection("用户不在房间内。")

                # TODO: 用户连接超时？
                # if room_data['status'] != 'waiting':
                #     raise DenyConnection("游戏已经开始。")

                # 公开频道
                await self.channel_layer.group_add(
                    f"room_{room_id}",
                    self.channel_name
                )

                # 私有频道，用于消息通知
                await self.channel_layer.group_add(
                    f"user_{user_id}",
                    self.channel_name
                )

                room_data['players'][user_id]['online'] = True
                await self.update_room_in_cache(room_id, room_data)

                await self.accept()

                await self.send(text_data=json.dumps({
                    "type": "game_info",
                    "game": room_data
                }))

                await self.broadcast_game_update(room_id, "player_joined", room_data)

                # TODO: 用户全部连接后，开始游戏

        except DenyConnection as e:
            await self.accept()
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))
            await self.close()

    async def disconnect(self, close_code):
        room_id = self.scope['url_route']['kwargs']['room_id']
        user_id = str(self.scope['user'].id)

        await self.channel_layer.group_discard(f"room_{room_id}", self.channel_name)
        await self.channel_layer.group_discard(f"user_{user_id}", self.channel_name)

        # 获取房间缓存
        room_data = await self.get_room_data_from_cache(room_id)
        room_data['players'][user_id]['online'] = False
        await self.update_room_in_cache(room_id, room_data)
        await self.broadcast_game_update(room_id, "player_left", room_data)
        # TODO: 将离开玩家的昵称广播给其他玩家？

    async def receive(self, text_data=None, bytes_data=None):
        """
        接收客户端发送的消息。应该根据游戏目前所处阶段处理信息。
        """
        pass

    # TODO: 根据用户角色发送消息？
    async def game_message(self, event):
        # 从 event 中获取广播数据
        event_type = event.get("event")
        game_data = event.get("game")

        # TODO: 去掉敏感信息
        keys_to_remove = ["roles_for_humans_first", "game_specified_prompt", "victims_info", "poisoned_victims_info"]
        for key in keys_to_remove:
            game_data.pop(key, None)

        keys_to_remove_in_players = ["role", "role_skills"]
        for player in game_data['players']:
            for key in keys_to_remove_in_players:
                game_data['players'][player].pop(key, None)

        for ai_player in game_data['ai_players']:
            for key in keys_to_remove_in_players:
                game_data['ai_players'][ai_player].pop(key, None)

        # 将广播的消息发送到客户端
        await self.send(text_data=json.dumps({
            "type": event_type,
            "game": game_data
        }))

    @classmethod
    async def broadcast_game_update(cls, room_id, event_type, game_data):
        try:
            channel_layer = get_channel_layer()

            await channel_layer.group_send(
                f"room_{room_id}",
                {
                    "type": "game_message",
                    "event": event_type,
                    "game": game_data
                }
            )
        except Exception as e:
            print(f"广播消息时出错：{e}")

    async def role_info(self, event):
        role_info = event.get("role_info")

        """
        {
            "role_info": {
                "role": "Witch",
                "skills": { # 若非女巫则为null
                    "cure_count": 1,
                    "poison_count": 1
                }
            }
        }
        """

        await self.send(text_data=json.dumps({
            "type": "role_info",
            "role_info": role_info
        }))

    async def send_role_to_player(self, user_id, role_info):
        await self.channel_layer.send(
            f"user_{user_id}",
            {
                "type": "role_info",
                "role_info": role_info
            }
        )

    async def not_connected(self, event):
        event_type = event.get("event")
        message = event.get("message")
        offline_players = event.get("offline_players")

        await self.send(text_data=json.dumps({
            "type": event_type,
            "message": message,
            "offline_players": offline_players
        }))

    @classmethod
    async def handle_not_connected(cls, room_id, event_type, message, offline_players):
        try:
            channel_layer = get_channel_layer()

            await channel_layer.group_send(
                f"room_{room_id}",
                {
                    "type": "not_connected",
                    "event": event_type,
                    "message": message,
                    "offline_players": offline_players
                }
            )
        except Exception as e:
            print(f"广播消息时出错：{e}")


    # 从缓存中获取房间信息
    @database_sync_to_async
    def get_room_data_from_cache(self, room_id):
        return self.game_cache.get(f"room:{room_id}")

    # 存储房间信息到缓存
    @database_sync_to_async
    def update_room_in_cache(self, room_id, room_data):
        return self.game_cache.set(f"room:{room_id}", room_data)