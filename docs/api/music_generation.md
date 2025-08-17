# 音乐生成（Music Generation）API文档

## 功能概述
- ✅ AI音乐创作与生成
- ✅ 支持歌词与音乐灵感描述
- ✅ 多种音乐风格支持
- ✅ 自定义音频参数
- ✅ 90秒以内音乐生成
- ✅ 流式与非流式输出

## 接口地址
- **音乐生成**: `https://api.minimaxi.com/v1/music_generation?GroupId={YOUR_GROUP_ID}`

## 支持模型

### music-1.5 模型特性
| 特性 | 说明 |
|------|------|
| **音乐风格** | 支持独立民谣、流行音乐、古典等多种风格 |
| **情绪表达** | 忧郁、欢快、内省、渴望等情绪控制 |
| **场景适配** | 咖啡馆、雨天、夜晚、海边等场景描述 |
| **歌词支持** | 完整歌词输入，支持歌词结构标记 |
| **时长限制** | 90秒以内音乐生成 |
| **输出格式** | 支持MP3、WAV、PCM格式 |

## 接口参数说明

### 请求参数
| 参数 | 类型 | 必填 | 范围 | 说明 |
|------|------|------|------|------|
| model | string | ✅ | "music-1.5" | 固定模型选择 |
| prompt | string | ✅ | 10-300字符 | 音乐灵感描述 |
| lyrics | string | ✅ | 10-600字符 | 歌词内容 |
| stream | bool | ❌ | - | 是否开启流式输出 |
| output_format | string | ❌ | "url"/"hex" | 输出格式，默认hex |
| audio_setting | object | ❌ | - | 音频设置参数 |
| aigc_watermark | bool | ❌ | - | 是否添加水印 |

### audio_setting 参数
| 参数 | 类型 | 范围 | 说明 |
|------|------|------|------|
| sample_rate | int | [16000,24000,32000,44100] | 采样率，默认44100 |
| bitrate | int | [32000,64000,128000,256000] | 比特率，默认256000 |
| format | string | ["mp3","wav","pcm"] | 音频格式，默认mp3 |

## 使用示例

### 基础音乐生成
```python
import requests
import json

group_id = "your_group_id"
api_key = "your_api_key"

url = f"https://api.minimaxi.com/v1/music_generation?GroupId={group_id}"

# 基础音乐生成
payload = json.dumps({
    "model": "music-1.5",
    "prompt": "独立民谣,忧郁,内省,渴望,独自漫步,咖啡馆",
    "lyrics": "[verse]\n街灯微亮晚风轻抚\n影子拉长独自漫步\n旧外套裹着深深忧郁\n不知去向渴望何处\n[chorus]\n推开木门香气弥漫\n熟悉的角落陌生人看",
    "audio_setting": {
        "sample_rate": 44100,
        "bitrate": 256000,
        "format": "mp3"
    }
})

headers = {
    'authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
result = response.json()

# 获取音频数据
audio_hex = result["data"]["audio"]
print(f"音乐生成完成，音频长度: {len(audio_hex)} 字符")
```

### 不同风格音乐生成

#### 流行音乐
```python
pop_music = {
    "model": "music-1.5",
    "prompt": "流行音乐,欢快,夏日海滩,派对,青春,阳光",
    "lyrics": "[Intro]\n阳光沙滩海浪声\n[Verse]\n穿上比基尼走向海边\n椰子树下冰啤酒甜\n朋友们都在身边\n这一刻永远停留心间\n[Chorus]\n夏日狂欢现在开始\n跟着节拍尽情跳舞\n青春不需要解释\n快乐就是全部的意义",
    "audio_setting": {
        "sample_rate": 44100,
        "bitrate": 256000,
        "format": "mp3"
    }
}
```

#### 古典音乐
```python
classical_music = {
    "model": "music-1.5",
    "prompt": "古典音乐,宁静,优雅,钢琴独奏,夜晚,月光",
    "lyrics": "[Intro]\n月光如水洒落窗前\n[Verse]\n黑白键上指尖轻舞\n旋律如水静静流淌\n夜色温柔心事轻放\n钢琴声中寻找答案\n[Bridge]\n每一个音符都是故事\n每一段旋律都是回忆\n[Outro]\n月光下的琴声悠扬",
    "audio_setting": {
        "sample_rate": 44100,
        "bitrate": 256000,
        "format": "wav"
    }
}
```

