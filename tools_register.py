# tools_register.py

import json
import inspect
from typing import Callable, Dict, Any, get_origin, Annotated
from types import GenericAlias

# 存储已注册的工具函数
registered_tools: Dict[str, Callable] = {}
tool_descriptions = []

def register_tool(func: Callable) -> Callable:
    """
    注册工具函数，供大模型调用。
    """
    tool_name = func.__name__
    tool_description = inspect.getdoc(func).strip() or "No description provided."
    python_params = inspect.signature(func).parameters
    tool_params = {}
    for name, param in python_params.items():
        annotation = param.annotation
        if annotation is inspect.Parameter.empty:
            raise TypeError(f"Parameter `{name}` missing type annotation")
        if get_origin(annotation) != Annotated:
            raise TypeError(f"Annotation type for `{name}` must be typing.Annotated")
        typ, (description, required) = annotation.__args__, annotation.__metadata__
        tool_params[name] = {
            "type": str(typ),
            "description": description,
            "required": required,
        }
    # 存储工具的描述信息
    tool_def = {
        "name": tool_name,
        "description": tool_description,
        "parameters": tool_params,
    }
    tool_descriptions.append(tool_def)
    registered_tools[tool_name] = func
    return func

def dispatch_tool(tool_name: str, code: str, session_id: str) -> Any:
    """
    调用已注册的工具函数。

    :param tool_name: 工具函数名称
    :param code: JSON字符串，包含工具函数的参数
    :param session_id: 会话ID
    :return: 工具函数的返回值
    """
    if tool_name not in registered_tools:
        raise ValueError(f"未找到名为 '{tool_name}' 的工具函数")
    
    # 解析JSON字符串，获取参数
    try:
        params = json.loads(code)
    except json.JSONDecodeError as e:
        raise ValueError(f"无法解析工具参数的JSON字符串：{e}")
    
    func = registered_tools[tool_name]
    
    try:
        # 调用工具函数并返回结果
        result = func(**params)
        return result
    except Exception as e:
        raise RuntimeError(f"调用工具函数 '{tool_name}' 时出错：{e}")

def get_tools() -> list:
    """
    获取所有已注册工具的描述信息
    """
    return tool_descriptions
