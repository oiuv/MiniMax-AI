# 快速复刻（Voice Cloning）API文档

## 功能概述
- ✅ 支持个人/企业认证用户
- ✅ IP复刻、音色克隆场景
- ✅ 支持单/双声道复刻
- ✅ 临时音色保留7天
- ✅ 试听功能支持

## 接口地址
- **文件上传**: `https://api.minimaxi.com/v1/files/upload?GroupId={YOUR_GROUP_ID}`
- **声音复刻**: `https://api.minimaxi.com/v1/voice_clone?GroupId={YOUR_GROUP_ID}`

## 使用限制

### 音频文件规范
| 项目 | 要求 |
|------|------|
| **格式** | mp3, m4a, wav |
| **时长** | 10秒 - 5分钟 |
| **大小** | ≤ 20MB |
| **声道** | 支持单/双声道 |

### 认证要求
- 必须完成个人或企业认证
- 复刻音色为临时音色，7天内需使用
- 首次使用复刻音色时才收费

## 音色ID规范

### 命名规则
| 要求 | 说明 |
|------|------|
| **长度** | 8-256字符 |
| **首字符** | 必须为英文字母 |
| **允许字符** | 数字、字母、-、_ |
| **末字符** | 不可为-或_ |

### 正确示例
- `MiniMax001`
- `my_voice_clone`
- `TestVoice123`

## 使用流程

### 1. 上传音频文件
```bash
curl --location 'https://api.minimaxi.com/v1/files/upload?GroupId={group_id}' \
--header 'Authorization: Bearer YOUR_API_KEY' \
--header 'content-type: multipart/form-data' \
--form 'purpose="voice_clone"' \
--form 'file=@"path/to/audio.mp3"'
```

### 2. 执行音色复刻
```bash
curl --location 'https://api.minimaxi.com/v1/voice_clone?GroupId={group_id}' \
--header 'Authorization: Bearer YOUR_API_KEY' \
--header 'content-type: application/json' \
--data '{
    "file_id": 123456,
    "voice_id": "my_clone_voice"
}'
```

## 接口参数说明

### 文件上传参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| purpose | string | ✅ | 固定值: "voice_clone" |
| file | file | ✅ | 音频文件(mp3/m4a/wav) |

### 音色复刻参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file_id | int64 | ✅ | 上传音频的file_id |
| voice_id | string | ✅ | 自定义音色ID |
| clone_prompt | object | ❌ | 增强复刻参数 |
| text | string | ❌ | 试听文本(≤2000字符) |
| model | string | ❌ | 试听模型 |
| need_noise_reduction | bool | ❌ | 是否降噪，默认false |
| need_volume_normalization | bool | ❌ | 是否音量归一化，默认false |
| aigc_watermark | bool | ❌ | 是否添加水印，默认false |

### clone_prompt参数
```json
{
    "prompt_audio": 789012,  // 示例音频file_id
    "prompt_text": "这是示例音频对应的文本。"
}
```

### prompt_audio要求
- 时长必须小于8秒
- 格式: mp3, m4a, wav
- 需同步提供对应文本

## 返回参数

### 成功响应
```json
{
    "input_sensitive": false,
    "input_sensitive_type": 0,
    "demo_audio": "试听音频URL(如果提供text参数)",
    "base_resp": {
        "status_code": 0,
        "status_msg": "success"
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
| 1013 | 服务内部错误 |
| 2013 | 输入格式信息不正常 |
| 2038 | 无复刻权限，请检查账号认证状态 |

## 完整Python示例

### 1. 上传音频文件
```python
import requests
import json

group_id = "your_group_id"
api_key = "your_api_key"

# 上传复刻音频
url = f'https://api.minimaxi.com/v1/files/upload?GroupId={group_id}'
headers = {
    'Authorization': f'Bearer {api_key}'
}

data = {'purpose': 'voice_clone'}
files = {'file': open('clone_audio.mp3', 'rb')}

response = requests.post(url, headers=headers, data=data, files=files)
file_id = response.json().get("file").get("file_id")
print(f"复刻音频file_id: {file_id}")
```

### 2. 执行音色复刻
```python
# 音色复刻
url = f'https://api.minimaxi.com/v1/voice_clone?GroupId={group_id}'
payload = json.dumps({
    "file_id": file_id,
    "voice_id": "my_custom_voice_001",
    "text": "你好，这是复刻音色的试听效果",
    "model": "speech-2.5-hd-preview",
    "need_noise_reduction": True,
    "need_volume_normalization": True
})

headers = {
    'Authorization': f'Bearer {api_key}',
    'content-type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)
```

### 3. 使用复刻音色
```python
# 使用复刻音色进行语音合成
url = f'https://api.minimaxi.com/v1/t2a_v2?GroupId={group_id}'

synthesis_data = {
    "model": "speech-2.5-hd-preview",
    "text": "这是使用复刻音色合成的语音",
    "voice_id": "my_custom_voice_001",
    "voice_setting": {
        "speed": 1.0,
        "vol": 1.0,
        "pitch": 0
    }
}

response = requests.post(url, headers=headers, json=synthesis_data)
result = response.json()
```

## 高级用法示例

### 带增强参数的复刻
```python
# 上传示例音频（可选增强）
prompt_url = f'https://api.minimaxi.com/v1/files/upload?GroupId={group_id}'
prompt_data = {'purpose': 'prompt_audio'}
prompt_files = {'file': open('prompt_sample.mp3', 'rb')}

prompt_response = requests.post(prompt_url, headers=headers, 
                               data=prompt_data, files=prompt_files)
prompt_file_id = prompt_response.json().get("file").get("file_id")

# 带增强参数的复刻
enhanced_payload = json.dumps({
    "file_id": file_id,
    "voice_id": "enhanced_voice_001",
    "clone_prompt": {
        "prompt_audio": prompt_file_id,
        "prompt_text": "这是示例音频的对应文本。"
    },
    "text": "增强复刻音色的试听效果",
    "model": "speech-2.5-hd-preview",
    "need_noise_reduction": True,
    "need_volume_normalization": True,
    "aigc_watermark": False
})

response = requests.request("POST", url, headers=headers, data=enhanced_payload)
```

## 使用场景
- **个人音色克隆**: 复刻个人声音用于个性化应用
- **IP复刻**: 复刻知名人物声音用于内容创作
- **多音色支持**: 为不同角色创建独特音色
- **语音定制**: 根据需求创建特定风格的语音

## 注意事项
1. **认证要求**: 必须完成个人或企业认证
2. **时效性**: 复刻音色7天内必须使用，否则自动删除
3. **费用**: 首次使用复刻音色时才收费
4. **试听**: 提供试听功能，试听按正常T2A费用收取
5. **风控**: 系统会进行内容安全检测