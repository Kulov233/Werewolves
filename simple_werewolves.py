import random

role_translations = {
    "Werewolf": "狼人",
    "Villager": "平民",
    "Prophet": "预言家",
    "Witch": "女巫"
}

# 基础玩家类
class Player:
    def __init__(self, name):
        self.name = name
        self.is_alive = True

    def __str__(self):
        return f"{self.name} ({role_translations[self.__class__.__name__]})"

    def speak(self):
        print(f"{self.name} 发言：")
        input()

# 村民类
class Villager(Player):
    def __init__(self, name):
        super().__init__(name)

# 预言家类
class Prophet(Player):
    def __init__(self, name):
        super().__init__(name)

    def check(self, players):
        print("预言家，请选择要查验的玩家：")
        for index, player in enumerate(players):
            print(f"{index + 1}. {player.name}")
        while True:
            check_index = input("输入要查验玩家的序号：")
            if not check_index.isdigit():
                print("输入序号无效，请重新输入")
                continue
            check_index = int(check_index) - 1
            if check_index < 0 or check_index >= len(players):
                print("输入序号超出范围，请重新输入")
                continue
            print(f"{players[check_index].name} 的身份是 {role_translations[players[check_index].__class__.__name__]}")
            return

# 女巫类
class Witch(Player):
    def __init__(self, name):
        super().__init__(name)
        self.heal_used = False
        self.poison_used = False

    def heal(self, victim):
        print(f"{victim.name} 死了")
        if not self.heal_used:
            print("女巫，请选择是否使用解药 (yes/no)：")
            use_heal = input().lower()
            if use_heal == "yes":
                print(f"{victim.name} 被救活")
                self.heal_used = True
                return True
        else:
            print("你已经使用过解药")
        return False

    def poison(self, players):
        if not self.poison_used:
            print("女巫，请选择是否使用毒药 (yes/no)：")
            use_poison = input().lower()
            if use_poison == "yes":
                print("请选择要毒杀的玩家：")
                for index, player in enumerate(players):
                    print(f"{index + 1}. {player.name}")
                while True:
                    poison_index = input("输入要毒杀的玩家序号：")
                    if not poison_index.isdigit():
                        print("输入序号无效，请重新输入")
                        continue
                    poison_index = int(poison_index) - 1
                    if poison_index < 0 or poison_index >= len(players):
                        print("输入序号超出范围，请重新输入")
                        continue
                    print(f"{players[poison_index].name} 被毒杀")
                    self.poison_used = True
                    return players[poison_index]
        else:
            print("你已经使用过毒药")
            return

# 狼人类
class Werewolf(Player):
    def __init__(self, name):
        super().__init__(name)

    def kill(self, players):
        print(f"{self.name}，请选择今晚要猎杀的目标，注意你需要和你的队友选择同一个人：")
        for index, player in enumerate(players):
            print(f"{index + 1}. {player.name}")
        while True:
            victim_index = input("输入被猎杀玩家的序号：")
            if not victim_index.isdigit():
                print("输入序号无效，请重新输入")
                continue
            victim_index = int(victim_index) - 1
            if victim_index < 0 or victim_index >= len(players):
                print("输入序号超出范围，请重新输入")
                continue
            print(f"你选择猎杀 {players[victim_index].name}")
            return players[victim_index]

