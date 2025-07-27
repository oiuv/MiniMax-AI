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
        self.base_url = "https://api.minimax.chat/v1"
        
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
    
    def chat_completion(self, message: str, model: str = "abab5.5-chat", stream: bool = False) -> str:
        """智能对话 - 基于官方API文档
        
        支持的模型:
        - abab6.5s-chat: 最新版本，支持复杂对话
        - abab6.5-chat: 标准版本，平衡性能与成本  
        - abab5.5s-chat: 轻量版本，响应速度快
        - abab5.5-chat: 基础版本，成本优化
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
    
    def generate_image(self, prompt: str, aspect_ratio: str = "16:9", n: int = 1) -> list:
        """图像生成"""
        data = {
            "model": "image-01",
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "response_format": "url",
            "n": n,
            "prompt_optimizer": True
        }
        
        response = self._make_request("POST", "image_generation", json=data)
        
        if 'data' in response:
            return [img['url'] for img in response['data']]
        elif 'task_id' in response:
            # 某些接口返回task_id，需要轮询
            return [f"任务已提交: {response['task_id']}"]
        else:
            return [str(response)]
    
    def generate_video(self, prompt: str, model: str = "T2V-01-Director") -> str:
        """视频生成"""
        data = {"prompt": prompt, "model": model}
        
        response = self._make_request("POST", "video_generation", json=data)
        return response['task_id']
    
    def query_video_status(self, task_id: str) -> Dict[str, Any]:
        """查询视频生成状态"""
        return self._make_request("GET", f"query/video_generation?task_id={task_id}")
    
    def generate_music(self, lyrics: str, refer_voice: str = None, 
                      refer_instrumental: str = None, refer_vocal: str = None) -> str:
        """音乐生成"""
        payload = {
            'lyrics': lyrics,
            'model': 'music-01',
            'audio_setting': '{"sample_rate":44100,"bitrate":256000,"format":"mp3"}'
        }
        
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
        """语音克隆"""
        data = {
            "file_id": int(file_id),
            "voice_id": voice_id,
            "text": text,
            "model": model
        }
        
        return self._make_request("POST", f"voice_clone?GroupId={self.group_id}", json=data)

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
        
        # 模型选择
        models = [
            "abab6.5s-chat (最新版本，支持复杂对话)",
            "abab6.5-chat (标准版本，平衡性能与成本)",
            "abab5.5s-chat (轻量版本，响应速度快)",
            "abab5.5-chat (基础版本，成本优化)"
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
        """图像生成界面"""
        console.print(Panel.fit("[bold blue]🎨 图像生成[/bold blue]"))
        
        prompt = Prompt.ask("请输入图像描述")
        aspect_ratio = Prompt.ask("选择宽高比", default="16:9", 
                                 choices=["1:1", "16:9", "9:16", "4:3"])
        count = int(Prompt.ask("生成数量", default="1"))
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("生成图像中...", total=None)
            urls = self.client.generate_image(prompt, aspect_ratio, count)
            progress.update(task, completed=True)
        
        console.print(f"[green]生成完成！共 {len(urls)} 张图像[/green]")
        for i, url in enumerate(urls, 1):
            console.print(f"图像 {i}: {url}")
    
    def video_interface(self):
        """视频生成界面"""
        console.print(Panel.fit("[bold magenta]🎬 视频生成[/bold magenta]"))
        
        prompt = Prompt.ask("请输入视频描述")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("提交任务...", total=None)
            task_id = self.client.generate_video(prompt)
            progress.update(task, completed=True)
        
        console.print(f"[yellow]任务已提交，ID: {task_id}[/yellow]")
        console.print("正在生成中，请稍候...")
        
        while True:
            time.sleep(10)
            status = self.client.query_video_status(task_id)
            
            if status['status'] == 'Success':
                console.print(f"[green]视频生成完成！[/green]")
                console.print(f"下载链接: {status['file_id']}")
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
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')
    
    args = parser.parse_args()
    
    client = MiniMaxClient()
    
    # 命令行模式
    if args.chat:
        message = ' '.join(args.chat)
        response = client.chat_completion(message)
        print(response)
    elif args.image:
        urls = client.generate_image(args.image)
        for url in urls:
            print(url)
    elif args.video:
        task_id = client.generate_video(args.video)
        print(f"任务ID: {task_id}")
    elif args.music:
        audio_data = client.generate_music(args.music)
        print(f"音乐数据已生成，长度: {len(audio_data)}")
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
            elif "退出" in choice:
                console.print("[yellow]感谢使用！[/yellow]")
                break
    else:
        parser.print_help()

if __name__ == "__main__":
    main()