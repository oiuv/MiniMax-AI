# 同步语音合成（T2A）API文档

## 接口地址
- **主接口**: https://api.minimaxi.com/v1/t2a_v2?GroupId={YOUR_GROUP_ID}
- **备用接口**: https://api-bj.minimaxi.com/v1/t2a_v2?GroupId={YOUR_GROUP_ID}

## 功能特性
- ✅ 支持100+系统音色和复刻音色
- ✅ 最大10000字符单次合成
- ✅ 40种语言支持
- ✅ 音量、语调、语速可调
- ✅ 支持mp3、pcm、flac、wav格式
- ✅ 支持流式输出

## 支持模型

| 模型 | 特性 |
|------|------|
| **speech-2.5-hd-preview** | 最新HD模型，韵律出色，复刻相似度极佳 |
| **speech-2.5-turbo-preview** | 最新Turbo模型，支持40个语种 |
| **speech-02-hd** | 出色韵律、稳定性和复刻相似度 |
| **speech-02-turbo** | 出色韵律和稳定性，小语种能力加强 |
| **speech-01-hd** | 超高复刻相似度，音质突出 |
| **speech-01-turbo** | 快速生成速度 |

## 接口参数说明

### 请求头
- **Authorization**: Bearer Token 认证 (必填)
- **Content-Type**: application/json (必填)
- **GroupId**: 用户组ID (添加到URL末尾)

### 请求体参数

#### 必填参数
- **model**: string - 模型版本选择
- **text**: string - 待合成文本，<10000字符
- **voice_id** 或 **timbre_weights**: string - 音色ID (二选一必填)

#### 可选参数
- **voice_setting**: object - 声音设置
  - **speed**: [0.5,2] 语速，默认1.0
  - **vol**: (0,10] 音量，默认1.0
  - **pitch**: [-12,12] 语调，默认0
- **audio_setting**: object - 音频设置
  - **sample_rate**: [8000,16000,22050,24000,32000,44100] 采样率，默认32000
  - **bitrate**: [32000,64000,128000,256000] 比特率，默认128000
  - **format**: [mp3,pcm,flac,wav] 格式，默认mp3
  - **channel**: [1,2] 声道数，默认1
- **emotion**: string - 情绪控制 ["happy","sad","angry","fearful","disgusted","surprised","calm"]
- **stream**: boolean - 是否流式输出，默认false

## 系统音色列表

### 中文音色
| 音色ID | 描述 |
|--------|------|
| male-qn-qingse | 青涩青年音色 |
| male-qn-jingying | 精英青年音色 |
| male-qn-badao | 霸道青年音色 |
| male-qn-daxuesheng | 青年大学生音色 |
| female-shaonv | 少女音色 |
| female-yujie | 御姐音色 |
| female-chengshu | 成熟女性音色 |
| female-tianmei | 甜美女性音色 |
| presenter_male | 男性主持人 |
| presenter_female | 女性主持人 |

### 特色音色
| 音色ID | 描述 |
|--------|------|
| audiobook_male_1 | 男性有声书1 |
| audiobook_female_1 | 女性有声书1 |
| clever_boy | 聪明男童 |
| cute_boy | 可爱男童 |
| lovely_girl | 萌萌女童 |
| Santa_Claus | 圣诞老人 |
| Charming_Santa | 魅力圣诞老人 |

## 返回参数

### 成功响应
```json
{
  "data": {
    "audio": "hex编码的音频数据",
    "status": 2
  },
  "extra_info": {
    "audio_length": 5746,
    "audio_sample_rate": 32000,
    "audio_size": 100845,
    "audio_bitrate": 128000,
    "audio_format": "mp3",
    "usage_characters": 630
  },
  "trace_id": "会话ID",
  "base_resp": {
    "status_code": 0,
    "status_msg": ""
  }
}
```

## 完整示例

### 非流式请求
```bash
curl --location 'https://api.minimaxi.com/v1/t2a_v2?GroupId=${group_id}' \
--header 'Authorization: Bearer $MiniMax_API_KEY' \
--header 'Content-Type: application/json' \
--data '{
    "model": "speech-2.5-hd-preview",
    "text": "你好，欢迎使用MiniMax语音合成",
    "voice_setting": {
        "voice_id": "female-chengshu",
        "speed": 1.0,
        "vol": 1.0,
        "pitch": 0
    },
    "audio_setting": {
        "sample_rate": 32000,
        "bitrate": 128000,
        "format": "mp3"
    }
}'
```

### Python示例
```python
import requests

url = f"https://api.minimaxi.com/v1/t2a_v2?GroupId={group_id}"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}

data = {
    "model": "speech-2.5-hd-preview",
    "text": "你好，欢迎使用MiniMax语音合成",
    "voice_setting": {
        "voice_id": "female-chengshu",
        "speed": 1.0,
        "vol": 1.0,
        "pitch": 0
    }
}

response = requests.post(url, headers=headers, json=data)
result = response.json()
audio_hex = result["data"]["audio"]
```

## 错误码说明
| 状态码 | 说明 |
|--------|------|
| 1000 | 未知错误 |
| 1001 | 超时 |
| 1002 | 触发限流 |
| 1004 | 鉴权失败 |
| 1039 | 触发TPM限流 |
| 1042 | 非法字符超过10% |
| 2013 | 输入格式信息不正常 |

## 使用场景
- 短句语音生成
- 语音聊天应用
- 在线社交场景
- 播客内容制作
- 语音助手开发