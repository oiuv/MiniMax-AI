# 音色设计（Voice Design）API文档

## 功能概述
- ✅ 基于描述生成个性化定制音色
- ✅ 支持任意声音特征定制
- ✅ 临时音色7天有效期
- ✅ 试听功能支持
- ✅ 与T2A接口无缝集成

## 接口地址
- **音色设计**: `https://api.minimaxi.com/v1/voice_design?GroupId={YOUR_GROUP_ID}`

## 功能特点

### 音色描述能力
- **声音特征**: 音调、音色、语速、情感
- **角色设定**: 播音员、演员、特定人物
- **场景适配**: 悬疑、欢快、严肃、温柔
- **语言风格**: 正式、口语、文学、商业

### 使用限制
| 项目 | 说明 |
|------|------|
| **认证要求** | 需完成个人/企业认证 |
| **音色有效期** | 7天（168小时） |
| **试听费用** | 2元/万字符 |
| **收费时机** | 首次使用音色时收费 |

## 接口参数说明

### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | ✅ | 音色描述文本 |
| preview_text | string | ✅ | 试听文本（≤2000字符） |
| voice_id | string | ❌ | 自定义音色ID，不传入则自动生成 |
| aigc_watermark | bool | ❌ | 是否添加水印，默认false |

### prompt描述规范

#### 描述维度
| 维度 | 描述示例 |
|------|----------|
| **音色特征** | "低沉磁性男声"、"清脆少女音"、"浑厚男中音" |
| **语速节奏** | "语速缓慢沉稳"、"节奏明快活泼"、"时快时慢营造悬念" |
| **情感色彩** | "温暖亲切"、"严肃权威"、"神秘诡异"、"欢快愉悦" |
| **角色设定** | "新闻播音员"、"故事讲述者"、"客服专员"、"学术讲师" |
| **使用场景** | "适合睡前故事"、"商务演讲"、"情感电台"、"教学讲解" |
| **语言特点** | "标准普通话"、"轻微地方口音"、"英语发音纯正" |

#### 优秀描述示例
```
"专业新闻女主播，声音清亮悦耳，语速适中偏快，吐字清晰有力，带有轻微的权威感但不失亲和力，适合播报时事新闻"

"温柔治愈系女声，音色柔和温暖，语速缓慢轻柔，每个字都像是轻轻诉说，适合睡前故事和情感电台"

"悬疑故事讲述者，男声，声音低沉富有磁性，语速时快时慢，在紧张处刻意放慢营造悬念，整体音色神秘而有魅力"

"活泼可爱的少女音，音色明亮轻快，语速较快，语调起伏明显，充满青春活力，适合儿童内容和娱乐播报"
```

## 返回参数

### 成功响应
```json
{
    "trial_audio": "hex编码音频数据",
    "voice_id": "ttv-voice-2025060717322425-xxxxxxxx",
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
| 1002 | 触发RPM限流 |
| 1004 | 鉴权失败 |
| 1008 | 余额不足 |
| 1013 | 服务内部错误 |
| 1027 | 输出内容错误 |
| 1039 | 触发TPM限流 |
| 2013 | 输入格式信息不正常 |

## 使用示例

### 基础音色设计
```python
import requests
import json

group_id = "your_group_id"
api_key = "your_api_key"

url = f"https://api.minimaxi.com/v1/voice_design?GroupId={group_id}"

payload = json.dumps({
    "prompt": "专业新闻女主播，声音清亮悦耳，语速适中偏快，吐字清晰，适合播报时事新闻",
    "preview_text": "各位听众晚上好，欢迎收听今晚的新闻联播。今天的主要新闻有："
})

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}',
}

response = requests.request("POST", url, headers=headers, data=payload)
result = response.json()

voice_id = result["voice_id"]
print(f"生成的音色ID: {voice_id}")
```

### 自定义音色ID
```python
# 使用自定义音色ID
custom_payload = json.dumps({
    "prompt": "温柔治愈系女声，音色柔和温暖，语速缓慢，适合睡前故事",
    "preview_text": "夜深了，小兔子慢慢闭上眼睛，进入了甜美的梦乡...",
    "voice_id": "gentle-bedtime-voice"
})

response = requests.request("POST", url, headers=headers, data=custom_payload)
```

### 高级音色描述
```python
# 复杂场景音色设计
advanced_payload = json.dumps({
    "prompt": "悬疑故事讲述者，男声，声音低沉富有磁性，语速时快时慢营造紧张氛围，在关键处刻意停顿，整体音色神秘而有魅力，适合深夜电台的恐怖故事",
    "preview_text": "在那个风雨交加的夜晚，古老的宅邸里传来了...咚咚咚...敲门声，他颤抖着走向门口，每走一步，心跳就加快一分...",
    "aigc_watermark": True
})
```

## 音色应用

### 在T2A中使用设计的音色
```python
# 使用设计的音色进行语音合成
t2a_url = f"https://api.minimaxi.com/v1/t2a_v2?GroupId={group_id}"

