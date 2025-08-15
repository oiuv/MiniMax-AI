# 查询可用声音ID（Get Voice）API文档

## 功能概述
- ✅ 查询当前账号全部可用音色
- ✅ 支持分类查询：系统音色、克隆音色、文生音色、音乐音色
- ✅ 包含音色详细信息：ID、名称、描述、创建时间
- ✅ 统一音色管理接口

## 接口地址
- **查询音色**: `https://api.minimaxi.com/v1/get_voice?GroupId={YOUR_GROUP_ID}`

## 支持查询的音色类型

### voice_type参数说明
| 类型 | 说明 | 包含内容 |
|------|------|----------|
| **system** | 系统音色 | 官方预设的200+系统音色 |
| **voice_cloning** | 快速复刻音色 | 通过Voice Cloning API创建的音色 |
| **voice_generation** | 文生音色 | 通过Voice Design API生成的音色 |
| **music_generation** | 音乐音色 | 音乐生成产生的人声/伴奏音色 |
| **all** | 全部音色 | 以上所有类型的音色 |

## 接口参数说明

### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| voice_type | string | ✅ | 音色类型选择 |

### 请求头
```
Authorization: Bearer YOUR_API_KEY
```

## 返回数据结构

### 完整响应结构
```json
{
    "system_voice": [
        {
            "voice_id": "female-chengshu",
            "voice_name": "成熟女性",
            "description": ["成熟女性音色", "温柔知性"]
        }
    ],
    "voice_cloning": [
        {
            "voice_id": "my_clone_001",
            "description": ["我的声音克隆", "低沉男声"],
            "created_time": "2024-01-15"
        }
    ],
    "voice_generation": [
        {
            "voice_id": "ttv-voice-20241201",
            "description": ["温柔治愈女声", "适合睡前故事"],
            "created_time": "2024-12-01"
        }
    ],
    "music_generation": [
        {
            "voice_id": "music-vocal-001",
            "instrumental_id": "music-inst-001",
            "description": ["流行歌曲人声", "轻快节奏"],
            "created_time": "2024-12-05"
        }
    ]
}
```

## 使用示例

### 基础查询
```python
import requests

group_id = "your_group_id"
api_key = "your_api_key"

url = f'https://api.minimaxi.com/v1/get_voice?GroupId={group_id}'
headers = {
    'Authorization': f'Bearer {api_key}'
}

# 查询所有音色
data = {'voice_type': 'all'}
response = requests.post(url, headers=headers, data=data)
result = response.json()

print(f"系统音色数量: {len(result.get('system_voice', []))}")
print(f"克隆音色数量: {len(result.get('voice_cloning', []))}")
print(f"文生音色数量: {len(result.get('voice_generation', []))}")
print(f"音乐音色数量: {len(result.get('music_generation', []))}")
```

### 分类查询示例
```python
def get_voices_by_type(voice_type, api_key, group_id):
    """按类型查询音色"""
    url = f'https://api.minimaxi.com/v1/get_voice?GroupId={group_id}'
    headers = {'Authorization': f'Bearer {api_key}'}
    data = {'voice_type': voice_type}
    
    response = requests.post(url, headers=headers, data=data)
    return response.json()

# 查询系统音色
system_voices = get_voices_by_type('system', api_key, group_id)

# 查询克隆音色
cloning_voices = get_voices_by_type('voice_cloning', api_key, group_id)

# 查询文生音色
generated_voices = get_voices_by_type('voice_generation', api_key, group_id)
```

## 音色管理工具类

