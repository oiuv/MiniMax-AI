import subprocess
import requests
import os
from datetime import datetime


def get_env_variable(var_name: str) -> str:
    return os.getenv(var_name)


group_id = get_env_variable('MINIMAX_GROUP_ID')
api_key = get_env_variable('MINIMAX_API_KEY')

url = "https://api.minimax.chat/v1/music_generation"

refer_voice = 'vocal-2025020811390925-MgTTWloT'
refer_instrumental = 'instrumental-2025020811390925-fRmJBzrU'
refer_vocal = 'YYSLS000'

payload = {
            'refer_voice': refer_voice,
            'refer_instrumental': refer_instrumental,
            'refer_vocal': refer_vocal,
            'lyrics': '##煨烟火开题序篇花缀眉眼边\n误认谁家女儿作神仙\n提灯罗袖堪堪遮了半面\n谎说翩翩赴人间一宴\n转个糖画尝鲜 巷口戏法开眼\n看官你捧场赏个钱\n兜来清辉泼染衣衫两件\n长街灯如昼叫做上元\n##',
            'model': 'music-01',
            'audio_setting': '{"sample_rate":44100,"bitrate":256000,"format":"mp3"}'
        }

headers = {
    'authorization': 'Bearer ' + api_key,
}


def audio_play(data: str) -> bytes:
    mpv_command = ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"]
    mpv_process = subprocess.Popen(
        mpv_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # convert hex into bytes
    decoded_hex = bytes.fromhex(data)
    mpv_process.stdin.write(decoded_hex)  # type: ignore
    mpv_process.stdin.flush()  # type: ignore

    if mpv_process.stdin:
        mpv_process.stdin.close()
    mpv_process.wait()

    return decoded_hex


response = requests.post(url, headers=headers, data=payload)
print(response.text)
audio_hex = response.json()['data']['audio']
audio = audio_play(audio_hex)

# 获取当前时间戳
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

# 构造文件名，包含 voice_id 和时间戳
file_name = f'{refer_voice}_{current_time}.MP3'
# 将结果保存到以 voice_id 命名的文件中
with open(file_name, 'wb') as file:
    file.write(audio)

print(f"音频已保存为: {file_name}")
