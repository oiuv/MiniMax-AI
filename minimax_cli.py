#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniMax AI 统一命令行工具
提供用户友好的交互界面，整合所有AI功能
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import Optional, Dict, Any
import argparse
from pathlib import Path

# 尝试导入可选依赖
interactive_mode = True
try:
    import inquirer
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    console = Console()
except ImportError:
    interactive_mode = False
    console = None

class MiniMaxClient:
    def __init__(self):
        self.group_id = os.getenv('MINIMAX_GROUP_ID')
        self.api_key = os.getenv('MINIMAX_API_KEY')
        self.base_url = "https://api.minimaxi.com/v1"
        
        if not self.group_id or not self.api_key:
            self._setup_credentials()
    
    def _setup_credentials(self):
        """首次使用时的配置向导"""
        if interactive_mode:
            console.print(Panel.fit("[bold cyan]欢迎使用 MiniMax AI 工具[/bold cyan]"))
            console.print("首次使用需要配置API密钥信息")
            
            group_id = Prompt.ask("请输入您的 MiniMax Group ID")
            api_key = Prompt.ask("请输入您的 MiniMax API Key")
            
            # 保存到环境变量文件
            env_file = Path.home() / '.minimax_env'
            with open(env_file, 'w') as f:
                f.write(f"MINIMAX_GROUP_ID={group_id}\n")
                f.write(f"MINIMAX_API_KEY={api_key}\n")
            
            console.print(f"[green]配置已保存到 {env_file}[/green]")
            console.print("请重新运行程序，或使用: source ~/.minimax_env")
            sys.exit(0)
        else:
            print("请设置环境变量 MINIMAX_GROUP_ID 和 MINIMAX_API_KEY")
            sys.exit(1)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """统一请求封装"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 添加GroupId到查询参数（如果需要）
        if 't2a_v2' in endpoint or 'voice_clone' in endpoint:
            url += f"?GroupId={self.group_id}"
        
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            result = response.json()
            
            # 检查API错误
            if 'base_resp' in result and result['base_resp']['status_code'] != 0:
                error_msg = result['base_resp'].get('status_msg', '未知错误')
                raise Exception(f"API错误: {error_msg}")
                
            return result
        except requests.exceptions.RequestException as e:
            if interactive_mode:
                console.print(f"[red]网络请求失败: {e}[/red]")
            else:
                print(f"网络请求失败: {e}")
            sys.exit(1)
        except Exception as e:
            if interactive_mode:
                console.print(f"[red]错误: {e}[/red]")
            else:
                print(f"错误: {e}")
            sys.exit(1)
    
    def chat_completion(self, message: str, model: str = "MiniMax-Text-01", stream: bool = False) -> str:
        """智能对话 - 基于最新官方API文档
        
        支持的最新模型:
        - MiniMax-Text-01: 最新文本生成模型，最大token数 1,000,192
        - MiniMax-M1: 高性能文本模型，最大token数 1,000,192
        
        注意：原abab系列模型已升级为MiniMax-Text-01和MiniMax-M1
        """
        import requests
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "你是一个有用、诚实且友好的AI助手。"},
                {"role": "user", "content": message}
            ],
            "stream": False,
            "max_tokens": 1024,
            "temperature": 0.8,
            "top_p": 0.95
        }
        
        url = f"{self.base_url}/text/chatcompletion_v2"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # 根据官方API格式解析响应
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    return choice['message']['content']
                else:
                    return "抱歉，未能获取有效回复"
            else:
                return f"API响应异常: {result}"
                
        except requests.exceptions.RequestException as e:
            return f"网络请求失败: {e}"
        except Exception as e:
            return f"处理响应时出错: {e}"
    
    def generate_image(self, prompt: str, aspect_ratio: str = "1:1", n: int = 1, 
                      model: str = "image-01", width: int = None, height: int = None,
                      style: dict = None, subject_reference: list = None) -> list:
        """图像生成 - 支持完整官方API参数
        
        支持模型:
        - image-01: 画面表现细腻，支持文生图、图生图
        - image-01-live: 手绘、卡通画风增强
        
        宽高比支持: 1:1, 16:9, 4:3, 3:2, 2:3, 3:4, 9:16, 21:9
        分辨率: width/height 512-2048像素，需为8的倍数
        """
        data = {
            "model": model,
            "prompt": prompt,
            "response_format": "url",
            "n": min(n, 9),  # 最大9张
            "prompt_optimizer": True
        }
        
        # 添加宽高比或自定义分辨率
        if width and height:
            data["width"] = (width // 8) * 8  # 确保是8的倍数
            data["height"] = (height // 8) * 8
        else:
            data["aspect_ratio"] = aspect_ratio
        
        # 添加风格控制（仅image-01-live支持）
        if model == "image-01-live" and style:
            data["style"] = style
            
        # 添加主体参考（仅image-01支持）
        if model == "image-01" and subject_reference:
            data["subject_reference"] = subject_reference
            
        response = self._make_request("POST", "image_generation", json=data)
        
        # 正确处理响应格式
        if 'data' in response and 'image_urls' in response['data']:
            return response['data']['image_urls']
        elif 'data' in response and isinstance(response['data'], list):
            return [img['url'] for img in response['data']]
        elif 'task_id' in response:
            return [f"任务已提交: {response['task_id']}"]
        else:
            return [str(response)]
    
    def generate_video(self, prompt: str, model: str = "MiniMax-Hailuo-02") -> str:
        """视频生成 - 支持最新视频模型
        
        支持模型:
        - MiniMax-Hailuo-02: 新一代1080P超清视频，10秒生成
        - T2V-01-Director: 文生视频导演版，支持运镜指令
        - I2V-01-Director: 图生视频导演版，支持参考图片
        - I2V-01-live: 图生视频，卡通漫画风格增强
        - S2V-01: 主体参考视频，保持人物稳定性
        """
        data = {"prompt": prompt, "model": model}
        
        response = self._make_request("POST", "video_generation", json=data)
        return response['task_id']
    
    def query_video_status(self, task_id: str) -> Dict[str, Any]:
        """查询视频生成状态"""
        return self._make_request("GET", f"query/video_generation?task_id={task_id}")
    
    def download_file(self, file_id: str, filename: str = None, file_type: str = "video") -> str:
        """下载文件（视频/音频/图像）"""
        if not filename:
            ext = {
                "video": "mp4",
                "audio": "mp3", 
                "image": "jpg"
            }.get(file_type, "bin")
            filename = f"{file_type}_{file_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
        
        response = self._make_request("GET", f"files/retrieve?file_id={file_id}")
        download_url = response['file']['download_url']
        
        # 下载文件
        import requests
        file_data = requests.get(download_url).content
        
        # 保存到文件
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, 'wb') as f:
            f.write(file_data)
        
        return filepath
    
    def text_to_speech(self, text: str, voice_id: str = "female-chengshu", 
                      model: str = "speech-2.5-hd-preview", speed: float = 1.0, 
                      pitch: float = 0.0, volume: float = 1.0) -> str:
        """文本转语音 - 支持最新Speech 2.5模型"""
        if not text or not text.strip():
            raise ValueError("文本内容不能为空")
            
        data = {
            "model": model,
            "text": text.strip(),
            "voice_id": voice_id,
            "speed": float(max(0.5, min(2.0, speed))),
            "pitch": float(max(-1.0, min(1.0, pitch))),
            "volume": float(max(0.0, min(2.0, volume))),
        }
        
        # 移除可能为空的参数
        if speed == 1.0:
            data.pop("speed", None)
        if pitch == 0.0:
            data.pop("pitch", None)
        if volume == 1.0:
            data.pop("volume", None)
            
        response = self._make_request("POST", "t2a_v2", json=data)
        
        # 检查响应格式
        if 'data' in response and 'audio' in response['data']:
            return response['data']['audio']
        elif 'audio' in response:
            return response['audio']
        else:
            raise ValueError(f"API响应格式错误: {response}")

    def generate_music(self, prompt: str, lyrics: str = None, refer_voice: str = None, 
                      refer_instrumental: str = None, refer_vocal: str = None) -> str:
        """音乐生成 - 支持最新音乐模型
        
        支持模型:
        - music-1.5: 支持音乐描述和歌词生成
        - music-01: 支持上传音乐文件，通过干声和伴奏生成
        """
        payload = {
            'model': 'music-1.5',
            'prompt': prompt,
            'audio_setting': {
                'sample_rate': 44100,
                'bitrate': 256000,
                'format': 'mp3'
            }
        }
        
        if lyrics:
            payload['lyrics'] = lyrics
        
        if refer_voice:
            payload['refer_voice'] = refer_voice
        if refer_instrumental:
            payload['refer_instrumental'] = refer_instrumental
        if refer_vocal:
            payload['refer_vocal'] = refer_vocal
        
        response = self._make_request("POST", "music_generation", data=payload)
        return response['data']['audio']
    
    def clone_voice(self, file_id: str, voice_id: str, text: str, 
                   model: str = "speech-02-hd") -> Dict[str, Any]:
        """语音克隆 - 支持最新语音模型
        
        支持模型:
        - speech-02-hd: 持续更新的HD模型，出色韵律和复刻相似度
        - speech-02-turbo: 持续更新的Turbo模型，小语种能力加强
        - speech-01-hd: 稳定版本HD模型，超高复刻相似度
        - speech-01-turbo: 稳定版本Turbo模型，生成速度快
        """
        data = {
            "file_id": int(file_id),
            "voice_id": voice_id,
            "text": text,
            "model": model
        }
        
        return self._make_request("POST", f"voice_clone?GroupId={self.group_id}", json=data)

class PodcastUI:
    def __init__(self, client: MiniMaxClient):
        self.client = client
        try:
            from minimax_podcast import PodcastGenerator
            self.generator = PodcastGenerator(client)
        except ImportError:
            console.print("[red]播客模块未找到，请确保 minimax_podcast.py 存在[/red]")
            self.generator = None
    
    def show_podcast_menu(self):
        """显示播客菜单"""
        if not self.generator:
            console.print("[red]播客功能暂不可用[/red]")
            return
            
        console.print(Panel.fit("[bold purple]🎙️ 电台播客生成器[/bold purple]"))
        
        # 场景选择
        scenes = {
            "solo": "单人主播 - 温暖亲切的独白",
            "dialogue": "双人对话 - 轻松自然的讨论", 
            "panel": "多人圆桌 - 专业深入的论坛",
            "news": "新闻播报 - 正式权威的时事",
            "storytelling": "故事讲述 - 情感丰富的叙事"
        }
        
        scene_choices = [f"{key}: {desc}" for key, desc in scenes.items()]
        questions = [
            inquirer.List('scene',
                         message="选择播客场景",
                         choices=scene_choices)
        ]
        
        scene_choice = inquirer.prompt(questions)['scene']
        scene = scene_choice.split(':')[0]
        
        # 主题输入
        topic = Prompt.ask("播客主题")
        
        # 时长选择
        duration = int(Prompt.ask("时长(分钟)", default="10"))
        
        # 音色选择
        use_custom_voices = Confirm.ask("自定义音色？(否则使用推荐音色)")
        custom_voices = None
        
        if use_custom_voices:
            speaker_count = 1 if scene == "solo" else (2 if scene == "dialogue" else 3)
            custom_voices = []
            
            # 显示音色分类
            categories = list(self.generator.VOICE_CATEGORIES.keys())
            
            for i in range(speaker_count):
                console.print(f"\n[bold]为说话人{i+1}选择音色:[/bold]")
                
                # 选择分类
                category_choice = inquirer.list_input(
                    "音色分类",
                    choices=categories
                )
                
                # 选择具体音色
                voices = self.generator.VOICE_CATEGORIES[category_choice]
                voice_choices = [f"{desc} ({voice_id})" for voice_id, desc in voices.items()]
                
                voice_choice = inquirer.list_input(
                    f"说话人{i+1}音色",
                    choices=voice_choices
                )
                
                voice_id = voice_choice.split('(')[-1].rstrip(')')
                custom_voices.append(voice_id)
                console.print(f"[green]已选择: {voice_choice}[/green]")
        
        # 模型选择
        models = [
            "speech-2.5-hd-preview (极致相似度，2025-08-06发布)",
            "speech-2.5-turbo-preview (支持40个语种)",
            "speech-02-hd (出色韵律)",
            "speech-01-hd (超高复刻度)"
        ]
        
        model_choice = inquirer.list_input("选择语音模型", choices=models)
        model = model_choice.split(' ')[0]
        
        # 开始生成
        console.print(f"[yellow]正在生成{scene}播客: {topic}[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("生成播客中...", total=None)
            
            result = self.generator.generate_podcast(
                topic=topic,
                scene=scene,
                custom_voices=custom_voices,
                duration=duration,
                model=model
            )
            
            progress.update(task, completed=True)
        
        if result:
            console.print(f"[green]✅ 播客生成完成: {result}[/green]")
            
            # 提供播放选项
            if Confirm.ask("是否播放播客？"):
                try:
                    import subprocess
                    import platform
                    
                    if platform.system() == "Windows":
                        os.startfile(result)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.call(["open", result])
                    else:  # Linux
                        subprocess.call(["xdg-open", result])
                        
                except Exception as e:
                    console.print(f"[yellow]无法自动播放: {e}[/yellow]")
                    console.print(f"[dim]文件位置: {result}[/dim]")
        else:
            console.print("[red]播客生成失败[/red]")


class InteractiveUI:
    def __init__(self, client: MiniMaxClient):
        self.client = client
    
    def show_menu(self):
        """显示主菜单"""
        choices = [
            "💬 智能对话",
            "🎨 图像生成", 
            "🎬 视频生成",
            "🎵 音乐生成",
            "🎤 语音克隆",
            "🎙️ 电台播客",
            "📁 文件管理",
            "❌ 退出"
        ]
        
        questions = [
            inquirer.List('choice',
                         message="请选择功能",
                         choices=choices)
        ]
        
        return inquirer.prompt(questions)['choice']
    
    def chat_interface(self):
        """对话界面"""
        console.print(Panel.fit("[bold green]💬 智能对话[/bold green]"))
        
        # 模型选择 - 更新为最新模型
        models = [
            "MiniMax-Text-01 (最新文本生成模型，最大token数1,000,192)",
            "MiniMax-M1 (高性能文本模型，最大token数1,000,192)"
        ]
        
        model_choice = inquirer.list_input(
            "选择模型",
            choices=models
        )
        selected_model = model_choice.split(' ')[0]
        
        console.print(f"[dim]已选择模型: {selected_model}[/dim]")
        console.print("[dim]输入 'exit', 'quit' 或 '退出' 返回主菜单[/dim]\n")
        
        # 对话历史
        messages = [
            {"role": "system", "content": "你是一个有用、诚实且友好的AI助手。你会提供准确、有用的回答，并在不确定时承认自己的局限性。"}
        ]
        
        while True:
            message = Prompt.ask("[bold cyan]你[/bold cyan]")
            if message.lower() in ['exit', 'quit', '退出']:
                break
            
            messages.append({"role": "user", "content": message})
            
            try:
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    task = progress.add_task("AI思考中...", total=None)
                    response = self.client.chat_completion(message, selected_model)
                    progress.update(task, completed=True)
                
                messages.append({"role": "assistant", "content": response})
                console.print(Panel(response, title="[bold green]AI助手[/bold green]", border_style="green"))
                
            except Exception as e:
                console.print(f"[red]对话出错: {e}[/red]")
                console.print("[yellow]请检查网络连接和API密钥配置[/yellow]")
    
    def image_interface(self):
        """图像生成界面 - 支持完整参数"""
        console.print(Panel.fit("[bold blue]🎨 图像生成[/bold blue]"))
        
        # 模型选择
        models = [
            "image-01 (画面细腻，支持文生图/图生图)",
            "image-01-live (手绘/卡通画风增强)"
        ]
        
        model_choice = inquirer.list_input("选择图像模型", choices=models)
        selected_model = model_choice.split(' ')[0]
        
        prompt = Prompt.ask("请输入图像描述")
        
        # 参数选择
        use_custom_size = Confirm.ask("使用自定义分辨率？(否则使用宽高比)")
        
        if use_custom_size:
            width = int(Prompt.ask("宽度(512-2048)", default="1024"))
            height = int(Prompt.ask("高度(512-2048)", default="1024"))
            aspect_ratio = None
        else:
            aspect_ratios = [
                "1:1 (正方形)",
                "16:9 (宽屏)", 
                "4:3 (标准)",
                "3:2 (照片)",
                "2:3 (竖版)",
                "3:4 (竖屏)",
                "9:16 (手机竖屏)",
                "21:9 (超宽屏)"
            ]
            ratio_choice = inquirer.list_input("选择宽高比", choices=aspect_ratios)
            aspect_ratio = ratio_choice.split(' ')[0]
            width = height = None
        
        count = int(Prompt.ask("生成数量(1-9)", default="1"))
        
        # 风格设置（仅image-01-live支持）
        style = None
        if selected_model == "image-01-live":
            styles = [
                "手绘",
                "卡通", 
                "漫画",
                "水彩",
                "油画",
                "素描"
            ]
            style_choice = inquirer.list_input("选择画风", choices=styles)
            style = {"style": style_choice}
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("生成图像中...", total=None)
            urls = self.client.generate_image(
                prompt, 
                aspect_ratio=aspect_ratio,
                width=width,
                height=height,
                n=count,
                model=selected_model,
                style=style
            )
            progress.update(task, completed=True)
        
        console.print(f"[green]生成完成！共 {len(urls)} 张图像[/green]")
        for i, url in enumerate(urls, 1):
            console.print(f"图像 {i}: {url}")
            
        # 提供下载选项
        if Confirm.ask("是否下载所有图像？"):
            for i, url in enumerate(urls, 1):
                filename = f"image_{i}.jpg"
                console.print(f"下载图像 {i}...")
                # 这里可以添加实际下载逻辑
    
    def video_interface(self):
        """视频生成界面"""
        console.print(Panel.fit("[bold magenta]🎬 视频生成[/bold magenta]"))
        
        # 模型选择
        models = [
            "MiniMax-Hailuo-02 (1080P超清，10秒生成)",
            "T2V-01-Director (文生视频导演版)",
            "I2V-01-Director (图生视频导演版)",
            "I2V-01-live (卡通漫画增强)",
            "S2V-01 (主体参考)"
        ]
        
        model_choice = inquirer.list_input("选择视频模型", choices=models)
        selected_model = model_choice.split(' ')[0]
        
        prompt = Prompt.ask("请输入视频描述")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("提交任务...", total=None)
            task_id = self.client.generate_video(prompt, selected_model)
            progress.update(task, completed=True)
        
        console.print(f"[yellow]任务已提交，ID: {task_id}[/yellow]")
        console.print("正在生成中，请稍候...")
        
        while True:
            time.sleep(10)
            status = self.client.query_video_status(task_id)
            
            if status['status'] == 'Success':
                console.print(f"[green]视频生成完成！[/green]")
                
                # 自动下载
                filename = f"video_{task_id}.mp4"
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    download_task = progress.add_task("下载视频中...", total=None)
                    filepath = self.client.download_file(status['file_id'], filename, "video")
                    progress.update(download_task, completed=True)
                
                console.print(f"[green]视频已下载: {filepath}[/green]")
                break
            elif status['status'] == 'Fail':
                console.print("[red]视频生成失败[/red]")
                break
            else:
                console.print(f"状态: {status['status']}...")

def main():
    parser = argparse.ArgumentParser(description='MiniMax AI 统一命令行工具')
    parser.add_argument('--chat', help='智能对话模式', nargs='+')
    parser.add_argument('--image', help='图像生成')
    parser.add_argument('--video', help='视频生成')
    parser.add_argument('--music', help='音乐生成')
    parser.add_argument('--clone', help='语音克隆')
    parser.add_argument('--aspect-ratio', dest='aspect_ratio', default='1:1', 
                       choices=['1:1', '16:9', '4:3', '3:2', '2:3', '3:4', '9:16', '21:9'])
    parser.add_argument('--count', type=int, default=1, choices=range(1, 10))
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')
    parser.add_argument('--podcast', help='生成播客 (主题内容)')
    parser.add_argument('--scene', choices=['solo', 'dialogue', 'panel', 'news', 'storytelling'], 
                       default='solo', help='播客场景')
    parser.add_argument('--voice', action='append', help='自定义音色 (可多次使用)')
    
    args = parser.parse_args()
    
    client = MiniMaxClient()
    
    # 命令行模式
    if args.chat:
        message = ' '.join(args.chat)
        response = client.chat_completion(message)
        print(response)
    elif args.image:
        urls = client.generate_image(
            args.image, 
            aspect_ratio=args.aspect_ratio, 
            n=args.count
        )
        for url in urls:
            print(url)
    elif args.video:
        task_id = client.generate_video(args.video)
        print(f"任务ID: {task_id}")
    elif args.music:
        # 使用用户输入作为prompt，可选提供歌词
        audio_data = client.generate_music(
            prompt=args.music,
            lyrics="欢迎收听友彩伴您节目\n让我们一起分享精彩时光"
        )
        print(f"音乐数据已生成，长度: {len(audio_data)}")
    elif args.podcast:
        try:
            from minimax_podcast import PodcastGenerator
            generator = PodcastGenerator(client)
            
            result = generator.generate_podcast(
                topic=args.podcast,
                scene=args.scene,
                custom_voices=args.voice,
                duration=10
            )
            
            if result:
                print(f"播客生成完成: {result}")
            else:
                print("播客生成失败")
                
        except ImportError as e:
            print(f"播客模块未找到: {e}")
    elif args.interactive or interactive_mode:
        if not interactive_mode:
            print("请先安装依赖: pip install inquirer rich")
            sys.exit(1)
        
        ui = InteractiveUI(client)
        
        while True:
            choice = ui.show_menu()
            
            if "智能对话" in choice:
                ui.chat_interface()
            elif "图像生成" in choice:
                ui.image_interface()
            elif "视频生成" in choice:
                ui.video_interface()
            elif "音乐生成" in choice:
                print("音乐生成功能开发中...")
            elif "语音克隆" in choice:
                print("语音克隆功能开发中...")
            elif "电台播客" in choice:
                podcast_ui = PodcastUI(self.client)
                podcast_ui.show_podcast_menu()
            elif "退出" in choice:
                console.print("[yellow]感谢使用！[/yellow]")
                break
    else:
        parser.print_help()

if __name__ == "__main__":
    main()