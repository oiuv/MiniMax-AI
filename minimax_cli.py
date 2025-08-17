#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniMax AI 统一命令行工具
简洁高效，无垃圾代码版本
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import argparse

class MiniMaxClient:
    """精简版MiniMax客户端"""
    
    def __init__(self):
        self.group_id = os.getenv('MINIMAX_GROUP_ID')
        self.api_key = os.getenv('MINIMAX_API_KEY')
        self.base_url = "https://api.minimaxi.com/v1"
        self.verbose = False
        
        if not self.group_id or not self.api_key:
            self._setup_credentials()
    
    def _log(self, message: str, level: str = "INFO"):
        """日志输出"""
        print(f"[{level}] {message}")
    
    def _log_request(self, method: str, endpoint: str, data: dict = None):
        """请求日志"""
        self._log(f"🚀 {method} {endpoint}")
        if self.verbose and data:
            self._log(f"📤 请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    def _setup_credentials(self):
        """配置向导"""
        config_file = Path.home() / '.minimax_ai' / 'config.json'
        config_file.parent.mkdir(exist_ok=True)
        
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                    self.group_id = config.get('group_id')
                    self.api_key = config.get('api_key')
                    if self.group_id and self.api_key:
                        return
            except Exception:
                pass
        
        print("⚠️  需要配置API密钥")
        group_id = input("请输入Group ID: ").strip()
        api_key = input("请输入API Key: ").strip()
        
        if not group_id or not api_key:
            print("❌ Group ID和API Key不能为空")
            sys.exit(1)
        
        with open(config_file, 'w') as f:
            json.dump({'group_id': group_id, 'api_key': api_key}, f, indent=2)
        
        print(f"✅ 配置已保存到 {config_file}")
        print("请重新运行程序")
        sys.exit(0)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """统一请求"""
        url = f"{self.base_url}/{endpoint}"
        if any(k in endpoint for k in ['t2a_v2', 'voice_clone', 'music_generation']):
            url += f"?GroupId={self.group_id}"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        self._log_request(method, endpoint, kwargs.get('json'))
        
        for attempt in range(3):
            try:
                response = requests.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                result = response.json()
                
                self._log(f"📥 响应状态: {response.status_code}")
                
                if 'base_resp' in result and result['base_resp']['status_code'] != 0:
                    self._log(f"⚠️ API错误: {result['base_resp']['status_msg']}", "ERROR")
                    if result['base_resp']['status_code'] == 1002 and attempt < 2:
                        time.sleep(2 * (attempt + 1))
                        continue
                    raise Exception(f"API错误: {result['base_resp']['status_msg']}")
                
                self._log(f"✅ 请求成功")
                return result
                
            except Exception as e:
                if attempt == 2:
                    self._log(f"❌ 请求失败: {e}", "ERROR")
                    sys.exit(1)
                self._log(f"🔄 重试第{attempt+1}次...", "WARN")
                time.sleep(1)
    
    def chat(self, message: str, model: str = "MiniMax-Text-01") -> str:
        """智能对话"""
        self._log("🤖 开始生成对话内容...")
        data = {
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "max_tokens": 1024
        }
        response = self._request("POST", "text/chatcompletion_v2", json=data)
        content = response['choices'][0]['message']['content']
        self._log(f"📄 生成内容长度: {len(content)} 字符")
        return content
    
    def image(self, prompt: str, model: str = "image-01", n: int = 1, aspect_ratio: str = "1:1", seed: int = None) -> list:
        """图像生成"""
        self._log(f"🎨 开始生成图像...")
        data = {
            "model": model,
            "prompt": prompt,
            "response_format": "url",
            "n": n,
            "aspect_ratio": aspect_ratio,
            "prompt_optimizer": True
        }
        if seed is not None:
            data["seed"] = seed
        response = self._request("POST", "image_generation", json=data)
        urls = response.get('data', {}).get('image_urls', [])
        self._log(f"📸 生成图片数量: {len(urls)} 张")
        return urls
    
    def video(self, prompt: str, model: str = "MiniMax-Hailuo-02") -> str:
        """视频生成"""
        self._log(f"🎬 开始生成视频...")
        data = {
            "prompt": prompt,
            "model": model,
            "duration": 6,
            "resolution": "1080P"
        }
        response = self._request("POST", "video_generation", json=data)
        task_id = response.get('task_id', '')
        self._log(f"🎯 视频任务ID: {task_id}")
        return task_id
    
    def video_status(self, task_id: str) -> Dict[str, Any]:
        """查询视频状态"""
        return self._request("GET", f"query/video_generation?task_id={task_id}")
    
    def download_video(self, file_id: str, filename: str = None) -> str:
        """下载视频文件"""
        self._log(f"📥 开始下载视频...")
        if not filename:
            filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        
        # 获取下载URL
        download_response = self._request("GET", f"files/retrieve?file_id={file_id}")
        
        download_url = download_response['file']['download_url']
        
        # 下载文件
        import urllib.request
        filepath = Path('./output/videos') / filename
        filepath.parent.mkdir(exist_ok=True)
        self._log(f"🎯 正在下载: {filename}")
        urllib.request.urlretrieve(download_url, filepath)
        self._log(f"✅ 下载完成: {filepath}")
        return str(filepath)
    
    def music(self, prompt: str, lyrics: str) -> str:
        """音乐生成"""
        self._log("🎵 开始生成音乐...")
        import sys
        
        # 严格校验长度
        prompt = prompt.strip()
        lyrics = lyrics.strip()
        
        if len(prompt) < 10:
            print(f"❌ prompt过短 ({len(prompt)}字符)")
            print(f"💡 建议: 添加更多描述，如风格、情绪、场景")
            print(f"📝 示例: '古风武侠音乐，适合江湖场景，悠扬笛子伴奏'")
            sys.exit(1)
        
        if len(prompt) > 300:
            print(f"❌ prompt过长 ({len(prompt)}字符)")
            print(f"💡 建议: prompt内容请控制在300字符以内")
            print(f"📊 当前长度: {len(prompt)}字符，超出限制: {len(prompt) - 300}字符")
            print(f"📝 提示: 可以精简描述或使用更精确的关键词")
            sys.exit(1)
        
        if not lyrics or not lyrics.strip():
            print(f"❌ 歌词为必填参数")
            print(f"💡 建议: 提供歌词内容或文件路径")
            print(f"📝 示例: '[Verse]\n江湖路远\n[Chorus]\n仗剑天涯'")
            sys.exit(1)
            
        if len(lyrics) < 10:
            print(f"❌ 歌词过短 ({len(lyrics)}字符)")
            print(f"💡 建议: 歌词内容请控制在10-600字符")
            print(f"📝 示例: '[Verse]\n江湖路远\n[Chorus]\n仗剑天涯'")
            sys.exit(1)
        
        if len(lyrics) > 600:
            print(f"❌ 歌词过长 ({len(lyrics)}字符)")
            print(f"💡 建议: 歌词内容请控制在600字符以内")
            print(f"📊 当前长度: {len(lyrics)}字符，超出限制: {len(lyrics) - 600}字符")
            print(f"📝 提示: 可以精简歌词或分段生成")
            sys.exit(1)
        
        data = {
            "model": "music-1.5",
            "prompt": prompt,
            "lyrics": lyrics,
            "audio_setting": {
                "sample_rate": 44100,
                "bitrate": 256000,
                "format": "mp3"
            }
        }
        response = self._request("POST", "music_generation", json=data)
        audio_url = response.get('data', {}).get('audio', '')
        self._log(f"🎶 音乐生成完成")
        return audio_url
    
    def tts(self, text: str, voice_id: str = "female-chengshu", emotion: str = "calm") -> str:
        """文本转语音，支持情感控制"""
        self._log("🎤 开始语音合成...")
        data = {
            "model": "speech-2.5-hd-preview",
            "text": text,
            "voice_setting": {
                "voice_id": voice_id,
                "emotion": emotion,
                "speed": 1.0,
                "vol": 1.0,
                "pitch": 0
            },
            "audio_setting": {
                "sample_rate": 44100,
                "format": "mp3",
                "bitrate": 256000
            }
        }
        response = self._request("POST", "t2a_v2", json=data)
        audio_url = response.get('data', {}).get('audio', '')
        self._log("🗣️ 语音合成完成")
        return audio_url

    def list_voices(self, voice_type: str = "all") -> Dict[str, Any]:
        """查询可用音色列表"""
        self._log("🔍 查询可用音色列表...")
        
        # 检查缓存
        cache_file = Path("./cache/voices.json")
        cache_file.parent.mkdir(exist_ok=True)
        
        # 缓存有效期：2小时
        cache_valid = False
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    if cache_data.get('voice_type') == voice_type:
                        cache_time = datetime.fromisoformat(cache_data.get('timestamp', ''))
                        if (datetime.now() - cache_time).total_seconds() < 7200:  # 2小时
                            self._log("📋 使用缓存数据")
                            return cache_data.get('data', {})
            except Exception:
                pass
        
        # API支持的参数映射
        valid_types = {
            'system': 'system',
            'cloning': 'voice_cloning',
            'generation': 'voice_generation',
            'music': 'music_generation',
            'all': 'all'
        }
        
        # 使用有效的API参数
        api_param = valid_types.get(voice_type, 'all')
        
        # 调用API获取最新数据
        url = "https://api.minimaxi.com/v1/get_voice"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {'voice_type': api_param}
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # 缓存结果
            cache_data = {
                'voice_type': voice_type,
                'timestamp': datetime.now().isoformat(),
                'data': result
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self._log("✅ 音色列表已更新并缓存")
            return result
            
        except Exception as e:
            # 如果API失败，尝试使用缓存（即使过期也显示提示）
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                        self._log("⚠️ 使用过期缓存数据，建议稍后刷新", "WARN")
                        return cache_data.get('data', {})
                except Exception:
                    pass
            
            self._log(f"❌ 获取音色列表失败: {e}", "ERROR")
            return {}
    
    def podcast(self, user_input: str) -> str:
        """智能播客生成 - 完全自然语言输入"""
        self._log("🎙️ 开始生成智能播客...")
        
        # 读取系统提示词模板
        template_path = Path("templates/podcast_system_prompt.txt")
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
        else:
            system_prompt = "你是一个智能播客生成助手，请根据用户描述生成JSON格式对话。"
        
        # 定义JSON schema确保格式正确
        json_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "speaker": {"type": "string", "description": "说话人姓名"},
                    "text": {"type": "string", "description": "说话内容"},
                    "voice_id": {"type": "string", "description": "音色ID"},
                    "emotion": {"type": "string", "enum": ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm"], "description": "情感类型"}
                },
                "required": ["speaker", "text", "voice_id", "emotion"],
                "additionalProperties": False
            },
            "minItems": 2
        }
        
        # 构建消息结构
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # 使用标准格式请求，避免response_format参数
        data = {
            "model": "MiniMax-Text-01",
            "messages": messages,
            "max_tokens": 20480,
            "temperature": 0.8
        }
        
        response = self._request("POST", "text/chatcompletion_v2", json=data)
        content = response['choices'][0]['message']['content']
        
        # 保存原始响应到本地文件
        log_dir = Path('./output/logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存完整的API响应
        response_log = {
            "timestamp": timestamp,
            "user_input": user_input,
            "response": content,
            "dialogue_count": None,
            "status": "success"
        }
        
        try:
            # 清理可能的Markdown格式并解析JSON
            cleaned_content = content.strip()
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()
            
            dialogues = json.loads(cleaned_content)
            response_log["dialogue_count"] = len(dialogues)
            
            # 保存解析后的JSON文件
            json_file = log_dir / f"podcast_dialogue_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(dialogues, f, ensure_ascii=False, indent=2)
            
            # 保存完整响应日志
            log_file = log_dir / f"podcast_response_{timestamp}.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(response_log, f, ensure_ascii=False, indent=2)
            
            self._log(f"📝 对话内容已保存: {json_file}")
            self._log(f"🎭 成功解析对话：{len(dialogues)} 段")
            
            # 为每段生成音频
            audio_segments = []
            for dialogue in dialogues:
                speaker = dialogue.get('speaker', '未知')
                text = dialogue.get('text', '')
                voice_id = dialogue.get('voice_id', 'female-chengshu')
                emotion = dialogue.get('emotion', 'calm')
                
                if text and len(text.strip()) > 5:
                    # 验证并修正情感类型
                    valid_emotions = ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm"]
                    corrected_emotion = emotion.lower()
                    if corrected_emotion not in valid_emotions:
                        # 智能映射到有效情感
                        emotion_mapping = {
                            "excited": "happy",
                            "joyful": "happy",
                            "delighted": "happy",
                            "cheerful": "happy",
                            "upset": "sad",
                            "depressed": "sad",
                            "disappointed": "sad",
                            "mad": "angry",
                            "furious": "angry",
                            "irritated": "angry",
                            "scared": "fearful",
                            "terrified": "fearful",
                            "anxious": "fearful",
                            "shocked": "surprised",
                            "amazed": "surprised",
                            "startled": "surprised",
                            "disgusted": "disgusted",
                            "revolted": "disgusted",
                            "neutral": "calm",
                            "thoughtful": "calm",
                            "curious": "surprised",
                            "concerned": "fearful",
                            "nostalgic": "sad",
                            "proud": "happy",
                            "confident": "happy"
                        }
                        corrected_emotion = emotion_mapping.get(corrected_emotion, "calm")
                        self._log(f"⚠️ 情感映射: {emotion} → {corrected_emotion}")
                    
                    self._log(f"🗣️ {speaker}({voice_id}): {text[:50]}...")
                    audio = self.tts(text.strip(), voice_id, corrected_emotion)
                    audio_segments.append(audio)
            
            if audio_segments:
                # 合并所有音频
                combined_audio = "".join(audio_segments)
                self._log("✅ 播客生成完成")
                return combined_audio
            else:
                self._log("❌ 没有有效音频内容", "ERROR")
                return ""
                
        except json.JSONDecodeError as e:
            response_log["status"] = "error"
            response_log["error"] = str(e)
            
            # 保存错误日志
            log_file = log_dir / f"podcast_error_{timestamp}.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(response_log, f, ensure_ascii=False, indent=2)
                
            self._log(f"❌ JSON解析失败: {e}", "ERROR")
            self._log(f"📝 错误日志已保存: {log_file}")
            if self.verbose:
                self._log(f"📝 原始内容: {content}")
            return ""

class FileManager:
    """文件管理"""
    
    def __init__(self):
        self.base_dir = Path('./output')
        self.base_dir.mkdir(exist_ok=True)
        
        for subdir in ['audio', 'images', 'videos', 'music', 'podcasts']:
            (self.base_dir / subdir).mkdir(exist_ok=True)
    
    def save_file(self, data: str, filename: str, subdir: str) -> str:
        """保存文件"""
        filepath = self.base_dir / subdir / filename
        
        if data.startswith('http'):
            # 下载URL
            import urllib.request
            urllib.request.urlretrieve(data, filepath)
        else:
            # 保存十六进制数据
            with open(filepath, 'wb') as f:
                f.write(bytes.fromhex(data))
        
        return str(filepath)
    
    def play_audio(self, filepath: str):
        """自动播放音频文件"""
        import subprocess
        import platform
        
        try:
            system = platform.system()
            if system == "Windows":
                subprocess.run(["start", filepath], shell=True, check=True)
            elif system == "Darwin":  # macOS
                subprocess.run(["afplay", filepath], check=True)
            elif system == "Linux":
                subprocess.run(["mpg123", filepath], check=True)
            else:
                print(f"📁 音频已保存，请手动播放: {filepath}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"📁 音频已保存，请手动播放: {filepath}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='MiniMax AI 工具')
    
    # 🎯 核心功能（参数支持内容或.txt/.md文件路径）
    generate_group = parser.add_argument_group('核心功能（参数支持内容或.txt/.md文件路径）')
    generate_group.add_argument('-c', '--chat', metavar='对话内容', help='AI智能对话')
    generate_group.add_argument('-i', '--image', metavar='图像描述', help='AI图像生成')
    generate_group.add_argument('-v', '--video', metavar='视频描述', help='AI视频生成')
    generate_group.add_argument('-m', '--music', metavar='音乐描述', help='AI音乐生成')
    generate_group.add_argument('-t', '--tts', metavar='语音文本', help='文本转语音')
    generate_group.add_argument('-p', '--podcast', metavar='播客主题', help='AI播客生成')
    
    # 🎨 图像生成选项
    image_group = parser.add_argument_group('图像生成选项')
    image_group.add_argument('--n', type=int, default=1, choices=range(1, 10), help='生成图片数量 (1-9)，默认1')
    image_group.add_argument('--aspect-ratio', default='1:1', choices=['1:1', '16:9', '4:3', '3:2', '2:3', '3:4', '9:16', '21:9'], help='图像宽高比，默认1:1')
    image_group.add_argument('--seed', type=int, help='随机种子，相同种子生成相似图片')
    
    # 🎭 音色管理
    voice_group = parser.add_argument_group('音色管理')
    voice_group.add_argument('--voice', type=str, default="female-chengshu", 
                            help='指定音色ID (如: male-qn-jingying, female-yujie)')
    voice_group.add_argument('-l', '--list-voices', choices=['system', 'cloning', 'generation', 'music', 'all'], 
                            help='查询可用音色列表')
    voice_group.add_argument('-r', '--refresh-voices', action='store_true', help='强制刷新音色缓存')
    voice_group.add_argument('-f', '--filter-voices', type=str, help='过滤音色列表关键词')
    
    # 🎵 音乐生成
    music_group = parser.add_argument_group('音乐生成')
    music_group.add_argument('--lyrics', help='音乐歌词内容或文件路径(.txt/.md) [必填: 10-600字符]')
    
    # 📺 视频管理
    video_group = parser.add_argument_group('视频管理')
    video_group.add_argument('-s', '--video-status', metavar='任务ID', help='查询视频状态（传入task_id）')
    video_group.add_argument('-d', '--download-video', metavar='文件ID', help='下载视频文件（传入file_id）')
    
    # ⚙️ 通用选项
    common_group = parser.add_argument_group('通用选项')
    common_group.add_argument('-I', '--interactive', action='store_true', help='交互模式')
    common_group.add_argument('-V', '--verbose', action='store_true', help='显示详细日志')
    common_group.add_argument('-P', '--play', action='store_true', help='生成后自动播放音频')
    
    args = parser.parse_args()
    
    client = MiniMaxClient()
    file_mgr = FileManager()
    
    if args.verbose:
        client.verbose = True
    
    if args.interactive:
        print("💬 MiniMax AI 交互模式 (输入 'quit' 退出)")
        while True:
            try:
                cmd = input("\n选择功能 [chat/image/video/music/tts/quit]: ").strip()
                if cmd == 'quit':
                    break
                elif cmd == 'chat':
                    message = input("消息: ")
                    print(client.chat(message))
                elif cmd == 'image':
                    prompt = input("描述: ")
                    urls = client.image(prompt)
                    for url in urls:
                        print(url)
                        save = input("保存文件? (y/n): ")
                        if save.lower() == 'y':
                            filepath = file_mgr.save_file(url, f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg", "images")
                            print(f"✅ 已保存: {filepath}")
                elif cmd == 'video':
                    prompt = input("描述: ")
                    task_id = client.video(prompt)
                    print(f"🎬 任务ID: {task_id}")
                    check = input("查询状态? (y/n): ")
                    if check.lower() == 'y':
                        status = client.video_status(task_id)
                        print(f"状态: {status}")
                elif cmd == 'music':
                    prompt = input("音乐描述: ")
                    lyrics = input("歌词内容: ")
                    if not lyrics.strip():
                        print("❌ 音乐生成需要歌词内容")
                        continue
                    
                    audio = client.music(prompt, lyrics)
                    if audio:
                        filepath = file_mgr.save_file(audio, f"music_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3", "music")
                        print(f"✅ 音乐已保存: {filepath}")
                elif cmd == 'tts':
                    text = input("文本: ")
                    voice = input("音色ID (默认 female-chengshu): ").strip() or "female-chengshu"
                    audio = client.tts(text, voice)
                    if audio:
                        filepath = file_mgr.save_file(audio, f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3", "audio")
                        print(f"✅ 已保存: {filepath}")
                elif cmd == 'podcast':
                    user_input = input("播客描述: ")
                    audio = client.podcast(user_input)
                    if audio:
                        filepath = file_mgr.save_file(audio, f"podcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3", "podcasts")
                        print(f"✅ 播客已保存: {filepath}")
            except KeyboardInterrupt:
                break
    
    elif args.chat:
        content = args.chat
        if content.endswith(('.txt', '.md')) and Path(content).exists():
            with open(content, 'r', encoding='utf-8') as f:
                content = f.read()
        print(client.chat(content))
    elif args.image:
        prompt = args.image
        if prompt.endswith(('.txt', '.md')) and Path(prompt).exists():
            with open(prompt, 'r', encoding='utf-8') as f:
                prompt = f.read()
        urls = client.image(prompt, n=args.n, aspect_ratio=args.aspect_ratio, seed=args.seed)
        if urls:
            for i, url in enumerate(urls):
                filepath = file_mgr.save_file(url, f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}.jpg", "images")
                print(f"✅ 图片已保存: {filepath}")
                print(f"🔗 图片URL: {url}")
                if args.play:
                    import webbrowser
                    webbrowser.open(url)
    elif args.video:
        prompt = args.video
        if prompt.endswith(('.txt', '.md')) and Path(prompt).exists():
            with open(prompt, 'r', encoding='utf-8') as f:
                prompt = f.read()
        task_id = client.video(prompt)
        print(f"🎬 视频生成任务已提交")
        print(f"📊 任务ID: {task_id}")
        print(f"💡 查询状态: python minimax_cli.py -s {task_id}")
        print(f"⏱️  预计2-5分钟完成，可多次查询状态")
    elif args.music:
        # 处理文件路径或文本内容
        prompt = args.music
        if prompt.endswith(('.txt', '.md')) and Path(prompt).exists():
            with open(prompt, 'r', encoding='utf-8') as f:
                prompt = f.read()
        
        # 歌词为必填
        if not args.lyrics:
            print("❌ 音乐生成需要歌词参数")
            print("💡 使用: --lyrics '歌词内容' 或 --lyrics lyrics.txt")
            print("📝 提示: 使用换行符分隔，支持[Intro][Verse][Chorus][Bridge][Outro]结构")
            sys.exit(1)
        
        lyrics = args.lyrics
        if lyrics.endswith(('.txt', '.md')) and Path(lyrics).exists():
            with open(lyrics, 'r', encoding='utf-8') as f:
                lyrics = f.read()
        
        audio = client.music(prompt, lyrics)
        if audio:
            filepath = file_mgr.save_file(audio, f"music_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3", "music")
            print(filepath)
            if args.play:
                file_mgr.play_audio(filepath)
    elif args.tts:
        text = args.tts
        if text.endswith(('.txt', '.md')) and Path(text).exists():
            with open(text, 'r', encoding='utf-8') as f:
                text = f.read()
        audio = client.tts(text, args.voice)
        if audio:
            filepath = file_mgr.save_file(audio, f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3", "audio")
            print(filepath)
            if args.play:
                file_mgr.play_audio(filepath)
    elif args.podcast:
        user_input = args.podcast
        if user_input.endswith(('.txt', '.md')) and Path(user_input).exists():
            with open(user_input, 'r', encoding='utf-8') as f:
                user_input = f.read()
        audio = client.podcast(user_input)
        if audio:
            filepath = file_mgr.save_file(audio, f"podcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3", "podcasts")
            print(filepath)
            if args.play:
                file_mgr.play_audio(filepath)
    elif args.video_status:
        status = client.video_status(args.video_status)
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
        # 如果成功，提供下载链接
        if status.get('status') == 'Success':
            file_id = status.get('file_id')
            print(f"🎬 视频已生成，文件ID: {file_id}")
            print(f"📥 下载命令: python minimax_cli.py --download-video {file_id}")
    elif args.download_video:
        filepath = client.download_video(args.download_video)
        print(f"✅ 视频已下载: {filepath}")
    elif args.list_voices or args.refresh_voices:
        voice_type = args.list_voices or "all"
        
        if args.refresh_voices:
            # 强制刷新缓存
            cache_file = Path("./cache/voices.json")
            if cache_file.exists():
                cache_file.unlink()
                print("🔄 已清除音色缓存")
        
        voices_data = client.list_voices(voice_type)
        if not voices_data:
            print("❌ 无法获取音色列表")
            return
            
        filter_keyword = args.filter_voices
        
        # 格式化输出
        def format_voices(voice_list, title):
            if not voice_list:
                return
            
            print(f"\n🎭 {title}")
            for voice in voice_list:
                voice_id = voice.get('voice_id', '')
                name = voice.get('voice_name', voice_id)
                desc = " ".join(voice.get('description', [])) if isinstance(voice.get('description'), list) else str(voice.get('description', ''))
                
                # 过滤关键词
                if filter_keyword and filter_keyword.lower() not in f"{voice_id} {name} {desc}".lower():
                    continue
                    
                print(f"├─ {voice_id:<20} {name:<15} [{desc}]")
        
        # 系统音色
        format_voices(voices_data.get('system_voice', []), "系统音色")
        format_voices(voices_data.get('voice_cloning', []), "克隆音色")
        format_voices(voices_data.get('voice_generation', []), "生成音色")
        format_voices(voices_data.get('music_generation', []), "音乐音色")
        
        total_count = sum(len(voices_data.get(k) or []) for k in ['system_voice', 'voice_cloning', 'voice_generation', 'music_generation'])
        print(f"\n📊 总计: {total_count} 个音色")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()