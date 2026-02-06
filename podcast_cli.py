#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniMax AI 播客生成器
独立播客生成工具，支持多角色对话、语音合成、音频编辑
"""

import os
import sys
import json
import time
import base64
import glob
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# 导入 MiniMaxClient
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from minimax_cli import MiniMaxClient


class PodcastGenerator:
    """播客生成器"""

    def __init__(self):
        self.client = MiniMaxClient()
        self.base_dir = Path('./output/podcasts')
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir = Path('templates')

    def _log(self, message: str, level: str = "INFO"):
        """日志输出"""
        print(f"[{level}] {message}")

    def run_ffmpeg(self, args, check=True) -> bool:
        """运行ffmpeg命令"""
        result = subprocess.run(['ffmpeg', '-y'] + args, capture_output=True, text=True)
        if result.returncode != 0 and check:
            self._log(f"FFmpeg错误: {result.stderr[:200]}", "WARN")
        return result.returncode == 0

    def hex_to_mp3(self, hex_data: str, output_path: str):
        """hex转MP3"""
        audio_bytes = bytes.fromhex(hex_data)
        with open(output_path, 'wb') as f:
            f.write(audio_bytes)

    def normalize_audio(self, input_path: str, output_path: str) -> bool:
        """转MP3（不调整音量）"""
        if not Path(input_path).exists():
            self._log(f"文件不存在: {input_path}", "ERROR")
            return False
        return self.run_ffmpeg(['-i', input_path, '-c:a', 'libmp3lame', '-f', 'mp3', output_path], check=False)

    def concat_audio(self, files: list, output_path: str) -> bool:
        """拼接音频，统一转MP3"""
        if not files:
            return False
        list_content = ''
        for f in files:
            list_content += f"file '{Path(f).absolute().as_posix()}'\n"
        list_file = self.base_dir / 'concat_list.txt'
        with open(list_file, 'w', encoding='utf-8') as f:
            f.write(list_content)
        return self.run_ffmpeg(
            ['-f', 'concat', '-safe', '0', '-i', str(list_file),
             '-c:a', 'libmp3lame', '-q:a', '2', output_path],
            check=False
        )

    def generate_dialogue(self, user_input: str, welcome_text: str = "欢迎收听本期节目！") -> str:
        """生成播客音频"""
        self._log("🎙️ 开始生成播客...")

        # 音色配置
        MINI_VOICE = "moss_audio_aaa1346a-7ce7-11f0-8e61-2e6e3c7ee85d"
        MAX_VOICE = "moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85"

        self._log(f"📝 欢迎语: {welcome_text}")

        # 读取系统提示词
        template_path = self.templates_dir / "podcast_system_prompt.txt"
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
        else:
            system_prompt = "你是一个智能播客生成助手，请根据用户描述生成JSON格式对话。"

        # 构建请求
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        data = {
            "model": "MiniMax-M2.1",
            "messages": messages,
            "max_tokens": 20480,
            "temperature": 0.8
        }

        response = self.client._request("POST", "text/chatcompletion_v2", json=data)
        content = response['choices'][0]['message']['content']

        # 保存日志
        log_dir = Path('./output/logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        response_log = {
            "timestamp": timestamp,
            "user_input": user_input,
            "response": content,
            "dialogue_count": None,
            "status": "success"
        }

        try:
            # 清理JSON
            cleaned_content = content.strip()

            # 处理Markdown格式
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]
            elif cleaned_content.startswith('```'):
                cleaned_content = cleaned_content[3:]
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()

            # 处理转义JSON
            try:
                inner = json.loads(cleaned_content)
                cleaned_content = inner
            except json.JSONDecodeError:
                pass

            dialogues = json.loads(cleaned_content) if isinstance(cleaned_content, str) else cleaned_content
            response_log["dialogue_count"] = len(dialogues)

            # 保存对话JSON
            json_file = log_dir / f"podcast_dialogue_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(dialogues, f, ensure_ascii=False, indent=2)

            self._log(f"📝 对话已保存: {json_file}")
            self._log(f"🎭 解析对话: {len(dialogues)} 段")

            # 音频处理
            dialogue_audios = []
            valid_emotions = ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm"]
            emotion_mapping = {
                "excited": "happy", "joyful": "happy", "delighted": "happy", "cheerful": "happy",
                "upset": "sad", "depressed": "sad", "disappointed": "sad",
                "mad": "angry", "furious": "angry", "irritated": "angry",
                "scared": "fearful", "terrified": "fearful", "anxious": "fearful",
                "shocked": "surprised", "amazed": "surprised", "startled": "surprised",
                "neutral": "calm", "thoughtful": "calm", "curious": "surprised"
            }

            for dialogue in dialogues:
                speaker = dialogue.get('speaker', '未知')
                text = dialogue.get('text', '')
                voice_id = dialogue.get('voice_id', MINI_VOICE)
                emotion = dialogue.get('emotion', 'calm')

                if text and len(text.strip()) > 5:
                    corrected_emotion = emotion.lower()
                    if corrected_emotion not in valid_emotions:
                        corrected_emotion = emotion_mapping.get(corrected_emotion, "calm")

                    self._log(f"🗣️ {speaker}: {text[:40]}...")
                    audio_hex = self.client.tts(text.strip(), voice_id, corrected_emotion)
                    if audio_hex:
                        dialogue_audios.append(audio_hex)

            if not dialogue_audios:
                self._log("没有有效音频内容", "ERROR")
                return ""

            # 生成欢迎语
            self._log("🎵 合成欢迎语...")
            welcome_hex = self.client.tts(welcome_text, MINI_VOICE, "happy")
            if not welcome_hex:
                self._log("欢迎语生成失败", "ERROR")
                return ""
            welcome_path = self.base_dir / 'welcome.mp3'
            self.hex_to_mp3(welcome_hex, str(welcome_path))

            # 保存对话音频
            dialogue_files = []
            for i, audio_hex in enumerate(dialogue_audios):
                dia_path = self.base_dir / f'dia_{i}.mp3'
                self.hex_to_mp3(audio_hex, str(dia_path))
                dialogue_files.append(str(dia_path))

            # 合并对话
            dialogue_concat = self.base_dir / 'dialogue.mp3'
            if len(dialogue_files) == 1:
                dialogue_files[0].rename(dialogue_concat)
            else:
                if not self.concat_audio(dialogue_files, str(dialogue_concat)):
                    self._log("对话合并失败", "ERROR")
                    return ""

            # BGM处理
            bgm01_path = self.templates_dir / 'bgm01.wav'
            bgm02_path = self.templates_dir / 'bgm02.wav'
            all_parts = []

            bgm01_part = self.base_dir / 'bgm01_part.mp3'
            if self.normalize_audio(str(bgm01_path), str(bgm01_part)):
                all_parts.append(str(bgm01_part))

            welcome_norm = self.base_dir / 'welcome_norm.mp3'
            if self.normalize_audio(str(welcome_path), str(welcome_norm)):
                all_parts.append(str(welcome_norm))

            bgm02_norm = self.base_dir / 'bgm02_norm.mp3'
            bgm02_part = self.base_dir / 'bgm02_fade.mp3'
            if self.normalize_audio(str(bgm02_path), str(bgm02_norm)):
                self.run_ffmpeg(['-i', str(bgm02_norm), '-af', 'afade=t=out:st=0:d=1',
                                '-c:a', 'libmp3lame', str(bgm02_part)])
                all_parts.append(str(bgm02_part))

            dialogue_norm = self.base_dir / 'dialogue_norm.mp3'
            if dialogue_concat.exists() and self.normalize_audio(str(dialogue_concat), str(dialogue_norm)):
                all_parts.append(str(dialogue_norm))

            if Path(bgm01_part).exists():
                all_parts.append(str(bgm01_part))
            if Path(bgm02_part).exists():
                all_parts.append(str(bgm02_part))

            if not all_parts:
                self._log("没有有效音频片段", "ERROR")
                return ""

            # 最终拼接
            output_path = self.base_dir / f'podcast_{timestamp}.mp3'
            if not self.concat_audio(all_parts, str(output_path)):
                self._log("最终拼接失败", "ERROR")
                return ""

            if not output_path.exists():
                self._log("播客拼接失败", "ERROR")
                return ""

            # 获取时长
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', str(output_path)],
                capture_output=True, text=True
            )
            total_duration = float(result.stdout.strip()) if result.stdout.strip() else 0

            self._log(f"✅ 播客生成完成: {output_path}")
            self._log(f"📊 总时长: {total_duration:.1f}秒")

            # 清理临时文件
            self._log("🧹 清理临时文件...")
            temp_patterns = [
                self.base_dir / 'dia_*.mp3',
                self.base_dir / 'welcome*.mp3',
                self.base_dir / 'bgm01_part.mp3',
                self.base_dir / 'bgm02_norm.mp3',
                self.base_dir / 'bgm02_fade.mp3',
                self.base_dir / 'dialogue*.mp3',
                self.base_dir / 'concat_list.txt',
            ]
            for pattern in temp_patterns:
                for f in glob.glob(str(pattern)):
                    try:
                        Path(f).unlink()
                    except:
                        pass

            return str(output_path)

        except json.JSONDecodeError as e:
            response_log["status"] = "error"
            response_log["error"] = str(e)
            log_file = log_dir / f"podcast_error_{timestamp}.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(response_log, f, ensure_ascii=False, indent=2)
            self._log(f"JSON解析失败: {e}", "ERROR")
            return ""

        except Exception as e:
            self._log(f"播客生成错误: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return ""


def main():
    parser = argparse.ArgumentParser(
        description='MiniMax AI 播客生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python podcast_cli.py "生成一期关于AI的播客"
  python podcast_cli.py topic.txt --welcome-text "听众朋友们好！"
  python podcast_cli.py topic.txt -o ./my_podcasts
        """
    )

    # 核心参数
    parser.add_argument('topic', help='播客主题描述或.txt/.md文件路径')
    parser.add_argument('-o', '--output', type=str, help='输出目录，默认 ./output/podcasts')

    # 播客选项
    parser.add_argument('--welcome-text', type=str,
                        default="欢迎收听本期节目！",
                        help='自定义欢迎语')
    parser.add_argument('--bgm-dir', type=str, default="templates",
                        help='BGM文件目录')
    parser.add_argument('--verbose', action='store_true', help='显示详细日志')

    args = parser.parse_args()

    # 设置输出目录
    if args.output:
        generator = PodcastGenerator()
        generator.base_dir = Path(args.output)
        generator.base_dir.mkdir(parents=True, exist_ok=True)
    else:
        generator = PodcastGenerator()

    # 读取主题
    topic = args.topic
    if args.topic.endswith(('.txt', '.md')) and Path(args.topic).exists():
        with open(args.topic, 'r', encoding='utf-8') as f:
            topic = f.read()
        print(f"📄 从文件读取主题: {args.topic}")

    if not topic.strip():
        print("❌ 播客主题不能为空")
        sys.exit(1)

    # 生成播客
    output_path = generator.generate_dialogue(topic, welcome_text=args.welcome_text)

    if output_path:
        print(f"\n🎉 播客生成成功！")
        print(f"📁 输出文件: {output_path}")

        # 询问是否播放
        try:
            play = input("\n🎵 是否播放播客? (y/n): ").strip().lower()
            if play == 'y':
                import platform
                system = platform.system()
                if system == "Windows":
                    subprocess.run(["start", output_path], shell=True)
                elif system == "Darwin":
                    subprocess.run(["afplay", output_path])
                elif system == "Linux":
                    subprocess.run(["mpg123", output_path])
        except KeyboardInterrupt:
            pass
    else:
        print("❌ 播客生成失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