### 统一音色管理器
```python
import json
from datetime import datetime

class VoiceInventory:
    def __init__(self, api_key, group_id):
        self.api_key = api_key
        self.group_id = group_id
        self.base_url = f"https://api.minimaxi.com/v1/get_voice?GroupId={group_id}"
    
    def get_all_voices(self):
        """获取所有音色"""
        return self._query_voices('all')
    
    def get_system_voices(self):
        """获取系统音色"""
        return self._query_voices('system')
    
    def get_cloning_voices(self):
        """获取克隆音色"""
        return self._query_voices('voice_cloning')
    
    def get_generated_voices(self):
        """获取文生音色"""
        return self._query_voices('voice_generation')
    
    def get_music_voices(self):
        """获取音乐音色"""
        return self._query_voices('music_generation')
    
    def _query_voices(self, voice_type):
        """内部查询方法"""
        headers = {'Authorization': f'Bearer {self.api_key}'}
        data = {'voice_type': voice_type}
        
        response = requests.post(self.base_url, headers=headers, data=data)
        return response.json()
    
    def search_voice_by_name(self, keyword, voice_type='all'):
        """按名称搜索音色"""
        voices = self._query_voices(voice_type)
        
        results = []
        for category, voice_list in voices.items():
            for voice in voice_list:
                if keyword.lower() in str(voice).lower():
                    voice['category'] = category
                    results.append(voice)
        
        return results
    
    def get_voice_statistics(self):
        """获取音色统计信息"""
        all_voices = self._query_voices('all')
        
        stats = {}
        for category, voice_list in all_voices.items():
            stats[category] = {
                'count': len(voice_list),
                'voice_ids': [v['voice_id'] for v in voice_list]
            }
        
        return stats
    
    def export_voice_list(self, filename=None):
        """导出音色列表到文件"""
        all_voices = self._query_voices('all')
        
        if filename is None:
            filename = f"voice_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_voices, f, ensure_ascii=False, indent=2)
        
        return filename

# 使用示例
inventory = VoiceInventory(api_key, group_id)
stats = inventory.get_voice_statistics()
print(json.dumps(stats, indent=2, ensure_ascii=False))
```

### 音色选择器
```python
class VoiceSelector:
    def __init__(self, api_key, group_id):
        self.inventory = VoiceInventory(api_key, group_id)
    
    def select_voice_by_description(self, description_keywords, voice_type='all'):
        """根据描述关键词选择音色"""
        voices = self.inventory._query_voices(voice_type)
        
        matches = []
        for category, voice_list in voices.items():
            for voice in voice_list:
                description = ' '.join(voice.get('description', []))
                if all(keyword.lower() in description.lower() 
                       for keyword in description_keywords):
                    voice['category'] = category
                    matches.append(voice)
        
        return matches
    
    def get_system_voice_categories(self):
        """获取系统音色分类"""
        system_voices = self.inventory.get_system_voices()
        
        categories = {}
        for voice in system_voices.get('system_voice', []):
            description = ' '.join(voice.get('description', []))
            
            # 简单分类逻辑
            if '男' in description:
                categories.setdefault('男性', []).append(voice)
            elif '女' in description:
                categories.setdefault('女性', []).append(voice)
            
            if '青年' in description:
                categories.setdefault('青年', []).append(voice)
            elif '成熟' in description:
                categories.setdefault('成熟', []).append(voice)
        
        return categories
    
    def interactive_voice_selection(self):
        """交互式音色选择"""
        all_voices = self.inventory._query_voices('all')
        
        print("=== 可用音色列表 ===")
        
        for category, voices in all_voices.items():
            print(f"\n{category.upper()}:")
            for i, voice in enumerate(voices, 1):
                description = ' '.join(voice.get('description', []))
                print(f"  {i}. {voice['voice_id']} - {description}")
        
        return all_voices
```

## 系统音色参考

### 常用系统音色示例
```python
SYSTEM_VOICES = {
    "中文女声": [
        {
            "voice_id": "female-shaonv",
            "voice_name": "少女",
            "description": ["少女音色", "甜美可爱"]
        },
        {
            "voice_id": "female-yujie", 
            "voice_name": "御姐",
            "description": ["御姐音色", "成熟魅力"]
        },
        {
            "voice_id": "female-chengshu",
            "voice_name": "成熟女性", 
            "description": ["成熟女性音色", "温柔知性"]
        }
    ],
    "中文男声": [
        {
            "voice_id": "male-qn-qingse",
            "voice_name": "青涩青年",
            "description": ["青涩青年音色", "青春阳光"]
        },
        {
            "voice_id": "male-qn-jingying",
            "voice_name": "精英青年",
            "description": ["精英青年音色", "专业自信"]
        }
    ]
}
```

