# 同步语音合成WebSocket API文档

## 接口地址
- **WebSocket地址**: `wss://api.minimaxi.com/ws/v1/t2a_v2`

## 功能特性
- ✅ 实时流式语音合成
- ✅ 支持长文本分段合成
- ✅ 低延迟音频流输出
- ✅ 支持音频播放控制
- ✅ 支持自定义停顿时间

## 建立连接

### 连接步骤
1. 使用WebSocket库建立连接
2. 在请求头中添加Authorization
3. 等待服务器返回`connected_success`事件

### 连接请求头
```
Authorization: Bearer YOUR_API_KEY
```

### 连接成功响应
```json
{
    "session_id": "xxxx",
    "event": "connected_success",
    "trace_id": "0303a2882bf18235ae7a809ae0f3cca7",
    "base_resp": {
        "status_code": 0,
        "status_msg": "success"
    }
}
```

## 任务流程

### 1. 任务开始 (task_start)
发送任务开始事件，正式开始合成任务

#### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| event | string | ✅ | 固定值: "task_start" |
| model | string | ✅ | 模型选择: speech-02-hd, speech-02-turbo, speech-01-hd, speech-01-turbo |
| voice_setting | object | ✅ | 声音设置 |
| audio_setting | object | ✅ | 音频设置 |
| emotion | string | ❌ | 情绪控制: happy, sad, angry, fearful, disgusted, surprised, neutral |
| pronunciation_dict | object | ❌ | 发音字典 |
| language_boost | string | ❌ | 语言增强 |
| voice_modify | object | ❌ | 声音效果器 |

#### voice_setting参数
```json
{
    "voice_id": "female-chengshu",
    "speed": 1.0,
    "vol": 1.0,
    "pitch": 0,
    "emotion": "happy"
}
```

#### audio_setting参数
```json
{
    "sample_rate": 32000,
    "bitrate": 128000,
    "format": "mp3",
    "channel": 1
}
```

#### 音色列表
| 音色ID | 描述 |
|--------|------|
| **中文音色** |
| male-qn-qingse | 青涩青年音色 |
| male-qn-jingying | 精英青年音色 |
| male-qn-badao | 霸道青年音色 |
| male-qn-daxuesheng | 青年大学生音色 |
| female-shaonv | 少女音色 |
| female-yujie | 御姐音色 |
| female-chengshu | 成熟女性音色 |
| female-tianmei | 甜美女性音色 |
| **特色音色** |
| clever_boy | 聪明男童 |
| cute_boy | 可爱男童 |
| lovely_girl | 萌萌女童 |
| cartoon_pig | 卡通猪小琪 |
| bingjiao_didi | 病娇弟弟 |
| junlang_nanyou | 俊朗男友 |
| chunzhen_xuedi | 纯真学弟 |
| lengdan_xiongzhang | 冷淡学长 |
| badao_shaoye | 霸道少爷 |
| tianxin_xiaoling | 甜心小玲 |
| qiaopi_mengmei | 俏皮萌妹 |
| wumei_yujie | 妩媚御姐 |
| diadia_xuemei | 嗲嗲学妹 |
| danya_xuejie | 淡雅学姐 |
| **节日音色** |
| Santa_Claus | 圣诞老人 |
| Grinch | 格林奇 |
| Rudolph | 驯鹿鲁道夫 |
| Arnold | 阿诺德 |
| Charming_Santa | 魅力圣诞老人 |
| Charming_Lady | 魅力女士 |
| Sweet_Girl | 甜美女孩 |
| Cute_Elf | 可爱精灵 |
| Attractive_Girl | 迷人女孩 |
| Serene_Woman | 宁静女士 |

### 2. 任务继续 (task_continue)
发送文本片段进行语音合成

#### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| event | string | ✅ | 固定值: "task_continue" |
| text | string | ✅ | 待合成文本，<10000字符 |

#### 文本格式说明
- 支持换行符作为段落分隔
- 支持自定义停顿时间: `<#x#>` (x=0.01-99.99秒)
- 示例: `你好<#2#>世界` (停顿2秒)

