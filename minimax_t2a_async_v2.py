import requests
import json
import os
from datetime import datetime

def get_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"环境变量 {var_name} 未设置")
    return value

def save_response(text_file_id: int, response_data: str, headers: dict):
    """保存响应内容到文件"""
    # 创建logs目录（如果不存在）
    os.makedirs('logs', exist_ok=True)
    
    # 生成时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 构建文件名
    filename = f"logs/task_{text_file_id}_{timestamp}.json"
    
    # 准备保存的数据
    data_to_save = {
        "timestamp": timestamp,
        "text_file_id": text_file_id,
        "response": json.loads(response_data),
        "headers": {
            "Trace-ID": headers.get('Trace-ID'),
            # 可以根据需要添加其他需要保存的headers
        }
    }
    
    # 保存到文件
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    
    return filename

def create_t2a_request(text_file_id: int):
    """创建文本转语音的请求"""
    return json.dumps({
        "model": "speech-02-turbo",
        "text_file_id": text_file_id,
        "language_boost": "auto",
        "voice_setting": {
            "voice_id": "m-lichengzhi-01",
            "speed": 1,
            "vol": 4,
            "pitch": 0,
            "emotion": "neutral"
        },
        "pronunciation_dict": {
            "tone": [
                "草地/(cao3)(di1)"
            ]
        },
        "audio_setting": {
            "audio_sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 2
        }
    })

def get_text_file_id() -> int:
    """获取用户输入的text_file_id"""
    while True:
        try:
            text_file_id = input("\n请输入要处理的文本文件ID: ")
            return int(text_file_id)
        except ValueError:
            print("错误：请输入有效的数字ID")

def main():
    print("=== MiniMax 文本转语音异步任务 ===")
    
    # 获取用户输入的text_file_id
    text_file_id = get_text_file_id()

    group_id = get_env_variable('MINIMAX_GROUP_ID')
    api_key = get_env_variable('MINIMAX_API_KEY')
    
    url = f"https://api.minimax.chat/v1/t2a_async_v2?GroupId={group_id}"

    headers = {
        'authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # 创建请求payload
    payload = create_t2a_request(text_file_id)

    print(f"\n正在处理文本文件ID: {text_file_id}")
    response = requests.request("POST", url, headers=headers, data=payload)
    
    # 保存响应内容到文件
    saved_file = save_response(text_file_id, response.text, response.headers)
    
    # 打印响应内容和保存位置
    print("\n响应内容：")
    print(json.dumps(json.loads(response.text), ensure_ascii=False, indent=2))
    print(f"\nTrace-ID: {response.headers['Trace-ID']}")
    print(f"\n响应内容已保存到文件：{saved_file}")

if __name__ == "__main__":
    main()