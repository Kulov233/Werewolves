from api import api_key_zhipuai
from zhipuai import ZhipuAI
 
client = ZhipuAI(api_key=api_key_zhipuai) # 填写您自己的APIKey
while True:
    prompt = input("user:")
    response = client.chat.completions.create(
        model="glm-4-0520", # 填写需要调用的模型名称
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    answer = response.choices[0].message.content
    print(answer)