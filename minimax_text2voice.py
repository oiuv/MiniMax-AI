"""
https://platform.minimaxi.com/document/VoiceGeneration?key=669f5af198ff2c57eeb9a0f0

# Voice Generation（文生音色）| 2元/万字符
该API支持基于用户输入的声音性别、声音年龄、声音描述信息，来生成音色（voice_id）；并支持使用该生成的音色（voice_id）在T2A v2、T2A Large v2接口中进行语音生成。
该接口支持以下功能：
1.
支持指定音色性别（男、女两种）、声音年龄（小孩到老人，五种年龄段）；
2.
支持对音色风格进行自定义描述；
3.
支持根据自定义文本内容生成音频，对合成音色进行试听。
该接口的适用场景：基于文本描述，生成符合描述的个性化定制音色，以供语音生成接口使用。
"""

import subprocess
import requests
import json
import os

url = "https://api.minimax.chat/v1/text2voice"
api_key = os.getenv('MINIMAX_API_KEY')

# 声音的性别取值可选：1.male、2.female。
# 声音的年龄取值可选：1.child、2.teenager、3.young、4.middle-aged、5.old。
payload = json.dumps({
    "gender": "female",
    "age": "teenager",
    "voice_desc": [
        "Kind and friendly",
        "Kind and amiable",
        "Kind hearted",
        "Calm tone"
    ],
    "text": "牛牛，你这个小宝贝真是可爱极了！聪明得像个小大人，每次看到你的笑容，心都要化了。你是最棒的小天使！"
})
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}',
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)


mpv_process = subprocess.Popen(
    ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"],
    stdin=subprocess.PIPE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

data = json.loads(response.text)
decoded_hex = bytes.fromhex(data.get('trial_audio'))
mpv_process.stdin.write(decoded_hex)  # type: ignore
mpv_process.stdin.flush()
mpv_process.stdin.close()
mpv_process.wait()

with open(data.get('voice_id') + '.mp3', 'wb') as file:
    file.write(decoded_hex)
