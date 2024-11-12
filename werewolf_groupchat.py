from zhipuai import ZhipuAI
import time
from keys import ZHIPUAI_API_KEY
from typing import Literal, List, Dict
from prompts import PromptGenerator


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
    def __init__(self, index: int, name: str,
                 output_limit: int = 100,
                 identity: Literal["狼人", "平民", "预言家"] = "平民",
                 game_specified_prompt = "本局游戏中有四个玩家，其中有两个狼人、四个平民。",):
        """

        :param index: 序号
        :param name: 名字
        :param output_limit: 输出字数限制
        :param identity: 身份(Literal["狼人", "平民", "预言家"])
        """
        super().__init__(index)
        self.type = 'AI'
        self.prompt_generator = PromptGenerator(game_specified_prompt=game_specified_prompt,
                                                output_limit=output_limit, identity=identity)
        self.client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
        self.session_id = time.time_ns()

    def create(self, new_messages: List[Dict[str, str]]):
        self.client.chat.completions.create(new_messages)

    def talk(self):
        pass

class HumanPlayer(Player):
    def __init__(self, index:int, name: str):
        super().__init__(index)
        self.type = 'HUMAN'
    def talk(self):
        pass





