import json
import requests
import os
from datetime import datetime

def get_env_variable(var_name: str) -> str:
    return os.getenv(var_name)

def save_to_json(data: dict, filename: str) -> None:
    """将数据保存为JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_voice_list():
    group_id = get_env_variable('MINIMAX_GROUP_ID')
    api_key = get_env_variable('MINIMAX_API_KEY')

    url = f'https://api.minimax.chat/v1/get_voice'
    headers = {
        'authority': 'api.minimax.chat',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'voice_type': 'all'
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # 检查请求是否成功
        parsed_data = response.json()
        
        # 生成文件名
        filename = f'voice_list_{group_id}.json'
        
        # 保存数据到JSON文件
        save_to_json(parsed_data, filename)
        print(f'数据已成功保存到文件: {filename}')
        
        return parsed_data
    
    except requests.exceptions.RequestException as e:
        print(f'请求失败: {e}')
        return None
    except json.JSONDecodeError as e:
        print(f'JSON解析失败: {e}')
        return None

if __name__ == '__main__':
    voice_data = get_voice_list()
    if voice_data:
        # 可以在这里添加其他数据处理逻辑
        # 例如打印系统音色列表
        if 'system_voice' in voice_data:
            system_voice_ids = [item['voice_id'] for item in voice_data['system_voice']]
            print('系统音色ID列表:', system_voice_ids)