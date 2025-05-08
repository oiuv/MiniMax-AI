import requests
import json
import os
from datetime import datetime
import argparse

def get_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"环境变量 {var_name} 未设置")
    return value

def save_to_json(data: dict, file_id: int) -> str:
    """将数据保存为JSON文件，返回文件名"""
    timestamp = datetime.now().strftime('%Y%m%d')
    filename = f'file_{file_id}_{timestamp}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename

def retrieve_file(file_id: int):
    try:
        group_id = get_env_variable('MINIMAX_GROUP_ID')
        api_key = get_env_variable('MINIMAX_API_KEY')

        url = f'https://api.minimax.chat/v1/files/retrieve?GroupId={group_id}&file_id={file_id}'
        headers = {
            'authority': 'api.minimax.chat',
            'content-type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        # 打印响应头信息
        print("\n=== 响应头信息 ===")
        for header, value in response.headers.items():
            print(f"{header}: {value}")
        print("=== 响应头信息结束 ===\n")

        # 解析响应数据
        result = response.json()
        
        # 保存到JSON文件
        filename = save_to_json(result, file_id)
        print(f"数据已保存到文件: {filename}")
        
        return result

    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return None
    except Exception as e:
        print(f"发生未知错误: {e}")
        return None

def get_file_id_from_user() -> int:
    while True:
        file_id = input("请输入要获取的文件ID: ").strip()
        if file_id.isdigit():
            return int(file_id)
        else:
            print("文件ID必须为数字，请重新输入。")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='获取 MiniMax 平台文件信息')
    parser.add_argument('file_id', nargs='?', type=int, help='要获取的文件ID')
    args = parser.parse_args()

    if args.file_id is not None:
        file_id = args.file_id
    else:
        file_id = get_file_id_from_user()
    
    print(f"开始获取文件 ID: {file_id} 的信息...")
    result = retrieve_file(file_id)
    
    if result:
        print("文件获取成功！")
    else:
        print("文件获取失败，请检查以下可能的问题：")
        print("1. 文件ID是否有效")
        print("2. 环境变量是否正确设置")
        print("3. API密钥是否有效")
        print("4. 网络连接是否正常")