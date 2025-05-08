import requests
import json
import os


def get_env_variable(var_name: str) -> str:
    return os.getenv(var_name)


group_id = get_env_variable('MINIMAX_GROUP_ID')
api_key = get_env_variable('MINIMAX_API_KEY')

purpose = 't2a_async_input'
file_id = 234318506328179


url = f'https://api.minimax.chat/v1/files/delete?GroupId={group_id}'
headers = {
    'authority': 'api.minimax.chat',
    'content-type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

payload = {
    'purpose': purpose,
    'file_id': file_id,
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response.text)