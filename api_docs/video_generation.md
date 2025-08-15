# 视频生成（Video Generation）API文档

## 功能概述
- ✅ 文生视频、图生视频、主体参考视频
- ✅ 支持1080P高清视频生成
- ✅ 6秒/10秒时长选择
- ✅ 运镜控制指令
- ✅ 异步任务处理
- ✅ 回调通知机制

## 接口概览

### 整体流程
1. **创建任务** → `POST /v1/video_generation`
2. **查询状态** → `GET /v1/query/video_generation?task_id={task_id}`
3. **下载结果** → `GET /v1/files/retrieve?file_id={file_id}`

## 支持模型

### 模型对比表
| 模型 | 功能特点 | 分辨率支持 | 时长 | 特殊能力 |
|------|----------|------------|------|----------|
| **MiniMax-Hailuo-02** | 新一代模型，精准指令遵循 | 512P/768P/1080P | 6s/10s | 多种分辨率 |
| **T2V-01-Director** | 文生视频导演版 | 720P | 6s | 运镜指令 |
| **I2V-01-Director** | 图生视频导演版 | 720P | 6s | 运镜指令 |
| **I2V-01-live** | 卡通/漫画增强 | 720P | 6s | 手绘风格增强 |
| **S2V-01** | 主体参考视频 | 720P | 6s | 人物一致性 |

## 创建视频生成任务

### 接口地址
`POST https://api.minimaxi.com/v1/video_generation?GroupId={YOUR_GROUP_ID}`

### 请求参数

#### 基础参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | ✅ | 模型选择 |
| prompt | string | ✅ | 视频描述，≤2000字符 |
| duration | int | ❌ | 时长：6或10秒，默认6 |
| resolution | string | ❌ | 分辨率设置 |
| prompt_optimizer | bool | ❌ | 自动优化prompt，默认True |
| fast_pretreatment | bool | ❌ | 加速预处理，仅Hailuo-02 |

#### 分辨率与时长对应表
| 模型 | 时长 | 可选分辨率 | 默认 |
|------|------|------------|------|
| MiniMax-Hailuo-02 | 6s | 512P, 768P, 1080P | 768P |
| MiniMax-Hailuo-02 | 10s | 512P, 768P | 768P |
| 01系列全模型 | 6s | 720P | 720P |

### 运镜控制指令

#### 支持的15种运镜方式
| 类型 | 指令 | 说明 |
|------|------|------|
| **平移** | [左移] [右移] | 左右水平移动 |
| **摇摄** | [左摇] [右摇] | 左右旋转视角 |
| **推拉** | [推进] [拉远] | 镜头前后移动 |
| **升降** | [上升] [下降] | 镜头上下移动 |
| **俯仰** | [上摇] [下摇] | 镜头上下旋转 |
| **变焦** | [变焦推近] [变焦拉远] | 镜头变焦 |
| **其他** | [晃动] [跟随] [固定] | 特殊运镜效果 |

#### 运镜使用示例
```python
# 单一运镜
prompt = "男子拿起一本书[上升]，然后阅读[固定]"

# 组合运镜
prompt = "镜头[推进]拍摄人物，然后[左摇]展示周围环境"

# 顺序运镜
prompt = "先[上升]俯瞰全景，然后[右移]展示城市风光"
```

### 图片输入参数

#### 首帧图片 (first_frame_image)
- **适用模型**: MiniMax-Hailuo-02, I2V-系列
- **格式**: data:image/jpeg;base64,{data} 或 URL
- **要求**: JPG/JPEG/PNG/WebP, 2:5 < 长宽比 < 5:2, 短边≥300px, ≤20MB

#### 主体参考图片 (subject_reference)
- **适用模型**: S2V-01
- **格式**: Base64编码或URL
- **限制**: 单主体，人物面部，≤20MB

### 请求示例

#### 文生视频
```python
import requests
import json

group_id = "your_group_id"
api_key = "your_api_key"

url = f"https://api.minimaxi.com/v1/video_generation?GroupId={group_id}"

# 基础文生视频
payload = json.dumps({
    "model": "MiniMax-Hailuo-02",
    "prompt": "一只可爱的熊猫在竹林中悠闲散步，阳光透过竹叶洒下斑驳的光影",
    "duration": 6,
    "resolution": "1080P"
})

headers = {
    'authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
task_id = response.json()['task_id']
print(f"任务创建成功: {task_id}")
```

