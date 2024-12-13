# game/tasks.py
import asyncio
import json
import random
import time
from functools import wraps

from celery import shared_task
from celery.result import AsyncResult
from django.core.cache import caches
# from channels.layers import get_channel_layer

from asgiref.sync import async_to_sync

from .ai.ai_executor import AIExecutor
from .consumers import GameConsumer
from app.celery import app

def with_game_data_lock_async(timeout=5):
    def decorator(func):
        @wraps(func)
        async def wrapper(room_id, *args, **kwargs):
            cache = caches["game_cache"]

            lock_id = f"lock:game:room:{room_id}"
            retry_count = 3
            retry_delay = 0.5  # 500ms

            for attempt in range(retry_count):
                delay = retry_delay * (2 ** attempt)
                if cache.add(lock_id, 1, timeout):
                    try:
                        return await func(room_id, *args, **kwargs)
                    finally:
                        cache.delete(lock_id)

                await asyncio.sleep(delay)

            print(f"有关房间{room_id}的操作超时。")

        return wrapper

    return decorator

def with_game_data_lock(timeout=5):
    def decorator(func):
        @wraps(func)
        def wrapper(room_id, *args, **kwargs):
            cache = caches["game_cache"]

            lock_id = f"lock:game:room:{room_id}"
            retry_count = 3
            retry_delay = 0.5  # 500ms

            for attempt in range(retry_count):
                delay = retry_delay * (2 ** attempt)
                if cache.add(lock_id, 1, timeout):
                    try:
                        return func(room_id, *args, **kwargs)
                    finally:
                        cache.delete(lock_id)

                time.sleep(delay)

            print(f"有关房间{room_id}的操作超时。")

        return wrapper

    return decorator


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


def handle_game_readiness(room_id, result):
    """
    发送房间准备状态消息
    """
    # channel_layer = get_channel_layer()

    # 获取玩家列表
    # room_cache = caches['room_cache']
    # room_data = room_cache.get(f"room:{room_id}")
    # players = room_data['players']

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
        pass
        #async_to_sync(GameConsumer.handle_not_connected)(room_id, result['status'], result['message'],
                                                         # result['offline_players'])
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
        print(f"初始化游戏失败：{str(e)}")
        return {"room_id": room_id, "status": "error", "message": "初始化游戏失败。", "error": str(e)}


def assign_roles_to_players(room_id):
    try:
        game_cache = caches['game_cache']
        game_data = game_cache.get(f"room:{room_id}")

        human_players = [player for player, _ in game_data["players"].items()]  # 以UserID表示
        ai_players = [player for player, _ in game_data["ai_players"].items()]  # 以uuid表示
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
                        game_data["players"][player]["role"] = role_class
                        game_data["players"][player]["role_skills"] = {"cure_count": cure_count, "poison_count": poison_count}
                    else:
                        game_data["players"][player]["role"] = role_class
                    remaining_roles.remove(role_class)
                else:
                    if ai_players:
                        ai_player = ai_players.pop(0)
                        if role_class == "Witch":
                            cure_count = game_data["witch_config"]["cure_count"]
                            poison_count = game_data["witch_config"]["poison_count"]
                            game_data["ai_players"][ai_player]["role"] = role_class
                            game_data["ai_players"][ai_player]["role_skills"] = {"cure_count": cure_count,
                                                                                 "poison_count": poison_count}
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
                game_data["ai_players"][ai_player]["role_skills"] = {"cure_count": cure_count,
                                                                     "poison_count": poison_count}
            else:
                game_data["ai_players"][ai_player]["role"] = role_class

        werewolves = []

        # TODO: 完成分配角色后，发送消息
        for user_id, data in game_data["players"].items():
            if data["role"] == "Werewolf":
                werewolves.append(data["index"])

            role_info = {
                "role": data["role"],
                "role_skills": data["role_skills"]
            }
            async_to_sync(GameConsumer.send_role_to_player)(room_id, user_id, role_info)

        for uuid, data in game_data["ai_players"].items():
            if data["role"] == "Werewolf":
                werewolves.append(data["index"])

            message = f"你的角色是{data['role']}"
            if data["role"] == "Witch":
                message += f"，解药{data['role_skills']['cure_count']}瓶，毒药{data['role_skills']['poison_count']}瓶"
            message += "。"
            game_data["action_history"].append({
                f"{data['index']}": message
            })

        # TODO: 通知狼人他们的队友
        message = "狼人玩家的编号分别是："

        message += "、".join(werewolves)

        game_data["action_history"].append({
            "Werewolf": message
        })

        game_cache.set(f"room:{room_id}", game_data)
        return {"room_id": room_id, "status": "success", "message": f"房间{room_id}分配角色成功。"}


    except Exception as e:
        print(f"分配角色失败：{str(e)}")
        return {"room_id": room_id, "status": "error", "message": f"房间{room_id}分配角色失败。", "error": str(e)}