#### 电子音乐
```python
electronic_music = {
    "model": "music-1.5",
    "prompt": "电子音乐,动感,夜店,节奏感,现代,都市夜晚",
    "lyrics": "[Intro]\n霓虹闪烁都市夜晚\n[Verse]\n电子节拍心跳同步\n灯光迷离脚步不乱\n都市节奏我们主宰\n音乐声中释放自我\n[Chorus]\n跟着节奏不要停\n让音乐带我们飞\n电子世界无限可能\n今夜我们永不疲倦",
    "audio_setting": {
        "sample_rate": 44100,
        "bitrate": 256000,
        "format": "mp3"
    }
}
```

## 歌词结构标记

### 支持的歌词结构
| 标记 | 含义 | 示例 |
|------|------|------|
| [Intro] | 前奏 | [Intro]\n轻柔的吉他前奏 |
| [Verse] | 主歌 | [Verse]\n故事开始了... |
| [Chorus] | 副歌 | [Chorus]\n高潮部分... |
| [Bridge] | 桥段 | [Bridge]\n情绪转换... |
| [Outro] | 尾奏 | [Outro]\n温柔的结尾 |

### 完整歌词示例
```python
complete_song = {
    "model": "music-1.5",
    "prompt": "华语流行,温柔治愈,爱情,思念,夜晚,星空",
    "lyrics": """[Intro]
钢琴声轻轻响起
像星星在夜空闪烁

[Verse 1]
想念你的时候
总是看着同一片天空
你的笑容在记忆里
像月光一样温柔

[Chorus]
如果星星会说话
一定会传达我的思念
在每个孤单的夜晚
你都是我心中的光

[Verse 2]
走过熟悉的街道
回忆在心头荡漾
你的声音还在耳边
像风一样轻轻歌唱

[Bridge]
时间带不走真挚的情感
距离隔不断深深的眷恋

[Chorus]
如果星星会说话
一定会传达我的思念
在每个孤单的夜晚
你都是我心中的光

[Outro]
就让这首歌
带着我的思念飞向远方""",
    "audio_setting": {
        "sample_rate": 44100,
        "bitrate": 256000,
        "format": "mp3"
    }
}
```

## 统一音乐生成类

### 完整封装类
```python
import requests
import json
import base64
from typing import Optional, Dict, Any

class MusicGenerator:
    def __init__(self, api_key: str, group_id: str):
        self.api_key = api_key
        self.group_id = group_id
        self.base_url = f"https://api.minimaxi.com/v1/music_generation?GroupId={group_id}"
    
    def generate_music(self, 
                      prompt: str, 
                      lyrics: str,
                      audio_format: str = "mp3",
                      sample_rate: int = 44100,
                      bitrate: int = 256000,
                      stream: bool = False,
                      watermark: bool = False) -> Dict[str, Any]:
        """生成音乐"""
        
        payload = {
            "model": "music-1.5",
            "prompt": prompt,
            "lyrics": lyrics,
            "stream": stream,
            "audio_setting": {
                "sample_rate": sample_rate,
                "bitrate": bitrate,
                "format": audio_format
            }
        }
        
        if not stream:
            payload["output_format"] = "hex"
            payload["aigc_watermark"] = watermark
        
        headers = {
            'authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(self.base_url, headers=headers, json=payload)
        return response.json()
    
    def save_audio(self, hex_data: str, filename: str) -> str:
        """保存音频文件"""
        audio_bytes = bytes.fromhex(hex_data)
        
        with open(filename, 'wb') as f:
            f.write(audio_bytes)
        
        return filename
    
    def generate_and_save(self, prompt: str, lyrics: str, filename: str, **kwargs) -> str:
        """一键生成并保存音乐"""
        print("🎵 正在生成音乐...")
        
        result = self.generate_music(prompt, lyrics, **kwargs)
        
        if result["data"]["status"] == 2:
            audio_hex = result["data"]["audio"]
            file_path = self.save_audio(audio_hex, filename)
            print(f"✅ 音乐生成完成: {file_path}")
            return file_path
        else:
            raise Exception("音乐生成失败")
    
    def create_pop_song(self, theme: str, lyrics: str, filename: str) -> str:
        """生成流行歌曲"""
        prompt = f"流行音乐,欢快,{theme},青春,活力"
        return self.generate_and_save(prompt, lyrics, filename)
    
    def create_ballad(self, mood: str, lyrics: str, filename: str) -> str:
        """生成民谣"""
        prompt = f"独立民谣,温柔,{mood},治愈,夜晚"
        return self.generate_and_save(prompt, lyrics, filename)
    
    def create_classical(self, mood: str, lyrics: str, filename: str) -> str:
        """生成古典音乐"""
        prompt = f"古典音乐,优雅,{mood},钢琴,宁静"
        return self.generate_and_save(prompt, lyrics, filename)

# 使用示例
generator = MusicGenerator(api_key, group_id)

# 生成治愈民谣
song_path = generator.create_ballad(
    mood="治愈",
    lyrics="""[Intro]
轻柔的吉他声响起
[Verse]
夜色温柔心事轻放
你的笑容在记忆里
像月光一样明亮
[Chorus]
就让这首歌带着温暖
治愈每个孤单的夜晚""",
    filename="healing_ballad.mp3"
)
```