# 游戏类
class WerewolfGame:
    def __init__(self):
        self.players = []
        self.night_count = 1
        self.role_classes = [Villager, Villager, Prophet, Witch, Werewolf, Werewolf]

    def assign_roles(self):
        random.shuffle(self.role_classes)
        for i, role_class in enumerate(self.role_classes):
            while True:
                player_name = input(f"请输入玩家 {i + 1} 的名字: ")
                if player_name in [player.name for player in self.players]:
                    print("玩家名字重复，请重新输入")
                    continue
                if not player_name:
                    print("玩家名字不能为空，请重新输入")
                    continue
                player = role_class(player_name)
                self.players.append(player)
                break
        print("\n游戏角色分配完毕：")
        for index, player in enumerate(self.players):
            print(f"{index + 1}. {player}")

    def get_alive_players(self):
        return [player for player in self.players if player.is_alive]

    def night_phase(self):
        print(f"\n--- 夜晚 {self.night_count} ---")
        print("天黑请闭眼，狼人请睁眼：")
        victim = None
        poisoned_victim = None

        # 狼人选择猎杀目标
        wolves = [player for player in self.players if isinstance(player, Werewolf) and player.is_alive]
        if wolves:
            while True:
                # 保证统一刀口
                choices = set()
                for wolf in wolves:
                    choices.add(wolf.kill(self.get_alive_players()))
                if len(choices) == 1:
                    victim = choices.pop()
                    print(f"狼人选择猎杀 {victim.name}")
                    break
                print("狼人选择的目标不一致，请重新选择")

        print("狼人请闭眼，预言家请睁眼：")

        # 预言家查验身份
        prophet = next((player for player in self.players if isinstance(player, Prophet) and player.is_alive), None)
        if prophet:
            prophet.check(self.get_alive_players())

        print("预言家请闭眼，女巫请睁眼：")

        # 女巫技能
        witch = next((player for player in self.players if isinstance(player, Witch) and player.is_alive), None)
        if witch:
            if witch.heal(victim):
                victim = None  # 解药生效，取消猎杀
            if victim: # 没有解药或者不使用解药
                poisoned_victim = witch.poison(self.get_alive_players())

        # 猎杀结果
        if victim and victim.is_alive:
            victim.is_alive = False
            print(f"{victim.name} 死了")
        if poisoned_victim and poisoned_victim.is_alive:
            poisoned_victim.is_alive = False
            print(f"{poisoned_victim.name} 死了")
        if not victim and not poisoned_victim:
            print("今晚是平安夜")

        self.night_count += 1

    def day_phase(self):
        print("\n--- 白天 ---")
        print("天亮了")
        print("玩家发言阶段：")
        for player in self.get_alive_players():
            player.speak()

        # 投票放逐
        votes = {player.name: 0 for player in self.get_alive_players()}
        for player in self.get_alive_players():
            vote = None
            while True:
                print(f"{player.name} 是否投票放逐一位玩家 (yes/no)：")
                vote = input().lower()
                if vote == "yes":
                    break
                elif vote == "no":
                    break
                else:
                    print("输入无效，请重新输入")
            if vote == "yes":
                print("请投票放逐一位玩家：")
                for index, _player in enumerate(self.get_alive_players()):
                    print(f"{index + 1}. {_player.name}")
                while True:
                    vote_index = input("输入放逐玩家的序号：")
                    if not vote_index.isdigit():
                        print("输入序号无效，请重新输入")
                        continue
                    vote_index = int(vote_index) - 1
                    if vote_index < 0 or vote_index >= len(self.get_alive_players()):
                        print("输入序号超出范围，请重新输入")
                        continue
                    print(f"{player.name} 选择放逐 {self.get_alive_players()[vote_index].name}")
                    votes[self.get_alive_players()[vote_index].name] += 1
                    break
            else:
                print(f"{player.name} 选择不投票")

        # 统计投票结果
        max_votes = max(votes.values())
        max_voted_players = [player for player, vote in votes.items() if vote == max_votes]
        if len(max_voted_players) == 1:
            max_voted_player = next(player for player in self.get_alive_players() if player.name == max_voted_players[0])
            max_voted_player.is_alive = False
            print(f"{max_voted_player.name} 被放逐")
        else:
            print("出现平票，无法确定放逐玩家")


    def check_victory(self):
        alive_good = [player for player in self.get_alive_players() if not isinstance(player, Werewolf)]
        alive_wolves = [player for player in self.get_alive_players() if isinstance(player, Werewolf)]
        if len(alive_wolves) == 0:
            print("好人阵营获胜！")
            return True
        if len(alive_good) <= len(alive_wolves):
            print("狼人阵营获胜！")
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

# 运行游戏
game = WerewolfGame()
game.play()