@shared_task
@with_game_data_lock(timeout=5)
def combined_game_check(room_id):
    """
    组合检查和发送消息的任务
    """
    # 先执行检查
    result = check_is_game_ready(room_id)
    # 直接执行发送消息
    handle_game_readiness(room_id, result)
    return result


def get_kill_result(room_id):
    """
    获取狼人杀人结果
    """
    # TODO: BUG len()
    game_cache = caches['game_cache']
    game_data = game_cache.get(f"room:{room_id}")

    # 获取狼人选择
    werewolves_targets = game_data["werewolves_targets"]

    votes = {}
    for _, target in werewolves_targets.items():
        if target is not None:
            votes[target] = votes.get(target, 0) + 1

    # 获取最高票数
    max_votes = max(votes.values(), default=0)

    # 获取最高票数的玩家
    players_with_max_votes = [player for player, count in votes.items() if count == max_votes]

    kill_result = None
    # 如果有多个玩家最高票数，则不杀
    if len(players_with_max_votes) > 1:
        pass
    else:
        # 暂存被杀玩家，白天时统一处理
        if players_with_max_votes:
            kill_result = players_with_max_votes[0]
            game_data["victims_info"].append(kill_result)
            game_cache.set(f"room:{room_id}", game_data)

    async_to_sync(GameConsumer.send_kill_result)(room_id, kill_result)


def get_vote_result(room_id):
    """
    获取投票
    """
    # TODO: bug len()
    game_cache = caches['game_cache']
    game_data = game_cache.get(f"room:{room_id}")

    # 获取玩家选择
    targets = game_data["votes"]

    vote_result_str = "投票结果："

    votes = {}
    for voter, target in targets.items():
        if target is not None:
            votes[target] = votes.get(target, 0) + 1
            vote_result_str += f"\n{voter}号玩家投给{target}号玩家。"
        else:
            vote_result_str += f"\n{voter}号玩家弃权。"

    game_data["action_history"].append({
        "all": vote_result_str
    })

    # 获取最高票数
    max_votes = max(votes.values(), default=0)

    # 获取最高票数的玩家
    players_with_max_votes = [player for player, count in votes.items() if count == max_votes]

    # 如果有多个玩家最高票数，则不放逐
    # TODO: 计算比例？
    if len(players_with_max_votes) > 1:
        pass
    else:
        if max_votes > game_data["max_players"] / 2:
            vote_result = players_with_max_votes[0]
            game_data["voted_victims_info"].append(vote_result)

    game_cache.set(f"room:{room_id}", game_data)


