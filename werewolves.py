import random
from math import gamma

from keys import ZHIPUAI_API_KEY
from zhipuai import ZhipuAI
from typing import Literal
from werewolf_groupchat import AIPlayer
from utils import Message
client = ZhipuAI(api_key=ZHIPUAI_API_KEY)


    
role_translations = {
    "Werewolf": "狼人",
    "Villager": "平民",
    "Prophet": "预言家",
    "Witch": "女巫"
}

PLAYER_LIST = []
# TODO: 这是个全局变量，这非常不好。必须要修改。但现在没有合适方案。设计的太乱了。

def send_message(mes: Message):
    # 这里假设sendmessage的实现已经完成，对于类型1和2，会有返回值
    if mes.message_type == 1:
        # 发送给人类玩家，获取输入
        print(mes.content)
        response = input()

        return response
    elif mes.message_type == 2:
        if mes.recipient is None:
            raise ValueError("You must specify a recipient")
        else:
            print(mes.recipient.ai.recv(mes))
    elif mes.message_type == 3:
        # 发送给全体玩家，无需返回值
        print(mes.content)
        for player in PLAYER_LIST:
            player.recv(mes)
    else:
        pass

def get_input_from_player(player, prompt):
    message_type = 1 if player.is_human else 2
    mes = Message(message_type=message_type, content=prompt, recipient=player)
    response = send_message(mes)
    return response

# 基础玩家类
class Player:
    def __init__(self, name):
        self.name = name
        self.is_alive = True
        self.is_human = False  # 默认为AI玩家
        self.ai = None

    def __str__(self):
        return f"{self.name} ({role_translations[self.__class__.__name__]})"

    def speak(self) -> str:

        prompt = f"请你发言："
        response = get_input_from_player(self, prompt)
        # 可以根据需要处理玩家的发言内容
        response = f"{self.name}说: {response}"
        return response


    def set_ai(self, ai: AIPlayer):
        self.ai = ai

# 村民类
class Villager(Player):
    def __init__(self, name):
        super().__init__(name)

# 预言家类
class Prophet(Player):
    def check(self, players):
        prompt = "预言家，请选择要查验的玩家：\n"
        for index, player in enumerate(players):
            prompt += f"{index + 1}. {player.name}\n"
        while True:
            response = get_input_from_player(self, prompt)
            if not response.isdigit():
                prompt = "输入序号无效，请重新输入\n"
                continue
            check_index = int(response) - 1
            if check_index < 0 or check_index >= len(players):
                prompt = "输入序号超出范围，请重新输入\n"
                continue
            result = f"{players[check_index].name} 的身份是 {role_translations[players[check_index].__class__.__name__]}"
            mes = Message(message_type=(1 if self.is_human else 2), content=result, recipient=self)
            send_message(mes)
            return

# 女巫类
class Witch(Player):
    def __init__(self, name):
        super().__init__(name)
        self.heal_used = False
        self.poison_used = False

    def heal(self, victim):
        if not victim:
            return False
        content = f"{victim.name} 死了\n"
        if not self.heal_used:
            content += "女巫，请选择是否使用解药 (yes/no)："
            while True:
                response = get_input_from_player(self, content)
                if response.lower() == "yes":
                    content = f"{victim.name} 被救活"
                    mes = Message(message_type=(1 if self.is_human else 2), content=content, recipient=self)
                    send_message(mes)
                    self.heal_used = True
                    return True
                elif response.lower() == "no":
                    return False
                else:
                    content = "输入无效，请输入yes或no："
        else:
            content += "你已经使用过解药"
            mes = Message(message_type=(1 if self.is_human else 2), content=content, recipient=self)
            send_message(mes)
        return False

    def poison(self, players):
        if not self.poison_used:
            content = "女巫，请选择是否使用毒药 (yes/no)："
            while True:
                response = get_input_from_player(self, content)
                if response.lower() == "yes":
                    prompt = "请选择要毒杀的玩家：\n"
                    for index, player in enumerate(players):
                        prompt += f"{index + 1}. {player.name}\n"
                    while True:
                        poison_response = get_input_from_player(self, prompt)
                        if not poison_response.isdigit():
                            prompt = "输入序号无效，请重新输入\n"
                            continue
                        poison_index = int(poison_response) - 1
                        if poison_index < 0 or poison_index >= len(players):
                            prompt = "输入序号超出范围，请重新输入\n"
                            continue
                        content = f"{players[poison_index].name} 被毒杀"
                        mes = Message(message_type=(1 if self.is_human else 2), content=content, recipient=self)
                        send_message(mes)
                        self.poison_used = True
                        return players[poison_index]
                elif response.lower() == "no":
                    return None
                else:
                    content = "输入无效，请输入yes或no："
        else:
            content = "你已经使用过毒药"
            mes = Message(message_type=(1 if self.is_human else 2), content=content, recipient=self)
            send_message(mes)
        return None

