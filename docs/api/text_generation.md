# 文本生成（ChatCompletion）API文档

## 接口地址
- **主接口**: https://api.minimaxi.com/v1/text/chatcompletion_v2
- **文档地址**: https://platform.minimaxi.com/document/对话?key=66701d281d57f38758d581d0

## 支持模型

| 模型名称 | 最大token数 | 特点 |
|----------|-------------|------|
| MiniMax-M1 | 1,000,192 | 推理模型，输出tokens较多，建议使用流式输出 |
| MiniMax-Text-01 | 1,000,192 | 全新架构，支持1M超长上下文 |

## 接口参数说明

### 请求头
- **Authorization**: Bearer Token 认证 (必填)
- **Content-Type**: application/json (必填)

### 请求体参数

#### 必填参数
- **model**: string - 模型ID，支持 MiniMax-M1 或 MiniMax-Text-01
- **messages**: array - 对话内容数组

#### 可选参数
- **stream**: bool - 是否流式返回，默认false
- **max_tokens**: int64 (0,40000] - 最大生成token数
  - MiniMax-M1默认：8192
  - MiniMax-Text-01默认：2048
- **temperature**: float (0,1] - 随机性控制
  - MiniMax-M1推荐：[0.8,1]
  - MiniMax-Text-01推荐：低(0.01~0.2)或高(0.7~1)
- **top_p**: float (0,1] - 采样方法，默认0.95
- **mask_sensitive_info**: bool - 敏感信息打码，默认false

### messages参数结构

#### 消息对象字段
- **role**: string (必填) - 发送者类型
  - system: 系统设定
  - user: 用户消息
  - assistant: 助手回复
  - tool: 工具调用
- **content**: string或array (必填) - 消息内容
- **name**: string - 发送者名称

#### 内容类型支持
- **text**: 纯文本内容
- **image_url**: 图片URL或base64编码图片

### 工具调用支持
- **tool_calls**: 模型生成的工具调用信息
- **tool_choice**: 工具选择模式 (none/auto)
- **tools**: 支持的工具定义

### 结构化输出支持（仅MiniMax-Text-01支持）
- **response_format**: object - 指定JSON Schema格式输出
  - type: "json_schema"
  - json_schema: JSON Schema对象

## 返回参数

### 成功响应格式
```json
{
  "id": "response_id",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "回复内容"
      },
      "finish_reason": "stop"
    }
  ],
  "created": 1234567890,
  "model": "MiniMax-Text-01",
  "usage": {
    "total_tokens": 100
  }
}
```

### 错误码说明
| 状态码 | 说明 |
|--------|------|
| 1000 | 未知错误 |
| 1001 | 请求超时 |
| 1002 | 触发RPM限流 |
| 1004 | 鉴权失败 |
| 1008 | 余额不足 |
| 1013 | 服务内部错误 |
| 1027 | 输出内容错误 |
| 1039 | Token限制 |
| 2013 | 参数错误 |

## 使用示例

### 基本对话
```bash
curl -X POST https://api.minimaxi.com/v1/text/chatcompletion_v2 \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "MiniMax-Text-01",
    "messages": [
      {"role": "user", "content": "你好，请介绍AI"}
    ]
  }'
```

### Python示例
```python
import requests

url = "https://api.minimaxi.com/v1/text/chatcompletion_v2"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
data = {
    "model": "MiniMax-Text-01",
    "messages": [
        {"role": "system", "content": "你是一个AI助手"},
        {"role": "user", "content": "你好"}
    ],
    "max_tokens": 2048,
    "temperature": 0.7
}

response = requests.post(url, headers=headers, json=data)
result = response.json()
print(result["choices"][0]["message"]["content"])
```