import random
from player import Player, Werewolf, Villager, Prophet, Witch, role_translations
from message import Message, send_message, get_input_from_player
from ai import AIPlayer
from tools import dispatch_tool
from typing import List
import json

class WerewolfGame:
    #初始化游戏，定义游戏人数，获取角色卡数量和获胜条件
    def __init__(self, total_players: int, human_num=1, ai_num=3):
        with open('game_config.json', 'r') as file:
            configs = json.load(file)
            if str(total_players) in configs:
                game_config = configs[str(total_players)]
            else:
                raise ValueError("No configuration available for the given number of players.")
        self.total_players = total_players
        self.human_num = human_num
        self.ai_num = ai_num
        self.players: List[Player] = []

        self.night_count: int = 1

        self.role_classes = self.assign_roles_from_config(game_config['roles'])
        self.victory_conditions = game_config['victory_conditions']

        self.ai_players = []

    #从json中读取角色卡
    def assign_roles_from_config(self, roles: List[str]) -> List[type]:
        role_map = {
            "Villager": Villager,
            "Werewolf": Werewolf,
            "Prophet": Prophet,
            "Witch": Witch
        }
        return [role_map[role] for role in roles]
    
    #获取玩家名字
    def get_player_names(self) -> None:
        for i in range(self.total_players):
            while True:
                if i < self.human_num:
                    player_name = input(f"请输入你的名字: ")
                else:
                    player_name = f"AI_Player_{i+1}"
                if player_name in [player.name for player in self.players]:
                    print("玩家名字重复，请重新输入")
                    continue
                if not player_name:
                    print("玩家名字不能为空，请重新输入")
                    continue
                player = Player(player_name, index=i+1)
                player.is_human = True if i < self.human_num else False
                self.players.append(player)
                break

    #随机分配角色
    def assign_roles_to_players(self) -> None:
        random.shuffle(self.role_classes)
        for i, player in enumerate(self.players):
            role_class = self.role_classes[i]
            new_player = role_class(player.name, player.index)
            new_player.is_human = player.is_human
            self.players[i] = new_player

    #告诉玩家角色
    def notify_players_of_roles(self) -> None:
        for player in self.players:
            if not player.is_human:
                ai_player = AIPlayer(name=player.name, identity=role_translations[player.__class__.__name__])
                self.ai_players.append(ai_player)
                player.set_ai(ai_player)
            # 组装消息，通知玩家他们的角色
            content = f"你的角色是：{role_translations[player.__class__.__name__]}"
            mes = Message(content=content, message_type='info', recipients=player)
            # 发送消息
            send_message(mes, self.players)

    def setup_players(self) -> None:
        self.get_player_names()
        self.assign_roles_to_players()
        self.notify_players_of_roles()
        # 显示所有玩家（调试用）
        print("\n游戏角色分配完毕：")
        for player in self.players:
            print(f"{player.index}. {player}")
    

    def get_alive_players(self):
        return [player for player in self.players if player.is_alive]

    def night_phase(self):
        content = f"\n--- 夜晚 {self.night_count} ---\n天黑请闭眼，狼人请睁眼："
        mes = Message(content=content, message_type='info', recipients='all')
        send_message(mes, self.players)
        victim = None
        poisoned_victim = None

        # 狼人选择猎杀目标
        wolves = [player for player in self.players if isinstance(player, Werewolf) and player.is_alive]
        if wolves:
            alive_players = self.get_alive_players()

            human_wolves = [wolf for wolf in wolves if wolf.is_human]
            ai_wolves = [wolf for wolf in wolves if not wolf.is_human]

            wolf_indices = [wolf.index for wolf in wolves]
            alive_player_indices = [player.index for player in alive_players]
            alive_player_dict = {player.index: player for player in alive_players}

            wolf_names = [wolf.name for wolf in wolves]
            alive_player_names = [player.name for player in self.get_alive_players()]
        
            consensus_target_index = None
            if human_wolves:
                human_decisions = []
                while True:
                    for wolf in human_wolves:
                        prompt = f"{wolf.name}，请选择今晚要猎杀的目标(请给出序号而非名字)：\n" + \
                                "\n".join(f"{player.index}. {player.name}" for player in self.get_alive_players())
                        mes = Message(content=prompt, message_type='action_request', recipients=wolf, expect_reply=True)
                        response = send_message(mes, self.players)
                        victim_index = int(response.get(wolf.name))
                        if victim_index in alive_player_indices:
                            human_decisions.append(victim_index)

                    # 检查真人玩家的决策是否一致
                    if len(set(human_decisions)) > 1:
                        prompt = "狼人之间的选择不一致，请重新选择"
                        continue

                    # 一致的决定
                    consensus_target_index = human_decisions[0] if human_decisions else None
                    break
                
                # 将一致的决定传递给AI狼人，并获取他们的同意
                if consensus_target_index:
                    for wolf in ai_wolves:
                        prompt = f"真人玩家已选择猎杀目标为 {consensus_target_index}，请选择"
                        mes = Message(content=prompt, message_type='action_request', recipients=wolf, expect_reply=True)
                        response = send_message(mes, self.players)
                        #AI逻辑
                        if response[wolf.name].lower() != "yes":
                            print(f"{wolf.name} 不同意，需要重新协商")
                            return self.night_phase()

            if not human_wolves or not consensus_target_index:
                #测试用
                tool_params = json.dumps({
                    "wolf_indexs": wolf_indices,
                    "alive_player_indexs": alive_player_indices
                })
                consensus_target_index = int(dispatch_tool("wolf_kill", tool_params, session_id="wolf_group"))

                """ 不知道符不符合tools的传递规范，具体的tools如何处理的逻辑要改send_message
                tool_params = {
                    "wolf_names": wolf_names,
                    "alive_player_names": alive_player_names
                }
                # 构建发送给AI狼人的消息，包括调用工具的参数
                wolf_decisions = []
                while True:
                    for wolf in ai_wolves:
                        prompt = f"请根据存活玩家序号选择猎杀目标：\n" + \
                            "\n".join(f"{player.index}. {player.name} {'(狼人)' if self.players.index(player) + 1 in wolf_indices else ''}" 
                                    for player in alive_players)
                        mes = Message(content=prompt, message_type='tool_request', recipients=wolf, expect_reply=True, tools_functions=[tool_params])
                        response = send_message(mes, [wolf])
                        victim_index = int(response)
                        if victim_index in alive_player_indices:
                            wolf_decisions.append(victim_index)

                        # 检查狼人玩家的决策是否一致
                        if len(set(wolf_decisions)) > 1:
                            continue

                        # 一致的决定
                        consensus_target_index = wolf_decisions[0] if wolf_decisions else None
                        break"""
                #TODO:确保AI狼人杀一个人，若AI狼人返回是一个序号可以直接使用上述判断
            # 确定并执行猎杀
            victim = alive_player_dict.get(consensus_target_index)

        

        # 预言家查验身份
        content = "狼人请闭眼，预言家请睁眼："
        mes = Message(content=content, message_type='info', recipients='all')
        send_message(mes, self.players)
        prophets = [player for player in self.players if isinstance(player, Prophet) and player.is_alive]
        if prophets:
            for prophet in prophets:
                alive_players = self.get_alive_players()
                alive_player_indices = [player.index for player in alive_players]
                alive_player_dict = {player.index: player for player in alive_players}
            
                if prophet.is_human:
                    # 人类预言家选择要查验的玩家
                    prompt = f"{prophet.index}号 {prophet.name}，请选择要查验的玩家（输入序号）：\n"
                    options = [f"{p.index}. {p.name}" for p in alive_players if p != prophet]
                    prompt += "\n".join(options)
                    mes = Message(content=prompt, message_type='action_request', recipients=prophet, expect_reply=True)
                    response = send_message(mes, self.players)
                    player_reply = response.get(prophet.name)
                    if player_reply and player_reply.isdigit():
                        target_index = int(player_reply)
                        target_player = alive_player_dict.get(target_index)
                        if target_player:
                            # 发送查验结果给预言家
                            role_info = "好人" if not isinstance(target_player, Werewolf) else "狼人"
                            result = f"{target_player.index}号玩家 {target_player.name} 的身份是 {role_info}"
                            mes = Message(content=result, message_type='info', recipients=prophet)
                            send_message(mes, self.players)
                else:
                    # AI预言家
                    # 准备工具参数
                    tool_params = {
                        "seer_index": prophet.index,
                        "alive_player_indices": alive_player_indices,
                        "player_roles": {p.index: ("好人" if not isinstance(p, Werewolf) else "狼人") for p in self.players}
                    }
                    # 发送工具请求给 AI 预言家
                    prompt = f"{prophet.index}号 {prophet.name}，请选择要查验的玩家（输入序号）："
                    mes = Message(content=prompt, message_type='tool_request', recipients=prophet, expect_reply=True, tools_functions=[tool_params])
                    response = send_message(mes, self.players)
                    if response and response.isdigit():
                        target_index = int(response)
                        target_player = alive_player_dict.get(target_index)
                        if target_player:
                            # 发送查验结果给 AI 预言家
                            role_info = "好人" if not isinstance(target_player, Werewolf) else "狼人"
                            result = f"{target_player.index}号玩家 {target_player.name} 的身份是 {role_info}"
                            mes = Message(content=result, message_type='info', recipients=prophet)
                            send_message(mes, self.players)

        # 女巫行动
        content = "预言家请闭眼，女巫请睁眼："
        mes = Message(content=content, message_type='info', recipients='all')
        send_message(mes, self.players)
        witches = [player for player in self.players if isinstance(player, Witch) and player.is_alive]

        if witches:
            for witch in witches:
                alive_players = self.get_alive_players()
                alive_player_indices = [player.index for player in alive_players]
                alive_player_dict = {player.index: player for player in alive_players}

                # 女巫有两个可能的行动：救人和毒人
                # 首先，女巫是否要救被狼人杀的玩家
                if witch.is_human:
                    # 人类女巫
                    if witch.has_healing_potion and victim:
                        prompt = f"今晚 {victim.index}号玩家 {victim.name} 遭到了袭击，你是否要使用解药？(yes/no)"
                        mes = Message(content=prompt, message_type='action_request', recipients=witch, expect_reply=True)
                        response = send_message(mes, self.players)
                        player_reply = response.get(witch.name)
                        if player_reply and player_reply.lower() == "yes":
                            witch.use_healing_potion()
                            victim = None  # 被救活
                    # 接下来，女巫是否要毒人
                    if witch.has_poison_potion:
                        prompt = "你是否要使用毒药？(yes/no)"
                        mes = Message(content=prompt, message_type='action_request', recipients=witch, expect_reply=True)
                        response = send_message(mes, self.players)
                        player_reply = response.get(witch.name)
                        if player_reply and player_reply.lower() == "yes":
                            # 选择要毒杀的玩家
                            prompt = "请选择要毒杀的玩家（输入序号）：\n" + \
                                    "\n".join(f"{p.index}. {p.name}" for p in alive_players if p != witch)
                            mes = Message(content=prompt, message_type='action_request', recipients=witch, expect_reply=True)
                            response = send_message(mes, self.players)
                            player_reply = response.get(witch.name)
                            if player_reply and player_reply.isdigit():
                                target_index = int(player_reply)
                                poisoned_victim = alive_player_dict.get(target_index)
                                if poisoned_victim and poisoned_victim != witch:
                                    witch.use_poison_potion()
                else:
                    # AI女巫
                    # 准备工具参数
                    tool_params = {
                        "witch_index": witch.index,
                        "victim_index": victim.index if victim else None,
                        "has_healing_potion": witch.has_healing_potion,
                        "has_poison_potion": witch.has_poison_potion,
                        "alive_player_indices": alive_player_indices,
                    }
                    # 发送工具请求给 AI 女巫
                    prompt = "女巫行动，请决策你的行动。"
                    mes = Message(content=prompt, message_type='tool_request', recipients=witch, expect_reply=True, tools_functions=[tool_params])
                    response = send_message(mes, self.players)
                    # 解析 AI 女巫的决策
                    # 假设 response 是一个 JSON 字符串，包含 'heal' 和 'poison' 的决策
                    if response:
                        try:
                            action = json.loads(response.get(witch.name))
                            if action.get('heal') and witch.has_healing_potion and victim:
                                witch.use_healing_potion()
                                victim = None
                            if action.get('poison') and witch.has_poison_potion:
                                target_index = action.get('poison')
                                poisoned_victim = alive_player_dict.get(target_index)
                                if poisoned_victim and poisoned_victim != witch:
                                    witch.use_poison_potion()
                        except json.JSONDecodeError:
                            print("AI女巫的行动响应解析失败")

        # 公布夜晚结果
        content = "女巫请闭眼，天亮了。"
        mes = Message(content=content, message_type='info', recipients='all')
        send_message(mes, self.players)

        if victim and victim.is_alive:
            victim.is_alive = False
            content = f"{victim.name} 死了"
            mes = Message(content=content, message_type='info', recipients='all')
            send_message(mes, self.players)
        if poisoned_victim and poisoned_victim.is_alive:
            poisoned_victim.is_alive = False
            content = f"{poisoned_victim.name} 被毒杀"
            mes = Message(content=content, message_type='info', recipients='all')
            send_message(mes, self.players)
        if not victim and not poisoned_victim:
            content = "昨晚是平安夜"
            mes = Message(content=content, message_type='info', recipients='all')
            send_message(mes, self.players)

        self.night_count += 1

    def day_phase(self):
        content = "\n--- 白天 ---\n天亮了，现在开始发言。"
        mes = Message(content=content, message_type='info', recipients='all')
        send_message(mes, self.players)

        # 玩家发言
        for player in self.get_alive_players():
            # 向当前玩家发送消息请求发言
            prompt = f"{player.index}号 {player.name}，请发表您的观点："
            request_message = Message(content=prompt, message_type='action_request', recipients=player, expect_reply=True)
            response = send_message(request_message, self.players)
            speech = response.get(player.name)

             # 将获取的发言广播给其他所有玩家包括自身
            for other_player in self.players:
                inform_message = Message(content=f"{player.index}号 {player.name}说：{speech}", message_type='info', recipients=other_player)
                send_message(inform_message, self.players) # 发送消息给每个其他玩家

        # 投票阶段
        votes = {player.index: 0 for player in self.get_alive_players()}
        alive_players = self.get_alive_players()
        for player in self.get_alive_players():
            if player.is_human:
                vote_prompt = f"{player.index}号 {player.name}，请选择要投票放逐的玩家（输入序号）：\n"
                for p in self.get_alive_players():
                    vote_prompt += f"{p.index}. {p.name}\n"
                while True:
                    request_message = Message(content=vote_prompt, message_type='action_request', recipients=player, expect_reply=True)
                    response = send_message(request_message, self.players)
                    player_reply = response.get(player.name)
                    if not player_reply.isdigit():
                        vote_prompt = "输入序号无效，请重新输入：\n"
                        continue
                    vote_index = int(player_reply)
                    voted_player = next((p for p in alive_players if p.index == vote_index), None)
                    if not voted_player :
                        vote_prompt = "输入序号超出范围，请重新输入：\n"
                        continue
                    votes[voted_player.index] += 1
                    break
            else:
                # AI玩家投票
                alive_player_indices = [player.index for player in alive_players]

                tool_params = json.dumps({
                    "player_index": player.index,
                    "alive_player_indexs": alive_player_indices
                })
                session_id = f"vote_session_{player.index}"  # 为 AI 玩家生成唯一的 session_id
                try:
                    # 调用工具，确保返回的值是可解析的数字
                    vote_index = dispatch_tool("vote_exile", tool_params, session_id=session_id)
                    voted_player = next((p for p in alive_players if p.index == vote_index), None)
                except (ValueError, TypeError):
                    print(f"AI玩家 {player.name} 投票返回了无效值")
                
                #测试用
                print(f"AI玩家 {player.name} 投了{vote_index}")
                if voted_player:
                    votes[voted_player.index] += 1



                """ 不知道符不符合tools的传递规范，具体的tools如何处理的逻辑要改send_message
                tool_params = {
                    "player_name": player.index,
                    "alive_player_names": alive_player_indices
                }
                # 构建发送给AI狼人的消息，包括调用工具的参数
                prompt = f"请根据存活玩家序号选择投票：\n" + \
                    "\n".join(f"{index + 1}. {player.name} {'(狼人)' if self.players.index(player) + 1 in wolf_indices else ''}" 
                            for index, player in alive_players)
                mes = Message(content=prompt, message_type='tool_request', recipients=wolf, expect_reply=True, tools_functions=[tool_params])
                response = send_message(mes, [wolf])
                voted_index = int(response[wolf.name])
                voted_player = next((p for p in alive_players if p.index == vote_index), None)
                if voted_player:
                    votes[voted_player.index] += 1
                """

        # 确定被放逐的玩家
        max_votes = max(votes.values())
        max_voted_indices = [index for index, count in votes.items() if count == max_votes]
        if len(max_voted_indices) == 1:
            exiled_player = next(player for player in self.get_alive_players() if player.index  == max_voted_indices[0])
            if exiled_player:
                exiled_player.is_alive = False
                content = f"{exiled_player.index}号 {exiled_player.name} 被放逐了。"
                mes = Message(content=content, message_type='info', recipients='all')
                send_message(mes, self.players)
        else:
            content = "投票结果出现平票，没有人被放逐。"
            mes = Message(content=content, message_type='info', recipients='all')
            send_message(mes, self.players)

    def check_victory(self) -> bool:
        good_num = sum(1 for p in self.get_alive_players() if not isinstance(p, Werewolf))
        wolf_num = sum(1 for p in self.get_alive_players() if isinstance(p, Werewolf))

        gods_alive = any(isinstance(p, (Prophet, Witch)) for p in self.get_alive_players() if p.is_alive)
        villagers_alive = any(isinstance(p, Villager) for p in self.get_alive_players() if p.is_alive)

        if eval(self.victory_conditions['good_win'], {"wolf_num": wolf_num, "good_num": good_num}):
            print("好人阵营获胜")
            return True
        if eval(self.victory_conditions['wolf_win'], {"wolf_num": wolf_num, "good_num": good_num, "gods_alive": gods_alive, "villagers_alive": villagers_alive}):
            print("狼人阵营获胜")
            return True
        return False


    def play(self):
        self.setup_players()
        while True:
            self.night_phase()
            if self.check_victory():
                break
            self.day_phase()
            if self.check_victory():
                break
