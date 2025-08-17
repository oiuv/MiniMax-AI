# 图像生成（Image Generation）API文档

## 功能概述
- ✅ 文生图：基于文本描述生成创意图像
- ✅ 图生图：基于参考图片进行图像生成
- ✅ 画风控制：支持漫画、元气、中世纪、水彩等风格
- ✅ 主体参考：支持人像主体参考，上传人脸照片
- ✅ 比例控制：支持多种宽高比例设置
- ✅ 分辨率自定义：512-2048像素范围
- ✅ 批量生成：单次请求可生成1-9张图片

## 接口地址
- **图像生成**: `https://api.minimaxi.com/v1/image_generation`

## 支持模型

### 模型对比表
| 模型名称 | 功能特点 | 支持画风控制 | 主体参考 | 分辨率控制 |
|----------|----------|--------------|----------|------------|
| **image-01** | 全新图像生成模型，画面表现细腻 | ❌ | ✅ | ✅ |
| **image-01-live** | 支持画风设置，风格化生成 | ✅ | ✅ | ❌ |

## 接口参数说明

### 基础参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| **model** | string | ✅ | 模型选择：image-01 或 image-01-live |
| **prompt** | string | ✅ | 图像描述，最大1500字符 |
| **aspect_ratio** | string | ❌ | 宽高比：1:1, 16:9, 4:3, 3:2, 2:3, 3:4, 9:16, 21:9，默认1:1 |
| **response_format** | string | ❌ | 返回格式：url 或 base64，默认url |
| **n** | int | ❌ | 生成图片数量，1-9，默认1 |
| **seed** | int | ❌ | 随机种子，相同种子生成相似图片 |
| **prompt_optimizer** | bool | ❌ | 自动优化prompt，默认false |
| **aigc_watermark** | bool | ❌ | 添加水印，默认false |

### 分辨率参数（仅image-01支持）
| 参数 | 类型 | 范围 | 说明 |
|------|------|------|------|
| **width** | int | [512, 2048] | 图片宽度，需为8的倍数 |
| **height** | int | [512, 2048] | 图片高度，需为8的倍数 |

### 主体参考参数
| 参数 | 类型 | 说明 |
|------|------|------|
| **subject_reference** | array | 主体参考图片数组 |
| **type** | string | 主体类型，仅支持"character" |
| **image_file** | string | 参考图片，支持Base64或URL |

### 画风控制参数（仅image-01-live支持）
| 参数 | 类型 | 说明 |
|------|------|------|
| **style_type** | string | 画风：漫画、元气、中世纪、水彩 |
| **style_weight** | float | 画风权重，(0,1]，默认0.8 |

## 图片要求

### 参考图片规范
- **格式**: JPG、JPEG、PNG
- **大小**: 小于10MB
- **类型**: 
  1. Base64格式：`data:image/jpeg;base64,{data}`
  2. 公网URL（可直接访问）
- **人像要求**: 单人人脸正面照片，模型理解更准确
- **数组限制**: 当前仅支持单图参考（数组长度=1）

## 使用示例

### 基础文生图
```python
import requests
import json

url = "https://api.minimaxi.com/v1/image_generation"
api_key = "your_api_key"

payload = json.dumps({
    "model": "image-01",
    "prompt": "men Dressing in white t shirt, full-body stand front view image :25, outdoor, Venice beach sign, full-body image, Los Angeles, Fashion photography of 90s, documentary, Film grain, photorealistic",
    "aspect_ratio": "16:9",
    "response_format": "url",
    "n": 3,
    "prompt_optimizer": True
})

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
result = response.json()

print(f"生成成功数量: {result['metadata']['success_count']}")
for i, url in enumerate(result['data']['image_urls']):
    print(f"图片{i+1}: {url}")
```

### 图生图（主体参考）
```python
import base64

# 读取参考图片并转换为Base64
def image_to_base64(image_path):
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('utf-8')

# 使用参考图片
reference_image = image_to_base64("person_photo.jpg")
reference_data = f"data:image/jpeg;base64,{reference_image}"

payload = json.dumps({
    "model": "image-01",
    "prompt": "同一个人，穿着太空服，在月球表面行走，科幻风格",
    "subject_reference": [
        {
            "type": "character",
            "image_file": reference_data
        }
    ],
    "aspect_ratio": "16:9",
    "n": 1
})

response = requests.request("POST", url, headers=headers, data=payload)
```

