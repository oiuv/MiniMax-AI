# 删除声音（Delete Voice）API文档

## 功能概述
- ✅ 删除自定义音色
- ✅ 支持删除克隆音色和文生音色
- ✅ 即时生效，不可恢复
- ✅ 清理临时音色资源

## 接口地址
- **删除声音**: `https://api.minimaxi.com/v1/delete_voice?GroupId={YOUR_GROUP_ID}`

## 支持删除的音色类型

### voice_type参数说明
| 类型 | 说明 | 来源 |
|------|------|------|
| **voice_cloning** | 克隆的音色 | Voice Cloning API |
| **voice_generation** | 文生音色生成的音色 | Voice Generation API |

## 接口参数说明

### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| voice_type | string | ✅ | 音色类型: "voice_cloning" 或 "voice_generation" |
| voice_id | string | ✅ | 要删除的音色ID |

## 使用示例

### 删除克隆音色
```bash
curl --location 'https://api.minimaxi.com/v1/delete_voice?GroupId=${group_id}' \
--header 'content-type: application/json' \
--header 'authorization: Bearer $MiniMax_API_KEY' \
--data '{
    "voice_type":"voice_cloning",
    "voice_id":"my_clone_voice_001"
}'
```

### 删除文生音色
```bash
curl --location 'https://api.minimaxi.com/v1/delete_voice?GroupId=${group_id}' \
--header 'content-type: application/json' \
--header 'authorization: Bearer $MiniMax_API_KEY' \
--data '{
    "voice_type":"voice_generation",
    "voice_id":"ttv-voice-2025060717322425-xxxxxxxx"
}'
```

## Python使用示例

### 基础删除
```python
import requests
import json

group_id = "your_group_id"
api_key = "your_api_key"

url = f"https://api.minimaxi.com/v1/delete_voice?GroupId={group_id}"

# 删除克隆音色
payload = json.dumps({
    "voice_type": "voice_cloning",
    "voice_id": "my_clone_voice_001"
})

headers = {
    'content-type': 'application/json',
    'authorization': f'Bearer {api_key}'
}

response = requests.request("POST", url, headers=headers, data=payload)
result = response.json()

if result["base_resp"]["status_code"] == 0:
    print(f"✅ 音色删除成功: {result['voice_id']}")
    print(f"创建时间: {result['created_time']}")
else:
    print(f"❌ 删除失败: {result['base_resp']['status_msg']}")
```

### 批量删除函数
```python
def delete_voice(voice_type, voice_id, api_key, group_id):
    """删除指定音色"""
    url = f"https://api.minimaxi.com/v1/delete_voice?GroupId={group_id}"
    
    payload = json.dumps({
        "voice_type": voice_type,
        "voice_id": voice_id
    })
    
    headers = {
        'content-type': 'application/json',
        'authorization': f'Bearer {api_key}'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

# 使用示例
result = delete_voice("voice_cloning", "old_clone_voice", api_key, group_id)
```

### 音色管理工具类
```python
class VoiceManager:
    def __init__(self, api_key, group_id):
        self.api_key = api_key
        self.group_id = group_id
        self.base_url = f"https://api.minimaxi.com/v1/delete_voice?GroupId={group_id}"
    
    def delete_clone_voice(self, voice_id):
        """删除克隆音色"""
        return self._delete_voice("voice_cloning", voice_id)
    
    def delete_generated_voice(self, voice_id):
        """删除文生音色"""
        return self._delete_voice("voice_generation", voice_id)
    
    def _delete_voice(self, voice_type, voice_id):
        """内部删除方法"""
        payload = json.dumps({
            "voice_type": voice_type,
            "voice_id": voice_id
        })
        
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {self.api_key}'
        }
        
        response = requests.request("POST", self.base_url, headers=headers, data=payload)
        return response.json()

# 使用示例
manager = VoiceManager(api_key, group_id)
result = manager.delete_clone_voice("test_voice_001")
```

## 返回参数说明

### 成功响应
```json
{
    "voice_id": "yanshang11123",
    "created_time": "1728962464",
    "base_resp": {
        "status_code": 0,
        "status_msg": "success"
    }
}
```

### 参数说明
| 参数 | 类型 | 说明 |
|------|------|------|
| voice_id | string | 被删除的音色ID |
| created_time | string | 音色创建时间戳 |
| base_resp.status_code | int64 | 状态码 |
| base_resp.status_msg | string | 状态详情 |

## 错误处理

### 错误码说明
| 状态码 | 说明 | 解决方案 |
|--------|------|----------|
| 0 | 删除成功 | - |
| 2013 | 输入非法 | 检查voice_type和voice_id格式 |
| 1004 | 鉴权失败 | 检查API密钥和权限 |
| 1000 | 未知错误 | 稍后重试或联系技术支持 |

