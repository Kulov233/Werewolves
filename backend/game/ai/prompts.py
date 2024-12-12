from socket import socket
from typing import List, Literal, Dict

character_prompts = {
            "狼人":  "你的角色是狼人，属于狼人阵营。你的特殊能力是每晚可以和其他狼人一起杀死一位其他玩家。"
                    "你的任务是尽可能隐藏自身身份，并尽可能塑造自身的好人形象，误导其他玩家的投票。",
            "平民":   "你的角色是平民，属于好人阵营。没有特殊能力。你的任务是想办法从对话中找出狼人，并尽可能发动大家向他投票。此外，可以想办法保护好人阵营的特殊角色。",
            "预言家": "你的角色是预言家，属于好人阵营。你的特殊能力是每晚可以查验一位玩家的身份。"
                     "你的任务是指导好人阵营进行投票，找出真正的狼人。你可以隐藏身份来避免太早被狼人杀死，"
                      "但如果你发现有狼人冒充预言家，一定要站出来用真实信息反驳他。",
            "女巫": "你的角色是女巫，属于好人阵营。你拥有一瓶解药和一瓶毒药，各使用一次。每晚你可以选择使用或不使用它们。"
                    "解药可以救活当晚被狼人杀害的玩家，毒药可以毒死任意一位玩家。"
                    "你的任务是利用你的药品保护好人阵营，也要谨慎狼人自刀，如果能够充分确认某人的狼人身份则使用毒药毒死他，同时尽量隐藏自己的身份。",
            "白痴": "你的角色是白痴，属于好人阵营。你没有特殊能力，但如果你在白天被投票出局，你可以展示你的身份牌，从而不会被出局。"
                    "你的任务是尽可能通过发言和推理引导其他玩家找出狼人，必要时可以引诱狼人在白天发言中归票自己，来帮助其他好人确定狼人身份。",
        }

basic_logis_prompts = """
    如果昨晚是平安夜，那么证明是女巫用解药救了被杀的人（如果本局中有女巫），或者守卫保护了今晚被杀的人（如果本局中有女巫）。
"""

