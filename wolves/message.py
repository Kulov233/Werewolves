from typing import List, Optional, Union, Literal, Any, TYPE_CHECKING


if TYPE_CHECKING:
    from player import Player

class Message:
    def __init__(
        self,
        content: str,
        type: Literal["info", "info_team", "reply", "speak", "vote", "kill", "check", "witch", "guard"],
        recipients: Union['Player', List['Player'], str],
        expect_reply: bool = False,
        special_info: dict[str, Any] = None,
        tools_functions: Optional[List[str]] = None
    ):
        """
        :param content: 消息内容。
        :param type: 消息类型，如 'info' 或 'action_request'。
        :param recipients: 消息接收者，可以是 Player 对象、Player 对象列表或 'all'。
        :param expect_reply: 是否需要回复。
        :param special_info: 特殊信息，如女巫的解药和毒药数量。
        :param tools_functions: 需要发送给AI的工具函数名称列表。
        """
        self.content = content
        self.type = type
        self.recipients = recipients
        self.expect_reply = expect_reply
        self.special_info = special_info
        self.tools_functions = tools_functions or []

def send_message(mes: Message, all_players: List['Player'],
                 alive_players: List['Player']=None) -> Optional[dict]:
    """
    发送消息给指定的接收者。
    :param alive_players: 目前还活着的玩家序号名单，vote/kill/witch等行动需要用
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
            print(f"消息给 {recipient.index}号玩家: {mes.content}")
            if mes.expect_reply:
                reply = input(f"{recipient.index}号玩家, 请输入你的回应: ")
                replies[recipient.index] = reply
        else:
            # 对于AI玩家
            reply = recipient.receive(mes, alive_players)
            if mes.expect_reply:
                replies[recipient.index] = reply
    if mes.expect_reply:
        return replies
