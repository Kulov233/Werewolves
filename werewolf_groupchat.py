from autogen import ConversableAgent, GroupChat, GroupChatManager
from keys import ZHIPUAI_API_KEY
from typing import Literal
from prompts import Prompts

config_list = [
    {
        'model': 'glm-4-plus',
        'api_key': ZHIPUAI_API_KEY,  # 输入用户自己的api_key
        'base_url': 'https://open.bigmodel.cn/api/paas/v4/',
        'api_type': 'openai'
    }
]

llm_config={
        "config_list": config_list,
}


class Player:
    def __init__(self, index: int):
        self.index = index
        self.character = None

    def set_character(self, character: Literal["平民","狼人","预言家"]):
        self.character = character

class AIPlayer(Player):
    def __init__(self, index:int, name: str,
                 personality: str = "你是一名狼人杀玩家。"):
        """
        :param name: 角色名称
        :param personality: 性格prompt
        """
        super().__init__(index)
        self.personality = personality
        self.type = 'AI'
        self.prompt_generator = Prompts()

    def get_prompt(self):
        self.prompt_generator.generate_system_prompt()
    def talk(self):
        pass

class HumanPlayer(Player):
    def __init__(self, index:int, name: str):
        super().__init__(index)
        self.type = 'HUMAN'
    def talk(self):
        pass





