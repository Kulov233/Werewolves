from typing import List, Optional, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from player import Player

class Message:
    def __init__(
        self,
        content: str,
        message_type: str,
        recipients: Union['Player', List['Player'], str],
        expect_reply: bool = False,
        tools_functions: Optional[List[str]] = None
    ):
        """
        :param content: 消息内容。
        :param message_type: 消息类型，如 'info' 或 'action_request'。
        :param recipients: 消息接收者，可以是 Player 对象、Player 对象列表或 'all'。
        :param expect_reply: 是否需要回复。
        :param tools_functions: 需要发送给AI的工具函数名称列表。
        """
        self.content = content
        self.message_type = message_type
        self.recipients = recipients
        self.expect_reply = expect_reply
        self.tools_functions = tools_functions or []

def send_message(mes: Message, all_players: List['Player']) -> Optional[dict]:
    """
    发送消息给指定的接收者。
    :param mes: Message 对象。
    :param all_players: 所有玩家的列表。
    :return: 如果需要回复，返回 {player_name: reply} 的字典。
    """
    from player import Player
    replies = {}
    recipients = mes.recipients
    if recipients == 'all' and all_players:
        recipients = all_players
    elif isinstance(recipients, Player):
        recipients = [recipients]

    for recipient in recipients:
        if recipient.is_human:
            # 对于人类玩家
            print(f"消息给 {recipient.name}: {mes.content}")
            if mes.expect_reply:
                reply = input(f"{recipient.name}, 请输入你的回应: ")
                replies[recipient.name] = reply
        else:
            # 对于AI玩家
            reply = recipient.receive(mes)
            if mes.expect_reply:
                replies[recipient.name] = reply
    if mes.expect_reply:
        return replies


def get_input_from_player(player, prompt):
    message_type = 1 if player.is_human else 2
    mes = Message(content=prompt, message_type=message_type, recipient=player)
    response = send_message(mes)
    return response
