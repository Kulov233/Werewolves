from typing import Literal

class Message:
    def __init__(self, content, message_type: Literal["sysinfo", "chat", "vote", "kill", "check"], recipient=None, req_reply: bool = False):
        """

        :param content: 信息内容，文字
        :param message_type: 信息类型。TODO: 同步添加新类型，例如女巫和守卫
        :param recipient: 接收者，明确发送到的角色。TODO: 如果只分成AIPlayer和HumanPlayer两个类，就不需要路由转发了。
        :param req_reply: 是否需要回复。
        """
        self.content = content
        self.message_type = message_type# 1: 发送给人类玩家, 2: 发送给AI玩家, 3: 发送给全体
        self.recipient = recipient
        self.req_reply = req_reply
        # TODO: 修改这个类使其更完整，并方便AI端处理
        # TODO: 可能需要添加其他方法，目前还没想到