### 画风控制示例
```python
# 水彩风格人像
payload = json.dumps({
    "model": "image-01-live",
    "prompt": "一位优雅的女性，在花园中写生，阳光温暖",
    "style": {
        "style_type": "水彩",
        "style_weight": 0.9
    },
    "aspect_ratio": "4:3",
    "n": 2
})

# 漫画风格场景
payload = json.dumps({
    "model": "image-01-live",
    "prompt": "城市街景，霓虹灯闪烁，夜晚氛围，赛博朋克",
    "style": {
        "style_type": "漫画",
        "style_weight": 0.8
    },
    "aspect_ratio": "16:9"
})
```

### 分辨率自定义
```python
# 高分辨率生成
payload = json.dumps({
    "model": "image-01",
    "prompt": "超高清风景摄影，山川湖泊，日出时分，8K画质",
    "width": 1920,
    "height": 1080,
    "response_format": "url",
    "n": 1
})

# 正方形图片
payload = json.dumps({
    "model": "image-01",
    "prompt": "可爱猫咪头像，卡通风格，大眼睛，毛茸茸",
    "width": 1024,
    "height": 1024
})
```

## 批量生成示例

### 同一描述多图生成
```python
def generate_multiple_images(prompt, count=4, aspect_ratio="16:9"):
    """批量生成图片"""
    payload = json.dumps({
        "model": "image-01",
        "prompt": prompt,
        "n": min(count, 9),  # 最大9张
        "aspect_ratio": aspect_ratio,
        "response_format": "url"
    })
    
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

# 使用示例
results = generate_multiple_images(
    prompt="未来城市，高楼林立，飞行汽车，科幻风格",
    count=4,
    aspect_ratio="16:9"
)

for i, img_url in enumerate(results['data']['image_urls']):
    print(f"图片 {i+1}: {img_url}")
```

### 不同比例对比
```python
def compare_aspect_ratios(prompt):
    """对比不同宽高比效果"""
    ratios = ["1:1", "16:9", "4:3", "3:2", "21:9"]
    
    for ratio in ratios:
        payload = json.dumps({
            "model": "image-01",
            "prompt": prompt,
            "aspect_ratio": ratio,
            "n": 1
        })
        
        response = requests.request("POST", url, headers=headers, data=payload)
        result = response.json()
        
        print(f"比例 {ratio}: {result['data']['image_urls'][0]}")
```

## 统一图像生成类

### 完整封装类
```python
import requests
import json
import base64
from typing import List, Dict, Any, Optional

class ImageGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.minimaxi.com/v1/image_generation"
    
    def generate_text_to_image(self, 
                             prompt: str,
                             model: str = "image-01",
                             aspect_ratio: str = "1:1",
                             width: Optional[int] = None,
                             height: Optional[int] = None,
                             n: int = 1,
                             seed: Optional[int] = None,
                             prompt_optimizer: bool = False,
                             response_format: str = "url") -> Dict[str, Any]:
        """文生图"""
        
        payload = {
            "model": model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "n": n,
            "prompt_optimizer": prompt_optimizer,
            "response_format": response_format
        }
        
        if width and height and model == "image-01":
            payload["width"] = width
            payload["height"] = height
        
        if seed:
            payload["seed"] = seed
        
        return self._make_request(payload)
    
    def generate_with_reference(self,
                              prompt: str,
                              reference_image: str,
                              model: str = "image-01",
                              aspect_ratio: str = "1:1",
                              n: int = 1) -> Dict[str, Any]:
        """图生图 - 主体参考"""
        
        payload = {
            "model": model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "n": n,
            "subject_reference": [
                {
                    "type": "character",
                    "image_file": reference_image
                }
            ]
        }
        
        return self._make_request(payload)
    
    def generate_with_style(self,
                          prompt: str,
                          style_type: str,
                          style_weight: float = 0.8,
                          aspect_ratio: str = "1:1",
                          n: int = 1) -> Dict[str, Any]:
        """画风控制生成"""
        
        payload = {
            "model": "image-01-live",
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "n": n,
            "style": {
                "style_type": style_type,
                "style_weight": style_weight
            }
        }
        
        return self._make_request(payload)
    
    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """统一请求方法"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(self.base_url, headers=headers, json=payload)
        return response.json()
    
    def download_images(self, result: Dict[str, Any], output_dir: str = "./images") -> List[str]:
        """下载生成的图片"""
        import os
        import urllib.request
        
        os.makedirs(output_dir, exist_ok=True)
        
        image_urls = result['data']['image_urls']
        downloaded_files = []
        
        for i, url in enumerate(image_urls):
            filename = f"generated_{i+1}.jpg"
            filepath = os.path.join(output_dir, filename)
            
            urllib.request.urlretrieve(url, filepath)
            downloaded_files.append(filepath)
            
        return downloaded_files

# 使用示例
generator = ImageGenerator("your_api_key")

# 文生图
result = generator.generate_text_to_image(
    prompt="日落时分的海滩，金色阳光，海浪轻拍，浪漫氛围",
    aspect_ratio="16:9",
    n=2
)

# 图生图
person_image = "data:image/jpeg;base64,{base64_data}"
result = generator.generate_with_reference(
    prompt="同一个人，穿着古代汉服，在樱花树下",
    reference_image=person_image
)

# 画风控制
result = generator.generate_with_style(
    prompt="城市街景，霓虹灯光，赛博朋克风格",
    style_type="漫画",
    style_weight=0.9
)
```

