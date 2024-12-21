
from zhipuai import ZhipuAI
import time, json, random
from .keys import ZHIPUAI_API_KEY
from typing import Literal, List, Dict, Optional, Tuple, Any
from .prompts import PromptGenerator
# from zhipuai.types.chat.chat_completion import Completion
# from player import Player

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
    def __init__(self, name: str,
                 output_limit: int,
                 identity: Literal["狼人", "平民", "预言家", "女巫", "白痴"],
                 game_specified_prompt):
        """

        :param name: 名字
        :param output_limit: 输出字数限制
        :param identity: 身份(Literal["狼人", "平民", "预言家"])
        """
        self.type = 'AI'
        self.prompt_generator = PromptGenerator(game_specified_prompt=game_specified_prompt,
                                                output_limit=output_limit, identity=identity)
        self.client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
        self.session_id = time.time_ns()
        # self.messages: List[Message] = []

        # self.tools_functions = {}  # 存储需要的工具函数
        # self.faction_indices: List[str] = []
        self.index = -1  # 未定义

    def set_messages(self, messages: List[str]):
        self.messages = messages

    # def set_character(self, character: Literal["平民","狼人","预言家"]):
    #     self.character = character

    def set_index(self, index: str):
        self.index = index
        self.prompt_generator.set_index(index)

    def create(self, messages_to_send) -> str:
        response = self.client.chat.completions.create(
            model="glm-4-plus",
            messages=messages_to_send,
            stream=False,
            temperature=0.6)
        ans = response.choices[0].message.content
        # self.messages.append(Message(content=ans, type='reply', recipients=[]))
        return ans

    def recv(self, message, alive_players: List[str]):
        #if message.type == "info":
        #    self.messages.append(message)
        if message["type"] == "speak":
            prompt = self.prompt_generator.speak_prompt(self.messages)
            return self.create(prompt)
        elif message["type"] == "vote":
            return self.vote(alive_players)
        elif message["type"] == "kill":
            return self.kill(alive_players)
        elif message["type"] == "check":
            return self.check(alive_players)
        elif message["type"] == "witch":
            return self.witch(alive_players, message["special_info"])
        elif message["type"] == "info_team":
            # 处理狼人队友的消息，获取队友的索引
            team_indices = list(map(int, message["content"].split('：')[1].split(',')))  # 解析队友序号
            self.prompt_generator.set_faction_indices(team_indices)  # 设置队友序号
        else:
            raise ValueError(f"unknown message type: {message['type']}")

    def vote(self, alive_players: List[str]) -> str:
        # 投票
        alive_indices = []
        for player_index in alive_players:
            if player_index != self.index:
                alive_indices.append(player_index)
        random.shuffle(alive_indices)
        prompt = self.prompt_generator.vote_prompt(self.messages)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "vote",
                    "description": f"投票放逐一位玩家，输入为玩家序号，范围为{(alive_indices.__str__())}",
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
            return str(result)
        except Exception as e:
            print(f"模型调用vote发生错误{e}")
            return "-1"


    def kill(self, alive_players: List[str]) -> str:
        # 投票
        alive_indices = []
        for player_index in alive_players:
            if player_index != self.index:
                alive_indices.append(player_index)
        random.shuffle(alive_indices)
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
            return str(result)
        except Exception as e:
            print(f"模型调用kill发生错误{e}")
            return "-1"

    def check(self, alive_players: List[str]) -> str:
        # 预言家查验身份
        alive_indices = []
        for player_index in alive_players:
            if player_index != self.index:
                alive_indices.append(player_index)
        random.shuffle(alive_indices)
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
            return str(result)
        except Exception as e:
            print(f"模型调用check发生错误{e}")
            return "-1"
        pass

    def witch(self, alive_players: List[str], special_info: dict[str, bool]) -> tuple[str, str]:
        # TODO: 请照着这里的模板修改女巫接口。输入例子：["cure": 0, "poison": 1]
        alive_indices = []
        for player_index in alive_players:
            if player_index != self.index:
                alive_indices.append(player_index)
        random.shuffle(alive_indices)

        cure_tool = {
            "type": "function",
            "function": {
                "name": "cure",
                "description": f"选择对一位玩家使用解药，输入为玩家序号，范围为{special_info['victims']}。"
                               f"注意，你自己今晚被杀。请一定要使用解药。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "int",
                            "description": "解药目标的序号，若不使用则为-1",
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
                "description": f"选择对一位玩家使用毒药，输入为玩家序号，范围为{special_info['targets']}。如果选择不使用，则输入-1",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "int",
                            "description": "毒药目标的序号，若不使用则为-1",
                        },
                    },
                    "required": ["target"],
                },
            }
        }

        tools = []
        result1 = -1
        result2 = -1

        tool_prompt = ""
        if special_info["cure"] > 0:
            if self.index in special_info["victims"]:
                result1 = self.index
            else:
                tool_prompt += (f"你可以选择调用cure函数使用一瓶解药，目标是今晚死去的角色，范围为{special_info['victims']}。"
                                f"如果选择不使用，则调用函数输入-1。")
                tools.append(cure_tool)
        if special_info["poison"] > 0:
            tool_prompt += f"你可以选择调用poison函数使用一瓶毒药，目标是今晚还活着的角色，范围为{special_info['targets']}。"
            tools.append(poison_tool)
        if tools:
            prompt = self.prompt_generator.witch_prompt(self.messages, special_info, tool_prompt)
            response = self.client.chat.completions.create(
                model="glm-4-plus",
                messages=prompt,
                tools=tools,
                tool_choice="auto",
                stream=False,
                temperature=0,
            )
            if tools.__len__() == 2:
                result1 = json.loads(response.choices[0].message.tool_calls[0].function.arguments)["target"]
                result2 = json.loads(response.choices[0].message.tool_calls[1].function.arguments)["target"]
                return str(result1), str(result2)
            else:
                result = json.loads(response.choices[0].message.tool_calls[0].function.arguments)["target"]
                if cure_tool in tools:
                    result1 = result
                else:
                    result2 = result

        return str(result1), str(result2)