synthesis_data = {
    "model": "speech-02-hd",  # 推荐使用speech-02-hd获得最佳效果
    "text": "今天我们要讨论的是人工智能如何改变我们的生活方式",
    "voice_id": voice_id,  # 使用设计的音色ID
    "voice_setting": {
        "speed": 1.0,
        "vol": 1.0,
        "pitch": 0
    }
}

response = requests.post(t2a_url, headers=headers, json=synthesis_data)
```

## 音色描述模板库

### 新闻播报类
```
"{性别}新闻{角色}，声音{音色特征}，语速{速度描述}，{语言特点}，适合{使用场景}"

示例：
"男新闻播音员，声音浑厚有力，语速适中偏快，吐字清晰标准，适合播报时事新闻"
```

### 故事讲述类
```
"{性别}故事讲述者，{音色特征}，语速{节奏描述}，{情感色彩}，{氛围营造}，适合{内容类型}"

示例：
"女声故事讲述者，音色温暖柔和，语速缓慢富有感情，营造温馨治愈的氛围，适合儿童睡前故事"
```

### 商业应用类
```
"{性别}客服专员，{音色特征}，{服务态度}，{专业程度}，适合{业务场景}"

示例：
"女声客服专员，音色亲切友好，语速适中，服务态度热情专业，适合电商客服场景"
```

### 教育讲解类
```
"{性别}讲师，{音色特征}，{教学风格}，{专业特点}，适合{教学内容}"

示例：
"男声学术讲师，音色沉稳权威，语速适中条理清晰，逻辑性强，适合高等教育课程讲解"
```

## 音色管理

### 音色列表查询
```python
# 查询已创建的音色（通过文件管理接口）
files_url = f"https://api.minimaxi.com/v1/files/list?GroupId={group_id}"
headers = {'Authorization': f'Bearer {api_key}'}

response = requests.get(files_url, headers=headers)
# 筛选purpose为voice_design的音色文件
```

### 音色有效期管理
- **创建时间**: 音色创建时记录
- **最后使用时间**: 每次调用T2A接口时更新
- **自动清理**: 超过7天未使用的音色自动删除

## 使用场景示例

### 1. 个性化播客
```python
podcast_voice = {
    "prompt": "知性女主播，声音成熟优雅，语速适中，语调富有变化，适合科技播客",
    "preview_text": "欢迎收听科技前沿，今天我们聊聊人工智能的最新发展..."
}
```

### 2. 儿童教育
```python
education_voice = {
    "prompt": "温柔女教师，声音甜美耐心，语速缓慢清晰，每个字都充满关爱，适合儿童教育",
    "preview_text": "小朋友们好，今天我们来学习数字1到10，跟着我一起读..."
}
```

### 3. 商务应用
```python
business_voice = {
    "prompt": "专业男声，音色沉稳商务，语速适中专业，给人信任感，适合商务演示",
    "preview_text": "各位合作伙伴，今天我将为大家介绍我们最新的产品解决方案..."
}
```

## 最佳实践

### 描述优化技巧
1. **具体明确**: 避免模糊描述，使用具体特征词汇
2. **多维描述**: 从音色、语速、情感、场景多个角度描述
3. **对比参照**: 可以参考知名人物或角色的声音特点
4. **场景适配**: 根据使用场景调整描述重点

### 测试验证
```python
# 测试不同描述的效果
descriptions = [
    "温暖治愈女声",
    "温暖治愈女声，语速缓慢轻柔，适合睡前故事",
    "温暖治愈女声，音色柔和如春风，语速缓慢轻柔，每个字都带着安抚的力量，适合3-6岁儿童睡前故事"
]

for desc in descriptions:
    payload = json.dumps({
        "prompt": desc,
        "preview_text": "晚安，宝贝，今天的故事讲完了，做个好梦..."
    })
    
    response = requests.request("POST", url, headers=headers, data=payload)
    print(f"描述: {desc}")
    print(f"结果: {response.json()['voice_id']}")
    print("---")
```

## 注意事项
1. **描述长度**: 建议50-200字，过短可能不够具体，过长可能影响效果
2. **语言清晰**: 使用标准中文描述，避免生僻词和网络用语
3. **场景匹配**: 描述要与实际使用场景相匹配
4. **试听验证**: 始终使用preview_text试听验证效果
5. **备份管理**: 记录成功的音色描述和ID，便于重复使用