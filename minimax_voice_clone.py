"""
https://platform.minimaxi.com/document/Voice%20Cloning?key=66719032a427f0c8a570165b

# 快速复刻（Voice Cloning）| 9.9元/音色，试听字符收费：2元/万字符。
本接口支持个人认证及企业认证用户调用。接口本身为无状态接口，即单次调用时，模型所接收到的信息量仅为接口传入内容，不涉及业务逻辑，同时模型也不存储您传入的数据。
本接口适用场景：IP复刻、音色克隆等需要快速复刻某一音色的相关场景。
本接口支持单、双声道复刻声音，支持按照指定音频文件快速复刻相同音色的语音。
注：
调用本接口获得复刻音色时，不会立即收取音色复刻费用。音色的复刻费用将在首次使用此复刻音色进行语音合成时收取（不包含本接口内的试听行为）。

本接口产出的快速复刻音色为临时音色，如您希望永久保留某复刻音色，请于48小时内在任意T2A语音合成接口中调用该音色（不包含本接口内的试听行为）；否则，该音色将被删除。
"""

import json
import requests
import os

# ====== 便于修改的参数区域 ======
VOICE_ID = "MyVoice01_hd"  # 英文字母开头，至少8位，可用字母、数字、下划线和中划线，末尾只能字母或数字
TEXT = """
阿然怕挑不出最好的荷花酥，所以阿然问了刘奶奶和爹爹，这里面最漂亮的荷花酥是哪一个？
他们都和她说，是这一个。
荷花酥脆得很，于是阿然得轻一点，再轻一点，把荷花酥放在了桌子最中间。
但她不知道要去哪里找你，江湖人总是到处跑，你总是有很多地方可以去。
她唯一找到你的那次，是跨过南门百坊，摔了好多跤，听到好多好多声音，终于在来苏蒙学听到了你的声音。
可是，这里离她唯一找到你的来苏蒙学，太远太远了，要是荷花酥碎掉了怎么办？
于是阿然只能和荷花酥一起在这里等你。
"""
MODEL = "speech-02-hd"  # 可选项：speech-02-hd speech-02-turbo speech-01-hd speech-01-turbo
# ============================

def get_env_variable(var_name: str) -> str:
    return os.getenv(var_name)


def get_file_id_from_user() -> int:
    """提示用户输入 file_id，并校验输入有效性"""
    while True:
        file_id = input("请输入要用于音色复刻的音频 file_id（仅数字）: ").strip()
        if file_id.isdigit():
            return int(file_id)
        else:
            print("file_id 必须为数字，请重新输入。")


group_id = get_env_variable('MINIMAX_GROUP_ID')
api_key = get_env_variable('MINIMAX_API_KEY')


# 用户输入 file_id，避免误操作
file_id = get_file_id_from_user()

# 音频复刻
url = f"https://api.minimax.chat/v1/voice_clone?GroupId={group_id}"
payload2 = json.dumps({
    "file_id": file_id,
    "voice_id": VOICE_ID,
    "text": TEXT,  # 复刻试听内容参数，限制2000字符以内
    "model": MODEL
})
headers2 = {
    'authorization': f'Bearer {api_key}',
    'content-type': 'application/json'
}
response = requests.request("POST", url, headers=headers2, data=payload2)
print(response.text)
