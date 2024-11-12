import autogen
from api import api_key_zhipuai
config_list = [
    {
        'model': 'glm-4-plus',
        'api_key': api_key_zhipuai,#输入用户自己的api_key
        'base_url': 'https://open.bigmodel.cn/api/paas/v4/',
        'api_type': 'openai'
    }
]

# 创建"assistant" 代理
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={
        "cache_seed": 42,  # seed 用户缓存中间结果
        "config_list": config_list, 
        "temperature": 0,  
    },  
)
# 创建"user_proxy"代理
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",#可更改为ALWAYS来进行人工对话
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,  
    },
)
# 交互循环：用户可以输入问题
while True:
    # 用户输入问题
    user_message = input("请问你有什么问题？(输入 'exit' 退出): ")
    
    # 退出循环
    if user_message.lower() == "exit":
        print("结束对话。")
        break

    # 确保输入非空，然后代理接收消息
    if user_message.strip():
        response = user_proxy.initiate_chat(
            assistant,
            message=user_message
        )
        
        # 输出助手的回复
        print("Assistant的回答:", response.content if hasattr(response, 'content') else "没有收到回应")
    else:
        print("请输入有效的问题。")
