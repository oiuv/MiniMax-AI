import requests
import json
import os


def get_env_variable(var_name: str) -> str:
    return os.getenv(var_name)


group_id = get_env_variable('MINIMAX_GROUP_ID')
api_key = get_env_variable('MINIMAX_API_KEY')

url = "https://api.minimax.chat/v1/image_generation"

payload = json.dumps({
  "model": "image-01", 
  "prompt": "a beautiful chinese girl, full-body stand front view image :25, outdoor, smile, dancing, full-body image, beach, Fashion photography of 90s, documentary, Film grain, photorealistic",
  "aspect_ratio": "16:9",
  "response_format": "url",
  "n": 3,
  "prompt_optimizer": True
})
headers = {
  'Authorization': f'Bearer {api_key}',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)