def check_victory(room_id):
    """
    检查游戏胜利条件
    """
    game_cache = caches['game_cache']
    game_data = game_cache.get(f"room:{room_id}")

    # 检查游戏胜利条件
    idiot_voted_out = False
    good_num = sum(1 for player in game_data["players"].values() if player["role"] != "Werewolf" and player["alive"])
    good_num += sum(
        1 for player in game_data["ai_players"].values() if player["role"] != "Werewolf" and player["alive"])
    wolf_num = sum(1 for player in game_data["players"].values() if player["role"] == "Werewolf" and player["alive"])
    wolf_num += sum(
        1 for player in game_data["ai_players"].values() if player["role"] == "Werewolf" and player["alive"])

    gods_alive = any(
        player["role"] in ["Prophet", "Witch"] and player["alive"] for player in game_data["players"].values())
    villagers_alive = any(player["role"] == "Villager" and player["alive"] for player in game_data["players"].values())

    result = {
        "end": False,
        "victory": None,
        "victory_side": None,
        "reveal_role": None
    }

    players = {**game_data["players"], **game_data["ai_players"]}

    try:
        for victim in game_data["voted_victims_info"]:
            for _, data in players.items():
                if data["index"] == victim:
                    if data["role"] == "Idiot":
                        idiot_voted_out = True
                        break

        if eval(game_data["victory_conditions"]['idiot_win'], {"voted_out": idiot_voted_out}):
            # TODO: 白痴胜利
            result["end"] = True
            result["victory"] = {
                role: False
                for role, _ in game_data["roles"].items()
            }
            result["victory"]["Idiot"] = True
            result["victory_side"] = "Idiot"
            result["reveal_role"] = {}
            for _, data in players.items():
                result["reveal_role"][data["index"]] = data["role"]
            return result
    except:
        pass
    if eval(game_data["victory_conditions"]['good_win'], {"wolf_num": wolf_num, "good_num": good_num}):
        # TODO: 好人胜利
        result["end"] = True
        result["victory"] = {
            role: False
            for role, _ in game_data["roles"].items()
        }
        result["victory"]["Villager"] = True
        result["victory"]["Prophet"] = True
        result["victory"]["Witch"] = True
        result["victory_side"] = "Good"
        result["reveal_role"] = {}
        for _, data in players.items():
            result["reveal_role"][data["index"]] = data["role"]
        return result
    if eval(game_data["victory_conditions"]['wolf_win'],
            {"wolf_num": wolf_num, "good_num": good_num, "gods_alive": gods_alive, "villagers_alive": villagers_alive}):
        result["end"] = True
        result["victory"] = {
            role: False
            for role, _ in game_data["roles"].items()
        }
        result["victory"]["Werewolf"] = True
        result["victory_side"] = "Bad"
        result["reveal_role"] = {}
        for _, data in players.items():
            result["reveal_role"][data["index"]] = data["role"]
        return result
    return result

# @with_game_data_lock(timeout=5)
def end_current_phase(room_id): # TODO: BUG
    try:
        game_cache = caches['game_cache']
        task_id = game_cache.get(f"room_{room_id}_current_task")

        # TODO: 检验是否能够按预期工作？
        app.control.revoke(task_id, terminate=True)

        game_data = game_cache.get(f"room:{room_id}")
        current_phase = game_data["current_phase"]
        print(f"{room_id}中{current_phase}阶段被提前结束。")
        handle_phase_timed_out.delay(room_id, current_phase)

    except Exception as e:
        print(f"Error in end_current_phase: {e}")