# 狼人类
class Werewolf(Player):
    def __init__(self, name):
        super().__init__(name)

    def kill(self, players):
        prompt = f"{self.name}，请选择今晚要猎杀的目标，注意你需要和你的队友选择同一个人：\n"
        for index, player in enumerate(players):
            prompt += f"{index + 1}. {player.name}\n"
        while True:
            response = get_input_from_player(self, prompt)
            if not response.isdigit():
                prompt = "输入序号无效，请重新输入\n"
                continue
            victim_index = int(response) - 1
            if victim_index < 0 or victim_index >= len(players):
                prompt = "输入序号超出范围，请重新输入\n"
                continue
            content = f"你选择猎杀 {players[victim_index].name}"
            mes = Message(message_type=(1 if self.is_human else 2), content=content, recipient=self)
            send_message(mes)
            return players[victim_index]

# 游戏类
class WerewolfGame:
    def __init__(self, human_num=1, AI_num=3):
        self.human_num = human_num
        self.AI_num = AI_num
        self.players = []
        self.night_count = 1
        self.role_classes = [Werewolf, Villager, Villager, Villager]

    def assign_roles(self):
        total_players = self.human_num + self.AI_num
        # 获取所有玩家的名字
        for i in range(total_players):
            while True:
                if i < self.human_num:
                    content = "请输入你的名字: "
                    mes = Message(message_type=1, content=content)
                    player_name = send_message(mes)
                else:
                    content = "请输入AI玩家的名字: "
                    mes = Message(message_type=1, content=content)
                    player_name = send_message(mes)
                if player_name in [player.name for player in self.players]:
                    content = "玩家名字重复，请重新输入"
                    mes = Message(message_type=1, content=content)
                    send_message(mes)
                    continue
                if not player_name:
                    content = "玩家名字不能为空，请重新输入"
                    mes = Message(message_type=1, content=content)
                    send_message(mes)
                    continue
                player = Player(player_name)
                player.is_human = True if i < self.human_num else False
                self.players.append(player)
                break
         # 分配角色
        # random.shuffle(self.role_classes)
        for i, player in enumerate(self.players):
            role_class = self.role_classes[i]
            new_player = role_class(player.name)
            new_player.is_human = player.is_human
            self.players[i] = new_player

        # 通知玩家他们的角色
        for player in self.players:
            if not player.is_human:
                created_ai = AIPlayer(name=player.name , identity=role_translations[player.__class__.__name__])
                PLAYER_LIST.append(created_ai)
                player.set_ai(
                    created_ai
                )
            message_type = 1 if player.is_human else 2
            content = f"你的角色是：{role_translations[player.__class__.__name__]}"
            mes = Message(message_type=message_type, content=content, recipient=player)
            send_message(mes)

        # 显示所有玩家（调试用）
        print("\n游戏角色分配完毕：")
        for index, player in enumerate(self.players):
            print(f"{index + 1}. {player}")

    def get_alive_players(self):
        return [player for player in self.players if player.is_alive]

    def night_phase(self):
        content = f"\n--- 夜晚 {self.night_count} ---\n天黑请闭眼，狼人请睁眼："
        mes = Message(message_type=3, content=content)
        send_message(mes)
        victim = None
        poisoned_victim = None

        # 狼人选择猎杀目标
        wolves = [player for player in self.players if isinstance(player, Werewolf) and player.is_alive]
        if wolves:
            while True:
                choices = set()
                for wolf in wolves:
                    choices.add(wolf.kill(self.get_alive_players()))
                if len(choices) == 1:
                    victim = choices.pop()
                    content = f"狼人选择猎杀 {victim.name}"
                    mes = Message(message_type=3, content=content)
                    send_message(mes)
                    break
                else:
                    content = "狼人选择的目标不一致，请重新选择"
                    mes = Message(message_type=3, content=content)
                    send_message(mes)

        content = "狼人请闭眼，预言家请睁眼："
        mes = Message(message_type=3, content=content)
        send_message(mes)

        ## 预言家查验身份
        #prophet = next((player for player in self.players if isinstance(player, Prophet) and player.is_alive), None)
        #if prophet:
        #    prophet.check(self.get_alive_players())