#### 图生视频
```python
# 图生视频示例
payload = json.dumps({
    "model": "I2V-01-Director",
    "prompt": "让图片中的风景动起来，[右移]展示更多景色",
    "duration": 6,
    "first_frame_image": "data:image/jpeg;base64,{base64_image_data}"
})
```

#### 主体参考视频
```python
# 主体参考视频示例
payload = json.dumps({
    "model": "S2V-01",
    "prompt": "保持人物特征一致，展示不同角度的微笑",
    "duration": 6,
    "subject_reference": [{
        "type": "character",
        "image": "data:image/jpeg;base64,{person_image_data}"
    }]
})
```

## 查询任务状态

### 接口地址
`GET https://api.minimaxi.com/v1/query/video_generation?task_id={task_id}`

### 状态说明
| 状态 | 含义 |
|------|------|
| **Preparing** | 准备中 |
| **Queueing** | 队列中 |
| **Processing** | 生成中 |
| **Success** | 成功 |
| **Fail** | 失败 |

### 查询示例
```python
import time

def query_video_status(task_id, api_key):
    url = f"https://api.minimaxi.com/v1/query/video_generation?task_id={task_id}"
    headers = {'authorization': f'Bearer {api_key}'}
    
    response = requests.request("GET", url, headers=headers)
    result = response.json()
    
    return {
        'status': result['status'],
        'file_id': result.get('file_id', ''),
        'width': result.get('video_width', 0),
        'height': result.get('video_height', 0)
    }

# 轮询查询
while True:
    status_info = query_video_status(task_id, api_key)
    
    if status_info['status'] == 'Success':
        print(f"✅ 视频生成完成: {status_info['file_id']}")
        break
    elif status_info['status'] == 'Fail':
        print("❌ 视频生成失败")
        break
    else:
        print(f"⏳ 状态: {status_info['status']}")
        time.sleep(10)
```

## 回调通知机制

### 回调配置
```python
from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.post("/video_callback")
async def handle_video_callback(request: Request):
    json_data = await request.json()
    
    # 验证请求
    challenge = json_data.get("challenge")
    if challenge:
        return {"challenge": challenge}
    
    # 处理回调
    task_id = json_data.get("task_id")
    status = json_data.get("status")
    file_id = json_data.get("file_id")
    
    print(f"任务 {task_id} 状态更新: {status}")
    if status == "Success":
        print(f"文件ID: {file_id}")
    
    return {"status": "success"}
```

## 完整使用流程

### 完整Python示例
```python
import os
import time
import requests
import json

class VideoGenerator:
    def __init__(self, api_key, group_id):
        self.api_key = api_key
        self.group_id = group_id
        self.base_url = f"https://api.minimaxi.com/v1"
    
    def create_video_task(self, prompt, model="MiniMax-Hailuo-02", 
                         duration=6, resolution="1080P", **kwargs):
        """创建视频生成任务"""
        url = f"{self.base_url}/video_generation?GroupId={self.group_id}"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "duration": duration,
            "resolution": resolution
        }
        
        # 添加可选参数
        if 'first_frame_image' in kwargs:
            payload['first_frame_image'] = kwargs['first_frame_image']
        if 'subject_reference' in kwargs:
            payload['subject_reference'] = kwargs['subject_reference']
        if 'callback_url' in kwargs:
            payload['callback_url'] = kwargs['callback_url']
        
        headers = {
            'authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, json=payload)
        return response.json()['task_id']
    
    def wait_for_completion(self, task_id, check_interval=10):
        """等待任务完成"""
        url = f"{self.base_url}/query/video_generation?task_id={task_id}"
        headers = {'authorization': f'Bearer {self.api_key}'}
        
        while True:
            response = requests.get(url, headers=headers)
            result = response.json()
            
            status = result['status']
            print(f"当前状态: {status}")
            
            if status == 'Success':
                return {
                    'file_id': result['file_id'],
                    'width': result['video_width'],
                    'height': result['video_height']
                }
            elif status == 'Fail':
                raise Exception("视频生成失败")
            
            time.sleep(check_interval)
    
    def download_video(self, file_id, output_path):
        """下载生成的视频"""
        url = f"{self.base_url}/files/retrieve?file_id={file_id}"
        headers = {'authorization': f'Bearer {self.api_key}'}
        
        response = requests.get(url, headers=headers)
        download_url = response.json()['file']['download_url']
        
        video_data = requests.get(download_url).content
        
        with open(output_path, 'wb') as f:
            f.write(video_data)
        
        return output_path
    
    def generate_video(self, prompt, output_file, **kwargs):
        """一键生成视频"""
        print("🎬 创建视频任务...")
        task_id = self.create_video_task(prompt, **kwargs)
        
        print(f"📋 任务ID: {task_id}")
        print("⏳ 等待生成完成...")
        
        result = self.wait_for_completion(task_id)
        
        print("💾 下载视频...")
        file_path = self.download_video(result['file_id'], output_file)
        
        print(f"✅ 完成: {file_path}")
        return file_path

# 使用示例
generator = VideoGenerator(api_key, group_id)

generator.generate_video(
    prompt="一只可爱的熊猫在竹林中悠闲散步[跟随]，阳光透过竹叶洒下斑驳的光影",
    output_file="panda_video.mp4",
    model="MiniMax-Hailuo-02",
    duration=6,
    resolution="1080P"
)
```

