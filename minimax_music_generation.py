import requests
import json
import os
from datetime import datetime


def get_env_variable(var_name: str) -> str:
    return os.getenv(var_name)


group_id = get_env_variable('MINIMAX_GROUP_ID')
api_key = get_env_variable('MINIMAX_API_KEY')

# 修正的端点URL
url = f"https://api.minimaxi.com/v1/music_generation?GroupId={group_id}"

# 测试音乐生成
def generate_music_example():
    """音乐生成示例"""
    
    payload = {
        "model": "music-1.5",
        "prompt": "独立民谣,忧郁,内省,夜晚,咖啡馆,治愈",
        "lyrics": """[Intro]
轻柔的吉他前奏
[Verse 1]
夜色温柔心事轻放
街灯下的影子拉长
独自坐在咖啡馆
品味着孤独的香
[Chorus]
让音乐带走忧伤
治愈每个孤单的夜晚
[Verse 2]
回忆如潮水般涌来
你的笑容在记忆里
像月光一样明亮
温暖着我的心房
[Outro]
音乐渐渐结束
留下美好的回忆""",
        "audio_setting": {
            "sample_rate": 44100,
            "bitrate": 256000,
            "format": "mp3"
        }
    }

    headers = {
        'authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print("响应结果:", json.dumps(result, indent=2, ensure_ascii=False))
        
        if 'data' in result and 'audio' in result['data']:
            audio_hex = result['data']['audio']
            
            # 保存音频文件
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_music_{current_time}.mp3"
            
            # 将十六进制转换为字节
            audio_bytes = bytes.fromhex(audio_hex)
            
            with open(filename, 'wb') as f:
                f.write(audio_bytes)
            
            print(f"✅ 音乐生成完成: {filename}")
            print(f"📊 文件大小: {len(audio_bytes):,} bytes")
            return filename
        else:
            print("❌ 响应格式错误:", result)
            return None
            
    except Exception as e:
        print(f"❌ 音乐生成失败: {e}")
        return None


if __name__ == "__main__":
    if not group_id or not api_key:
        print("❌ 请先设置环境变量 MINIMAX_GROUP_ID 和 MINIMAX_API_KEY")
    else:
        generate_music_example()