#
        ##content = "预言家请闭眼，女巫请睁眼："
        ##mes = Message(message_type=3, content=content)
        ##send_message(mes)
#
        ## 女巫技能
        #witch = next((player for player in self.players if isinstance(player, Witch) and player.is_alive), None)
        #if witch:
        #    if witch.heal(victim):
        #        victim = None  # 解药生效，取消猎杀
        #    poisoned_victim = witch.poison(self.get_alive_players())
#
        ## 猎杀结果
        #if victim and victim.is_alive:
        #    victim.is_alive = False
        #    content = f"{victim.name} 死了"
        #    mes = Message(message_type=3, content=content)
        #    send_message(mes)
        #if poisoned_victim and poisoned_victim.is_alive:
        #    poisoned_victim.is_alive = False
        #    content = f"{poisoned_victim.name} 死了"
        #    mes = Message(message_type=3, content=content)
        #    send_message(mes)
        #if not victim and not poisoned_victim:
        #    content = "今晚是平安夜"
        #    mes = Message(message_type=3, content=content)
        #    send_message(mes)
#
        #self.night_count += 1

    def day_phase(self):
        content = "\n--- 白天 ---\n天亮了"
        mes = Message(message_type=3, content=content)
        send_message(mes)
        content = "玩家发言阶段："
        mes = Message(message_type=3, content=content)
        send_message(mes)
        for player in self.get_alive_players():
            response = player.speak()
            for player in self.get_alive_players():
                if not player.is_human:
                    send_message(Message(message_type=2, content=response, recipient=player))

        # 投票放逐
        votes = {player.name: 0 for player in self.get_alive_players()}
        for player in self.get_alive_players():
            vote_prompt = f"{player.name} 是否投票放逐一位玩家 (yes/no)："
            while True:
                response = get_input_from_player(player, vote_prompt)
                if response.lower() == "yes":
                    prompt = "请投票放逐一位玩家：\n"
                    for index, _player in enumerate(self.get_alive_players()):
                        prompt += f"{index + 1}. {_player.name}\n"
                    while True:
                        vote_response = get_input_from_player(player, prompt)
                        if not vote_response.isdigit():
                            prompt = "输入序号无效，请重新输入\n"
                            continue
                        vote_index = int(vote_response) - 1
                        if vote_index < 0 or vote_index >= len(self.get_alive_players()):
                            prompt = "输入序号超出范围，请重新输入\n"
                            continue
                        content = f"{player.name} 选择放逐 {self.get_alive_players()[vote_index].name}"
                        mes = Message(message_type=(1 if player.is_human else 2), content=content, recipient=player)
                        send_message(mes)
                        votes[self.get_alive_players()[vote_index].name] += 1
                        break
                    break
                elif response.lower() == "no":
                    content = f"{player.name} 选择不投票"
                    mes = Message(message_type=(1 if player.is_human else 2), content=content, recipient=player)
                    send_message(mes)
                    break
                else:
                    vote_prompt = "输入无效，请输入yes或no："

        # 统计投票结果
        max_votes = max(votes.values())
        max_voted_players = [player for player, vote in votes.items() if vote == max_votes]
        if len(max_voted_players) == 1:
            max_voted_player = next(player for player in self.get_alive_players() if player.name == max_voted_players[0])
            max_voted_player.is_alive = False
            content = f"{max_voted_player.name} 被放逐"
            mes = Message(message_type=3, content=content)
            send_message(mes)
        else:
            content = "出现平票，无法确定放逐玩家"
            mes = Message(message_type=3, content=content)
            send_message(mes)

    def check_victory(self):
        alive_good = [player for player in self.get_alive_players() if not isinstance(player, Werewolf)]
        alive_wolves = [player for player in self.get_alive_players() if isinstance(player, Werewolf)]
        if len(alive_wolves) == 0:
            content = "好人阵营获胜！"
            mes = Message(message_type=3, content=content)
            send_message(mes)
            return True
        if len(alive_good) <= len(alive_wolves):
            content = "狼人阵营获胜！"
            mes = Message(message_type=3, content=content)
            send_message(mes)
            return True
        return False

    def play(self):
        self.assign_roles()
        while True:
            self.night_phase()
            if self.check_victory():
                break
            self.day_phase()
            if self.check_victory():
                break
if __name__ == '__main__':

    # 运行游戏
    # human_num = int(input("请输入真人玩家人数："))
    # AI_num = int(input("请输入AI玩家人数："))
    #
    # game = WerewolfGame(human_num=human_num, AI_num=AI_num)
    game = WerewolfGame()
    game.play()