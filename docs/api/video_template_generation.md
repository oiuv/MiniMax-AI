# 视频生成Agent（Video Template Generation）API文档

## 功能概述
- ✅ 基于模板的视频生成
- ✅ 支持人物/宠物换脸
- ✅ 专业场景模板（跳水、吊环等）
- ✅ 商业广告模板（麦当劳、试穿广告）
- ✅ 创意写真模板（藏族风、四季写真）
- ✅ 幽默动画模板（绝地求生、生无可恋）

## 接口概览

### 整体流程
1. **创建任务** → `POST /v1/video_template_generation`
2. **查询状态** → `GET /v1/query/video_template_generation?task_id={task_id}`
3. **下载结果** → 通过返回的`video_url`直接下载

## 支持模板

### 模板分类表
| 模板ID | 模板名称 | 功能描述 | 媒体输入 | 文本输入 | 使用场景 |
|--------|----------|----------|----------|----------|----------|
| **392753057216684038** | 跳水 | 主体完成完美跳水动作 | ✅ 图片 | ❌ | 运动/表演 |
| **393881433990066176** | 吊环 | 宠物完成吊环动作 | ✅ 图片 | ❌ | 宠物娱乐 |
| **393769180141805569** | 绝地求生 | 宠物野外求生视频 | ✅ 图片 | ✅ 野兽种类 | 创意/搞笑 |
| **394246956137422856** | 万物皆可labubu | labubu换脸视频 | ✅ 图片 | ❌ | 趣味换脸 |
| **393879757702918151** | 麦当劳宠物外卖员 | 宠物当外卖员 | ✅ 图片 | ❌ | 商业/宠物 |
| **393766210733957121** | 藏族风写真 | 藏族风格视频写真 | ✅ 图片 | ❌ | 民族写真 |
| **394125185182695432** | 生无可恋 | 角色痛苦生活动画 | ❌ | ✅ 主角描述 | 幽默动画 |
| **393857704283172864** | 情书写真 | 冬日雪景写真 | ✅ 图片 | ❌ | 浪漫写真 |
| **393866076583718914** | 女模特试穿广告 | 服装试穿广告 | ✅ 图片 | ❌ | 电商营销 |
| **398574688191234048** | 四季写真 | 四季变换写真 | ✅ 图片 | ❌ | 艺术写真 |
| **393876118804459526** | 男模特试穿广告 | 服装试穿广告 | ✅ 图片 | ❌ | 电商营销 |

## 创建视频Agent任务

### 接口地址
`POST https://api.minimaxi.com/v1/video_template_generation?GroupId={YOUR_GROUP_ID}`

### 请求参数

#### 基础参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| template_id | string | ✅ | 模板ID选择 |
| media_inputs | array | ❌ | 图片输入（需要时必填） |
| text_inputs | array | ❌ | 文本输入（需要时必填） |
| callback_url | string | ❌ | 回调通知URL |

#### 输入参数格式
```json
{
    "template_id": "393769180141805569",
    "media_inputs": [
        {
            "value": "图片URL或Base64数据"
        }
    ],
    "text_inputs": [
        {
            "value": "文本内容"
        }
    ]
}
```

### 图片输入要求
- **格式**: JPG/JPEG/PNG/WebP
- **比例**: 长宽比 > 2:5 且 < 5:2
- **尺寸**: 短边像素 > 300px
- **大小**: ≤ 20MB

## 模板使用详解

### 1. 运动类模板

#### 跳水模板 (392753057216684038)
```python
import requests
import json

group_id = "your_group_id"
api_key = "your_api_key"

url = f"https://api.minimaxi.com/v1/video_template_generation?GroupId={group_id}"

# 跳水模板 - 上传人物图片
payload = json.dumps({
    "template_id": "392753057216684038",
    "media_inputs": [
        {
            "value": "https://example.com/athlete.jpg"
        }
    ]
})

headers = {
    'authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
task_id = response.json()['task_id']
print(f"跳水视频任务ID: {task_id}")
```

### 2. 宠物娱乐模板

#### 绝地求生模板 (393769180141805569)
```python
# 宠物绝地求生 - 需要图片和野兽种类
payload = json.dumps({
    "template_id": "393769180141805569",
    "media_inputs": [
        {
            "value": "data:image/jpeg;base64,{pet_image_base64}"
        }
    ],
    "text_inputs": [
        {
            "value": "狮子"  # 可选：老虎/狼/熊等
        }
    ]
})
```

