import random
import json
from typing import List, Optional, Annotated
from tools_register import register_tool, dispatch_tool

@register_tool
def wolf_kill(
    wolf_indexs: Annotated[List[int], "狼人序号列表", True],
    alive_player_indexs: Annotated[List[int], "存活玩家序号列表", True]
) -> int:
    """
    狼人选择猎杀目标的工具
    :param wolf_indexs: 狼人序号列表
    :param alive_player_indexs: 存活玩家序号列表
    :return: 被猎杀的玩家序号
    """
    potential_targets = [index for index in alive_player_indexs if index not in wolf_indexs]
    victim_index = random.choice(potential_targets)
    return victim_index

@register_tool
def vote_exile(
    player_index: Annotated[int, "投票玩家的序号", True],
    alive_player_indexs: Annotated[List[int], "存活玩家序号列表", True]
) -> Optional[int]:
    """
    玩家进行投票放逐的工具
    :param player_index: 投票玩家的序号
    :param alive_player_indexs: 存活玩家序号列表
    :return: 被投票的玩家序号，若不投票则返回 None
    """
    if random.choice([True, False]):
        vote_targets = [index for index in alive_player_indexs if index != player_index]
        voted_index = random.choice(vote_targets)
        return voted_index
    else:
        return None

@register_tool
def seer_vision(
    seer_name: Annotated[str, "预言家的名字", True],
    alive_player_names: Annotated[List[str], "存活玩家名字列表", True],
    player_roles: Annotated[dict, "玩家角色字典", True]
) -> str:
    """
    预言家查验身份的工具
    :param seer_name: 预言家的名字
    :param alive_player_names: 存活玩家名字列表
    :param player_roles: 玩家角色字典，键为玩家名字，值为角色
    :return: 被查验的玩家名字和身份
    """
    targets = [name for name in alive_player_names if name != seer_name]
    checked_name = random.choice(targets)
    checked_role = player_roles[checked_name]
    result = f"{checked_name} 的身份是 {checked_role}"
    return result