class PromptGenerator:
    def __init__(self,
                 game_specified_prompt,
                 style_prompt: str = "发言时请注意风格规范：我们正在玩的狼人杀是一个接近纳什均衡策略的游戏，"
                                     "请你假设其他玩家会忽略不包含有效信息的内容，尽量多做针对具体的玩家的分析"
                                     "（无论分析是真是假）而不是使用情感打动其他玩家，少说空话和废话。",
                 output_limit: int = 100,
                 identity: Literal["狼人", "平民", "预言家", "女巫", "白痴"] = "平民",
                 ):
        self.faction_indices: List[int] = []
        self.intro = """
                你正在参与一款名为狼人杀的桌游。游戏中有多个角色，每个角色都有其特殊能力和胜利目标。
                游戏分为夜晚和白天两个阶段，会循环执行
                狼人的能力是每个夜晚可以秘密杀死一位玩家，胜利目标是在有狼人存活的情况下杀死所有非狼人角色；
                平民没有特殊能力，胜利目标是消灭所有狼人；
                预言家的特殊能力是每夜可以秘密查验一名玩家的身份，胜利目标是消灭所有狼人。
                此外，在每个白天阶段，所有存活的玩家会轮流进行一次发言，然后进行一次投票，得票最高的玩家将会被处决（杀死）。
                如果平票，则存活的其他玩家需要在平票的角色之间重新进行一次投票。
                """
        self.character_prompt = character_prompts[identity]

        self.game_specified_prompt = game_specified_prompt
        self.output_limits = output_limit
        self.style_prompt = style_prompt
        self.identity = identity
        self.index = None

    def set_index(self, index: str):
        self.index = index

    def set_faction_indices(self, faction_indices: List[int]):
        self.faction_indices = faction_indices

        print(f"狼人队友的索引: {self.faction_indices}")  # 调试输出

    def system_prompt(self) -> list[dict[str, str]]:

        system_prompt = [
            {"role": "system", "content": f"介绍：{self.intro}"},
            {"role": "system", "content": f"{self.game_specified_prompt}"},
            {"role": "system", "content": f"你的序号是：{self.index}你的身份是：{self.identity}。"},
            {"role": "system", "content": f"角色策略：{self.character_prompt}"}
        ]
        if self.faction_indices:
            system_prompt += [{"role": "system", "content":
                f"注意，{self.faction_indices}这几号玩家与你在同一阵营。你应当尽量暗中支持他们，"
                f"但在他们的发言过于激进或者已经暴露时也可以考虑放弃他们换取他人信任。"}]
        return system_prompt

    def past_messages(self, previous_messages: List[str]) -> list[dict[str, str]]:
        """

        :param previous_messages: List[Dict[str]], 用自然语言描述的过去消息列表
        :return: 处理好的过去消息列表
        """

        past_prompt = "以下是之前的游戏动态。"
        processed_messages = '\n'.join([message for message in previous_messages])
        result = [
            {"role": "system", "content": past_prompt},
            {"role": "system", "content": processed_messages}
        ]
        return result

    def speak_prompt(self, previous_messages: List[str]) -> list[dict[str, str]]:
        system_messages = self.system_prompt()
        past_messages = self.past_messages(previous_messages)
        user_messages = [
            {"role": "user", "content": self.style_prompt},
            {"role": "user", "content": "接下来，请参照以上信息做出你的发言。"
                                        "注意，你输出的内容会直接作为发言被其他玩家看到。"
                                        "你的输出内容应当全部为你的发言，无需添加任何额外内容。"
                                        f"发言限制在{self.output_limits}字以内。"}
        ]

        messages = system_messages + past_messages + user_messages
        return messages

    def vote_prompt(self, previous_messages: List[str], second_vote=False) -> list[dict[str, str]]:
        system_messages = self.system_prompt()
        past_messages = self.past_messages(previous_messages)
        user_messages = [
            {"role": "user", "content": self.style_prompt},
            {
                "role": "user", "content": "接下来，请你按照以上信息，投票放逐一位玩家。"
                                           "请调用函数vote，输入你投票放逐的玩家序号。"
                                           f"注意，你自己的序号是{self.index}。"
            }
        ]
        messages = system_messages + past_messages + user_messages
        return messages

    def kill_prompt(self, previous_messages: List[str], second_kill=False) -> list[dict[str, str]]:
        # TODO: 增加初次杀人的随机性
        system_messages = self.system_prompt()
        past_messages = self.past_messages(previous_messages)
        user_messages = [
            {"role": "user", "content": self.style_prompt},
            {
                "role": "user", "content": "接下来，请你按照以上信息，选择要杀死的玩家。"
                                           "请调用函数kill，输入你想要杀死的玩家序号。如果信息不足，可以随机杀一个非狼人阵营的人，但最好不要选1号。"
                                           f"注意，你自己的序号是{self.index}"
            }
        ]
        messages = system_messages + past_messages + user_messages
        return messages

    def check_prompt(self, previous_messages: List[str]) -> list[dict[str, str]]:
        # TODO:添加已经查过的人的信息，提醒一下。
        system_messages = self.system_prompt()
        past_messages = self.past_messages(previous_messages)
        user_messages = [
            {"role": "user", "content": self.style_prompt},
            {
                "role": "user", "content": "接下来，请你按照以上信息，选择要查验的玩家。"
                                           "请调用函数check，输入你想要查验身份的玩家序号。如果这是第一晚，可以随机查验一个人。"
                                           f"注意，你自己的序号是{self.index}"
            }
        ]
        messages = system_messages + past_messages + user_messages
        return messages

    def witch_prompt(self, previous_messages: List[str], special_info:dict, tool_prompt: str) -> list[dict[str, str]]:
        system_messages = self.system_prompt()
        past_messages = self.past_messages(previous_messages)

        user_messages = [
            {"role": "user", "content": self.style_prompt},
            {
                "role": "user", "content": "接下来，请你按照以上信息，调用函数进行女巫操作。"
                                           f"{tool_prompt}"
                                           f"一切回复均需要使用tool_call调用，如果不进行相应的操作则输入-1。"
                                           f"注意，你自己的序号是{self.index}。如果自己今晚被杀，那么无论如何要救活自己！"
                                           f"同时，如果狼人已经到了获胜的临界点，那么最好要救援晚上被杀的人。"
            }
        ]
        messages = system_messages + past_messages + user_messages
        return messages

A_prompt = "A(狼人): 昨晚是个平安夜。我们应该仔细观察今天的发言，看看有没有不一致的地方。"

B_prompt = "B(身份不明确): 我没有什么特别的线索，但我觉得我们应该听听预言家的意见，看看他有没有什么线索可以分享。"

sys_2 = "作为假扮的预言家，需要在发言中巩固你的预言家形象并试图引导其他玩家的怀疑方向。注意，发言限制在100字以内"

sys_3 = ("""发言时请注意风格规范：我们正在玩的狼人杀是一个接近纳什均衡策略的游戏，请你假设其他玩家会忽略不包含有效信息的内容，尽量
         多做针对具体的玩家的分析（无论分析是真是假）而不是使用情感打动其他玩家，少说空话和废话。""")

# User prompt: 指导AI生成狼人假扮预言家的发言
fake_prophet_prompt = ("你是一名假扮预言家的狼人，请参照以上信息，做出你的发言。"
               "注意，狼人的首要任务是隐藏自己的身份，并误导其他村民的投票。")

user_prompt_2 = "注意，你输出的内容会直接作为发言被其他玩家看到。你的输出内容应当全部为你的发言，无需添加任何额外内容。"