@shared_task
@with_game_data_lock(timeout=5)
def handle_phase_timed_out(room_id: str, current_phase: str):
    """
    阶段定时器
    :param room_id:
    :param current_phase: 当前阶段（函数被执行时该阶段将要结束）
    :return:
    """
    try:
        game_cache = caches['game_cache']
        game_data = game_cache.get(f"room:{room_id}")
        phase_transitions = game_data["phase_transitions"]

        if current_phase != game_data["current_phase"]:
            print(f"{room_id}中阶段转换异常！应该是{game_data['current_phase']}，而实际是{current_phase}。")

        print(f"{room_id}中{current_phase}阶段结束。")

        # 1. 获取下一个阶段
        next_phase = phase_transitions[current_phase]

        # 对于玩家发言，跳过死亡的玩家
        if next_phase.startswith("Speak_"):
            found = False
            players = {**game_data["players"], **game_data["ai_players"]}
            while next_phase != 'Vote' and not found:
                index = next_phase.split("_")[1]
                for _, data in players.items():
                    if data["index"] == str(index):
                        if not data["alive"]:
                            next_phase = phase_transitions[next_phase]
                            break
                        else:
                            found = True
                            break

        # 2. 通知当前阶段结束
        # TODO: 阶段结束，进行相应处理
        # 游戏数据应该分别在进行阶段处理的函数中更新
        if current_phase == 'Initialize':
            initialize(room_id)
            assign_roles_to_players(room_id)
        elif current_phase == 'Werewolf':
            # 结算狼人杀人
            get_kill_result(room_id)
            async_to_sync(GameConsumer.broadcast_game_update)(room_id, 'kill_phase_end', game_data)
            game_data = game_cache.get(f"room:{room_id}")
            game_data["action_history"].append({
                "all": "狼人请闭眼。"
            })
            game_cache.set(f"room:{room_id}", game_data)
        elif current_phase == 'Prophet':
            async_to_sync(GameConsumer.broadcast_game_update)(room_id, 'check_phase_end', game_data)
            game_data["action_history"].append({
                "all": "预言家请闭眼。"
            })
            game_cache.set(f"room:{room_id}", game_data)
        elif current_phase == 'Witch':
            async_to_sync(GameConsumer.broadcast_game_update)(room_id, 'witch_phase_end', game_data)
            game_data["action_history"].append({
                "all": "女巫请闭眼。"
            })
            game_cache.set(f"room:{room_id}", game_data)
        elif current_phase == 'Day':
            async_to_sync(GameConsumer.broadcast_game_update)(room_id, 'talk_phase', game_data)
            game_data["action_history"].append({
                "all": "请轮流发言。"
            })
            game_cache.set(f"room:{room_id}", game_data)
        elif current_phase.startswith("Speak_"):
            index = current_phase.split("_")[1]
            # 此处是游戏内编号！
            async_to_sync(GameConsumer.broadcast_talk_end)(room_id, index)
            if next_phase == 'Vote':
                async_to_sync(GameConsumer.broadcast_game_update)(room_id, 'talk_phase_end', game_data)
        elif current_phase == 'Vote':
            # 结算投票
            get_vote_result(room_id)
            async_to_sync(GameConsumer.broadcast_game_update)(room_id, 'vote_phase_end', game_data)
            async_to_sync(GameConsumer.broadcast_day_death_info)(room_id, game_data["voted_victims_info"])

            # 更新存活状态
            players = {**game_data["players"], **game_data["ai_players"]}
            for _, data in players.items():
                if data["index"] in game_data["voted_victims_info"]:
                    data["alive"] = False

            game_cache.set(f"room:{room_id}", game_data)

        elif current_phase.startswith('End'):
            # 结算游戏胜利
            victory_result = check_victory(room_id)
            end = victory_result["end"]
            victory = victory_result["victory"]
            victory_side = victory_result["victory_side"]
            reveal_role = victory_result["reveal_role"]
            async_to_sync(GameConsumer.broadcast_game_end)(room_id, end, victory, victory_side, reveal_role)
            if end:
                print(f"{room_id}游戏结束。")
                return
                # TODO: 清理房间数据，留一个阶段以供复盘？

        # 3. 开始下一个阶段
        next_phase_task = start_phase.delay(room_id, next_phase)

        # 4. 将task_id存入缓存，以便需要时取消
        game_cache.set(f"room_{room_id}_current_task", next_phase_task.id, timeout=3600)

        return next_phase_task.id

    except Exception as e:
        print(f"Error in phase_timer: {e}")
        # 可能需要进行错误恢复

def set_game_data(room_id, game_data):
    game_cache = caches['game_cache']
    game_cache.set(f"room:{room_id}", game_data)

