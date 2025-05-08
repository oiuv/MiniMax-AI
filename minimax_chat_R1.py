import os
from openai import OpenAI


def get_env_variable(var_name: str) -> str:
    return os.getenv(var_name)


group_id = get_env_variable('MINIMAX_GROUP_ID')
api_key = get_env_variable('MINIMAX_API_KEY')


url = f"https://api.minimax.chat/v1/text/chatcompletion_v2"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


client = OpenAI(api_key=api_key, base_url="https://api.minimax.chat/v1")

response = client.chat.completions.create(
    model="DeepSeek-R1",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    stream=True
)

for chunk in response:
    print(chunk)