## 音乐风格模板库

### 预定义风格模板
```python
class MusicStyleTemplates:
    @staticmethod
    def get_pop_template(theme: str) -> tuple:
        return (
            f"流行音乐,欢快,{theme},青春,活力,动感",
            "[Intro]\n动感节拍响起\n[Verse]\n跟着节奏一起摇摆\n[Chorus]\n这就是青春的模样"
        )
    
    @staticmethod
    def get_ballad_template(mood: str, scene: str) -> tuple:
        return (
            f"民谣,温柔,{mood},{scene},治愈,夜晚",
            f"[Intro]\n{scene}的夜晚\n[Verse]\n心事如潮水般涌来\n[Chorus]\n{scene}见证我的思念"
        )
    
    @staticmethod
    def get_rock_template(energy: str, theme: str) -> tuple:
        return (
            f"摇滚,激情,{energy},{theme},电吉他,鼓点",
            "[Intro]\n电吉他轰鸣\n[Verse]\n燃烧的青春\n[Chorus]\n永不熄灭的热情"
        )
    
    @staticmethod
    def get_electronic_template(vibe: str, setting: str) -> tuple:
        return (
            f"电子音乐,{vibe},{setting},现代,节奏感,都市",
            "[Intro]\n电子节拍心跳\n[Verse]\n都市霓虹闪烁\n[Chorus]\n跟着节奏舞动"
        )

# 使用模板
templates = MusicStyleTemplates()
prompt, lyrics = templates.get_ballad_template("忧郁", "雨天")
```

## 批量生成工具

### 音乐批量生成器
```python
class MusicBatchGenerator:
    def __init__(self, api_key: str, group_id: str):
        self.generator = MusicGenerator(api_key, group_id)
    
    def generate_song_series(self, themes: list, base_lyrics: str, output_dir: str) -> list:
        """生成歌曲系列"""
        results = []
        
        for theme in themes:
            prompt = f"流行音乐,{theme},青春,活力"
            filename = f"{theme.replace(' ', '_')}.mp3"
            filepath = os.path.join(output_dir, filename)
            
            try:
                song_path = self.generator.generate_and_save(
                    prompt, base_lyrics, filepath
                )
                results.append({
                    "theme": theme,
                    "path": song_path,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "theme": theme,
                    "error": str(e),
                    "status": "failed"
                })
        
        return results
    
    def generate_mood_series(self, moods: list, scene: str, output_dir: str) -> list:
        """生成情绪系列"""
        base_lyrics = """[Intro]
{scene}的夜晚
[Verse]
心事如潮水般涌来
[Chorus]
{scene}见证我的情感"""
        
        return self.generate_song_series(moods, base_lyrics, output_dir)

# 批量生成示例
batch_gen = MusicBatchGenerator(api_key, group_id)
moods = ["忧郁", "欢快", "治愈", "思念"]
results = batch_gen.generate_mood_series(moods, "夜晚", "mood_songs/")
```

## 错误处理

### 错误码说明
| 状态码 | 含义 | 解决方案 |
|--------|------|----------|
| 1001 | 超时 | 重试请求 |
| 1002 | 频率超限 | 降低请求频率 |
| 1004 | API密钥错误 | 检查密钥配置 |
| 1008 | 余额不足 | 充值账户 |
| 2013 | 参数错误 | 检查参数格式 |
| 2044 | 无权限 | 联系商务开通 |

