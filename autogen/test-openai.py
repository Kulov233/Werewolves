from openai import OpenAI 
from api import api_key_zhipuai
client = OpenAI(
    api_key=api_key_zhipuai,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
) 
while True:
    prompt = input("user:")
    completion = client.chat.completions.create(
        model="glm-4v",  
        messages=[    
            {"role": "user", "content": prompt},    
        ],
        top_p=0.7,
        temperature=0.9
     ) 
    print(completion.choices[0].message.content)