from message import Message, send_message, get_input_from_player
from tools import dispatch_tool


# 角色翻译
role_translations = {
    "Werewolf": "狼人",
    "Villager": "平民",
    "Prophet": "预言家",
    "Witch": "女巫"
}

class Player:
    def __init__(self, name, index: int):
        self.name = name
        self.is_alive = True
        self.is_human = False  # 默认为AI玩家
        self.ai = None
        self.index: int = index

    def __str__(self):
        return f"{self.name} ({role_translations[self.__class__.__name__]})"


    def receive(self, message: Message):
        # AI玩家处理接收到的消息
        if not self.is_human and self.ai:
            self.ai.recv(message)

    def set_ai(self, ai):
        self.ai = ai

class Villager(Player):
    def __init__(self, name, index):
        super().__init__(name, index)

class Prophet(Player):
    def __init__(self, name, index):
        super().__init__(name, index)

class Witch(Player):
    def __init__(self, name, index):
        super().__init__(name, index)
        self.has_healing_potion:int = 1  # 初始状态：女巫有解药
        self.has_poison_potion:int = 1  # 初始状态：女巫有毒药

    def use_healing_potion(self):
        """
        使用解药
        """
        if self.has_healing_potion:
            self.has_healing_potion -= 1

    def use_poison_potion(self)  -> bool:
        """
        使用毒药
        """
        if self.has_poison_potion:
            self.has_poison_potion -= 1

class Werewolf(Player):
    def __init__(self, name, index):
        super().__init__(name, index)
