# game/tasks.py
import json
import random

from celery import shared_task
from celery.result import AsyncResult
from django.core.cache import caches
# from channels.layers import get_channel_layer

from asgiref.sync import async_to_sync

from .consumers import GameConsumer

def check_is_game_ready(room_id):
    """
    检查游戏房间是否所有玩家已连接
    """
    game_cache = caches['game_cache']
    # channel_layer = get_channel_layer()

    # 获取房间数据
    game_data = game_cache.get(f"room:{room_id}")

    if not game_data:
        return {"room_id": room_id, "status": "error", "message": "房间不存在"}

    # 检查每个玩家的连接状态
    all_connected = all(player_data['online'] for player_data in game_data['players'].values())

    if all_connected:
        return {"room_id": room_id, "status": "success", "message": "游戏开始"}
    else:
        # 未全部连接，发送通知
        # TODO: 检查是谁未连接
        offline_players = [player['name'] for player in game_data['players'].values() if not player['online']]
        return {
            "room_id": room_id,
            "status": "error",
            "message": "有玩家连接失败，返回大厅。",
            "offline_players": offline_players
        }

def send_room_readiness_message(result):
    """
    发送房间准备状态消息
    """
    # channel_layer = get_channel_layer()

    # 获取玩家列表
    # room_cache = caches['room_cache']
    # room_data = room_cache.get(f"room:{room_id}")
    # players = room_data['players']

    room_id = result['room_id']

    # 发送消息
    if result['status'] == 'success':
        game_cache = caches['game_cache']
        game_data = game_cache.get(f"room:{room_id}")
        # 所有玩家已连接，开始游戏
        game_data['status'] = "debug_start"
        game_cache.set(f"room:{room_id}", game_data)
        async_to_sync(GameConsumer.broadcast_game_update)(room_id, "game_started", game_data)
        # TODO: 跳转到游戏逻辑
        print("游戏开始")
    else:
        # TODO: 返回未连接玩家列表
        async_to_sync(GameConsumer.handle_not_connected)(room_id, result['status'], result['message'], result['offline_players'])
        # TODO: 前端应该在此时返回大厅。处理channel和cache中的残留？

def initialize(room_id):
    try:
        game_cache = caches['game_cache']
        game_data = game_cache.get(f"room:{room_id}")

        # 读取游戏配置
        with open('game_config.json', 'r') as file:
            configs = json.load(file)
            if str(game_data['max_players']) in configs:
                game_config = configs[str(game_data['max_players'])]
            else:
                raise ValueError("没有找到对应玩家数量的游戏配置。")
        # TODO: 确定ai数量
        game_specified_prompt = "当前游戏中有"
        last_role = ""
        role_cnt = 0
        for role in game_config["roles"]:
            if role == last_role:
                role_cnt += 1
            else:
                if role_cnt > 0:
                    game_specified_prompt += f"{role_cnt}个{last_role}，"
                    game_data["roles"][last_role] = role_cnt
                role_cnt = 1
                last_role = role
        game_specified_prompt += f"{role_cnt}个{last_role}。"
        game_data["roles"][last_role] = role_cnt
        game_data["game_specified_prompt"] = game_specified_prompt

        game_data["victory_conditions"] = game_config["victory_conditions"]
        game_data["witch_config"] = game_config.get('witch_items', {'cure_count': 1, 'poison_count': 1})

        # TODO: 所有角色名都是字符串
        try:
            game_data["roles_for_humans_first"] = game_config["roles_for_humans_first"]
        except:
            game_data["roles_for_humans_first"] = None

        game_cache.set(f"room:{room_id}", game_data)

    except Exception as e:
        # TODO: 前端应该在此时返回大厅。处理channel和cache中的残留？
        return {"room_id": room_id, "status": "error", "message": "初始化游戏失败。", "error": str(e)}

def assign_roles_to_players(room_id):
    try:
        game_cache = caches['game_cache']
        game_data = game_cache.get(f"room:{room_id}")

        roles_assigned = []
        human_players = [player for player, _ in game_data["players"].items()] # 以UserID表示
        ai_players = [player for player, _ in game_data["ai_players"].items()] # 以uuid表示
        remaining_roles = [role for role, count in game_data["roles"].items() for _ in range(count)]
        if game_data["roles_for_humans_first"]:
            roles_for_humans_first = game_data["roles_for_humans_first"].copy()

            random.shuffle(roles_for_humans_first)

            for role_class in roles_for_humans_first:
                if human_players:
                    player = human_players.pop(0)
                    if role_class == "Witch":
                        cure_count = game_data["witch_config"]["cure_count"]
                        poison_count = game_data["witch_config"]["poison_count"]
                        game_data["players"][player] = {"role": role_class, "role_skills": {"cure_count": cure_count, "poison_count": poison_count}}
                    else:
                        game_data["players"][player] = {"role": role_class}
                    remaining_roles.remove(role_class)
                else:
                    if ai_players:
                        player = ai_players.pop(0)
                        if role_class == "Witch":
                            cure_count = game_data["witch_config"]["cure_count"]
                            poison_count = game_data["witch_config"]["poison_count"]
                            game_data["ai_players"][player] = {"role": role_class, "role_skills": {"cure_count": cure_count, "poison_count": poison_count}}
                        else:
                            game_data["ai_players"][player] = {"role": role_class}
                        remaining_roles.remove(role_class)
            random.shuffle(remaining_roles)

            remaining_players = human_players + ai_players

            for role_class, player in zip(remaining_roles, remaining_players):
                if role_class == "Witch":
                    cure_count = game_data["witch_config"]["cure_count"]
                    poison_count = game_data["witch_config"]["poison_count"]
                    game_data["players"][player] = {"role": role_class, "role_skills": {"cure_count": cure_count, "poison_count": poison_count}}
                else:
                    game_data["players"][player] = {"role": role_class}
                roles_assigned.append(player)

            game_cache.set(f"room:{room_id}", game_data)
            # TODO: 完成分配角色后，发送消息


    except Exception as e:
        return {"room_id": room_id, "status": "error", "message": "分配角色失败。", "error": str(e)}

@shared_task
def combined_game_check(room_id):
    """
    组合检查和发送消息的任务
    """
    # 先执行检查
    result = check_is_game_ready(room_id)
    # 直接执行发送消息
    send_room_readiness_message(result)
    return result


async def trigger_game_start_check(room_id) -> AsyncResult:
    """
    触发游戏开始前的检查
    """

    # 调用 Celery 任务进行检查
    result = combined_game_check.apply_async(
        args=[room_id],
        countdown=10
    )
    return result
