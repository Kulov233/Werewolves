# game/ai/ai_executor.py
from asgiref.sync import sync_to_async
from django.core.cache import caches
from .ai import AIPlayer

class AIExecutor:
    """AI执行器，不保存状态，每次行动时重新组装"""

    @staticmethod
    async def execute_action(room_id: str, ai_id: str, action: dict):
        """
        执行AI动作
        :param room_id: 房间ID
        :param ai_id: AI玩家UUID
        :param action: 动作类型（kill/check/vote等）及其附加信息
        :return: AI的选择结果
        """
        game_cache = caches['game_cache']
        game_data = game_cache.get(f"room:{room_id}")

        role_translations = {
            "Werewolf": "狼人",
            "Villager": "平民",
            "Prophet": "预言家",
            "Witch": "女巫",
            "Idiot": "白痴"
        }

        # 创建临时AI实例
        ai_player = AIPlayer(
            name=game_data['ai_players'][ai_id]['name'],
            output_limit=100,
            identity=role_translations[game_data['ai_players'][ai_id]['role']],
            game_specified_prompt=game_data['game_specified_prompt']
        )

        # ai_player.set_character(role_translations[game_data['ai_players'][ai_id]['role']])
        ai_player.set_index(game_data['ai_players'][ai_id]['index'])

        players = {**game_data["players"], **game_data["ai_players"]}
        alive_players = [data["index"] for _, data in players.items() if data['alive']]

        if game_data['ai_players'][ai_id]['role'] == "Werewolf":
            wolf_indices = [data["index"] for _, data in players.items() if data['role'] == "Werewolf"]
            mes = "狼人玩家的编号分别是："
            mes += ",".join(wolf_indices)
            message = {
                "type": "info_team",
                "content": mes
            }
            ai_player.recv(message, alive_players)

        messages = []
        # 组装历史记录
        for message in game_data['action_history']:
            for receiver, content in message.items():
                if (receiver == game_data['ai_players'][ai_id]['index'] or receiver == "all")\
                        or (game_data['ai_players'][ai_id]['role'] == receiver):
                    messages.append(content)

        # 设置AI的基本信息
        ai_player.set_messages(messages)
        ai_player.set_index(game_data['ai_players'][ai_id]['index'])

        result = None

        # 根据动作类型执行
        if action["type"] == "kill":
            message = {
                "type": "kill"
            }
            result = await sync_to_async(ai_player.recv)(message, alive_players)
        elif action["type"] == "check":
            message = {
                "type": "check"
            }
            result = await sync_to_async(ai_player.recv)(message, alive_players)
        elif action["type"] == "witch":
            message = {
                "type": "witch"
            }
            result = await sync_to_async(ai_player.recv)(message, alive_players)
        elif action["type"] == "speak":
            message = {
                "type": "speak"
            }
            result = await sync_to_async(ai_player.recv)(message, alive_players)
        elif action["type"] == "vote":
            message = {
                "type": "vote",
                "special_info": action["special_info"]
            }
            result = await sync_to_async(ai_player.recv)(message, alive_players)

        return result