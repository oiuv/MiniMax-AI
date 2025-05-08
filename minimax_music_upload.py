import requests
import os


def get_env_variable(var_name: str) -> str:
    return os.getenv(var_name)


group_id = get_env_variable('MINIMAX_GROUP_ID')
api_key = get_env_variable('MINIMAX_API_KEY')

url = "https://api.minimax.chat/v1/music_upload"

file_name = '闹元宵.mp3'
file_path = 'music.mp3'

payload = {
    'purpose': 'song'
}
files = [
    ('file', (file_name, open(file_path, 'rb'), 'audio/mpeg'))
]
headers = {
    'authorization': 'Bearer ' + api_key,
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)
print(response.headers.get('Trace-Id'))
print(response.text)