#### 返回参数
| 参数 | 类型 | 说明 |
|------|------|------|
| audio | string | hex编码的音频数据 |
| audio_length | int64 | 音频时长(毫秒) |
| audio_sample_rate | int64 | 采样率 |
| audio_size | int64 | 音频大小(字节) |
| usage_characters | int64 | 计费字符数 |
| is_final | bool | 是否为最终响应 |

### 3. 任务结束 (task_finish)
结束当前任务并关闭连接

#### 请求参数
```json
{
    "event": "task_finish"
}
```

## 完整流程示例

### Python WebSocket示例

```python
import asyncio
import websockets
import json
import ssl
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO

async def establish_connection(api_key):
    """建立WebSocket连接"""
    url = "wss://api.minimaxi.com/ws/v1/t2a_v2"
    headers = {"Authorization": f"Bearer {api_key}"}

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        ws = await websockets.connect(url, additional_headers=headers, ssl=ssl_context)
        connected = json.loads(await ws.recv())
        if connected.get("event") == "connected_success":
            print("连接成功")
            return ws
        return None
    except Exception as e:
        print(f"连接失败: {e}")
        return None

async def start_task(websocket, text):
    """发送任务开始请求"""
    start_msg = {
        "event": "task_start",
        "model": "speech-02-hd",
        "voice_setting": {
            "voice_id": "female-chengshu",
            "speed": 1,
            "vol": 1,
            "pitch": 0,
            "emotion": "happy"
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1
        }
    }
    await websocket.send(json.dumps(start_msg))
    response = json.loads(await websocket.recv())
    return response.get("event") == "task_started"

async def continue_task(websocket, text):
    """发送继续请求并收集音频数据"""
    await websocket.send(json.dumps({
        "event": "task_continue",
        "text": text
    }))

    audio_chunks = []
    while True:
        response = json.loads(await websocket.recv())
        if "data" in response and "audio" in response["data"]:
            audio = response["data"]["audio"]
            audio_chunks.append(audio)
        if response.get("is_final"):
            break
    return "".join(audio_chunks)

async def close_connection(websocket):
    """关闭连接"""
    if websocket:
        await websocket.send(json.dumps({"event": "task_finish"}))
        await websocket.close()
        print("连接已关闭")

async def main():
    API_KEY = "your_api_key_here"
    TEXT = "欢迎使用MiniMax实时语音合成"

    ws = await establish_connection(API_KEY)
    if not ws:
        return

    try:
        if not await start_task(ws, TEXT):
            print("任务启动失败")
            return

        hex_audio = await continue_task(ws, TEXT)

        # Hex解码音频数据
        audio_bytes = bytes.fromhex(hex_audio)

        # 保存为MP3文件
        with open("output.mp3", "wb") as f:
            f.write(audio_bytes)
        print("音频已保存为output.mp3")

        # 播放音频
        audio = AudioSegment.from_file(BytesIO(audio_bytes), format="mp3")
        print("正在播放音频...")
        play(audio)

    finally:
        await close_connection(ws)

if __name__ == "__main__":
    asyncio.run(main())
```

## 错误处理

### 任务失败事件 (task_failed)
```json
{
    "session_id": "xxxx",
    "event": "task_failed",
    "trace_id": "0303a2882bf18235ae7a809ae0f3cca7",
    "base_resp": {
        "status_code": 1004,
        "status_msg": "鉴权失败"
    }
}
```

### 错误码说明
| 状态码 | 说明 |
|--------|------|
| 1000 | 未知错误 |
| 1001 | 超时 |
| 1002 | 触发限流 |
| 1004 | 鉴权失败 |
| 1039 | 触发TPM限流 |
| 1042 | 非法字符超过10% |
| 2013 | 输入格式信息不正常 |
| 2201 | 超时断开连接 |
| 2202 | 非法事件 |
| 2203 | 空文本，跳过 |
| 2204 | 超过字符限制，跳过 |
| 2205 | 请求超限 |

## 使用场景
- 实时语音播报
- 交互式语音助手
- 长文本分段合成
- 在线语音聊天
- 实时字幕朗读