### 安全错误处理
```python
def safe_generate_music(prompt, lyrics, **kwargs):
    """安全生成音乐"""
    try:
        # 参数验证
        if not prompt or len(prompt) < 10 or len(prompt) > 300:
            raise ValueError("prompt长度必须在10-300字符之间")
        
        if not lyrics or len(lyrics) < 10 or len(lyrics) > 600:
            raise ValueError("lyrics长度必须在10-600字符之间")
        
        generator = MusicGenerator(api_key, group_id)
        return generator.generate_music(prompt, lyrics, **kwargs)
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None
        }
```

## CLI工具集成

### 命令行音乐生成
```python
import argparse

def music_cli():
    parser = argparse.ArgumentParser(description='AI音乐生成工具')
    parser.add_argument('--prompt', required=True, help='音乐灵感描述')
    parser.add_argument('--lyrics', required=True, help='歌词内容')
    parser.add_argument('--output', default="output.mp3", help='输出文件名')
    parser.add_argument('--format', choices=['mp3', 'wav', 'pcm'], default='mp3')
    parser.add_argument('--style', choices=['pop', 'ballad', 'classical', 'electronic'], default='pop')
    
    args = parser.parse_args()
    
    generator = MusicGenerator(api_key, group_id)
    
    # 根据风格调整prompt
    style_prompts = {
        'pop': f"流行音乐,{args.prompt},欢快,青春",
        'ballad': f"民谣,{args.prompt},温柔,治愈",
        'classical': f"古典音乐,{args.prompt},优雅,宁静",
        'electronic': f"电子音乐,{args.prompt},动感,现代"
    }
    
    prompt = style_prompts[args.style]
    
    try:
        generator.generate_and_save(
            prompt=prompt,
            lyrics=args.lyrics,
            filename=args.output,
            audio_format=args.format
        )
        print(f"🎵 音乐生成完成: {args.output}")
    except Exception as e:
        print(f"❌ 生成失败: {e}")

if __name__ == "__main__":
    music_cli()
```

## 使用场景示例

### 1. 个性化音乐创作
```python
def create_personalized_song(name: str, mood: str, memories: str):
    prompt = f"流行音乐,温柔,{mood},治愈,个人回忆"
    lyrics = f"""[Intro]
关于{name}的回忆
[Verse]
{memories}
[Chorus]
{name}永远在我心里"""
    
    return generator.generate_and_save(
        prompt=prompt,
        lyrics=lyrics,
        filename=f"{name}_memories.mp3"
    )
```

### 2. 商业配乐
```python
def create_business_music(brand: str, theme: str, style: str):
    prompt = f"商业音乐,{style},{theme},专业,品牌宣传"
    lyrics = f"""[Intro]
{brand}的音乐故事
[Verse]
品质与创新的结合
[Chorus]
{brand}与你同行"""
    
    return generator.generate_and_save(
        prompt=prompt,
        lyrics=lyrics,
        filename=f"{brand}_{theme}.mp3"
    )
```

### 3. 教育内容
```python
def create_education_music(subject: str, level: str):
    prompt = f"教育音乐,轻松,{subject},{level},儿童友好"
    lyrics = f"""[Intro]
欢迎来到{subject}的世界
[Verse]
学习其实很简单
[Chorus]
我们一起快乐成长"""
    
    return generator.generate_and_save(
        prompt=prompt,
        lyrics=lyrics,
        filename=f"education_{subject}.mp3"
    )
```

## 注意事项

### 使用限制
1. **字符限制**: prompt 10-300字符，lyrics 10-600字符
2. **时长限制**: 生成音乐90秒以内
3. **URL有效期**: 24小时，请及时下载
4. **内容合规**: 避免敏感内容
5. **歌词格式**: 使用换行符分隔每行

### 最佳实践
1. **灵感描述**: 具体描述音乐风格、情绪、场景
2. **歌词结构**: 使用[Intro][Verse][Chorus]等标记
3. **参数优化**: 根据需求调整采样率和比特率
4. **重试机制**: 网络异常时自动重试
5. **缓存管理**: 保存生成的音乐文件