import requests
import os
import argparse

def get_env_variable(var_name: str) -> str:
    return os.getenv(var_name)

def main():
    parser = argparse.ArgumentParser(description='上传文件到 MiniMax 平台')
    parser.add_argument('file_path', type=str, help='要上传的文件路径')
    args = parser.parse_args()

    file_path = args.file_path
    if not os.path.isfile(file_path):
        print(f"文件不存在: {file_path}")
        return

    group_id = get_env_variable('MINIMAX_GROUP_ID')
    api_key = get_env_variable('MINIMAX_API_KEY')

    url = f"https://api.minimax.chat/v1/files/upload?GroupId={group_id}"

    payload = {'purpose': 't2a_async_input'}
    # payload = {'purpose': 'voice_clone'}
    # payload = {'purpose': 'prompt_audio'}

    files = {'file': open(file_path, 'rb')}

    headers = {
        'authority': 'api.minimax.chat',
        'Authorization': f'Bearer {api_key}',
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    print(response.text)

if __name__ == "__main__":
    main()
