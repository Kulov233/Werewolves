from typing import List, Literal, Dict



class Prompts:
    def __init__(self,
                game_specified_prompt = "本局游戏中有四个玩家，其中有两个狼人、四个平民。",
                style_prompt: str = "发言时请注意风格规范：我们正在玩的狼人杀是一个接近纳什均衡策略的游戏，"
                                     "请你假设其他玩家会忽略不包含有效信息的内容，尽量多做针对具体的玩家的分析"
                                     "（无论分析是真是假）而不是使用情感打动其他玩家，少说空话和废话。",
                output_limits: int = 100
                 ):
        self.intro = """
                你正在参与一款名为狼人杀的桌游。游戏中有多个角色，每个角色都有其特殊能力和胜利目标。
                游戏分为夜晚和白天两个阶段，会循环执行
                狼人的能力是每个夜晚可以秘密杀死一位玩家，胜利目标是在有狼人存活的情况下杀死所有非狼人角色；
                平民没有特殊能力，胜利目标是消灭所有狼人；
                预言家的特殊能力是每夜可以秘密查验一名玩家的身份，胜利目标是消灭所有狼人。
                此外，在每个白天阶段，所有存活的玩家会轮流进行一次发言，然后进行一次投票，得票最高的玩家将会被处决（杀死）。
                如果平票，则存活的其他玩家需要在平票的角色之间重新进行一次投票。
                """
        self.character_prompts = {
            "狼人":  "你的角色是狼人，属于狼人阵营。你的特殊能力是每晚可以和其他狼人一起杀死一位其他玩家。"
                    "你的任务是尽可能隐藏自身身份，并尽可能塑造自身的好人形象，误导其他玩家的投票。",
            "平民":   "你的角色是平民，属于好人阵营。没有特殊能力。你的任务是想办法从对话中找出狼人，并尽可能发动大家向他投票。此外，可以想办法保护好人阵营的特殊角色。",
            "预言家": "你的角色是预言家，属于好人阵营。你的特殊能力是每晚可以查验一位玩家的身份。"
                     "你的任务是指导好人阵营进行投票，找出真正的狼人。你可以隐藏身份来避免太早被狼人杀死，"
                      "但如果你发现有狼人冒充预言家，一定要站出来用真实信息反驳他。"

        }

        self.game_specified_prompt = game_specified_prompt
        self.output_limits = output_limits
        self.style_prompt = style_prompt


    def generate_system_prompt(self,
            identity: Literal["狼人", "平民", "预言家"] = "平民",
        ):

        system_prompt = [
            {"role": "system", "content": f"介绍：{self.intro}\n"},
            {"role": "system", "content": f"{self.game_specified_prompt}\n"},
            {"role": "system", "content": f"你的身份是：{identity}。"},
            {"role": "system", "content": f"角色策略：{self.character_prompts[identity]}"}
        ]
        return system_prompt

    def generate_past_messages(self, previous_messages: List[Dict[str, str]] = None):
        """

        :param previous_messages: List[Dict[str, str]], 格式为{"speaker": "", "content", ""}
        :return: 处理好的过去消息列表
        """

        past_prompt = "以下是之前玩家发言的内容。"
        processed_messages = []
        for message in previous_messages:
            speaker = message["speaker"]
            if speaker.isnumeric():
                speaker += '号'
            processed_messages += [f"{speaker}：{message["content"]}"]
        result = [
            {"role": "system", "content": past_prompt},
            {"role": "system", "content": '\n'.join(processed_messages)}
        ]
        return result

    def generate_full_messages(self,
                               identity: Literal["狼人", "平民", "预言家"] = "平民",
                               previous_messages: List[Dict[str, str]] = None):
        system_messages = self.generate_system_prompt(identity)
        past_messages = self.generate_past_messages(previous_messages)
        user_messages = [
            {"role": "user", "content": self.style_prompt},
            {"role": "user", "content": "接下来，请参照以上信息做出你的发言。"
                                        "注意，你输出的内容会直接作为发言被其他玩家看到。"
                                        "你的输出内容应当全部为你的发言，无需添加任何额外内容。"
                                        f"发言限制在{self.output_limits}字以内。"}
        ]

        return system_messages + past_messages + user_messages




A_prompt = "A(狼人): 昨晚是个平安夜。我们应该仔细观察今天的发言，看看有没有不一致的地方。"

B_prompt = "B(身份不明确): 我没有什么特别的线索，但我觉得我们应该听听预言家的意见，看看他有没有什么线索可以分享。"

sys_2 = "作为假扮的预言家，需要在发言中巩固你的预言家形象并试图引导其他玩家的怀疑方向。注意，发言限制在100字以内"

sys_3 = ("""发言时请注意风格规范：我们正在玩的狼人杀是一个接近纳什均衡策略的游戏，请你假设其他玩家会忽略不包含有效信息的内容，尽量
         多做针对具体的玩家的分析（无论分析是真是假）而不是使用情感打动其他玩家，少说空话和废话。""")

# User prompt: 指导AI生成狼人假扮预言家的发言
fake_prophet_prompt = ("你是一名假扮预言家的狼人，请参照以上信息，做出你的发言。"
               "注意，狼人的首要任务是隐藏自己的身份，并误导其他村民的投票。")

user_prompt_2 = "注意，你输出的内容会直接作为发言被其他玩家看到。你的输出内容应当全部为你的发言，无需添加任何额外内容。"
