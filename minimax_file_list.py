import json
import requests
import os
from typing import List, Dict, Optional

def get_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"环境变量 {var_name} 未设置")
    return value

def save_to_json(data: dict, purpose: str) -> str:
    """将数据保存为JSON文件，文件名使用purpose命名"""
    filename = f'files_{purpose}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename

def get_file_list(purpose: str) -> Optional[Dict]:
    """获取指定purpose的文件列表"""
    try:
        group_id = get_env_variable('MINIMAX_GROUP_ID')
        api_key = get_env_variable('MINIMAX_API_KEY')

        url = f'https://api.minimax.chat/v1/files/list?GroupId={group_id}&purpose={purpose}'
        headers = {
            'authority': 'api.minimax.chat',
            'content-type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        # 保存到JSON文件
        filename = save_to_json(result, purpose)
        print(f"Purpose [{purpose}] 的文件列表已保存到: {filename}")
        
        return result

    except requests.exceptions.RequestException as e:
        print(f"请求错误 [{purpose}]: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析错误 [{purpose}]: {e}")
        return None
    except Exception as e:
        print(f"发生未知错误 [{purpose}]: {e}")
        return None

def get_all_purpose_files():
    """获取所有purpose类型的文件列表"""
    purposes = [
        't2a_async_input',    # 文本转语音
        'retrieval',          # 知识库检索
        'fine-tune',          # 模型finetune
        'fine-tune-result',   # 模型finetune训练结果
        'voice_clone',        # 快速复刻原始文件
        'prompt_audio',       # 音色复刻的示例音频
        'assistants',         # 助手
        'role-recognition'    # 文本角色分类
    ]
    
    results = {}
    for purpose in purposes:
        print(f"\n正在获取 {purpose} 类型的文件列表...")
        result = get_file_list(purpose)
        if result:
            results[purpose] = result
            print(f"成功获取 {purpose} 类型的文件列表")
        else:
            print(f"获取 {purpose} 类型的文件列表失败")
    
    return results

if __name__ == '__main__':
    print("开始获取所有类型的文件列表...")
    results = get_all_purpose_files()
    
    # 打印统计信息
    print("\n=== 获取结果统计 ===")
    for purpose, result in results.items():
        if 'files' in result:
            file_count = len(result['files'])
            print(f"{purpose}: {file_count} 个文件")
        else:
            print(f"{purpose}: 获取失败或无文件")
    print("=== 统计结束 ===")