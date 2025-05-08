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
VOICE_ID = "m-lichengzhi-01_hd"  # 性别-名称-编号[_hd]，如需更换音色ID请在此处修改
TEXT = """
各位同学下午好。在中午的休息之后，我们来讨论优先权和超级优先权的规则。
今天我们将讲解这个相对抽象的规则，单从法条来看，确实体现了民法条文的特点。
法条中的表达虽然不算生僻，但组合起来的含义却并不容易理解，这需要我们认真思考。
在准备理解这些内容时，大家可能会遇到一些困难，这一点非常明显。
大家也知道，我国的民法典和这些制度，是在借鉴海外法律实践的基础上形成的。
这种借鉴有时来自于所谓的欧陆国家，欧洲大陆国家有时候受到英美国家的影响。例如，这种超级限制规则源自美国的统一商法典。
这个域外法律制度被称为PMSI，这是一个相当新颖的说法。P代表Purchase，意思是购买；M代表Money，指的是购置款；SI代表Security Interest，也就是担保权益，具体来说是购置款的担保权益。
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
