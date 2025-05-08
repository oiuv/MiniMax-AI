import os
import time
import requests
import json


def get_env_variable(var_name: str) -> str:
    return os.getenv(var_name)


group_id = get_env_variable('MINIMAX_GROUP_ID')
api_key = get_env_variable('MINIMAX_API_KEY')


prompt = "[左移,右摇]一个美女在玩魔兽世界网络游戏"
model = "T2V-01-Director" 
output_file_name = "output.mp4" #请在此输入生成视频的保存路径

def invoke_video_generation()->str:
    print("-----------------提交视频生成任务-----------------")
    url = "https://api.minimax.chat/v1/video_generation"
    payload = json.dumps({
      "prompt": prompt,
      "model": model
    })
    headers = {
      'authorization': 'Bearer ' + api_key,
      'content-type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    task_id = response.json()['task_id']
    print("视频生成任务提交成功，任务ID："+task_id)
    return task_id

def query_video_generation(task_id: str):
    url = "https://api.minimax.chat/v1/query/video_generation?task_id="+task_id
    headers = {
      'authorization': 'Bearer ' + api_key
    }
    response = requests.request("GET", url, headers=headers)
    status = response.json()['status']
    if status == 'Preparing':
        print("...准备中...")
        return "", 'Preparing'
    elif status == 'Queueing':
        print("...队列中...")
        return "", 'Queueing'
    elif status == 'Processing':
        print("...生成中...")
        return "", 'Processing'
    elif status == 'Success':
        return response.json()['file_id'], "Finished"
    elif status == 'Fail':
        return "", "Fail"
    else:
        return "", "Unknown"

def fetch_video_result(file_id: str):
    print("---------------视频生成成功，下载中---------------")
    url = "https://api.minimax.chat/v1/files/retrieve?file_id="+file_id
    headers = {
        'authorization': 'Bearer '+api_key,
    }

    response = requests.request("GET", url, headers=headers)
    print(response.text)

    download_url = response.json()['file']['download_url']
    print("视频下载链接：" + download_url)
    with open(output_file_name, 'wb') as f:
        f.write(requests.get(download_url).content)
    print("已下载在："+os.getcwd()+'/'+output_file_name)


if __name__ == '__main__':
    task_id = invoke_video_generation()
    print("-----------------已提交视频生成任务-----------------")
    while True:
        time.sleep(10)

        file_id, status = query_video_generation(task_id)
        if file_id != "":
            fetch_video_result(file_id)
            print("---------------生成成功---------------")
            break
        elif status == "Fail" or status == "Unknown":
            print("---------------生成失败---------------")
            break