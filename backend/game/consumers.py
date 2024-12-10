# game/consumers.py
import json
from typing import Optional

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

                # 用户私聊频道，用于发送角色
                await self.channel_layer.group_add(
                    f"room_{room_id}_user_{user_id}",
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

    # noinspection PyUnresolvedReferences
    async def disconnect(self, close_code):
        room_id = self.scope['url_route']['kwargs']['room_id']
        user_id = str(self.scope['user'].id)

        await self.channel_layer.group_discard(f"room_{room_id}", self.channel_name)
        await self.channel_layer.group_discard(f"room_{room_id}_user_{user_id}", self.channel_name)

        # 获取房间缓存
        room_data = await self.get_room_data_from_cache(room_id)
        if room_data is None:
            return
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
            "type": "role_info",
            "role_info": {
                "role": "Witch",
                "role_skills": { // 若非女巫则为null
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

    async def join_werewolf_group(self, event):
        room_id = event.get('room_id')

        await self.channel_layer.group_add(
            f"room_{room_id}_werewolves",
            self.channel_name
        )

    @classmethod
    async def send_role_to_player(cls, room_id, user_id, role_info):
        try:
            channel_layer = get_channel_layer()

            await channel_layer.group_send(
                f"room_{room_id}_user_{user_id}",
                {
                    "type": "role_info",
                    "role_info": role_info
                }
            )

            if role_info['role'] == "Werewolf":
                # 将狼人加入狼人私有频道
                await channel_layer.group_send(
                    f"room_{room_id}",
                    {
                        "type": "join_werewolf_group",
                        "room_id": room_id
                    }
                )
        except Exception as e:
            print(f"发送角色信息时出错：{e}")

    async def wolf_sync(self, event):
        targets = event.get("targets")

        """
        {
          "type": "wolf_sync",
          "targets": {
            "1": "4",
            "3": null,  // null为弃权或者未投票
            "7": "4",
            "8": "1",
          }
        }
        """

        await self.send(text_data=json.dumps({
            "type": "wolf_sync",
            "targets": targets
        }))

    @classmethod
    async def sync_werewolf_target(cls, room_id: str, targets: dict[str, Optional[str]]):
        try:
            channel_layer = get_channel_layer()

            await channel_layer.group_send(
                f"room_{room_id}_werewolves",
                {
                    "type": "wolf_sync",
                    "targets": targets
                }
            )
        except Exception as e:
            print(f"同步狼人选择时出错：{e}")

    async def kill_result(self, event):
        result = event.get("result")

        """
        {
          "type": "kill_result",
          "result": "7",  // 玩家序号
        }
        {
          "type": "kill_result",
          "result": null,  // 没有投出刀人结果平票
        }
        """

        await self.send(text_data=json.dumps({
            "type": "kill_result",
            "result": result
        }))

    @classmethod
    async def send_kill_result(cls, room_id: str, result: Optional[str]):
        try:
            channel_layer = get_channel_layer()

            await channel_layer.group_send(
                f"room_{room_id}_werewolves",
                {
                    "type": "kill_result",
                    "result": result
                }
            )
        except Exception as e:
            print(f"发送狼人猎杀结果时出错：{e}")

    async def check_result(self, event):
        target = event.get("target")
        role = event.get("role")

        """
        {
          "type": "check_result",
          "target": "7",
          "role": "Witch",
        }
        """

        await self.send(text_data=json.dumps({
            "type": "check_result",
            "target": target,
            "role": role
        }))

    @classmethod
    async def send_check_result(cls, room_id: str, user_id: str, target: str, role: str):
        try:
            channel_layer = get_channel_layer()

            await channel_layer.group_send(
                f"room_{room_id}_user_{user_id}",
                {
                    "type": "check_result",
                    "target": target,
                    "role": role
                }
            )
        except Exception as e:
            print(f"发送预言家查验结果时出错：{e}")

    async def witch_info(self, event):
        cure_count = event.get("cure_count")
        poison_count = event.get("poison_count")
        cure_target = event.get("cure_target")

        """
        {
          "type": "witch_info",
          "cure_count": 1,
          "poison_count": 0,
          "cure_target": ["6", "8"], // 今晚死掉的玩家序号列表，玩家序号为字符串
        }
        """

        await self.send(text_data=json.dumps({
            "type": "witch_info",
            "cure_count": cure_count,
            "poison_count": poison_count,
            "cure_target": cure_target
        }))

    @classmethod
    async def send_witch_info(cls, room_id: str, user_id: str, cure_count: int, poison_count: int, cure_target: list[str]):
        try:
            channel_layer = get_channel_layer()

            await channel_layer.group_send(
                f"room_{room_id}_user_{user_id}",
                {
                    "type": "witch_info",
                    "cure_count": cure_count,
                    "poison_count": poison_count,
                    "cure_target": cure_target
                }
            )
        except Exception as e:
            print(f"发送女巫信息时出错：{e}")

    async def witch_action_result(self, event):
        cure = event.get("cure")
        poison = event.get("poison")

        """
        {
          "type": "witch_action_result",
          "cure": "6",
          "poison": null,  // 失败了或者操作非法
        }
        """

        await self.send(text_data=json.dumps({
            "type": "witch_action_result",
            "cure": cure,
            "poison": poison,
        }))

    @classmethod
    async def send_witch_action_result(cls, room_id: str, user_id: str, cure: Optional[str], poison: Optional[str]):
        try:
            channel_layer = get_channel_layer()

            await channel_layer.group_send(
                f"room_{room_id}_user_{user_id}",
                {
                    "type": "witch_action_result",
                    "cure": cure,
                    "poison": poison
                }
            )
        except Exception as e:
            print(f"发送女巫操作回复时出错：{e}")

    async def night_death_info(self, event):
        victims = event.get("victims")

        """
        {
          "type": "night_death_info",
          "victims": ["2", "4", "6"],
        }
        """

        await self.send(text_data=json.dumps({
            "type": "night_death_info",
            "victims": victims
        }))

    @classmethod
    async def broadcast_night_death_info(cls, room_id: str, victims: list[str]):
        try:
            channel_layer = get_channel_layer()

            await channel_layer.group_send(
                f"room_{room_id}",
                {
                    "type": "night_death_info",
                    "victims": victims
                }
            )
        except Exception as e:
            print(f"广播夜晚死亡玩家时出错：{e}")

    async def talk_update(self, event):
        source = event.get("source")
        message = event.get("message")

        """
        {
          "type": "talk_update",
          "source": "5",
          "message": "我会喷火，你会吗？"
        }
        """

        await self.send(text_data=json.dumps({
            "type": "talk_update",
            "source": source,
            "message": message
        }))

    @classmethod
    async def broadcast_talk_message(cls, room_id: str, source: str, message: str):
        try:
            channel_layer = get_channel_layer()

            await channel_layer.group_send(
                f"room_{room_id}",
                {
                    "type": "talk_update",
                    "source": source,
                    "message": message
                }
            )
        except Exception as e:
            print(f"广播玩家发言时出错：{e}")

    async def talk_start(self, event):
        player = event.get("player")

        """
        {
          "type": "talk_start",
          "player": "6",  // 发给当前说话的玩家
        }
        """

        await self.send(text_data=json.dumps({
            "type": "talk_start",
            "player": player
        }))

    @classmethod
    async def broadcast_talk_start(cls, room_id: str, player: str):
        try:
            channel_layer = get_channel_layer()

            await channel_layer.group_send(
                f"room_{room_id}",
                {
                    "type": "talk_start",
                    "player": player
                }
            )
        except Exception as e:
            print(f"广播接下来发言的玩家时出错：{e}")

    async def talk_end(self, event):
        player = event.get("player")

        """
        {
          "type": "talk_end",
          "player": 6,
        }
        """

        await self.send(text_data=json.dumps({
            "type": "talk_start",
            "player": player
        }))

    @classmethod
    async def broadcast_talk_end(cls, room_id: str, player: str):
        try:
            channel_layer = get_channel_layer()

            await channel_layer.group_send(
                f"room_{room_id}",
                {
                    "type": "talk_end",
                    "player": player
                }
            )
        except Exception as e:
            print(f"广播刚刚结束发言的玩家时出错：{e}")

    async def vote_result(self, event):
        result = event.get("result")

        """
        {
          "type": "vote_result",
          "result": "6", // null 平票
        }
        """

        await self.send(text_data=json.dumps({
            "type": "vote_result",
            "result": result
        }))

    @classmethod
    async def broadcast_vote_result(cls, room_id: str, result: Optional[str]):
        try:
            channel_layer = get_channel_layer()

            await channel_layer.group_send(
                f"room_{room_id}",
                {
                    "type": "vote_result",
                    "result": result
                }
            )
        except Exception as e:
            print(f"广播投票结果时出错：{e}")

    async def day_death_info(self, event):
        victims = event.get("victims")

        """
        {
          "type": "day_death_info",
          "victims": ["3", "6"],
        }
        """

        await self.send(text_data=json.dumps({
            "type": "day_death_info",
            "victims": victims
        }))

    @classmethod
    async def broadcast_day_death_info(cls, room_id: str, victims: list[str]):
        try:
            channel_layer = get_channel_layer()

            await channel_layer.group_send(
                f"room_{room_id}",
                {
                    "type": "day_death_info",
                    "victims": victims
                }
            )
        except Exception as e:
            print(f"广播白天死亡玩家时出错：{e}")

    async def game_end(self, event):
        end = event.get("end")
        victory = event.get("victory")
        victory_side = event.get("victory_side")
        reveal_role = event.get("reveal_role")

        """
        {
          "type": "game_end",
          "end": false // true
          "victory": {
            "Werewolf": false,
            "Villager": true,
            "Prophet": true,
            "Witch": true,
            "Idiot": false
          },  // 没结束为null
          "victory_side": "Good",
          "reveal_role": {
            "1": "Witch",
            "2": "Werewolf",
            ...
          }
        }
        """

        await self.send(text_data=json.dumps({
            "type": "game_end",
            "end": end,
            "victory": victory,
            "victory_side": victory_side,
            "reveal_role": reveal_role
        }))

    @classmethod
    async def broadcast_game_end(cls, room_id: str, end: bool, victory: Optional[dict], victory_side: Optional[str], reveal_role: Optional[dict]):
        try:
            channel_layer = get_channel_layer()

            await channel_layer.group_send(
                f"room_{room_id}",
                {
                    "type": "game_end",
                    "end": end,
                    "victory": victory,
                    "victory_side": victory_side,
                    "reveal_role": reveal_role
                }
            )
        except Exception as e:
            print(f"广播白天死亡玩家时出错：{e}")

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