@shared_task
def handle_ai_action(room_id: str, ai_id: str, phase: str, action: dict):
    """同步的 Celery 任务，用于处理 AI 动作"""
    try:
        result = async_to_sync(AIExecutor.execute_action)(room_id, ai_id, action)

        if result == "-1":
            return

        # 更新游戏状态
        game_cache = caches['game_cache']
        game_data = game_cache.get(f"room:{room_id}")

        alive_player_indices = []
        players = {**game_data["players"], **game_data["ai_players"]}

        # print(players)

        for _, data in players.items():
            if data['alive']: # TODO: BUG
                alive_player_indices.append(data['index'])

        if phase != game_data["current_phase"]:
            print(f"AI执行动作时阶段不匹配：{phase} != {game_data['current_phase']}")
            return None

        if action["type"] == "kill":
            if result not in alive_player_indices:
                print(f"AI在刀人时选择的目标不合法：{result}")
                return

            game_data['werewolves_targets'][ai_id] = result
            game_data['action_history'].append({
                game_data["ai_players"][ai_id]["index"]: f"我选择杀死 {result} 号玩家。"
            })
            async_to_sync(GameConsumer.sync_werewolf_target)(room_id, game_data['werewolves_targets'])
            print(f"{game_data['ai_players'][ai_id]['index']} 号AI {ai_id} 选择杀死 {result} 号玩家。")
        elif action["type"] == "check":
            if result not in alive_player_indices:
                print(f"AI在验人时选择的目标不合法：{result}")
                return

            role = None

            for _, data in players.items():
                if data['index'] == result:
                    role = data['role']
                    break

            game_data['action_history'].append({
                game_data["ai_players"][ai_id]["index"]: f"我选择查验 {result} 号玩家，他的角色是 {role}。"
            })
            print(f"AI {ai_id}选择查验 {result} 号玩家，他的角色是 {role}。")
        elif action["type"] == "witch":
            cure = result[0]
            poison = result[1]

            message = "今晚"
            if len(action["special_info"]["victims"]) > 1:
                message += "以下玩家死亡："
                message += ",".join(action["special_info"]["victims"])
            else:
                message += "没有人死亡"

            if cure != "-1":
                if cure not in game_data['victims_info']:
                    print(f"AI在救人时选择的目标不合法：{cure}，目标不在死亡名单中。")
                elif game_data['ai_players'][ai_id]['role_skills']['cure_count'] <= 0:
                    print(f"AI在救人时选择的目标不合法：{cure}，解药数量不足。")
                else:
                    message += f"。我选择将 {cure} 号玩家救活。\n"

                    game_data['victims_info'].remove(cure)
            else:
                message += "。我选择不救人。\n"
            if poison != "-1":
                if poison not in alive_player_indices:
                    print(f"AI在毒人时选择的目标不合法：{poison}")
                elif game_data['ai_players'][ai_id]['role_skills']['poison_count'] <= 0:
                    print(f"AI在毒人时选择的目标不合法：{poison}，毒药数量不足。")
                else:
                    if game_data["ai_players"][ai_id]["index"] != poison:
                        message += f"我选择毒死 {poison} 号玩家。"

                        game_data['poisoned_victims_info'].append(poison)
            else:
                message += "我选择不毒人。"

            game_data['action_history'].append({
                game_data["ai_players"][ai_id]["index"]: message
            })
            print(f"AI {ai_id}选择救人 {cure} 号玩家，毒人 {poison} 号玩家。")
        elif action["type"] == "speak":
            async_to_sync(GameConsumer.broadcast_talk_message)(room_id, game_data["ai_players"][ai_id]["index"], result)

            message = "我选择发言："
            message += result

            game_data['action_history'].append({
                game_data["ai_players"][ai_id]["index"]: message
            })

            end_current_phase(room_id)
        elif action["type"] == "vote":
            if result not in alive_player_indices:
                print(f"AI在投票时选择的目标不合法：{result}")
                return
            game_data['votes'][game_data["ai_players"][ai_id]["index"]] = result
            game_data['action_history'].append({
                game_data["ai_players"][ai_id]["index"]: f"我选择投票给 {result} 号玩家。"
            })

        set_game_data(room_id, game_data)
        return result
    except Exception as e:
        print(f"AI action error: {e}")
        return None

