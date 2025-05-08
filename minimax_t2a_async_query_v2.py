import requests
import json
import os
import time

def get_env_variable(var_name: str) -> str:
    return os.getenv(var_name)

def query_task_status(task_id: int) -> dict:
    group_id = get_env_variable('MINIMAX_GROUP_ID')
    api_key = get_env_variable('MINIMAX_API_KEY')

    url = f"https://api.minimax.chat/v1/query/t2a_async_query_v2?GroupId={group_id}&task_id={task_id}"

    payload = {}
    headers = {
        'authorization': f'Bearer {api_key}',
        'content-type': 'application/json',
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)

def wait_for_task_completion(task_id: int, max_retries: int = 60) -> dict:
    """
    等待任务完成，如果状态为Processing则等待1分钟后重试
    :param task_id: 任务ID
    :param max_retries: 最大重试次数（默认60次，即1小时）
    :return: 任务结果
    """
    retry_count = 0
    while retry_count < max_retries:
        result = query_task_status(task_id)
        status = result.get('status')
        
        if status == 'Processing':
            print(f"任务正在处理中... (第{retry_count + 1}次查询)")
            time.sleep(60)  # 等待1分钟
            retry_count += 1
        elif status in ['Success', 'Failed', 'Expired']:
            return result
        else:
            print(f"未知状态: {status}")
            return result
    
    return {"status": "Timeout", "message": "任务处理超时"}

def get_task_id() -> int:
    """获取用户输入的task_id"""
    while True:
        try:
            task_id = input("\n请输入要查询的任务ID: ")
            return int(task_id)
        except ValueError:
            print("错误：请输入有效的数字ID")

def main():
    print("=== MiniMax 文本转语音任务状态查询 ===")
    
    # 获取用户输入的task_id
    task_id = get_task_id()
    
    print(f"\n开始查询任务ID: {task_id}")
    result = wait_for_task_completion(task_id)
    print("\n查询结果：")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()