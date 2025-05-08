import os
import requests

# ==========================================
# 脚本功能简介
# ------------------------------------------
# 本脚本用于删除 MiniMax 平台上的自定义音色（支持"音色克隆"或"文生音色生成"两类）。
# 通过调用 MiniMax 提供的 delete_voice 接口，传入 voice_type 和 voice_id 实现音色删除。
# 适用于音色管理、音色清理等场景。
# 参考API文档：https://platform.minimaxi.com/document/eCLyrV1gIFJ5rhWeoYQZRhaV?key=670ddd7136edb220034f7f38
# ==========================================

def get_env_variable(var_name: str) -> str:
    """获取环境变量值"""
    return os.getenv(var_name)

# 获取API所需的Group ID和API Key
group_id = get_env_variable('MINIMAX_GROUP_ID')
api_key = get_env_variable('MINIMAX_API_KEY')

# MiniMax 删除音色接口URL
url = "https://api.minimax.chat/v1/delete_voice"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
params = {"GroupId": group_id}

# payload参数说明：
# voice_type: 必填，音色类型。可选值："voice_cloning"（克隆的音色）或 "voice_generation"（文生音色生成的音色）
# voice_id:   必填，要删除的音色ID
payload = {
    "voice_type": "voice_generation", # 取值范围"voice_cloning"/"voice_generation"
    "voice_id": "ttv-voice-2025020710370425-CYHd9Dyw"
}

try:
    # 发送POST请求，删除指定音色
    response = requests.post(
        url,
        headers=headers,
        params=params,
        json=payload
    )
    
    # 输出响应信息
    print(f"状态码: {response.status_code}")
    print("响应内容:")
    print(response.text)
    
except requests.exceptions.RequestException as e:
    # 网络请求异常处理
    print(f"请求出错: {e}")