### 错误处理示例
```python
def safe_delete_voice(voice_type, voice_id, api_key, group_id):
    """安全删除音色，包含错误处理"""
    try:
        url = f"https://api.minimaxi.com/v1/delete_voice?GroupId={group_id}"
        
        # 参数验证
        if voice_type not in ["voice_cloning", "voice_generation"]:
            raise ValueError("voice_type必须是 'voice_cloning' 或 'voice_generation'")
        
        if not voice_id or len(voice_id) < 8:
            raise ValueError("voice_id不能为空且长度至少8个字符")
        
        payload = json.dumps({
            "voice_type": voice_type,
            "voice_id": voice_id
        })
        
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {api_key}'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        result = response.json()
        
        if result["base_resp"]["status_code"] == 0:
            return {
                "success": True,
                "voice_id": result["voice_id"],
                "created_time": result["created_time"]
            }
        else:
            return {
                "success": False,
                "error": result["base_resp"]["status_msg"],
                "code": result["base_resp"]["status_code"]
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "code": -1
        }

# 使用示例
result = safe_delete_voice("voice_cloning", "test_voice_123", api_key, group_id)
if result["success"]:
    print(f"删除成功: {result['voice_id']}")
else:
    print(f"删除失败: {result['error']}")
```

## 使用场景

### 1. 定期清理临时音色
```python
def cleanup_expired_voices(api_key, group_id):
    """清理不再需要的临时音色"""
    # 获取音色列表（通过文件管理接口）
    files_url = f"https://api.minimaxi.com/v1/files/list?GroupId={group_id}"
    headers = {'Authorization': f'Bearer {api_key}'}
    
    response = requests.get(files_url, headers=headers)
    files = response.json().get('files', [])
    
    # 筛选需要删除的音色
    voice_files = [f for f in files if f.get('purpose') in ['voice_clone', 'voice_design']]
    
    deleted_count = 0
    for file in voice_files:
        # 根据文件信息删除对应音色
        voice_id = file.get('voice_id')
        voice_type = 'voice_cloning' if file.get('purpose') == 'voice_clone' else 'voice_generation'
        
        if voice_id:
            result = delete_voice(voice_type, voice_id, api_key, group_id)
            if result["base_resp"]["status_code"] == 0:
                deleted_count += 1
                print(f"已删除: {voice_id}")
    
    return deleted_count
```

### 2. 项目管理中的音色清理
```python
def cleanup_project_voices(project_prefix, api_key, group_id):
    """清理特定项目的音色"""
    # 获取所有以项目前缀命名的音色
    # 实际实现需要结合音色列表接口
    voices_to_delete = [
        f"{project_prefix}_voice_001",
        f"{project_prefix}_voice_002",
        # ... 更多音色ID
    ]
    
    for voice_id in voices_to_delete:
        result = delete_voice("voice_cloning", voice_id, api_key, group_id)
        print(f"删除 {voice_id}: {'成功' if result['base_resp']['status_code'] == 0 else '失败'}")
```

## 注意事项

### 重要提醒
1. **不可恢复**: 删除后音色无法恢复
2. **即时生效**: 删除后立即无法使用
3. **权限检查**: 确保有删除权限
4. **类型匹配**: voice_type必须与音色来源匹配
5. **依赖清理**: 删除前确保没有正在进行的任务使用该音色

### 最佳实践
```python
# 完整的音色管理流程
class VoiceLifecycleManager:
    def __init__(self, api_key, group_id):
        self.api_key = api_key
        self.group_id = group_id
        self.manager = VoiceManager(api_key, group_id)
    
    def create_and_manage_voice(self, audio_file, description):
        """完整的音色生命周期管理"""
        
        # 1. 上传音频
        # 2. 创建音色
        # 3. 使用音色
        # 4. 定期清理或主动删除
        
        try:
            # 这里整合创建和使用逻辑
            voice_id = self._create_voice(audio_file, description)
            
            # 使用音色进行合成
            self._use_voice(voice_id)
            
            # 7天后自动删除
            # 或根据业务逻辑删除
            
            return voice_id
            
        except Exception as e:
            print(f"音色管理失败: {e}")
            return None
```

## 监控和审计

### 删除日志记录
```python
import datetime

def log_voice_deletion(voice_id, voice_type, api_key, group_id):
    """记录音色删除操作"""
    timestamp = datetime.datetime.now().isoformat()
    
    result = delete_voice(voice_type, voice_id, api_key, group_id)
    
    log_entry = {
        "timestamp": timestamp,
        "voice_id": voice_id,
        "voice_type": voice_type,
        "success": result["base_resp"]["status_code"] == 0,
        "response": result
    }
    
    # 保存日志到文件或数据库
    with open("voice_deletion_log.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    return result
```

## 集成应用

### 在CLI工具中的集成
```python
def delete_voice_cli():
    """CLI方式的音色删除"""
    parser = argparse.ArgumentParser(description='删除自定义音色')
    parser.add_argument('--voice-id', required=True, help='要删除的音色ID')
    parser.add_argument('--type', choices=['cloning', 'generation'], 
                       required=True, help='音色类型')
    
    args = parser.parse_args()
    
    voice_type_map = {
        'cloning': 'voice_cloning',
        'generation': 'voice_generation'
    }
    
    result = delete_voice(
        voice_type_map[args.type], 
        args.voice_id, 
        api_key, 
        group_id
    )
    
    if result["base_resp"]["status_code"] == 0:
        print(f"✅ 音色 {args.voice_id} 删除成功")
    else:
        print(f"❌ 删除失败: {result['base_resp']['status_msg']}")
```