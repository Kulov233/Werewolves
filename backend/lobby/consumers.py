# lobby/consumers.py
import asyncio
import json
import uuid

from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import caches

from datetime import datetime, timedelta

from game.tasks import trigger_game_start_check

from functools import wraps


def with_room_lock(timeout=5):
    def decorator(func):
        @wraps(func)
        async def wrapper(consumer, data, *args, **kwargs):
            cache = caches["lobby_cache"]
            room_id = data.get("room_id")

            if not room_id:
                return await func(consumer, data, *args, **kwargs)

            lock_id = f"lock:room:{room_id}"
            retry_count = 3
            retry_delay = 0.5  # 500ms

            for attempt in range(retry_count):
                delay = retry_delay * (2 ** attempt)

                if cache.add(lock_id, 1, timeout):
                    try:
                        return await func(consumer, data, *args, **kwargs)
                    finally:
                        cache.delete(lock_id)

                await asyncio.sleep(delay)

            # 多次重试失败后才返回错误
            await consumer.send(text_data=json.dumps({
                "type": "error",
                "message": "操作失败，请稍后重试。"
            }))

        return wrapper

    return decorator


def with_room_list_lock(timeout=5):
    def decorator(func):
        @wraps(func)
        async def wrapper(consumer, *args, **kwargs):
            cache = caches["lobby_cache"]
            lock_id = "lock:room_list"

            retry_count = 3
            retry_delay = 0.5  # 500ms

            for attempt in range(retry_count):
                delay = retry_delay * (2 ** attempt)

                if cache.add(lock_id, 1, timeout):
                    try:
                        return await func(consumer, *args, **kwargs)
                    finally:
                        cache.delete(lock_id)

                await asyncio.sleep(delay)

            # 多次重试失败后才返回错误
            await consumer.send(text_data=json.dumps({
                "type": "error",
                "message": "服务器内部发生错误，请稍后重试。"
            }))

        return wrapper

    return decorator


class LobbyConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lobby_cache = caches["lobby_cache"]
        self.game_cache = caches["game_cache"]
        self.room_timeout = 3600  # 房间超时时间[s]
        self.status_update_interval = 30  # 用户在线状态更新间隔[s]

    # 连接时触发
    # noinspection PyUnresolvedReferences
    @with_room_list_lock(timeout=5)
    async def connect(self):
        try:
            if self.scope["user"].is_anonymous:
                # 如果用户未认证，拒绝连接
                raise DenyConnection("用户未认证。")
            else:
                # TODO: 需要检查用户是否已连接吗？
                # TODO: 需要检查用户是否在房间中吗？
                user_id = self.scope["user"].id

                # if await self.has_active_connection(user_id):
                #     # 如果有现有连接，拒绝连接
                #     raise DenyConnection("您已经有一个活跃连接。")

                # 接受连接并将用户加入组
                await self.channel_layer.group_add("lobby", self.channel_name)
                await self.channel_layer.group_add(f"lobby_user_{user_id}", self.channel_name)
                await self.accept()

                if bool(await self.is_user_online(user_id)):
                    await self.send(text_data=json.dumps({
                        "type": "warning",
                        "message": "您似乎已经有一个活跃连接，请确保没有重复连接。"
                    }))

                # 设置用户在线状态
                await self.set_online_status(user_id)
                # 启动定期更新状态的任务
                self.status_update_task = asyncio.create_task(self.update_online_status())

                # 将用户的连接信息添加到 channel_layer 中
                # await self.add_connection(user_id)

                # 清理信息
                await self.clear_user_room_in_cache(self.scope["user"].id)

                # 发送在线的好友列表
                online_friends = await self.get_online_friends(self.scope["user"].id)
                await self.send(text_data=json.dumps({
                    "type": "online_friends",
                    "friends": online_friends
                }))

                # 发送房间列表
                rooms = await self.get_room_list_from_cache()
                await self.send(text_data=json.dumps({
                    "type": "room_list",
                    "rooms": rooms
                }))
        except DenyConnection as e:
            await self.accept()
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))
            await self.close()

    # noinspection PyUnresolvedReferences
    async def disconnect(self, close_code):
        # 从 "lobby" 组移除用户
        user_id = self.scope["user"].id
        # await self.remove_connection(user_id)

        # 清除在线状态
        await self.remove_online_status(user_id)
        # 取消状态更新任务
        if hasattr(self, 'status_update_task'):
            self.status_update_task.cancel()

        # TODO: 游戏已开始？

        # TODO: 检查用户是否在房间中，如果在房间中则移除用户
        await self.channel_layer.group_discard("lobby", self.channel_name)
        await self.channel_layer.group_discard(f"lobby_user_{user_id}", self.channel_name)
        room_id = await self.get_user_room_from_cache(self.scope["user"].id)
        if room_id:
            await self.remove_player_from_room(room_id, self.scope["user"].id)
            await self.clear_user_room_in_cache(self.scope["user"].id)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            # 仅允许认证用户发送消息
            # if not self.scope["user"].is_authenticated:
            #     raise DenyConnection("没有权限。")

            data = json.loads(text_data)
            action = data.get("action")

            # 处理客户端发送的消息
            # 下面是客户端可以进行的操作

            # 创建房间
            if action == "create_room":
                await self.handle_create_room(data)
            # 获取房间列表
            elif action == "get_rooms":
                await self.handle_get_rooms(data)
            # 移除房间
            elif action == "remove_room":
                await self.handle_remove_room(data)
            # 加入房间
            elif action == "join_room":
                await self.handle_join_room(data)
            # 邀请玩家
            elif action == "invite_player":
                await self.handle_invite_player(data)
            # 移除玩家
            elif action == "remove_player_from_room":
                await self.handle_remove_player_from_room(data)
            # 添加 AI 玩家
            elif action == "add_ai_player":
                await self.handle_add_ai_player(data)
            # 移除 AI 玩家
            elif action == "remove_ai_player":
                await self.handle_remove_ai_player(data)
            # 编辑房间
            elif action == "edit_room":
                await self.handle_edit_room(data)
            # 离开房间
            elif action == "leave_room":
                await self.handle_leave_room(data)
            # 开始游戏
            elif action == "start_game":
                await self.handle_start_game(data)
            else:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "未知操作。"
                }))

        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))
            # await self.close()

    """
    下面是自定义的房间相关方法，考虑将它们模块化？
    """

    # noinspection PyUnresolvedReferences
    @with_room_list_lock(timeout=5)
    async def handle_get_rooms(self, data):
        rooms = await self.get_room_list_from_cache()
        await self.send(text_data=json.dumps({
            "type": "room_list",
            "rooms": rooms
        }))

    # noinspection PyUnresolvedReferences
    @with_room_list_lock(timeout=5)
    async def handle_create_room(self, data):
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
            "title": data.get("title", None),
            "description": data.get("description", None),
            "owner": self.scope["user"].id,
            "players": [self.scope["user"].id],
            "allow_ai_players": data.get("allow_ai_players", None),
            "ai_players": {},  # TODO: AI 玩家配置
            "max_players": data.get("max_players", 6),
            # "game_mode": data.get("game_mode", "default"),
            "status": "waiting",  # in-game
            "created_at": datetime.now().isoformat(),
            "expires_at": ""
        }

        allowed_max_players = [4, 6, 8, 10, 12, 16]

        # TODO: 校验房间数据
        if not room_data["title"]:
            await self.send(text_data=json.dumps({
                "type": "warning",
                "message": "房间标题为空，已设置为默认标题。"
            }))
            room_data["title"] = "未命名的房间"
        if not room_data["description"]:
            await self.send(text_data=json.dumps({
                "type": "warning",
                "message": "房间简介为空，已设置为默认简介。"
            }))
            room_data["description"] = "房主没有填写简介~"
        if not isinstance(room_data["allow_ai_players"], bool):
            await self.send(text_data=json.dumps({
                "type": "warning",
                "message": "房间是否允许 AI 玩家设置错误，已设置为默认值（允许）。"
            }))
            room_data["allow_ai_players"] = True
        if not isinstance(room_data["max_players"], int):
            try:
                await self.send(text_data=json.dumps({
                    "type": "warning",
                    "message": "最大玩家数不是一个整数，已尝试转换。"
                }))
                room_data["max_players"] = int(room_data["max_players"])
            except ValueError:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "最大玩家数必须是一个整数。"
                }))
                return
        if room_data["max_players"] not in allowed_max_players:
            await self.send(text_data=json.dumps({
                "type": "warning",
                "message": "不支持的最大玩家数，已设置为默认值（6人）。"}))
            room_data["max_players"] = 6

        await self.update_room_in_cache(room_id, room_data)
        await self.add_room_id_to_cache(room_id)  # 添加房间 ID 到列表
        await self.set_user_room_in_cache(self.scope["user"].id, room_id)
        await self.broadcast_room_update("room_created", room_data)

    # noinspection PyUnresolvedReferences
    async def remove_room(self, room_id):
        await self.remove_room_from_cache(room_id)
        await self.remove_room_id_from_cache(room_id)
        await self.broadcast_room_update("room_removed", {"id": room_id})

    # noinspection PyUnresolvedReferences
    @with_room_lock(timeout=5)
    @with_room_list_lock(timeout=5)
    async def handle_remove_room(self, data):
        """
        删除房间
        :param data: 客户端发送的text_data，里面应该有且仅有room_id
        :return: 不会返回值，但是会向所有客户端发送消息，遇到错误时只会向当前客户端发送消息
        """
        # 验证房主身份
        room_id = data.get("room_id")
        room_data = await self.get_room_data_from_cache(room_id)
        if room_data and room_data["owner"] == self.scope["user"].id:

            if room_data["status"] == "in-game":
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "游戏正在进行中，无法删除房间。"
                }))
                return

            await self.remove_room(room_id)
            # TODO: 前端在收到 "room_removed" 事件后，如果用户在房间中，应该自动退出房间

            for player in room_data["players"]:
                await self.clear_user_room_in_cache(player)
        else:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "无法删除房间。房间可能不存在，或者您不是房主。"
            }))

    # noinspection PyUnresolvedReferences
    @with_room_lock(timeout=5)
    async def handle_invite_player(self, data):
        if not await self.get_user_room_from_cache(self.scope["user"].id):
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "您不在任何房间中。"
            }))
            return

        room_id = data.get("room_id")
        room_data = await self.get_room_data_from_cache(room_id)

        if room_id != await self.get_user_room_from_cache(self.scope["user"].id):
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "您不在该房间中。"
            }))
            return

        if room_data:
            target = data.get("target")
            if not target:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "请提供要邀请的玩家的用户ID。"
                }))
                return
            if target == self.scope["user"].id:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "您不能邀请自己。"
                }))
                return
            if not await self.is_friend(self.scope["user"].id, target):
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "目标玩家不是您的好友。"
                }))
                return
            if not await self.is_user_online(target):
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "目标玩家不在线。"
                }))
                return
            if target in room_data["players"]:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "目标玩家已经在房间中。"
                }))
                return
            if len(room_data["players"]) + len(room_data["ai_players"]) >= room_data["max_players"]:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "房间已满。"
                }))
                return
            await self.send_game_invite(target, room_id)
            await self.send(text_data=json.dumps({
                "type": "info",
                "message": "邀请已发送。"
            }))

        else:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "房间不存在。"
            }))

    # noinspection PyUnresolvedReferences
    @with_room_lock(timeout=5)
    async def handle_join_room(self, data):
        """
        加入房间
        :param data: 客户端发送的text_data，里面应该有且仅有room_id
        :return: 不会返回值，但是会向客户端发送消息，遇到错误时只会向当前客户端发送消息
        """
        if await self.get_user_room_from_cache(self.scope["user"].id):
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "您已经在一个房间中。"
            }))
            return
        room_id = data.get("room_id")
        room_data = await self.get_room_data_from_cache(room_id)
        if room_data:
            if self.scope["user"].id in room_data["players"]:
                await self.set_user_room_in_cache(self.scope["user"].id, room_id)
                return

            if room_data["status"] == "in-game":
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "游戏正在进行中，无法加入房间。"
                }))
                return
            if len(room_data["players"]) + len(room_data["ai_players"]) >= room_data["max_players"]:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "房间已满。"
                }))
                return
            else:
                await self.add_player_to_room(room_id, self.scope["user"].id)
        else:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "房间不存在。"
            }))

    # noinspection PyUnresolvedReferences
    @with_room_lock(timeout=5)
    async def handle_add_ai_player(self, data):
        """
        player_info: {
            name: ""
        }
        """
        room_id = data.get("room_id")
        room_data = await self.get_room_data_from_cache(room_id)
        if room_data:
            if room_data["owner"] == self.scope["user"].id:
                if len(room_data["players"]) + len(room_data["ai_players"]) >= room_data["max_players"]:
                    await self.send(text_data=json.dumps({
                        "type": "error",
                        "message": "房间已满。"
                    }))
                    return
                else:
                    if not room_data["allow_ai_players"]:
                        await self.send(text_data=json.dumps({
                            "type": "error",
                            "message": "房间不允许 AI 玩家。"
                        }))
                        return
                    # TODO: 与前端对接
                    original_player_info = data.get("player_info")
                    if original_player_info:
                        player_info = {
                            "name": original_player_info.get("name", "AI 玩家")
                        }
                        await self.add_ai_player_to_room(room_id, player_info)
                    else:
                        await self.send(text_data=json.dumps({
                            "type": "error",
                            "message": "请提供 AI 玩家信息。"
                        }))


            else:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "只有房主可以添加 AI 玩家。"
                }))
        else:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "房间不存在。"
            }))

    # noinspection PyUnresolvedReferences
    @with_room_lock(timeout=5)
    async def handle_remove_ai_player(self, data):
        """
        id: ""
        """
        room_id = data.get("room_id")
        room_data = await self.get_room_data_from_cache(room_id)
        if room_data:
            if room_data["owner"] == self.scope["user"].id:
                await self.remove_ai_player_from_room(room_id, data.get("player_id"))
            else:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "只有房主可以移除 AI 玩家。"
                }))
        else:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "房间不存在。"
            }))

    # noinspection PyUnresolvedReferences
    @with_room_lock(timeout=5)
    async def handle_edit_room(self, data):
        room_id = data.get("room_id")
        room_data = await self.get_room_data_from_cache(room_id)
        if room_data:
            if room_data["owner"] == self.scope["user"].id:
                title = data.get("title", None)
                if not title:
                    await self.send(text_data=json.dumps({
                        "type": "warning",
                        "message": "房间标题为空，不作修改。"
                    }))
                else:
                    room_data["title"] = title

                description = data.get("description", None)
                if not description:
                    await self.send(text_data=json.dumps({
                        "type": "warning",
                        "message": "房间简介为空，不作修改。"
                    }))
                else:
                    room_data["description"] = description

                allow_ai_players = data.get("allow_ai_players", None)
                if not isinstance(allow_ai_players, bool):
                    await self.send(text_data=json.dumps({
                        "type": "warning",
                        "message": "房间是否允许 AI 玩家设置错误，不作修改。"
                    }))
                else:
                    room_data["allow_ai_players"] = allow_ai_players
                    if not allow_ai_players:
                        # 移除 AI 玩家
                        room_data["ai_players"] = {}

                max_players = data.get("max_players")

                allowed_max_players = [4, 6, 8, 10, 12, 16]

                if not isinstance(max_players, int):
                    try:
                        await self.send(text_data=json.dumps({
                            "type": "warning",
                            "message": "最大玩家数不是一个整数，已尝试转换。"
                        }))
                        max_players = int(max_players)
                    except ValueError:
                        await self.send(text_data=json.dumps({
                            "type": "error",
                            "message": "最大玩家数错误，不作修改。"
                        }))
                if isinstance(max_players, int):
                    if max_players not in allowed_max_players:
                        await self.send(text_data=json.dumps({
                            "type": "warning",
                            "message": "不支持的最大玩家数，不作修改。"}))
                    else:
                        if len(room_data["players"]) + len(room_data["ai_players"]) > max_players:
                            await self.send(text_data=json.dumps({
                                "type": "error",
                                "message": "房间人数已经超过了最大人数。"
                            }))
                            return
                        else:
                            room_data["max_players"] = max_players

                await self.update_room_in_cache(room_id, room_data)
                await self.broadcast_room_update("room_updated", room_data)
            else:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "只有房主可以编辑房间。"
                }))
        else:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "房间不存在。"}))

    # noinspection PyUnresolvedReferences
    @with_room_lock(timeout=5)
    async def handle_remove_player_from_room(self, data):
        room_id = data.get("room_id")
        room_data = await self.get_room_data_from_cache(room_id)
        if room_data:
            if room_data["owner"] == self.scope["user"].id:
                user_id = data.get("user_id")
                if user_id == self.scope["user"].id:
                    await self.send(text_data=json.dumps({
                        "type": "error",
                        "message": "不能踢出自己。"
                    }))
                    return

                if user_id in room_data["players"]:
                    await self.remove_player_from_room(room_id, user_id)
                else:
                    await self.send(text_data=json.dumps({
                        "type": "error",
                        "message": "玩家不在房间中。"
                    }))
            else:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "只有房主可以踢出玩家。"
                }))
        else:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "房间不存在。"}))

    # noinspection PyUnresolvedReferences
    @with_room_lock(timeout=5)
    async def handle_leave_room(self, data):
        """
        离开房间
        :param data: 客户端发送的text_data，里面应该有且仅有room_id
        :return: 不会返回值，但是会向客户端发送消息，遇到错误时只会向当前客户端发送消息
        """
        room_id = data.get("room_id")
        room_data = await self.get_room_data_from_cache(room_id)

        if room_data:
            if self.scope["user"].id in room_data["players"]:
                await self.remove_player_from_room(room_id, self.scope["user"].id)
            else:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "您不在该房间中。"
                }))
        else:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "房间不存在。"
            }))

    # noinspection PyUnresolvedReferences,PyTypeChecker
    @with_room_lock(timeout=5)
    async def handle_start_game(self, data):
        room_id = data.get("room_id")
        room_data = await self.get_room_data_from_cache(room_id)
        if room_data:
            if room_data["owner"] == self.scope["user"].id:
                if len(room_data["players"]) + len(room_data["ai_players"]) < room_data["max_players"]:
                    await self.send(text_data=json.dumps({
                        "type": "error",
                        "message": "房间人数不足。"
                    }))
                    return
                else:
                    if room_data["status"] == "in-game":
                        await self.send(text_data=json.dumps({
                            "type": "error",
                            "message": "游戏正在进行中，无法开始游戏。"
                        }))
                        return

                    # TODO: 开始游戏，前端应该在收到消息时，检查是否在房间中，如果在房间中则跳转到游戏页面，并连接到游戏的 WebSocket，如果不在，则将房间标记为“游戏中”
                    await self.broadcast_room_update("game_prepared", room_data)
                    # 将房间信息写入房间缓存
                    # TODO: 设计游戏房间数据结构
                    from django.contrib.auth.models import User

                    @database_sync_to_async
                    def get_user_name(user_id):
                        return User.objects.get(id=user_id).username

                    room_data_in_game = {
                        "id": room_data["id"],
                        "title": room_data["title"],
                        "description": room_data["description"],
                        "max_players": room_data["max_players"],
                        # "status": "waiting",  # waiting, night_<num>, day_<num>, finished
                        "night_count": 1,
                        "roles": {},
                        "roles_for_humans_first": [],  # 敏感
                        "witch_config": {},
                        "players": {
                            str(player): {  # 这里的 user_id 是字符串！
                                'index': str(idx + 1),  # 玩家编号，也是字符串，从 1 开始
                                'name': await get_user_name(player),
                                'alive': True,
                                'online': False,
                                'role': None,  # 敏感
                                'role_skills': None,  # 技能信息（女巫），敏感
                            }
                            for idx, player in enumerate(room_data["players"])
                        },
                        "ai_players": {
                            player_id: {
                                'index': str(idx + 1 + len(room_data["players"])),  # 接上真人玩家编号
                                'name': player_info["name"],
                                'alive': True,
                                'role': None,  # 敏感
                                'role_skills': None, # 敏感
                                # 'action_history': None # 敏感
                            }
                            for idx, (player_id, player_info) in enumerate(room_data["ai_players"].items())
                        },
                        "victory_conditions": {},  # 敏感
                        "game_specified_prompt": "",  # 敏感
                        "victims_info": [],  # 敏感
                        "poisoned_victims_info": [],  # 敏感
                        "voted_victims_info": [],  # 敏感
                        "werewolves_targets": {}, # 敏感
                        "votes": {},  # 敏感
                        "current_phase": "Waiting",
                        "action_history": [], # 敏感
                        "phase_timer": {
                            "Initialize": 1,
                            "Werewolf": 40,
                            "Prophet": 40,
                            "Witch": 40,
                            "Day": 3,
                            "Speak": 40,
                            "Vote": 40,
                            'End': 3,
                        },
                        "starts_at": datetime.now().isoformat(),
                        # ...
                    }
                    speaking_phases = [f"Speak_{i}" for i in range(1, room_data["max_players"] + 1)]
                    room_data_in_game["phase_transitions"] = {
                        "Initialize": "Werewolf",
                        "Werewolf": "Prophet",
                        "Prophet": "Witch",
                        "Witch": "End_Night",
                        "End_Night": "Day",
                        "Day": speaking_phases[0],
                    }
                    for i in range(room_data["max_players"] - 1):
                        room_data_in_game["phase_transitions"][speaking_phases[i]] = speaking_phases[i + 1]
                    room_data_in_game["phase_transitions"][speaking_phases[-1]] = "Vote"
                    room_data_in_game["phase_transitions"]["Vote"] = "End_Day"
                    room_data_in_game["phase_transitions"]["End_Day"] = "Werewolf"
                    """
                    Initialize -> Werewolf -> Prophet -> Witch -> End_Night -> Day -> Speak_1 ->
                     Speak_2 -> ... -> Speak_n -> Vote 
                     -> End_Day -> Werewolf
                     如果编号 n - len(room_data["players"]) > 0，则 Speak_n 为 AI 玩家发言
                    """

                    # all_phases = list(room_data_in_game["phase_transitions"].keys()) + list(
                    #     room_data_in_game["phase_transitions"].values())
                    # unique_phases = set(all_phases)
                    # unique_phases_list = list(unique_phases)
                    # room_data_in_game["phases"] = unique_phases_list

                    await self.set_room_data_in_game_cache(room_id, room_data_in_game)
                    # TODO: 在大厅中删除房间？
                    # await self.remove_room(room_id)
                    # for player in room_data["players"]:
                    #     await self.clear_user_room_in_cache(player)

                    # 触发游戏开始检查
                    await trigger_game_start_check(room_id)

            else:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "只有房主可以开始游戏。"
                }))
        else:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "房间不存在。"
            }))

    # noinspection PyUnresolvedReferences
    async def add_player_to_room(self, room_id, user_id):
        if await self.get_user_room_from_cache(user_id):
            return
        room_data = await self.get_room_data_from_cache(room_id)
        if room_data:
            await self.set_user_room_in_cache(user_id, room_id)
            if user_id not in room_data["players"]:
                room_data["players"].append(user_id)
                await self.update_room_in_cache(room_id, room_data)
                await self.broadcast_room_update("player_joined", room_data)

    # noinspection PyUnresolvedReferences
    async def add_ai_player_to_room(self, room_id, player_info):
        room_data = await self.get_room_data_from_cache(room_id)
        if room_data:
            player_id = str(uuid.uuid4())
            room_data["ai_players"][player_id] = player_info
            await self.update_room_in_cache(room_id, room_data)
            await self.broadcast_room_update("ai_player_joined", room_data)

    # noinspection PyUnresolvedReferences
    async def remove_ai_player_from_room(self, room_id, player_id):
        room_data = await self.get_room_data_from_cache(room_id)
        if room_data:
            if player_id in room_data["ai_players"]:
                room_data["ai_players"].pop(player_id)
            await self.update_room_in_cache(room_id, room_data)
            await self.broadcast_room_update("ai_player_left", room_data)

    # noinspection PyUnresolvedReferences
    async def remove_player_from_room(self, room_id, user_id):
        room_data = await self.get_room_data_from_cache(room_id)
        if room_data:
            if user_id in room_data["players"]:
                # 检查是否是房主，和退出之后房间是否为空
                if len(room_data["players"]) == 1:
                    # 如果房间只剩一个玩家，删除房间
                    await self.remove_room_from_cache(room_id)
                    await self.clear_user_room_in_cache(user_id)
                    await self.broadcast_room_update("room_removed", {"id": room_id})
                    return
                else:
                    if room_data["owner"] == user_id:
                        # 如果退出房间的是房主，将房主转移给下一个玩家
                        room_data["owner"] = room_data["players"][1]
                room_data["players"].remove(user_id)
                await self.clear_user_room_in_cache(user_id)
                await self.update_room_in_cache(room_id, room_data)
                # 房间更新可能包含房主变动！
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
        try:
            await self.channel_layer.group_send(
                "lobby",
                {
                    "type": "lobby_message",
                    "event": event_type,
                    "room": room_data
                }
            )
        except Exception as e:
            print(f"广播消息时出错：{e}")

    async def game_invite(self, event):
        """处理接收到的游戏邀请"""
        await self.send(text_data=json.dumps({
            "type": "game_invite",
            "source": event["sender_id"],
            "room_id": event["room_id"]
        }))

    async def send_game_invite(self, target_id: int, room_id: str):
        try:
            """发送游戏邀请"""
            await self.channel_layer.group_send(
                f"lobby_user_{target_id}",  # 目标用户的私人频道
                {
                    "type": "game_invite",
                    "sender_id": self.scope["user"].id,
                    "room_id": room_id
                }
            )
        except Exception as e:
            print(f"发送游戏邀请时出错：{e}")

    # @database_sync_to_async
    # def has_active_connection(self, user_id):
    #     # 使用 Django 缓存检查用户是否已有连接
    #     return self.lobby_cache.get(f"user:{user_id}:connected", False)
    #
    # @database_sync_to_async
    # def add_connection(self, user_id):
    #     # 将用户连接标记为 True，表示该用户已经连接
    #     self.lobby_cache.set(f"user:{user_id}:connected", True, timeout=None)
    #
    # @database_sync_to_async
    # def remove_connection(self, user_id):
    #     # 用户断开连接时，从缓存中删除连接标记
    #     self.lobby_cache.delete(f"user:{user_id}:connected")

    # 定期更新在线状态
    # noinspection PyUnresolvedReferences
    async def update_online_status(self):
        while True:
            user_id = self.scope["user"].id
            await self.set_online_status(user_id)
            await asyncio.sleep(self.status_update_interval)

    @database_sync_to_async
    def get_online_friends(self, user_id) -> list[int]:
        """获取在线好友列表"""
        from django.contrib.auth.models import User

        user = User.objects.get(id=user_id)
        # 获取所有好友
        friends = user.userprofile.friends.all()
        # 过滤出在线的好友
        online_friend_ids = []
        for friend in friends:
            if self.lobby_cache.get(f"user_online:{friend.id}"):
                online_friend_ids.append(friend.id)

        return online_friend_ids

    @database_sync_to_async
    def is_friend(self, user_id: int, target_id: int) -> bool:
        """检查target_id是否是user_id的好友"""
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)
        return user.userprofile.friends.filter(id=target_id).exists()

    # 设置用户在线状态
    @database_sync_to_async
    def set_online_status(self, user_id):
        self.lobby_cache.set(
            f"user_online:{user_id}",
            True,
            timeout=self.status_update_interval * 2
        )

    # 移除用户在线状态
    @database_sync_to_async
    def remove_online_status(self, user_id):
        self.lobby_cache.delete(f"user_online:{user_id}")

    # 检查用户是否在线
    @database_sync_to_async
    def is_user_online(self, user_id):
        return bool(self.lobby_cache.get(f"user_online:{user_id}"))

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
    def get_room_list_from_cache(self) -> list:
        room_list = self.lobby_cache.get("room_list", [])
        rooms = []
        for room_id in room_list:
            room_data = self.lobby_cache.get(f"room:{room_id}")
            if room_data:
                rooms.append(room_data)
            else:
                # 如果房间数据不存在，从房间列表中移除
                room_list.remove(room_id)
        self.lobby_cache.set("room_list", room_list, timeout=None)
        return rooms

    # 创建房间并保存到缓存或数据库中（此处使用缓存）
    @database_sync_to_async
    def update_room_in_cache(self, room_id, room_data):
        room_data["expires_at"] = (datetime.now() + timedelta(seconds=self.room_timeout)).isoformat()
        self.lobby_cache.set(f"room:{room_id}", room_data, timeout=self.room_timeout)  # TODO: 考虑timeout

    # 删除房间
    @database_sync_to_async
    def remove_room_from_cache(self, room_id):
        self.lobby_cache.delete(f"room:{room_id}")

    # 获取房间数据
    @database_sync_to_async
    def get_room_data_from_cache(self, room_id) -> dict:
        return self.lobby_cache.get(f"room:{room_id}")

    # 记录用户所在房间
    @database_sync_to_async
    def set_user_room_in_cache(self, user_id, room_id):
        self.lobby_cache.set(f"user_room:{user_id}", room_id, timeout=None)

    # 获取用户所在房间
    @database_sync_to_async
    def get_user_room_from_cache(self, user_id) -> str:
        # 直接从缓存获取用户所在的房间 ID
        return self.lobby_cache.get(f"user_room:{user_id}")

    # 移除用户所在房间
    @database_sync_to_async
    def clear_user_room_in_cache(self, user_id):
        # 删除用户的房间绑定记录
        self.lobby_cache.delete(f"user_room:{user_id}")

    # 将房间信息写入房间缓存
    @database_sync_to_async
    def set_room_data_in_game_cache(self, room_id, room_data):
        self.game_cache.set(f"room:{room_id}", room_data, timeout=self.room_timeout)