## 高级应用场景

### 1. 电商产品图生成
```python
def generate_product_images(product_name, style="modern"):
    """生成电商产品图"""
    prompts = {
        "modern": f"{product_name} 产品展示，简洁背景，专业摄影，电商风格",
        "lifestyle": f"{product_name} 生活场景使用，温馨家庭氛围，自然光",
        "luxury": f"{product_name} 高端奢华展示，精致背景，专业布光"
    }
    
    generator = ImageGenerator("your_api_key")
    return generator.generate_text_to_image(
        prompt=prompts[style],
        aspect_ratio="1:1",
        width=1024,
        height=1024,
        n=3
    )

# 使用示例
result = generate_product_images("智能手表", "modern")
```

### 2. 社交媒体内容
```python
def generate_social_content(theme, platform="instagram"):
    """生成社交媒体图片"""
    aspect_ratios = {
        "instagram": "1:1",
        "facebook": "16:9",
        "twitter": "16:9",
        "tiktok": "9:16"
    }
    
    prompt = f"{theme} 社交媒体风格，色彩鲜艳，吸引眼球，适合{platform}"
    
    generator = ImageGenerator("your_api_key")
    return generator.generate_text_to_image(
        prompt=prompt,
        aspect_ratio=aspect_ratios[platform],
        n=4
    )
```

### 3. 艺术创作
```python
def create_art_series(concept, art_style="水彩"):
    """创建艺术系列"""
    styles = ["水彩", "漫画", "中世纪", "元气"]
    
    generator = ImageGenerator("your_api_key")
    results = []
    
    for style in styles:
        result = generator.generate_with_style(
            prompt=f"{concept} 艺术作品",
            style_type=style,
            aspect_ratio="4:3"
        )
        results.append({"style": style, "result": result})
    
    return results
```

## 错误处理

### 错误码说明
| 状态码 | 含义 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | - |
| 1002 | 触发限流 | 稍后再试 |
| 1004 | 账号鉴权失败 | 检查API密钥 |
| 1008 | 余额不足 | 充值账户 |
| 1026 | 敏感内容 | 调整描述 |
| 2013 | 参数异常 | 检查参数格式 |
| 2049 | 无效API密钥 | 重新配置 |

### 错误处理示例
```python
def safe_generate_image(prompt, **kwargs):
    """安全生成图片"""
    generator = ImageGenerator("your_api_key")
    
    try:
        # 参数验证
        if len(prompt) > 1500:
            raise ValueError("prompt长度不能超过1500字符")
        
        result = generator.generate_text_to_image(prompt, **kwargs)
        
        if result["base_resp"]["status_code"] != 0:
            raise Exception(f"生成失败: {result['base_resp']['status_msg']}")
        
        return {
            "success": True,
            "data": result,
            "image_urls": result["data"]["image_urls"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None
        }

# 使用示例
result = safe_generate_image("可爱猫咪，卡通风格")
if result["success"]:
    print("生成成功！")
else:
    print(f"错误: {result['error']}")
```

## 最佳实践

### 1. Prompt优化技巧
- **具体描述**: 避免模糊词汇，使用具体场景描述
- **风格关键词**: 添加"专业摄影"、"手绘风格"等关键词
- **构图指导**: 使用"构图"、"视角"、"光线"等术语

### 2. 参数选择建议
- **电商**: 1:1比例，1024x1024分辨率
- **社交媒体**: 根据平台选择合适比例
- **壁纸**: 16:9或21:9比例
- **头像**: 1:1比例，512x512或1024x1024

### 3. 质量优化
- **使用prompt_optimizer**: 开启自动优化
- **设置seed**: 复现相同效果
- **批量生成**: 多图选择最佳效果
- **分辨率控制**: 避免过大分辨率影响质量

## 注意事项

### 使用限制
1. **字符限制**: prompt ≤ 1500字符
2. **图片大小**: 参考图片 < 10MB
3. **分辨率**: 建议200万像素范围内
4. **比例冲突**: 同时设置width/height和aspect_ratio时，以aspect_ratio为准
5. **URL有效期**: 24小时，请及时下载

### 性能建议
- 批量生成时控制n值（建议1-4张）
- 合理设置分辨率，避免过大尺寸
- 使用缓存避免重复生成相同图片