#### 吊环模板 (393881433990066176)
```python
# 宠物吊环表演
payload = json.dumps({
    "template_id": "393881433990066176",
    "media_inputs": [
        {
            "value": "https://example.com/dog.jpg"
        }
    ]
})
```

### 3. 商业广告模板

#### 麦当劳宠物外卖员 (393879757702918151)
```python
# 麦当劳宠物外卖员广告
payload = json.dumps({
    "template_id": "393879757702918151",
    "media_inputs": [
        {
            "value": "https://example.com/pet.jpg"
        }
    ]
})
```

#### 试穿广告模板
```python
# 女模特试穿广告
payload = json.dumps({
    "template_id": "393866076583718914",  # 女模特
    "media_inputs": [
        {
            "value": "data:image/jpeg;base64,{clothing_image_base64}"
        }
    ]
})

# 男模特试穿广告
payload = json.dumps({
    "template_id": "393876118804459526",  # 男模特
    "media_inputs": [
        {
            "value": "https://example.com/outfit.jpg"
        }
    ]
})
```

### 4. 写真模板

#### 藏族风写真 (393766210733957121)
```python
# 藏族风格写真
payload = json.dumps({
    "template_id": "393766210733957121",
    "media_inputs": [
        {
            "value": "https://example.com/portrait.jpg"
        }
    ]
})
```

#### 四季写真 (398574688191234048)
```python
# 四季变换写真
payload = json.dumps({
    "template_id": "398574688191234048",
    "media_inputs": [
        {
            "value": "data:image/jpeg;base64,{face_image_base64}"
        }
    ]
})
```

### 5. 创意模板

#### 万物皆可labubu (394246956137422856)
```python
# labubu换脸
payload = json.dumps({
    "template_id": "394246956137422856",
    "media_inputs": [
        {
            "value": "https://example.com/person.jpg"
        }
    ]
})
```

#### 生无可恋动画 (394125185182695432)
```python
# 痛苦生活动画 - 仅需文本描述
payload = json.dumps({
    "template_id": "394125185182695432",
    "text_inputs": [
        {
            "value": "周一早上8点，打工人挤地铁去上班"
        }
    ]
})
```

## 查询任务状态

### 接口地址
`GET https://api.minimaxi.com/v1/query/video_template_generation?task_id={task_id}`

### 状态说明
| 状态 | 含义 |
|------|------|
| **Preparing** | 准备中 |
| **Processing** | 生成中 |
| **Success** | 成功 |
| **Fail** | 失败 |

### 查询示例
```python
def query_agent_status(task_id, api_key):
    url = f"https://api.minimaxi.com/v1/query/video_template_generation?task_id={task_id}"
    headers = {'authorization': f'Bearer {api_key}'}
    
    response = requests.request("GET", url, headers=headers)
    result = response.json()
    
    return {
        'status': result['status'],
        'video_url': result.get('video_url', ''),
        'task_id': result['task_id']
    }

# 轮询等待完成
import time

def wait_for_completion(task_id, api_key, check_interval=10):
    """等待任务完成并获取视频链接"""
    while True:
        status_info = query_agent_status(task_id, api_key)
        
        if status_info['status'] == 'Success':
            print(f"✅ 生成完成: {status_info['video_url']}")
            return status_info['video_url']
        elif status_info['status'] == 'Fail':
            raise Exception("视频生成失败")
        
        print(f"⏳ 状态: {status_info['status']}")
        time.sleep(check_interval)
```

## 完整使用示例

