"""
https://platform.minimaxi.com/document/T2A%20V2?key=66719005a427f0c8a5701643

该API支持基于文本到语音的同步生成，单次文本传输最大10000字符。接口本身为无状态接口，即单次调用时，模型所接收到的信息量仅为接口传入内容，不涉及业务逻辑，同时模型也不存储您传入的数据。
该接口支持以下功能：
1. 支持100+系统音色、复刻音色自主选择；
2. 支持音量、语调、语速、输出格式调整；
3. 支持按比例混音功能；
4. 支持固定间隔时间控制；
5. 支持多种音频规格、格式，包括：mp3,pcm,flac,wav。注：wav仅在非流式输出下支持；
6. 支持流式输出。
该接口的适用场景：短句生成、语音聊天、在线社交等
"""

import json
import subprocess
from typing import Iterator
import requests
import os


def get_env_variable(var_name: str) -> str:
    return os.getenv(var_name)


group_id = get_env_variable('MINIMAX_GROUP_ID')
api_key = get_env_variable('MINIMAX_API_KEY')

url = f"https://api.minimax.chat/v1/t2a_v2?GroupId={group_id}"

# 参数配置
# 请求的模型版本：speech-02-hd、speech-02-turbo、speech-01-hd、speech-01-turbo
model = 'speech-02-hd'
# 生成声音的语速，可选范围[0.5,2]，默认值为1.0，取值越大，语速越快。
speed = 1.0
# 生成声音的音量，可选范围（0,10]，默认值为1.0，取值越大，音量越高。
vol = 3.0
# 生成声音的语调，可选范围[-12,12]，默认值为0，（0为原音色输出，取值需为整数）。
pitch = 0
# 情绪参数范围["happy", "sad", "angry", "fearful", "disgusted", "surprised", "neutral"]
emotion = 'happy'
# 生成的音频格式。默认mp3，范围[mp3,pcm,flac,wav]。wav仅在非流式输出下支持。
file_format = 'mp3'
# 生成音频的声道数.默认1：单声道，可选2：双声道
channel = 2

def build_tts_stream_headers(api_key: str) -> dict:
    return {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {api_key}",
    }


def build_tts_stream_body(text: str, voice_id: str) -> str:
    body = {
        "model": "speech-02-hd",
        "text": text,
        "stream": True,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": speed,
            "vol": vol,
            "pitch": pitch,
            "emotion": emotion
        },
        "pronunciation_dict": {
            "tone": [
                "皇上/(bi4)(xia4)",
                "omg/oh my god"
            ]
        },
        "audio_setting": {
            "audio_sample_rate": 32000,
            "bitrate": 128000,
            "format": file_format,
            "channel": channel
        }
    }
    return json.dumps(body)


def call_tts_stream(text: str, voice_id: str) -> Iterator[bytes]:
    headers = build_tts_stream_headers(api_key)
    body = build_tts_stream_body(text, voice_id)

    with requests.post(url, headers=headers, data=body, stream=True) as response:
        if response.status_code == 200:
            buffer = b""
            for chunk in response.iter_content(chunk_size=None):
                buffer += chunk
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    if line.startswith(b'data:'):
                        try:
                            data = json.loads(line[5:])
                            if "data" in data and "extra_info" not in data:
                                yield data["data"].get('audio', b'')
                        except json.JSONDecodeError:
                            continue


def audio_play(audio_stream: Iterator[bytes]) -> bytes:
    audio = b""
    mpv_process = subprocess.Popen(
        ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for chunk in audio_stream:
        if chunk:
            decoded_hex = bytes.fromhex(chunk)
            mpv_process.stdin.write(decoded_hex)  # type: ignore
            mpv_process.stdin.flush()
            audio += decoded_hex

    mpv_process.stdin.close()
    mpv_process.wait()
    return audio


if __name__ == "__main__":
    text = """
义士誓书
<#1#>
契丹入寇，犯我神州。
土为裂陁，民为鱼肉。
任胡纵乱，我岂无人？
四方豪杰，闻义而动。
聚百二十人，同守此关。
今一百一十九人，共下誓书：
山河寸土，誓死不易。
苟渝此盟，神人共殛。

（其下是密密麻麻的姓名与手印）
    """
    # 列出所有可用的 voice_id
    system_voice = ['male-qn-qingse', 'male-qn-jingying', 'male-qn-badao', 'male-qn-daxuesheng', 'female-shaonv', 'female-yujie', 'female-chengshu', 'female-tianmei', 'presenter_male', 'presenter_female', 'audiobook_male_1', 'audiobook_male_2', 'audiobook_female_1', 'audiobook_female_2', 'male-qn-qingse-jingpin', 'male-qn-jingying-jingpin', 'male-qn-badao-jingpin', 'male-qn-daxuesheng-jingpin', 'female-shaonv-jingpin', 'female-yujie-jingpin', 'female-chengshu-jingpin', 'female-tianmei-jingpin', 'clever_boy', 'cute_boy', 'lovely_girl', 'cartoon_pig', 'bingjiao_didi', 'junlang_nanyou', 'chunzhen_xuedi', 'lengdan_xiongzhang', 'badao_shaoye', 'tianxin_xiaoling', 'qiaopi_mengmei', 'wumei_yujie', 'diadia_xuemei', 'danya_xuejie', 'Santa_Claus ', 'Grinch', 'Rudolph', 'Arnold', 'Charming_Santa', 'Charming_Lady', 'Sweet_Girl', 'Cute_Elf', 'Attractive_Girl', 'Serene_Woman']
    voice_ids = ['TV-m01_hd']

    # 循环遍历每个 voice_id，生成并保存音频
    for voice_id in voice_ids:
        # 调用文本到语音流的函数
        audio_chunk_iterator = call_tts_stream(text, voice_id)
        audio = audio_play(audio_chunk_iterator)

        # 将结果保存到以 voice_id 命名的文件中
        file_name = f'{voice_id}_{model}_{emotion}.{file_format}'
        with open(file_name, 'wb') as file:
            file.write(audio)

        print(f"音频已保存为: {file_name}")
