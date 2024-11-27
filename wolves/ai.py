from audioop import error

from numpy import character
from pywin.framework.toolmenu import tools
from zhipuai import ZhipuAI
import time
import json
from keys import ZHIPUAI_API_KEY
from typing import Literal, List, Dict
from prompts import PromptGenerator
from zhipuai.types.chat.chat_completion import Completion
from message import Message
from player import Player

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





class AIPlayer():
    def __init__(self, name: str = "",
                 output_limit: int = 100,
                 identity: Literal["狼人", "平民", "预言家"] = "平民",
                 game_specified_prompt = "本局游戏中有四个玩家，其中有两个狼人、四个平民。",):
        """

        :param index: 序号
        :param name: 名字
        :param output_limit: 输出字数限制
        :param identity: 身份(Literal["狼人", "平民", "预言家"])
        """
        self.type = 'AI'
        self.prompt_generator = PromptGenerator(game_specified_prompt=game_specified_prompt,
                                                output_limit=output_limit, identity=identity)
        self.client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
        self.session_id = time.time_ns()
        self.messages: List[Message] = []
        
        self.tools_functions = {}  # 存储需要的工具函数
        self.character = character
        self.faction_indices: List[int] = []
        self.index = -1  # 未定义

    def set_character(self, character: Literal["平民","狼人","预言家"]):
        self.character = character

    def set_index(self, index: int):
        self.index = index
        self.prompt_generator.set_index(index)

    def set_faction_indices(self, faction_indices: List[int]):
        self.faction_indices = faction_indices

    def create(self, messages_to_send) -> str:
        response = self.client.chat.completions.create(
            model="glm-4-plus",
            messages=messages_to_send,
            stream=False,
            temperature=0.6)
        ans = response.choices[0].message.content
        self.messages.append(Message(content=ans, type='reply', recipients=[]))
        return ans

    def recv(self, message: Message, alive_players: List[Player]):
        if message.type == "info":
            self.messages.append(message)
        elif message.type == "speak":
            prompt = self.prompt_generator.speak_prompt(self.messages)
            return self.create(prompt)
        elif message.type == "vote":
            return self.vote(alive_players)
        elif message.type == "kill":
            return self.kill(message, alive_players)
        elif message.type == "check":
            return self.check(message, alive_players)
        elif message.type == "witch":
            return self.witch(message, alive_players, message.special_info)
        else:
            raise ValueError(f"unknown message type: {message.type}")

    def vote(self, alive_players: List[Player]) -> int:
        # 投票
        alive_indices = []
        for player in alive_players:
            if player.index != self.index:
                alive_indices.append(player.index)
        prompt = self.prompt_generator.vote_prompt(self.messages)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "vote",
                    "description": f"投票放逐一位玩家，输入为玩家序号，范围为{alive_indices.__str__()}",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target": {
                                "type": "int",
                                "description": "投票目标的序号",
                            },
                        },
                        "required": ["target"],
                    },
                }
            }
        ]
        response = self.client.chat.completions.create(
            model="glm-4-plus",  # 请填写您要调用的模型名称
            messages=prompt,
            tools=tools,
            tool_choice="auto",
            stream=False,
            temperature=0,
        )
        try:
            result = json.loads(response.choices[0].message.tool_calls[0].function.arguments)["target"]
            return int(result)
        except error as e:
            print(f"模型调用vote发生错误{e}")
            return -1


    def kill(self, message: Message, alive_players: List[Player]) -> int:
        # 投票
        alive_indices = []
        for player in alive_players:
            if player.index != self.index:
                alive_indices.append(player.index)
        prompt = self.prompt_generator.kill_prompt(self.messages)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "kill",
                    "description": f"选择作为狼人要杀的玩家，输入为玩家序号，范围为{alive_indices.__str__()}",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target": {
                                "type": "int",
                                "description": "选择目标的序号",
                            },
                        },
                        "required": ["target"],
                    },
                }
            }
        ]
        response = self.client.chat.completions.create(
            model="glm-4-plus",  # 请填写您要调用的模型名称
            messages=prompt,
            tools=tools,
            tool_choice="auto",
            stream=False,
            temperature=0,
        )
        try:
            result = json.loads(response.choices[0].message.tool_calls[0].function.arguments)["target"]
            return int(result)
        except error as e:
            print(f"模型调用kill发生错误{e}")
            return -1

    def check(self, message: Message, alive_players: List[Player]) -> int:
        # 预言家查验身份
        alive_indices = []
        for player in alive_players:
            if player.index != self.index:
                alive_indices.append(player.index)
        prompt = self.prompt_generator.vote_prompt(self.messages)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "vote",
                    "description": f"选择要查验的玩家，输入为玩家序号，范围为{alive_indices.__str__()}",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target": {
                                "type": "int",
                                "description": "查验目标的序号",
                            },
                        },
                        "required": ["target"],
                    },
                }
            }
        ]
        response = self.client.chat.completions.create(
            model="glm-4-plus",  # 请填写您要调用的模型名称
            messages=prompt,
            tools=tools,
            tool_choice="auto",
            stream=False,
            temperature=0,
        )
        try:
            result = json.loads(response.choices[0].message.tool_calls[0].function.arguments)["target"]
            return int(result)
        except error as e:
            print(f"模型调用check发生错误{e}")
            return -1
        pass

    def witch(self, message: Message, alive_players: List[Player], special_info: dict[str, bool]) -> dict[str, int]:
        # TODO: 请照着这里的模板修改女巫接口。输入例子：["cure": 0, "poison": 1]
        alive_indices = []
        for player in alive_players:
            if player.index != self.index:
                alive_indices.append(player.index)
        result = {"cure": -1, "poison": -1}  # 没用为-1

        cure_tool = {
            "type": "function",
            "function": {
                "name": "cure",
                "description": f"选择对一位玩家使用解药，输入为玩家序号，范围为{alive_indices.__str__()}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "int",
                            "description": "解药目标的序号",
                        },
                    },
                    "required": ["target"],
                },
            }
        }

        poison_tool = {
            "type": "function",
            "function": {
                "name": "poison",
                "description": f"选择对一位玩家使用毒药，输入为玩家序号，范围为{alive_indices.__str__()}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "int",
                            "description": "毒药目标的序号",
                        },
                    },
                    "required": ["target"],
                },
            }
        }

        tools = []
        
        if special_info["cure"]:
            tools.append(cure_tool)
        if special_info["poison"]:
            tools.append(poison_tool)
        if tools:
            prompt = self.prompt_generator.witch_prompt(self.messages)
            response = self.client.chat.completions.create(
                model="glm-4-plus",  # 请填写您要调用的模型名称
                messages=prompt,
                tools=tools,
                tool_choice="auto",
                stream=False,
                temperature=0,
            )