### 统一视频Agent类
```python
import requests
import json
import time
import os
from typing import Optional, Dict, Any

class VideoAgentGenerator:
    def __init__(self, api_key: str, group_id: str):
        self.api_key = api_key
        self.group_id = group_id
        self.base_url = f"https://api.minimaxi.com/v1"
    
    def create_agent_task(self, template_id: str, 
                         media_inputs: Optional[list] = None,
                         text_inputs: Optional[list] = None,
                         callback_url: Optional[str] = None) -> str:
        """创建视频Agent任务"""
        url = f"{self.base_url}/video_template_generation?GroupId={self.group_id}"
        
        payload = {"template_id": template_id}
        
        if media_inputs:
            payload["media_inputs"] = [{"value": inp} for inp in media_inputs]
        if text_inputs:
            payload["text_inputs"] = [{"value": inp} for inp in text_inputs]
        if callback_url:
            payload["callback_url"] = callback_url
        
        headers = {
            'authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, json=payload)
        return response.json()['task_id']
    
    def wait_for_completion(self, task_id: str, check_interval: int = 10) -> str:
        """等待任务完成"""
        url = f"{self.base_url}/query/video_template_generation?task_id={task_id}"
        headers = {'authorization': f'Bearer {self.api_key}'}
        
        while True:
            response = requests.get(url, headers=headers)
            result = response.json()
            
            if result['status'] == 'Success':
                return result['video_url']
            elif result['status'] == 'Fail':
                raise Exception("视频生成失败")
            
            print(f"状态: {result['status']}...")
            time.sleep(check_interval)
    
    def download_video(self, video_url: str, output_path: str) -> str:
        """下载生成的视频"""
        video_data = requests.get(video_url).content
        
        with open(output_path, 'wb') as f:
            f.write(video_data)
        
        return output_path
    
    def generate_with_template(self, template_id: str, 
                              media_inputs: Optional[list] = None,
                              text_inputs: Optional[list] = None,
                              output_file: str = "output.mp4") -> str:
        """一键生成模板视频"""
        print("🎬 创建视频Agent任务...")
        task_id = self.create_agent_task(template_id, media_inputs, text_inputs)
        
        print(f"📋 任务ID: {task_id}")
        print("⏳ 等待生成完成...")
        
        video_url = self.wait_for_completion(task_id)
        
        print("💾 下载视频...")
        file_path = self.download_video(video_url, output_file)
        
        print(f"✅ 完成: {file_path}")
        return file_path

# 使用示例
generator = VideoAgentGenerator(api_key, group_id)

# 示例1: 宠物绝地求生
video_url = generator.generate_with_template(
    template_id="393769180141805569",
    media_inputs=["https://example.com/dog.jpg"],
    text_inputs=["老虎"],
    output_file="pet_survival.mp4"
)

# 示例2: labubu换脸
video_url = generator.generate_with_template(
    template_id="394246956137422856",
    media_inputs=["data:image/jpeg;base64,{face_image}"],
    output_file="labubu_face_swap.mp4"
)
```

## 模板分类使用指南

### 1. 宠物娱乐
```python
def pet_entertainment_templates():
    """宠物娱乐模板"""
    return {
        "吊环表演": "393881433990066176",
        "绝地求生": "393769180141805569",
        "麦当劳外卖员": "393879757702918151"
    }

# 批量生成宠物视频
for template_name, template_id in pet_entertainment_templates().items():
    task_id = generator.create_agent_task(
        template_id=template_id,
        media_inputs=["pet_photo.jpg"]
    )
    print(f"{template_name}: {task_id}")
```

### 2. 商业广告
```python
def commercial_ad_templates():
    """商业广告模板"""
    return {
        "女模特试穿": "393866076583718914",
        "男模特试穿": "393876118804459526",
        "麦当劳宠物": "393879757702918151"
    }

# 服装广告生成
def generate_clothing_ad(clothing_image, gender="female"):
    template_id = "393866076583718914" if gender == "female" else "393876118804459526"
    return generator.generate_with_template(
        template_id=template_id,
        media_inputs=[clothing_image],
        output_file=f"{gender}_model_ad.mp4"
    )
```

### 3. 写真艺术
```python
def artistic_portrait_templates():
    """写真艺术模板"""
    return {
        "藏族风写真": "393766210733957121",
        "四季写真": "398574688191234048",
        "情书写真": "393857704283172864"
    }

# 批量写真生成
def generate_portrait_series(face_image):
    results = {}
    for name, template_id in artistic_portrait_templates().items():
        video_path = generator.generate_with_template(
            template_id=template_id,
            media_inputs=[face_image],
            output_file=f"{name.replace(' ', '_')}.mp4"
        )
        results[name] = video_path
    return results
```

### 4. 创意动画
```python
def creative_animation_templates():
    """创意动画模板"""
    return {
        "labubu换脸": "394246956137422856",
        "生无可恋": "394125185182695432"
    }

# 幽默动画生成
def generate_funny_animation(subject):
    return generator.generate_with_template(
        template_id="394125185182695432",
        text_inputs=[f"{subject}痛苦地早起上班"],
        output_file="funny_animation.mp4"
    )
```

## 错误处理