## 高级使用场景

### 运镜控制高级示例
```python
# 复杂运镜控制
advanced_prompt = """
一个优雅的芭蕾舞者在舞台上表演[上升]，
镜头[推进]聚焦舞者的表情，
然后[右摇]展示整个舞台，
最后[拉远]俯瞰全景，
展现优美的舞蹈姿态
"""

task_id = generator.create_video_task(
    prompt=advanced_prompt,
    model="T2V-01-Director",  # 导演版支持运镜
    duration=6
)
```

### 图生视频示例
```python
import base64

# 读取图片并转换为base64
def image_to_base64(image_path):
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('utf-8')

image_base64 = image_to_base64("landscape.jpg")
image_data_url = f"data:image/jpeg;base64,{image_base64}"

task_id = generator.create_video_task(
    prompt="让这幅风景画动起来[右移]展示更多景色",
    model="I2V-01-Director",
    duration=6,
    first_frame_image=image_data_url
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
| 1026 | 内容敏感 | 调整描述 |
| 2013 | 参数异常 | 检查参数 |
| 2049 | 无效API密钥 | 重新配置 |

### 错误处理示例
```python
def safe_generate_video(prompt, **kwargs):
    """安全生成视频"""
    try:
        generator = VideoGenerator(api_key, group_id)
        return generator.generate_video(prompt, **kwargs)
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return None

# 带重试的生成
def generate_with_retry(prompt, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            result = safe_generate_video(prompt, **kwargs)
            if result:
                return result
        except Exception as e:
            print(f"第{attempt+1}次尝试失败: {e}")
            if attempt < max_retries - 1:
                time.sleep(30)
    
    return None
```

## 注意事项

### 使用限制
1. **字符限制**: prompt ≤ 2000字符
2. **图片要求**: 格式、大小、比例限制
3. **模型选择**: 不同模型有不同能力
4. **分辨率**: 与时长和模型相关
5. **运镜**: 导演版模型支持完整运镜控制

### 最佳实践
1. **描述清晰**: 具体详细的场景描述
2. **运镜合理**: 运镜指令要符合逻辑
3. **图片质量**: 首帧图片清晰、主体明确
4. **耐心等待**: 视频生成需要5-15分钟
5. **监控状态**: 及时查询任务状态

## 集成应用

### CLI工具集成
```python
# 命令行视频生成
def video_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', required=True)
    parser.add_argument('--model', default='MiniMax-Hailuo-02')
    parser.add_argument('--duration', type=int, choices=[6, 10], default=6)
    parser.add_argument('--resolution', choices=['512P', '768P', '1080P'], default='768P')
    parser.add_argument('--output', default='output.mp4')
    
    args = parser.parse_args()
    
    generator = VideoGenerator(api_key, group_id)
    generator.generate_video(
        prompt=args.prompt,
        output_file=args.output,
        model=args.model,
        duration=args.duration,
        resolution=args.resolution
    )
```