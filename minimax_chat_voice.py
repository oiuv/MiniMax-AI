import requests
import json
import subprocess
from typing import Iterator
from datetime import datetime
import logging
import os

# =========================
# 脚本功能简介
# -------------------------
# 本脚本基于 MiniMax ChatCompletion v2 API 实现了一个"语音对话助手"。
# 用户输入文本后，脚本会调用 MiniMax 大模型接口，获取AI回复并实时合成语音流，
# 通过本地 mpv 播放器流式播放AI语音，同时将音频保存为本地mp3文件。
# 适合需要AI语音对话、语音播报等场景。
# 参考API文档：https://platform.minimaxi.com/document/ChatCompletion%20v2?key=66701d281d57f38758d581d0
# =========================

def get_env_variable(var_name: str) -> str:
    """获取环境变量值"""
    return os.getenv(var_name)

# 获取API所需的Group ID和API Key
group_id = get_env_variable('MINIMAX_GROUP_ID')
api_key = get_env_variable('MINIMAX_API_KEY')

# 日志配置
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] - [%(levelname)s]  %(message)s')

# mpv播放器命令，用于流式播放音频（需提前安装mpv，适用于Linux/mac）
mpv_command = ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"]
mpv_process = subprocess.Popen(
    mpv_command,
    stdin=subprocess.PIPE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

token = api_key

def ccv2_audio_stream(text) -> Iterator[bytes]:
    """
    与MiniMax ChatCompletion v2 API交互，获取AI语音流。
    参考API文档：https://platform.minimaxi.com/document/ChatCompletion%20v2?key=66701d281d57f38758d581d0
    :param text: 用户输入的文本
    :return: 音频流的十六进制字符串迭代器
    """
    payload = {
        "model": "abab6.5s-chat",  # 对话模型
        "messages": [
            {
                "role": "system",
                "name": "猫步香水",
                "content": "你是猫步香水，一个抖音游戏主播，只会直播玩游戏《燕云十六声》。"
            },
            {
                "role": "user",
                "name": "用户",
                "content": text
            },
        ],
        "stream": True,  # 开启流式输出
        "tools": [
            {"type": "web_search"}
        ],
        "tool_choice": "auto",
        "max_tokens": 1024,
        "stream_options": {  # 开启语音输出
            "speech_output": True
        },
        "voice_setting": {
            "model": "speech-01-turbo",  # 语音合成模型
            "voice_id": "YYSLS000"       # 语音风格ID
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    logging.info(f"【文本输入】{text}")

    # 发送POST请求，获取流式响应
    response = requests.post("http://api.minimax.chat/v1/text/chatcompletion_v2",
                             headers=headers, json=payload, stream=True)

    logging.info(f"Get response, trace-id: {response.headers.get('Trace-Id')}")
    i = 0
    # 处理Server-Sent Events流
    for line in response.iter_lines(decode_unicode=True):
        if not line.startswith("data:"):
            continue
        i += 1
        logging.debug(f"[sse] data chunck-{i}")
        resp = json.loads(line.strip("data:"))
        if resp.get("choices") and resp["choices"][0].get("delta"):
            delta = resp["choices"][0]["delta"]
            if delta.get("role") == "assistant":  # AI助手回复
                if delta.get("content"):
                    logging.info(f"【文本输出】 {delta['content']}")
                if delta.get("audio_content") and delta["audio_content"] != "":
                    # 返回音频内容（十六进制字符串）
                    yield delta["audio_content"]
                if delta.get("tool_calls"):
                    logging.info(f"【搜索中】...")

def audio_play(audio_stream: Iterator[bytes]):
    """
    播放音频流并保存为本地mp3文件
    :param audio_stream: 由ccv2_audio_stream返回的音频流
    """
    audio = b""
    for chunk in audio_stream:
        if chunk is not None and chunk != '\n':
            decoded_hex = bytes.fromhex(chunk)
            mpv_process.stdin.write(decoded_hex)  # type: ignore
            mpv_process.stdin.flush()
            audio += decoded_hex

    if not audio:
        return

    now = datetime.now().strftime('%Y%m%d-%H%M%S')
    file_name = f'ccv2_audio_{now}.mp3'
    with open(file_name, 'wb') as file:
        file.write(audio)
    logging.info(f"音频文件保存成功: {file_name}")

if __name__ == '__main__':
    # 新增交互循环
    print("欢迎与少东家聊天！输入内容开始对话（输入'exit'或'退出'结束）")
    while True:
        user_input = input("\n你：")
        if user_input.lower() in ("退出", "exit", "再见", "bye"):
            print("对话结束")
            break
            
        # 调用现有的语音对话功能
        audio_play(ccv2_audio_stream(user_input))