@shared_task
@with_game_data_lock(timeout=5)
def start_phase(room_id: str, phase: str):
    """
    开始一个阶段
    :param room_id:
    :param phase: 将要开始的阶段
    :return:
    """
    # TODO: 去掉注释
    # try:
    game_cache = caches['game_cache']
    game_data = game_cache.get(f"room:{room_id}")
    phase_timer = game_data["phase_timer"]

    game_data["current_phase"] = phase

    # 1. 通知阶段开始
    # TODO: 接入 AI
    action = {}
    delay = 10

    if phase == 'Werewolf':
        # 清理昨晚的数据
        game_data["victims_info"] = []
        game_data["poisoned_victims_info"] = []
        game_data["voted_victims_info"] = []
        game_data["votes"] = {}

        # 初始化狼人选择
        game_data["werewolves_targets"] = {
            data["index"]: None
            for user_id, data in game_data["players"].items() if data["role"] == "Werewolf"
        }

        # 通知狼人杀人
        async_to_sync(GameConsumer.broadcast_game_update)(room_id, 'night_phase', game_data)
        async_to_sync(GameConsumer.broadcast_game_update)(room_id, 'kill_phase', game_data)

        # 记录在对战历史中
        game_data["action_history"].append({
            "all": "天黑请闭眼。"
        })
        game_data["action_history"].append({
            "all": "狼人请睁眼。"
        })

        # 给出 AI 选择
        action["type"] = "kill"

        for ai_id, data in game_data["ai_players"].items():
            if data["role"] == "Werewolf" and data["alive"]:
                handle_ai_action.apply_async(
                    args=[room_id, ai_id, phase, action],
                    countdown=delay
                )
                delay = min(delay + 5, 40)
    elif phase == 'Prophet':
        # 通知预言家验人
        async_to_sync(GameConsumer.broadcast_game_update)(room_id, 'check_phase', game_data)

        # 记录在对战历史中
        game_data["action_history"].append({
            "all": "预言家请睁眼。"
        })
        action["type"] = "check"
        for ai_id, data in game_data["ai_players"].items():
            if data["role"] == "Prophet" and data["alive"]:
                handle_ai_action.apply_async(
                    args=[room_id, ai_id, phase, action],
                    countdown=delay
                )
                delay = min(delay + 5, 40)
    elif phase == 'Witch':
        # 通知女巫救人
        async_to_sync(GameConsumer.broadcast_game_update)(room_id, 'witch_phase', game_data)
        # 发送女巫的解药和毒药数量
        for user_id, data in game_data["players"].items():
            if data["role"] == "Witch" and data["alive"]:
                cure_count = data["role_skills"]["cure_count"]
                poison_count = data["role_skills"]["poison_count"]
                cure_target = game_data["victims_info"]
                async_to_sync(GameConsumer.send_witch_info)(room_id, user_id, cure_count, poison_count, cure_target)

        game_data["action_history"].append({
            "all": "女巫请睁眼。"
        })

        victim_indices = game_data["victims_info"]
        alive_indices = []
        players = {**game_data["players"], **game_data["ai_players"]}

        for _, data in players.items():
            if data['alive']:
                alive_indices.append(data['index'])

        action["type"] = "witch"
        for ai_id, data in game_data["ai_players"].items():
            if data["role"] == "Witch":
                special_info = {"cure": game_data["ai_players"][ai_id]["role_skills"]["cure_count"],
                                "poison": game_data["ai_players"][ai_id]["role_skills"]["poison_count"],
                                "victims": victim_indices, "targets": alive_indices}
                action["special_info"] = special_info
                handle_ai_action.apply_async(
                    args=[room_id, ai_id, phase, action],
                    countdown=delay
                )
                delay = min(delay + 5, 40)
    elif phase == 'Day':
        # 结算昨晚的结果
        victims = game_data["victims_info"] + game_data["poisoned_victims_info"]
        # 按序号排序
        victims.sort(key=int)

        # 更新存活状态
        players = {**game_data["players"], **game_data["ai_players"]}
        for _, data in players.items():
            if data["index"] in victims:
                data["alive"] = False

        # 通知天亮
        async_to_sync(GameConsumer.broadcast_game_update)(room_id, 'day_phase', game_data)

        async_to_sync(GameConsumer.broadcast_night_death_info)(room_id, victims)
        # 记录在对战历史中
        # TODO: 确定对战历史的数据结构
        if victims:
            victims_str = "、".join(victims)
            game_data["action_history"].append({
                "all": f"天亮了，昨晚序号为{victims_str}的玩家死亡。"
            })
        else:
            game_data["action_history"].append({
                "all": "天亮了，昨晚是平安夜。"
            })
    elif phase.startswith("Speak_"):
        index = phase.split("_")[1]
        # 此处是游戏内编号！
        async_to_sync(GameConsumer.broadcast_talk_start)(room_id, index)
        if int(index) - len(game_data["players"]) > 0:
            action["type"] = "speak"
            for ai_id, data in game_data["ai_players"].items():
                if data["index"] == index:
                    handle_ai_action.apply_async(
                        args=[room_id, ai_id, phase, action],
                        countdown=delay
                    )
    elif phase == "Vote":
        # 通知投票
        async_to_sync(GameConsumer.broadcast_game_update)(room_id, 'vote_phase', game_data)
        action["type"] = "vote"

        for ai_id, data in game_data["ai_players"].items():
            if data["alive"]:
                handle_ai_action.apply_async(
                    args=[room_id, ai_id, phase, action],
                    countdown=delay
                )
                delay = min(delay + 3, 40)

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
    game_cache.set(f"room:{room_id}", game_data)

    # 3. 存储当前task_id
    game_cache.set(f"room_{room_id}_current_task", timer_task.id, timeout=3600)

    return timer_task.id

    # except Exception as e:
    #     print(f"Error in start_phase: {e}")


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
