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

def handle_game_readiness(result):
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
        # game_data = game_cache.get(f"room:{room_id}")
        # 所有玩家已连接，开始游戏
        # game_data['status'] = "debug_start"
        # game_cache.set(f"room:{room_id}", game_data)
        # async_to_sync(GameConsumer.broadcast_game_update)(room_id, "game_start", game_data)
        # TODO: 跳转到游戏逻辑
        start_phase_task = start_phase.delay(room_id, 'Initialize')
        # 保存task_id
        game_cache.set(f"room_{room_id}_current_task", start_phase_task.id, timeout=3600)

    else:
        # TODO: 返回未连接玩家列表
        async_to_sync(GameConsumer.handle_not_connected)(room_id, result['status'], result['message'], result['offline_players'])
        # TODO: 前端应该在此时返回大厅。处理channel和cache中的残留？


def initialize(room_id):
    try:
        game_cache = caches['game_cache']
        game_data = game_cache.get(f"room:{room_id}")

        # 读取游戏配置
        with open('backend/game/game_config.json', 'r') as file:
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
                        ai_player = ai_players.pop(0)
                        if role_class == "Witch":
                            cure_count = game_data["witch_config"]["cure_count"]
                            poison_count = game_data["witch_config"]["poison_count"]
                            game_data["ai_players"][ai_player]["role"] = role_class
                            game_data["ai_players"][ai_player]["role_skills"] = {"cure_count": cure_count, "poison_count": poison_count}
                        else:
                            game_data["ai_players"][ai_player]["role"] = role_class
                        remaining_roles.remove(role_class)
        random.shuffle(remaining_roles)

        for player in human_players:
            role_class = remaining_roles.pop(0)
            if role_class == "Witch":
                cure_count = game_data["witch_config"]["cure_count"]
                poison_count = game_data["witch_config"]["poison_count"]
                game_data["players"][player]["role"] = role_class
                game_data["players"][player]["role_skills"] = {"cure_count": cure_count, "poison_count": poison_count}
            else:
                game_data["players"][player]["role"] = role_class

        for ai_player in ai_players:
            role_class = remaining_roles.pop(0)
            if role_class == "Witch":
                cure_count = game_data["witch_config"]["cure_count"]
                poison_count = game_data["witch_config"]["poison_count"]
                game_data["ai_players"][ai_player]["role"] = role_class
                game_data["ai_players"][ai_player]["role_skills"] = {"cure_count": cure_count, "poison_count": poison_count}
            else:
                game_data["ai_players"][ai_player]["role"] = role_class

        game_cache.set(f"room:{room_id}", game_data)
        # TODO: 完成分配角色后，发送消息

        for user_id, _ in game_data["players"].items():
            role_info = {
                "role": game_data["players"][user_id]["role"],
                "role_skills": game_data["players"][user_id]["role_skills"]
            }
            async_to_sync(GameConsumer.send_role_to_player)(room_id, user_id, role_info)

        return {"room_id": room_id, "status": "success", "message": f"房间{room_id}分配角色成功。"}


    except Exception as e:
        return {"room_id": room_id, "status": "error", "message": f"房间{room_id}分配角色失败。", "error": str(e)}

@shared_task
def combined_game_check(room_id):
    """
    组合检查和发送消息的任务
    """
    # 先执行检查
    result = check_is_game_ready(room_id)
    # 直接执行发送消息
    handle_game_readiness(result)
    return result


@shared_task
def handle_phase_timed_out(room_id: str, current_phase: str):
    """
    阶段定时器
    :param room_id:
    :param current_phase: 当前阶段（函数被执行时该阶段已结束）
    :return:
    """
    try:
        game_cache = caches['game_cache']
        game_data = game_cache.get(f"room:{room_id}")
        phase_transitions = game_data["phase_transitions"]
        #
        # event_type_map = {
        #     'Werewolf': 'kill_phase_end',
        #     'Prophet': 'check_phase_end',
        #     'Witch': 'witch_phase_end',
        #     'Vote': 'vote_phase_end'
        #     # TODO: 分玩家发言
        # }
        if current_phase != game_data["current_phase"]:
            print(f"{room_id}中阶段转换异常！应该是{game_data['current_phase']}，而实际是{current_phase}。")

        print(f"{room_id}中{current_phase}阶段结束。")

        # TODO: 阶段结束，进行相应处理
        if current_phase == 'Initialize':
            initialize(room_id)
            assign_roles_to_players(room_id)
        elif current_phase == 'End':
            print(f"{room_id}游戏结束。")
            return {"room_id": room_id, "status": "success", "message": "游戏结束。"}

        # # 1. 通知当前阶段结束
        # if current_phase in event_type_map:
        #     event_type = event_type_map[current_phase]
        #     async_to_sync(GameConsumer.broadcast_game_update)(room_id, event_type, game_data)
        # else:
        #     pass

        # 2. 获取下一个阶段
        next_phase = phase_transitions[current_phase]

        # 3. 开始下一个阶段
        next_phase_task = start_phase.delay(room_id, next_phase)

        # 4. 将task_id存入缓存，以便需要时取消
        game_cache.set(f"room_{room_id}_current_task", next_phase_task.id, timeout=3600)

        return next_phase_task.id

    except Exception as e:
        print(f"Error in phase_timer: {e}")
        # 可能需要进行错误恢复

@shared_task
def start_phase(room_id: str, phase: str):
    """
    开始一个阶段
    :param room_id:
    :param phase: 将要开始的阶段
    :return:
    """
    try:
        game_cache = caches['game_cache']
        game_data = game_cache.get(f"room:{room_id}")
        phase_timer = game_data["phase_timer"]

        # event_type_map = {
        #     'Prophet': 'check_phase_end',
        #     'Witch': 'witch_phase_end',
        #     'Vote': 'vote_phase_end'
        #     # TODO: 分玩家发言
        # }

        # channel_layer = get_channel_layer()
        #
        # # 1. 通知阶段开始
        # async_to_sync(channel_layer.group_send)(
        #     f"room_{room_id}",
        #     {
        #         "type": "phase_start",
        #         "phase": phase
        #     }
        # )

        # 2. 设置阶段结束定时器
        if phase.startswith("Speak_"):
            phase_duration = phase_timer["Speak"]
        else:
            phase_duration = phase_timer[phase]
        timer_task = handle_phase_timed_out.apply_async(
            args=[room_id, phase],
            countdown=phase_duration
        )
        print(f"{room_id}中{phase}阶段开始，将在{phase_duration}秒后结束。")
        game_data["current_phase"] = phase
        game_cache.set(f"room:{room_id}", game_data)

        # 3. 存储当前task_id
        game_cache.set(f"room_{room_id}_current_task", timer_task.id, timeout=3600)

        return timer_task.id

    except Exception as e:
        print(f"Error in start_phase: {e}")

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