## 集成应用示例

### 播客音色选择器
```python
def get_podcast_voices():
    """获取适合播客的音色"""
    inventory = VoiceInventory(api_key, group_id)
    
    # 获取所有音色
    all_voices = inventory.get_all_voices()
    
    podcast_suitable = []
    
    # 筛选适合的音色
    for category, voices in all_voices.items():
        for voice in voices:
            description = ' '.join(voice.get('description', [])).lower()
            
            # 播客适合的音色特征
            keywords = ['播音', '主播', '讲述', '成熟', '温柔', '知性', '专业']
            if any(keyword in description for keyword in keywords):
                voice['category'] = category
                podcast_suitable.append(voice)
    
    return podcast_suitable

# 使用示例
podcast_voices = get_podcast_voices()
for voice in podcast_voices:
    print(f"{voice['voice_id']} - {' '.join(voice['description'])}")
```

### 音色缓存管理
```python
import pickle
from pathlib import Path

class CachedVoiceInventory(VoiceInventory):
    def __init__(self, api_key, group_id, cache_file="voice_cache.pkl"):
        super().__init__(api_key, group_id)
        self.cache_file = Path(cache_file)
    
    def get_cached_voices(self, voice_type='all', max_age_minutes=60):
        """获取缓存的音色列表"""
        
        if self.cache_file.exists():
            cache_time = datetime.fromtimestamp(self.cache_file.stat().st_mtime)
            if (datetime.now() - cache_time).total_seconds() < max_age_minutes * 60:
                with open(self.cache_file, 'rb') as f:
                    return pickle.load(f)
        
        # 重新获取并缓存
        voices = self._query_voices(voice_type)
        with open(self.cache_file, 'wb') as f:
            pickle.dump(voices, f)
        
        return voices
```

## 错误处理

### 查询错误处理
```python
def safe_get_voices(voice_type, api_key, group_id):
    """安全查询音色"""
    try:
        url = f'https://api.minimaxi.com/v1/get_voice?GroupId={group_id}'
        headers = {'Authorization': f'Bearer {api_key}'}
        data = {'voice_type': voice_type}
        
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json(),
            "status_code": response.status_code
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "data": None
        }

# 使用示例
result = safe_get_voices('all', api_key, group_id)
if result["success"]:
    voices = result["data"]
    print(f"查询成功，共找到音色")
else:
    print(f"查询失败: {result['error']}")
```

## 使用场景

### 1. 播客制作音色选择
```python
def select_podcast_voices():
    """为播客选择合适音色"""
    selector = VoiceSelector(api_key, group_id)
    
    # 获取系统音色
    system_voices = selector.get_system_voices()
    
    # 推荐播客音色
    podcast_recommendations = [
        "female-chengshu",  # 成熟女性
        "male-qn-jingying",  # 精英青年
        "presenter_female",  # 女性主持人
        "presenter_male"    # 男性主持人
    ]
    
    return [voice for voice in system_voices.get('system_voice', [])
            if voice['voice_id'] in podcast_recommendations]
```

### 2. 应用启动时音色初始化
```python
def initialize_voice_library():
    """应用启动时初始化音色库"""
    inventory = VoiceInventory(api_key, group_id)
    
    # 获取所有可用音色
    all_voices = inventory.get_all_voices()
    
    # 构建音色映射表
    voice_map = {}
    for category, voices in all_voices.items():
        for voice in voices:
            voice_map[voice['voice_id']] = {
                'category': category,
                'name': voice.get('voice_name', ''),
                'description': ' '.join(voice.get('description', [])),
                'created_time': voice.get('created_time', '')
            }
    
    return voice_map
```

## 注意事项
1. **实时查询**: 每次调用都会实时查询API
2. **权限要求**: 需要有效的API密钥和权限
3. **数据完整**: 返回包含所有相关音色信息
4. **分类清晰**: 按音色来源分类返回
5. **时间格式**: created_time为yyyy-mm-dd格式