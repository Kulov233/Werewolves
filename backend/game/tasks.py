# game/tasks.py
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
        async_to_sync(GameConsumer.broadcast_game_update)(room_id, "游戏开始", game_data)
        # TODO: 跳转到游戏逻辑
        print("游戏开始")
    else:
        async_to_sync(GameConsumer.broadcast_game_update)(room_id, result['status'], result['message'])
        # TODO: 处理channel和cache中的残留？

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
