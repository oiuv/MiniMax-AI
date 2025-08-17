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
    
    def podcast(self, topic: str, scene: str = "dialogue", voices: list = None, voice: str = None) -> str:
        """多人对话播客生成"""
        self._log("🎙️ 开始生成多人对话播客...")
        
        # 定义角色和音色
        if voice:
            # 使用指定的音色
            host_voice = voice
            guest1_voice = voice
            guest2_voice = voice
        else:
            # 使用默认音色组合
            host_voice = "female-yujie"
            guest1_voice = "male-qn-jingying"
            guest2_voice = "female-chengshu"
        
        # 生成多人对话内容
        prompt = f"""请为播客节目生成关于'{topic}'的**多人对话**，格式如下：

        **主持人小雅**：大家好，欢迎收听本期播客...

        **嘉宾小明**：谢谢小雅，我认为...

        **嘉宾小红**：我补充一点...

        **主持人小雅**：感谢两位的分享...

        要求：
        1. 至少6-8轮完整对话
        2. 每段发言50-80字
        3. 包含开场、深入讨论、总结
        4. 用**角色名**：开头标识说话人
        5. 总长度1000-1500字
        """
        
        content = self.chat(prompt)
        self._log(f"📄 生成对话内容: {len(content)} 字符")
        
        # 打印原始内容用于调试
        if self.verbose:
            self._log(f"📝 原始内容: {content[:200]}...")
        
        # 解析对话段落 - 增强匹配规则
        paragraphs = [p.strip() for p in content.split('\n') if p.strip() and '：**' in p]
        self._log(f"🎭 解析对话段落: {len(paragraphs)} 段")
        
        if len(paragraphs) == 0:
            self._log("⚠️  未找到标准格式对话，尝试备用解析...")
            # 备用解析：寻找包含冒号的行
            paragraphs = [p.strip() for p in content.split('\n') if p.strip() and (':' in p or '：' in p)]
            self._log(f"🔄 备用解析结果: {len(paragraphs)} 段")
        
        # 为每段分配音色和生成音频
        voice_mapping = {
            "主持人小雅": host_voice,
            "嘉宾小明": guest1_voice,
            "嘉宾小红": guest2_voice
        }
        
        audio_segments = []
        valid_paragraphs = 0
        
        for para in paragraphs:
            for role, voice in voice_mapping.items():
                role_markers = [f"**{role}**", f"{role}:", f"{role}："]
                for marker in role_markers:
                    if para.startswith(marker):
                        text = para.replace(marker, "").strip()
                        if text and len(text) > 10:
                            self._log(f"🗣️ {role}({voice}): {text[:50]}...")
                            
                            # 为每个角色使用不同音色生成音频
                            audio = self.tts(text, voice)
                            audio_segments.append(audio)
                            valid_paragraphs += 1
                            break
        
        if audio_segments:
            # 合并所有音频段落
            self._log(f"🎵 合并{len(audio_segments)}段音频...")
            # 简单合并：按顺序连接
            combined_audio = "".join(audio_segments)
            return combined_audio
        else:
            self._log(f"❌ 播客生成失败: 有效段落不足({valid_paragraphs}段)", "ERROR")
            if not self.verbose:
                self._log("💡 使用 -V 查看详细内容分析")
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
                    topic = input("播客主题: ")
                    voice = input("音色ID (可选，默认多人对话): ").strip()
                    if voice:
                        audio = client.podcast(topic, voice=voice)
                    else:
                        audio = client.podcast(topic)
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
        topic = args.podcast
        if topic.endswith(('.txt', '.md')) and Path(topic).exists():
            with open(topic, 'r', encoding='utf-8') as f:
                topic = f.read()
        audio = client.podcast(topic, args.voice)
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