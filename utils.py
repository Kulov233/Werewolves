class Message:
    def __init__(self, content, message_type, recipient=None):
        self.content = content
        self.message_type = message_type# 1: 发送给人类玩家, 2: 发送给AI玩家, 3: 发送给全体
        self.recipient = recipient