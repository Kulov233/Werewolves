import random
from player import Player, Werewolf, Villager, Prophet, Witch, Idiot, role_translations
from message import Message, send_message
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
        self.game_specified_prompt = ""

        self.night_count: int = 1

        # 死亡人员及原因
        self.victims_info = []
        self.poisoned_victims_info = []
        self.voted_victims_info = []

        self.role_classes = self.assign_roles_from_config(game_config['roles'])
        self.victory_conditions = game_config['victory_conditions']
        # 获取女巫的解药和毒药数量
        self.witch_config = game_config.get('witch_items', {'cure_count': 1, 'poison_count': 1})
        try:
            self.roles_for_humans_first = self.assign_roles_from_config(game_config["roles_for_humans_first"])  # 优先真人玩家分配的角色
        except:
            self.roles_for_humans_first = None

        self.ai_players = []

    #从json中读取角色卡
    def assign_roles_from_config(self, roles: List[str]) -> List[type]:
        role_map = {
            "Villager": Villager,
            "Werewolf": Werewolf,
            "Prophet": Prophet,
            "Witch": Witch,
            "Idiot": Idiot
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
                self.players. append(player)
                break

    #随机分配角色
    def assign_roles_to_players(self) -> None:
        """
        随机分配角色，优先分配限定角色给真人玩家，限定角色分配完后再分配剩余角色
        :return:
        """
        roles_assigned = []
        remaining_roles = self.role_classes.copy()
        if self.roles_for_humans_first:
            # 1. 定义优先分配给真人玩家的角色
            roles_for_humans_first = self.roles_for_humans_first.copy()

            # 2. 获取真人玩家和 AI 玩家
            human_players = [player for player in self.players if player.is_human]
            ai_players = [player for player in self.players if not player.is_human]

            # 3. 打乱所有角色列表，准备后续分配
            random.shuffle(roles_for_humans_first) 

            # 4. 分配限定角色给真人玩家

            # 给真人玩家优先分配限定角色
            for role_class in roles_for_humans_first:
                if human_players:
                    player = human_players.pop(0)  # 从真人玩家中选一个
                    if role_class == Witch:
                        # 对于女巫角色，设置解药和毒药数量
                        cure_count = self.witch_config['cure_count']
                        poison_count = self.witch_config['poison_count']
                        new_player = role_class(player.name, player.index, cure_count, poison_count)
                    else:
                        new_player = role_class(player.name, player.index)
                    new_player.is_human = player.is_human
                    roles_assigned.append(new_player)
                    remaining_roles.remove(role_class)  # 从剩余角色中移除该角色
                else:
                    # 如果没有足够的真人玩家，剩余的限定角色分配给 AI 玩家
                    if ai_players:
                        player = ai_players.pop(0)  # 从 AI 玩家中选一个
                        if role_class == Witch:
                            # 对于女巫角色，设置解药和毒药数量
                            cure_count = self.witch_config['cure_count']
                            poison_count = self.witch_config['poison_count']
                            new_player = role_class(player.name, player.index, cure_count, poison_count)
                        else:
                            new_player = role_class(player.name, player.index)
                        new_player.is_human = player.is_human
                        roles_assigned.append(new_player)
                        remaining_roles.remove(role_class)  # 从剩余角色中移除该角色

        
        print("剩余角色：", remaining_roles)# 调试用
        random.shuffle(remaining_roles)  # 随机打乱剩余角色

        # 剩余的玩家，包括没有获得限定角色的真人玩家和所有 AI 玩家
        remaining_players = human_players + ai_players

        # 给剩余的玩家分配剩余的角色
        for role_class, player in zip(remaining_roles, remaining_players):
            if role_class == Witch:
                # 对于女巫角色，设置解药和毒药数量
                cure_count = self.witch_config['cure_count']
                poison_count = self.witch_config['poison_count']
                new_player = role_class(player.name, player.index, cure_count, poison_count)
            else:
                new_player = role_class(player.name, player.index)
            new_player.is_human = player.is_human
            roles_assigned.append(new_player)

        # 5. 更新玩家列表
        self.players = roles_assigned

    #告诉玩家角色
    def notify_players_of_roles(self) -> None:
        # 储存狼人队友
        werewolves = []

        for player in self.players:
            if not player.is_human:
                ai_player = AIPlayer(name=player.name, identity=role_translations[player.__class__.__name__])
                self.ai_players.append(ai_player)
                player.set_ai(ai_player)
            # 组装消息，通知玩家他们的角色
            if isinstance(player, Witch):
                # 如果玩家是女巫，附加解药和毒药数量
                content = f"你的角色是：{role_translations[player.__class__.__name__]}，解药数量：{player.cure_count}，毒药数量：{player.poison_count}"
            else:
                # 对于其他角色，直接显示角色名称
                content = f"你的角色是：{role_translations[player.__class__.__name__]}"
            mes = Message(content=content, type="info", recipients=player)
            # 发送消息
            send_message(mes, self.players)

            #处理狼人角色的特殊通知
            if isinstance(player, Werewolf):
                werewolves.append(player)  # 将狼人加入狼人队列
            
        for werewolf in werewolves:
            # 获取该狼人队友的信息
            werewolf_team_members = [p for p in werewolves if p != werewolf]  # 排除自己
            werewolf_team_indices = [p.index for p in werewolf_team_members]  # 获取队友的索引
            werewolf_content = f"你的狼人队友是：{', '.join(str(i) for i in werewolf_team_indices)}"
            mes = Message(content=werewolf_content, type="info_team", recipients=werewolf)
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
        mes = Message(content=content, type='info', recipients='all')
        send_message(mes, self.players)
        # 今晚死的玩家
        victims = []
        poisoned_victims = []
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

                # 构建发送给AI狼人的消息，包括调用工具的参数
                wolf_decisions = []
                #给出ai建议
                if ai_wolves:
                    #询问ai建议
                    for wolf in ai_wolves:
                        prompt = f"请根据存活玩家序号选择猎杀目标：\n" + \
                            "\n".join(f"{player.index}. {player.name} {'(狼人)' if self.players.index(player) + 1 in wolf_indices else ''}" 
                                    for player in alive_players)
                        mes = Message(content=prompt, type="kill", recipients=wolf, expect_reply=True)
                        response = send_message(mes, self.players, alive_players)
                        victim_index = int(response[wolf.index])
                        if victim_index in alive_player_indices:
                            wolf_decisions.append(victim_index)

                    #向真人传递ai建议
                    conflict_details = "\n".join(f"狼人{ai_wolves[i].name}选择了{wolf_decisions[i]}号玩家" for i in range(len(ai_wolves)))
                    prompt = f"当前选择情况：\n{conflict_details}"
    
                    for wolf in human_wolves:
                        mes = Message(content=prompt, type="info", recipients=wolf)
                        response = send_message(mes, self.players)

                human_decisions = []
                while True:
                    for wolf in human_wolves:
                        prompt = f"请根据存活玩家序号选择猎杀目标：\n" + \
                            "\n".join(f"{player.index}. {player.name} {'(狼人)' if self.players.index(player) + 1 in wolf_indices else ''}" 
                                    for player in alive_players)
                        mes = Message(content=prompt, type="kill", recipients=wolf, expect_reply=True)
                        response = send_message(mes, self.players)
                        victim_index = int(response.get(wolf.index))
                        if victim_index in alive_player_indices:
                            human_decisions.append(victim_index)

                    # 检查真人玩家的决策是否一致
                    if len(set(human_decisions)) > 1:
                        prompt = "狼人之间的选择不一致，请重新选择"
                        # TODO:这里给人类玩家发一条信息
                        continue

                    # 一致的决定
                    consensus_target_index = human_decisions[0] if human_decisions else None
                    break
                
                # 将一致的决定传递给AI狼人，通知他们而不要求其返回决定
                if consensus_target_index:
                    for wolf in ai_wolves:
                        prompt = f"真人玩家已选择猎杀目标为 {consensus_target_index}"
                        mes = Message(content=prompt, type="info", recipients=wolf)
                        response = send_message(mes, self.players)


            if not human_wolves:

                # 构建发送给AI狼人的消息，包括调用工具的参数
                wolf_decisions = []
                while True:
                    for wolf in ai_wolves:
                        prompt = f"请根据存活玩家序号选择猎杀目标：\n" + \
                            "\n".join(f"{player.index}. {player.name} {'(狼人)' if self.players.index(player) + 1 in wolf_indices else ''}" 
                                    for player in alive_players)
                        mes = Message(content=prompt, type="kill", recipients=wolf, expect_reply=True)
                        response = send_message(mes, self.players, alive_players)
                        victim_index = int(response[wolf.index])
                        if victim_index in alive_player_indices:
                            wolf_decisions.append(victim_index)
                    
                    # 检查狼人玩家的决策是否一致
                    if len(set(wolf_decisions)) > 1:
                        # 如果狼人们的决策不一致，展示不同狼人选择的目标并让他们重新选择
                        conflict_details = "\n".join(f"狼人{ai_wolves[i].name}选择了{wolf_decisions[i]}号玩家" for i in range(len(ai_wolves)))
                        prompt = f"当前狼人选择的猎杀目标不一致，请根据存活玩家序号再次选择猎杀目标。\n\n" \
                                f"当前选择情况：\n{conflict_details}\n\n请重新选择猎杀目标：\n" + \
                                "\n".join(f"{player.index}. {player.name} {'(狼人)' if self.players.index(player) + 1 in wolf_indices else ''}" 
                                        for player in alive_players)
                        
                        # 清空第一次选择的结果，准备记录第二次选择
                        wolf_decisions.clear()

                        # 再次发送消息让狼人重新选择
                        for wolf in ai_wolves:
                            mes = Message(content=prompt, type="kill", recipients=wolf, expect_reply=True)
                            response = send_message(mes, self.players, alive_players)
                            victim_index = int(response[wolf.index])
                            if victim_index in alive_player_indices:
                                wolf_decisions.append(victim_index)

                        # 第二次不一致，则按多数票决定
                        if len(set(wolf_decisions)) > 1:
                            # 少数服从多数
                            from collections import Counter
                            decision_counts = Counter(wolf_decisions)
                            # 获取出现次数最多的票数
                            max_count = decision_counts.most_common(1)[0][1]

                            # 获取所有票数等于最大票数的目标
                            consensus_targets = [target for target, count in decision_counts.items() if count == max_count]

                            # 如果有多个平票目标，随机选择一个
                            import random
                            consensus_target_index = random.choice(consensus_targets)

                            break
                        else:
                            # 所有狼人一致决定
                            consensus_target_index = wolf_decisions[0] if wolf_decisions else None
                            break
                    else:
                        # 所有狼人一致决定
                        consensus_target_index = wolf_decisions[0] if wolf_decisions else None
                        break

            #告知狼人猎杀目标
            for wolf in wolves:
                prompt = f"狼人已选择猎杀目标为 {consensus_target_index}"
                mes = Message(content=prompt, type="info", recipients=wolf)
                response = send_message(mes, self.players)
            
            # 确定并执行猎杀
            victim = alive_player_dict.get(consensus_target_index)
            victims.append(victim)  # 将死亡人员加入 victims 列表
            
        
        # 预言家查验身份
        # TODO: 如果看起来好搞的话，可以照着狼人的实现把预言家和女巫改了。不用管ai那边的prompt，我来处理。 --hts
        content = "狼人请闭眼，预言家请睁眼："
        mes = Message(content=content, type='info', recipients='all')
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
                    options = [f"{p.index}. {p.name}" for p in alive_players if p != prophet]  # 过滤掉预言家自己
                    prompt += "\n".join(options)
                    mes = Message(content=prompt, type='check', recipients=prophet, expect_reply=True)
                    response = send_message(mes, self.players)

                    while True:
                        player_reply = response.get(prophet.index)
                        
                        if player_reply and player_reply.isdigit():
                            target_index = int(player_reply)
                            target_player = alive_player_dict.get(target_index)
                            
                            if target_player and target_player != prophet:  # 确保不是选择自己
                                # 发送查验结果给预言家
                                role_info = "好人" if not isinstance(target_player, Werewolf) else "狼人"
                                result = f"{target_player.index}号玩家 {target_player.name} 的身份是 {role_info}"
                                mes = Message(content=result, type='info', recipients=prophet)
                                send_message(mes, self.players)
                                break  # 跳出循环，结束查验
                            else:
                                # 如果选择的是预言家自己，或无效玩家
                                prompt = "无效的选择，请重新输入一个有效的存活玩家序号："
                                mes = Message(content=prompt, type='check', recipients=prophet, expect_reply=True)
                                response = send_message(mes, self.players)
                        else:
                            # 如果输入无效（非数字）
                            prompt = "输入无效，请重新输入一个有效的玩家序号："
                            mes = Message(content=prompt, type='check', recipients=prophet, expect_reply=True)
                            response = send_message(mes, self.players)

                else:
                    # 让 AI 预言家选择check目标
                    prompt = f"{prophet.index}号 {prophet.name}，请选择要查验的玩家（输入序号）：\n"
                    options = [f"{p.index}. {p.name}" for p in alive_players if p != prophet]
                    prompt += "\n".join(options)
                    mes = Message(content=prompt, type='check', recipients=prophet, expect_reply=True)
                    response = send_message(mes, self.players, alive_players)
                    AI_reply = response.get(prophet.index)
                    if AI_reply:
                        if isinstance(AI_reply, str) and AI_reply.isdigit():
                            # 如果 AI_reply 是字符串且是数字，进行相应处理
                            target_index = int(AI_reply)
                        elif isinstance(AI_reply, int):
                            # 如果 AI_reply 是整数，直接使用它
                            target_index = AI_reply
                        target_player = alive_player_dict.get(target_index)
                        if target_player:
                            # 发送查验结果给 AI 预言家
                            role_info = "好人" if not isinstance(target_player, Werewolf) else "狼人"
                            result = f"{target_player.index}号玩家 {target_player.name} 的身份是 {role_info}"
                            mes = Message(content=result, type='info', recipients=prophet)
                            send_message(mes, self.players)


        # 女巫行动
        # TODO: 如果看起来好搞的话，可以照着狼人的实现把预言家和女巫改了。不用管ai那边的prompt，我来处理。 --hts
        content = "预言家请闭眼，女巫请睁眼："
        mes = Message(content=content, type='info', recipients='all')
        send_message(mes, self.players)
        witches = [player for player in self.players if isinstance(player, Witch) and player.is_alive]

        if witches:
            for witch in witches:
                alive_players = self.get_alive_players()
                alive_player_indices = [player.index for player in alive_players]
                alive_player_dict = {player.index: player for player in alive_players}

                victims = [v for v in victims if v.is_alive]
                # 女巫有两个可能的行动：救人和毒人
                # 首先，女巫是否要救被狼人杀的玩家
                
                if witch.is_human:
                    # 人类女巫
                    prompt = f"解药数量：{witch.cure_count}，毒药数量：{witch.poison_count}"
                    mes = Message(content=prompt, type='info', recipients=witch)
                    response = send_message(mes, self.players)

                    # 女巫是否救人
                    if witch.cure_count and victims:
                        # 将所有死亡玩家发给女巫
                        victim_list = "\n".join(f"{victim.index}. {victim.name}" for victim in victims)
                        prompt = f"今晚这些玩家死亡了：\n{victim_list}\n女巫，你是否要救活其中某个玩家？（输入玩家序号救人(最多救一人)，输入 -1 不救）"
                        mes = Message(content=prompt, type='witch', recipients=witch, expect_reply=True)
                        response = send_message(mes, self.players)
                        
                        while True:
                            player_reply = response.get(witch.index)
                            if player_reply and player_reply.isdigit():
                                target_index  = int(player_reply)
                                if target_index == -1:
                                    # 女巫选择不救
                                    break
                                elif any(victim.index == target_index for victim in victims):
                                    # 如果是有效的玩家序号，并且选择不为-1，救回该玩家
                                    victim_to_save = next(victim for victim in victims if victim.index == target_index)
                                    witch.use_healing_potion()  # 使用解药
                                    # 从victims列表中移除已救活的玩家
                                    victims.remove(victim_to_save)
                                    prompt = f"你已经成功救回 {victim.index}. {victim.name}。"
                                    mes = Message(content=prompt, type='info', recipients=witch)
                                    send_message(mes, self.players)
                                    break
                                else:
                                    # 处理无效输入
                                    content = "输入无效，请重新输入有效的死亡玩家序号，若不救请输-1："
                                    mes = Message(content=content, type='witch', recipients=witch, expect_reply=True)
                                    send_message(mes, self.players)
                            else:
                                # 如果输入无效，提示重新输入
                                prompt = "输入无效，请重新输入有效的死亡玩家序号，若不救请输-1："
                                mes = Message(content=prompt, type='witch', recipients=witch, expect_reply=True)
                                response = send_message(mes, self.players)

                    
                    elif not witch.cure_count:
                        prompt = "解药已用完"
                        mes = Message(content=prompt, type='witch', recipients=witch)
                        response = send_message(mes, self.players)
                    elif not victims:
                        prompt = "无人死亡"
                        mes = Message(content=prompt, type='witch', recipients=witch)
                        response = send_message(mes, self.players)
                    # 接下来，女巫是否要毒人
                    if witch.poison_count:
                        prompt = "请选择要毒杀的玩家（输入玩家序号杀人(最多杀一人)，输入 -1 不杀）：\n" + \
                                    "\n".join(f"{p.index}. {p.name}" for p in alive_players if p != witch)
                        mes = Message(content=prompt, type='witch', recipients=witch, expect_reply=True)
                        response = send_message(mes, self.players)
                        while True:
                            player_reply = response.get(witch.index)
                            if player_reply and player_reply.isdigit():
                                target_index  = int(player_reply)
                                if target_index == -1:
                                    # 女巫选择不使用毒药
                                    break
                                elif any(player.index == target_index for player in alive_players):
                                    # 如果是有效的玩家序号，并且选择不为-1，救回该玩家
                                    player_to_kill = next(player for player in alive_players if player.index == target_index)
                                    witch.use_poison_potion()  # 使用解药
                                    # 从victims列表中移除已救活的玩家
                                    poisoned_victims.append(player_to_kill)
                                    prompt = f"你已经成功杀掉 {player_to_kill.index}. {player_to_kill.name}。"
                                    mes = Message(content=prompt, type='info', recipients=witch)
                                    send_message(mes, self.players)
                                    break
                                else:
                                    # 处理无效输入
                                    content = "输入无效，请重新输入有效的玩家序号，若不使用毒药请输-1："
                                    mes = Message(content=content, type='witch', recipients=witch, expect_reply=True)
                                    send_message(mes, self.players)
                            else:
                                # 如果输入无效，提示重新输入
                                prompt = "输入无效，请重新输入有效的玩家序号，若不使用毒药请输-1："
                                mes = Message(content=prompt, type='witch', recipients=witch, expect_reply=True)
                                response = send_message(mes, self.players)
                    elif not witch.poison_count:
                        prompt = "毒药已用完"
                        mes = Message(content=prompt, type='witch', recipients=witch)
                        response = send_message(mes, self.players)
                else:

                    special_info = {"cure": witch.cure_count, "poison": witch.poison_count}
                    # 初始化 prompt 内容
                    prompt = ""
                    # 处理解药部分
                    if witch.cure_count:
                        # 如果有解药，列出死亡玩家信息并询问是否使用解药
                        death_prompt = "\n".join(f"{victim.index}. {victim.name}" for victim in victims)
                        prompt += f"你是否要使用解药？\n" + \
                                f"以下是已死亡的玩家：\n{death_prompt}\n"
                    else:
                        # 如果没有解药，提示解药已用完
                        prompt += "解药已用完。\n"

                    # 处理毒药部分
                    if witch.poison_count > 0:
                        # 如果有毒药，列出存活玩家信息并询问是否使用毒药
                        poison_prompt = "\n".join(f"{p.index}. {p.name}" for p in alive_players if p != witch)
                        prompt += f"请选择要毒杀的玩家（输入序号）：\n{poison_prompt}"
                    else:
                        # 如果没有毒药，提示毒药已用完
                        prompt += "毒药已用完。\n"

                    mes = Message(content=prompt, type='witch', recipients=witch, expect_reply=True, special_info=special_info)
                    response = send_message(mes, self.players, alive_players)
                    AI_reply = response.get(witch.index)
                    # 解析 AI 女巫的决策
                    # 假设 response 是一个 (救人玩家序号，杀人玩家序号)

                    # TODO:未处理若AI返回不符合情况当如何处理
                    # TODO:若AI女巫没有解药和毒药则直接返回-1.
                    if AI_reply:
                        cure_choice, poison_choice = AI_reply

                        if cure_choice and cure_choice.isdigit():
                            cure_index = int(cure_choice)
                            if cure_index == -1:
                                # 女巫选择不使用解药
                                prompt = "你选择不使用解药，跳过救人步骤。"
                                mes = Message(content=prompt, type='info', recipients=witch)
                                send_message(mes, self.players)
                            elif any(victim.index == cure_index for victim in victims):
                                # 如果是有效的玩家序号，并且玩家在victims列表中（已死亡）
                                victim_to_save = next(victim for victim in victims if victim.index == cure_index)
                                witch.use_healing_potion()  # 使用解药
                                victims.remove(victim_to_save)  # 从victims中移除被救回的玩家
                                prompt = f"你已经成功救回 {victim_to_save.index}. {victim_to_save.name}。"
                                mes = Message(content=prompt, type='info', recipients=witch)
                                send_message(mes, self.players)

                        # 处理杀人逻辑
                        if poison_choice and poison_choice.isdigit():
                            poison_index = int(poison_choice)
                            if poison_index == -1:
                                # 女巫选择不使用毒药
                                prompt = "你选择不使用毒药，跳过杀人步骤。"
                                mes = Message(content=prompt, type='info', recipients=witch)
                                send_message(mes, self.players)
                            elif any(player.index == poison_index for player in alive_players):
                                # 如果是有效的玩家序号，并且玩家在alive_players列表中（仍然活着）
                                player_to_kill = next(player for player in alive_players if player.index == poison_index)
                                witch.use_poison_potion()  # 使用毒药
                                poisoned_victims.append(player_to_kill)  # 将毒死的玩家加入poisoned_victims列表
                                prompt = f"你已经成功杀掉 {player_to_kill.index}. {player_to_kill.name}。"
                                mes = Message(content=prompt, type='info', recipients=witch)
                                send_message(mes, self.players)

        # 公布夜晚结果
        content = "女巫请闭眼，天亮了。"
        mes = Message(content=content, type='info', recipients='all')
        send_message(mes, self.players)

        for victim in victims:
            if victim and victim.is_alive:
                victim.is_alive = False
                content = f"{victim.name} 死了（被狼人杀）"
                mes = Message(content=content, type='info', recipients='all')
                send_message(mes, self.players)
        for poisoned_victim in poisoned_victims:
            if poisoned_victim and poisoned_victim.is_alive:
                poisoned_victim.is_alive = False
                content = f"{poisoned_victim.name} 死了（被女巫毒死）"
                mes = Message(content=content, type='info', recipients='all')
                send_message(mes, self.players)
        if not victims and not poisoned_victims:
            content = "昨晚是平安夜"
            mes = Message(content=content, type='info', recipients='all')
            send_message(mes, self.players)


        # 将死亡人员和信息加入，方便进行历史记录回顾
        for victim in victims:
            if victim:
                death_info = {
                    "victim": victim,  # 死亡玩家
                    "night_count": self.night_count  # 死亡发生的夜晚序号
                }
            self.victims_info.append(death_info)

        for poisoned_victim in poisoned_victims:
            if poisoned_victim:
                death_info = {
                    "poisoned_victim": poisoned_victim,  # 死亡玩家
                    "night_count": self.night_count  # 死亡发生的夜晚序号
                }
            self.poisoned_victims_info.append(death_info)


        self.night_count += 1


    def day_phase(self):
        content = "\n--- 白天 ---\n天亮了，现在开始发言。"
        mes = Message(content=content, type='info', recipients='all')
        voted_victims = []
        send_message(mes, self.players)

        # 玩家发言
        for player in self.get_alive_players():
            # 向当前玩家发送消息请求发言
            prompt = f"{player.index}号 {player.name}，请发表您的观点："
            request_message = Message(content=prompt, type='speak', recipients=player, expect_reply=True)
            response = send_message(request_message, self.players)
            speech = response.get(player.index)

             # 将获取的发言广播给其他所有玩家包括自身
            for other_player in self.players:
                inform_message = Message(content=f"{player.index}号 {player.name}说：{speech}", type='info', recipients=other_player)
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
                    request_message = Message(content=vote_prompt, type='vote', recipients=player, expect_reply=True)
                    response = send_message(request_message, self.players)
                    player_reply = response.get(player.index)
                    if not player_reply.isdigit():
                        vote_prompt = "输入序号无效，请重新输入：\n"
                        continue
                    vote_result = int(player_reply)
                    voted_player = next((p for p in alive_players if p.index == vote_result), None)
                    if not voted_player :
                        vote_prompt = "输入序号超出范围，请重新输入：\n"
                        continue
                    votes[voted_player.index] += 1
                    break
            else:
                # AI玩家投票
                alive_player_indices = [player.index for player in alive_players]

                try:
                    # 调用工具，确保返回的值是可解析的数字
                    request_message = Message(content="请投票", type='vote', recipients=player, expect_reply=True)
                    vote_result = send_message(request_message, self.players, alive_players)
                    voted_player = next((p for p in alive_players if p.index == vote_result[player.index]), None)
                    # 测试用
                    print(f"AI玩家 {player.name} 投了{vote_result[player.index]}")
                    if voted_player:
                        votes[voted_player.index] += 1


                except (ValueError, TypeError):
                    print(f"AI玩家 {player.name} 投票返回了无效值")


        max_votes = max(votes.values())
        max_voted_indices = [index for index, count in votes.items() if count == max_votes]
        if len(max_voted_indices) == 1:
            exiled_player = next(player for player in self.get_alive_players() if player.index  == max_voted_indices[0])
            if exiled_player:
                voted_victims.append(exiled_player)
                exiled_player.is_alive = False
                content = f"{exiled_player.index}号 {exiled_player.name} 被放逐了。"
                mes = Message(content=content, type='info', recipients='all')
                send_message(mes, self.players)
        else:
            content = "投票结果出现平票，没有人被放逐。"
            mes = Message(content=content, type='info', recipients='all')
            send_message(mes, self.players)

        for voted_victim in voted_victims:
            if voted_victim:
                death_info = {
                    "voted_victim": voted_victim,  # 死亡玩家
                    "day_count": self.night_count - 1 # 死亡发生的白天序号
                }
            self.voted_victims_info.append(death_info)

    def check_victory(self) -> bool:
        voted_out = False  # 假设投票被放逐为False
        good_num = sum(1 for p in self.get_alive_players() if not isinstance(p, Werewolf))
        wolf_num = sum(1 for p in self.get_alive_players() if isinstance(p, Werewolf))

        gods_alive = any(isinstance(p, (Prophet, Witch)) for p in self.get_alive_players() if p.is_alive)
        villagers_alive = any(isinstance(p, Villager) for p in self.get_alive_players() if p.is_alive)
        for death_info in self.voted_victims_info:
            voted_player = death_info['voted_victim']
            
            # 检查是否是白痴角色
            if isinstance(voted_player, Idiot):  # 假设Idiot是白痴角色类
                voted_out = True  # 如果白痴被投票出去，则设置为True
                break  # 如果已经找到了白痴，停止循环
            
        if eval(self.victory_conditions['idiot_win'], {"voted_out": voted_out}):
            content = "游戏结束，白痴获胜！"
            mes = Message(content=content, type='info', recipients='all')
            send_message(mes, self.players)
            return True
        if eval(self.victory_conditions['good_win'], {"wolf_num": wolf_num, "good_num": good_num}):
            content = "游戏结束，好人阵营获胜！"
            mes = Message(content=content, type='info', recipients='all')
            send_message(mes, self.players)
            return True
        if eval(self.victory_conditions['wolf_win'], {"wolf_num": wolf_num, "good_num": good_num, "gods_alive": gods_alive, "villagers_alive": villagers_alive}):
            content = "游戏结束，狼人阵营获胜！"
            mes = Message(content=content, type='info', recipients='all')
            send_message(mes, self.players)
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

        # 显示所有玩家（调试用）
        print("\n游戏角色分配完毕：")
        for player in self.players:
            print(f"{player.index}. {player}")