### 错误码说明
| 状态码 | 含义 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | - |
| 1002 | 触发限流 | 稍后再试 |
| 1004 | 鉴权失败 | 检查API密钥 |
| 1008 | 余额不足 | 充值账户 |
| 1026 | 内容敏感 | 调整输入 |
| 2013 | 参数异常 | 检查参数格式 |
| 2049 | 无效API密钥 | 重新配置 |

### 图片验证工具
```python
import imghdr
from PIL import Image
import io
import base64

def validate_image_input(image_data):
    """验证图片输入"""
    try:
        # 如果是URL，先下载
        if image_data.startswith('http'):
            response = requests.get(image_data)
            image_bytes = response.content
        else:
            # 解析Base64
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
        
        # 检查格式
        image_format = imghdr.what(None, image_bytes)
        if image_format not in ['jpeg', 'png', 'webp']:
            return False, "不支持的图片格式"
        
        # 检查尺寸
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
        ratio = width / height
        
        if ratio < 0.4 or ratio > 2.5:
            return False, "图片比例不符合要求"
        
        if min(width, height) < 300:
            return False, "图片尺寸太小"
        
        if len(image_bytes) > 20 * 1024 * 1024:
            return False, "图片太大"
        
        return True, "验证通过"
        
    except Exception as e:
        return False, str(e)

# 验证示例
is_valid, message = validate_image_input("pet_photo.jpg")
if not is_valid:
    print(f"图片验证失败: {message}")
```

## 回调通知机制

### 回调配置示例
```python
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/agent_callback")
async def handle_agent_callback(request: Request):
    json_data = await request.json()
    
    # 验证请求
    challenge = json_data.get("challenge")
    if challenge:
        return {"challenge": challenge}
    
    # 处理回调
    task_id = json_data.get("task_id")
    status = json_data.get("status")
    video_url = json_data.get("video_url")
    
    print(f"Agent任务更新: {task_id} - {status}")
    if status == "Success":
        print(f"视频URL: {video_url}")
        # 可以在这里触发后续处理
    
    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 使用场景示例

### 1. 电商营销
```python
def generate_product_ads(product_images, model_gender="female"):
    """批量生成产品广告"""
    template_id = "393866076583718914" if model_gender == "female" else "393876118804459526"
    
    results = []
    for img_path in product_images:
        video_path = generator.generate_with_template(
            template_id=template_id,
            media_inputs=[img_path],
            output_file=f"ad_{model_gender}_{os.path.basename(img_path)}.mp4"
        )
        results.append(video_path)
    
    return results
```

### 2. 社交媒体内容
```python
def generate_social_content(user_photos):
    """生成社交媒体内容"""
    templates = {
        "藏族风写真": "393766210733957121",
        "四季写真": "398574688191234048",
        "labubu换脸": "394246956137422856"
    }
    
    results = {}
    for template_name, template_id in templates.items():
        video_path = generator.generate_with_template(
            template_id=template_id,
            media_inputs=[user_photos[0]],
            output_file=f"social_{template_name}.mp4"
        )
        results[template_name] = video_path
    
    return results
```

### 3. 宠物内容创作
```python
def create_pet_content(pet_photos):
    """创建宠物内容"""
    pet_templates = {
        "吊环表演": "393881433990066176",
        "绝地求生": "393769180141805569",
        "麦当劳外卖员": "393879757702918151"
    }
    
    results = {}
    for template_name, template_id in pet_templates.items():
        if template_name == "绝地求生":
            text_inputs = ["老虎"]  # 可根据宠物选择
        else:
            text_inputs = None
            
        video_path = generator.generate_with_template(
            template_id=template_id,
            media_inputs=[pet_photos[0]],
            text_inputs=text_inputs,
            output_file=f"pet_{template_name}.mp4"
        )
        results[template_name] = video_path
    
    return results
```

## 注意事项

### 使用限制
1. **图片要求**: 格式、尺寸、大小限制
2. **文本限制**: 根据模板要求提供
3. **有效期**: 视频URL有效期9小时
4. **异步处理**: 需要等待任务完成
5. **内容合规**: 避免敏感内容

### 最佳实践
1. **图片质量**: 使用高清、主体明确的图片
2. **参数匹配**: 严格按模板要求提供参数
3. **错误处理**: 完善的错误处理和重试机制
4. **并发控制**: 避免大量并发请求
5. **结果缓存**: 缓存生成的视频URL