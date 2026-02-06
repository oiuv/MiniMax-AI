#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniMax AI 播客生成器
独立播客生成工具，支持多角色对话、语音合成、音频编辑

功能模块:
- DialogueGenerator: 对话生成器
- AudioSynthesizer: 音频合成器
- PodcastEditor: 播客编辑器
"""

import os
import sys
import json
import glob
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any


class DialogueGenerator:
    """对话生成器 - 根据主题生成对话或直接读取JSON"""

    def __init__(self, client, templates_dir: str = "templates"):
        self.client = client
        self.templates_dir = Path(templates_dir)

    def generate(self, topic: str, output_path: str = None) -> List[Dict]:
        """根据主题生成对话

        Args:
            topic: 播客主题描述
            output_path: 可选的JSON保存路径

        Returns:
            对话列表，每项包含 speaker, text, voice_id, emotion
        """
        # 读取系统提示词
        template_path = self.templates_dir / "podcast_system_prompt.txt"
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
        else:
            system_prompt = "你是一个智能播客生成助手，请根据用户描述生成JSON格式对话。"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": topic}
        ]

        data = {
            "model": "MiniMax-M2.1",
            "messages": messages,
            "max_tokens": 20480,
            "temperature": 0.8
        }

        response = self.client._request("POST", "text/chatcompletion_v2", json=data)
        content = response['choices'][0]['message']['content']

        # 解析JSON
        dialogues = self._parse_json(content)

        # 保存JSON
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(dialogues, f, ensure_ascii=False, indent=2)

        return dialogues

    def load(self, json_path: str) -> List[Dict]:
        """直接读取对话JSON文件"""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _parse_json(self, content: str) -> List[Dict]:
        """解析JSON内容"""
        cleaned = content.strip()

        # 处理Markdown格式
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # 处理转义JSON
        try:
            inner = json.loads(cleaned)
            cleaned = inner
        except json.JSONDecodeError:
            pass

        return json.loads(cleaned) if isinstance(cleaned, str) else cleaned


class AudioSynthesizer:
    """音频合成器 - 将对话转为音频片段"""

    def __init__(self, client, output_dir: str = "./output/podcasts"):
        self.client = client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, dialogues: List[Dict], welcome_text: str = "欢迎收听本期节目！",
                   welcome_voice: str = None) -> Dict[str, str]:
        """合成对话音频

        Args:
            dialogues: 对话列表（每项包含 speaker, text, voice_id, emotion）
            welcome_text: 欢迎语文本
            welcome_voice: 欢迎语音色ID

        Returns:
            dict: 包含 welcome_path 和 dialogue_files
        """
        # 默认欢迎语音色
        DEFAULT_VOICE = "moss_audio_aaa1346a-7ce7-11f0-8e61-2e6e3c7ee85d"
        welcome_voice = welcome_voice or DEFAULT_VOICE

        def hex_to_mp3(hex_data: str, path: str):
            audio_bytes = bytes.fromhex(hex_data)
            with open(path, 'wb') as f:
                f.write(audio_bytes)

        # 生成欢迎语
        print("🎵 合成欢迎语...")
        welcome_hex = self.client.tts(welcome_text, welcome_voice, "happy")
        if not welcome_hex:
            raise RuntimeError("欢迎语生成失败")
        welcome_path = self.output_dir / 'welcome.mp3'
        hex_to_mp3(welcome_hex, str(welcome_path))

        # 生成对话音频
        print(f"🎙️ 合成 {len(dialogues)} 段对话...")
        dialogue_files = []
        valid_emotions = ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm"]

        for i, dialogue in enumerate(dialogues):
            speaker = dialogue.get('speaker', '未知')
            text = dialogue.get('text', '')
            # 每段对话用自己的 voice_id 和 emotion
            v_id = dialogue.get('voice_id') or welcome_voice
            emo = dialogue.get('emotion', 'calm')  # 如果没有emotion字段，默认用calm

            if not text or len(text.strip()) <= 5:
                continue

            # 情感映射
            emo = emo.lower()
            mapping = {
                "excited": "happy", "joyful": "happy", "delighted": "happy", "cheerful": "happy",
                "upset": "sad", "depressed": "sad", "disappointed": "sad",
                "mad": "angry", "furious": "angry", "irritated": "angry",
                "scared": "fearful", "terrified": "fearful", "anxious": "fearful",
                "shocked": "surprised", "amazed": "surprised", "startled": "surprised",
                "neutral": "calm", "thoughtful": "calm", "curious": "surprised"
            }
            emo = mapping.get(emo, emo) if emo not in valid_emotions else emo

            print(f"  🗣️ {speaker}: {text[:30]}...")
            audio_hex = self.client.tts(text.strip(), v_id, emo)
            if audio_hex:
                dia_path = self.output_dir / f'dia_{i}.mp3'
                hex_to_mp3(audio_hex, str(dia_path))
                dialogue_files.append(str(dia_path))

        if not dialogue_files:
            raise RuntimeError("没有有效对话音频")

        return {
            'welcome_path': str(welcome_path),
            'dialogue_files': dialogue_files
        }

    def merge_dialogues(self, dialogue_files: List[str], output_path: str = None) -> str:
        """合并对话音频"""
        if not output_path:
            output_path = str(self.output_dir / 'dialogue.mp3')

        if len(dialogue_files) == 1:
            Path(dialogue_files[0]).rename(output_path)
        else:
            self._concat_audio(dialogue_files, output_path)

        return output_path

    def _concat_audio(self, files: list, output_path: str):
        """拼接音频"""
        list_content = ''
        for f in files:
            list_content += f"file '{Path(f).absolute().as_posix()}'\n"
        list_file = self.output_dir / 'concat_list.txt'
        with open(list_file, 'w', encoding='utf-8') as f:
            f.write(list_content)

        subprocess.run(
            ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(list_file),
             '-c:a', 'libmp3lame', '-q:a', '2', output_path],
            capture_output=True
        )


class PodcastEditor:
    """播客编辑器 - 拼接音频+背景音乐"""

    def __init__(self, output_dir: str = "./output/podcasts", templates_dir: str = "templates"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir = Path(templates_dir)

    def edit(self, welcome_path: str, dialogue_path: str,
             bgm01_path: str = None, bgm02_path: str = None,
             output_path: str = None) -> str:
        """编辑播客

        Args:
            welcome_path: 欢迎语音频
            dialogue_path: 对话音频
            bgm01_path: 背景音乐1
            bgm02_path: 背景音乐2（带淡出）
            output_path: 输出路径

        Returns:
            生成的播客文件路径
        """
        bgm01_path = bgm01_path or str(self.templates_dir / 'bgm01.wav')
        bgm02_path = bgm02_path or str(self.templates_dir / 'bgm02.wav')

        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = str(self.output_dir / f'podcast_{timestamp}.mp3')

        def run_ffmpeg(args):
            subprocess.run(['ffmpeg', '-y'] + args, capture_output=True)

        def normalize_audio(input_path: str, output_path: str):
            run_ffmpeg(['-i', input_path, '-c:a', 'libmp3lame', '-f', 'mp3', output_path])

        # 构建音频片段列表
        all_parts = []

        # BGM1
        bgm1_part = str(self.output_dir / 'bgm01_part.mp3')
        if normalize_audio(bgm01_path, bgm1_part):
            all_parts.append(bgm1_part)

        # 欢迎语
        welcome_norm = str(self.output_dir / 'welcome_norm.mp3')
        if normalize_audio(welcome_path, welcome_norm):
            all_parts.append(welcome_norm)

        # BGM2（淡出）
        bgm2_norm = str(self.output_dir / 'bgm02_norm.mp3')
        bgm2_part = str(self.output_dir / 'bgm02_fade.mp3')
        if normalize_audio(bgm02_path, bgm2_norm):
            run_ffmpeg(['-i', bgm2_norm, '-af', 'afade=t=out:st=0:d=1',
                       '-c:a', 'libmp3lame', bgm2_part])
            all_parts.append(bgm2_part)

        # 对话
        dialogue_norm = str(self.output_dir / 'dialogue_norm.mp3')
        if Path(dialogue_path).exists() and normalize_audio(dialogue_path, dialogue_norm):
            all_parts.append(dialogue_norm)

        # 结尾BGM
        if Path(bgm1_part).exists():
            all_parts.append(bgm1_part)
        if Path(bgm2_part).exists():
            all_parts.append(bgm2_part)

        if not all_parts:
            raise RuntimeError("没有有效音频片段")

        # 拼接
        list_content = ''
        for f in all_parts:
            list_content += f"file '{Path(f).absolute().as_posix()}'\n"
        list_file = self.output_dir / 'concat_list.txt'
        with open(list_file, 'w', encoding='utf-8') as f:
            f.write(list_content)

        subprocess.run(
            ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(list_file),
             '-c:a', 'libmp3lame', '-q:a', '2', output_path],
            capture_output=True
        )

        return output_path

    def cleanup(self):
        """清理临时文件"""
        patterns = [
            self.output_dir / 'dia_*.mp3',
            self.output_dir / 'welcome*.mp3',
            self.output_dir / 'bgm01_part.mp3',
            self.output_dir / 'bgm02_norm.mp3',
            self.output_dir / 'bgm02_fade.mp3',
            self.output_dir / 'dialogue*.mp3',
            self.output_dir / 'concat_list.txt',
        ]
        for pattern in patterns:
            for f in glob.glob(str(pattern)):
                try:
                    Path(f).unlink()
                except:
                    pass


class PodcastGenerator:
    """播客生成器 - 整合所有模块"""

    def __init__(self, output_dir: str = "./output/podcasts", templates_dir: str = "templates"):
        self.output_dir = Path(output_dir)
        self.templates_dir = Path(templates_dir)

        # 初始化MiniMaxClient
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from minimax_cli import MiniMaxClient
        self.client = MiniMaxClient()

        # 初始化模块
        self.dialogue_gen = DialogueGenerator(self.client, templates_dir)
        self.audio_synth = AudioSynthesizer(self.client, output_dir)
        self.editor = PodcastEditor(output_dir, templates_dir)

    def generate(self, topic: str, welcome_text: str = "欢迎收听本期节目！",
                 output_path: str = None, json_output: str = None) -> str:
        """完整播客生成流程（自动生成对话）

        Args:
            topic: 播客主题
            welcome_text: 欢迎语
            output_path: 最终播客输出路径
            json_output: 对话JSON保存路径

        Returns:
            播客文件路径
        """
        print("🎙️ 开始生成播客...")

        # 1. 生成对话
        print("📝 生成对话内容...")
        dialogues = self.dialogue_gen.generate(topic, json_output)
        print(f"  ✅ 生成 {len(dialogues)} 段对话")

        # 2. 合成音频
        print("🎵 合成音频...")
        audio_result = self.audio_synth.synthesize(dialogues, welcome_text)

        # 合并对话
        dialogue_path = self.audio_synth.merge_dialogues(audio_result['dialogue_files'])

        # 3. 编辑播客
        print("🎼 编辑播客...")
        podcast_path = self.editor.edit(audio_result['welcome_path'], dialogue_path)
        if output_path and output_path != podcast_path:
            Path(podcast_path).rename(output_path)
            podcast_path = output_path

        # 清理
        self.editor.cleanup()

        # 时长
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', podcast_path],
            capture_output=True, text=True
        )
        duration = float(result.stdout.strip()) if result.stdout.strip() else 0

        print(f"✅ 播客生成完成: {podcast_path}")
        print(f"📊 总时长: {duration:.1f}秒")

        return podcast_path

    def from_json(self, json_path: str, welcome_text: str = "欢迎收听本期节目！",
                  output_path: str = None) -> str:
        """从JSON文件生成播客

        Args:
            json_path: 对话JSON文件路径
            welcome_text: 欢迎语
            output_path: 输出路径

        Returns:
            播客文件路径
        """
        print("📄 从JSON文件生成播客...")

        # 读取对话（JSON中已包含每段的voice_id）
        dialogues = self.dialogue_gen.load(json_path)
        print(f"  ✅ 读取 {len(dialogues)} 段对话")

        # 合成音频（每段对话用自己的voice_id）
        audio_result = self.audio_synth.synthesize(dialogues, welcome_text)

        # 合并对话
        dialogue_path = self.audio_synth.merge_dialogues(audio_result['dialogue_files'])

        # 3. 编辑播客
        podcast_path = self.editor.edit(audio_result['welcome_path'], dialogue_path)
        if output_path:
            Path(podcast_path).rename(output_path)
            podcast_path = output_path

        # 清理
        self.editor.cleanup()

        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', podcast_path],
            capture_output=True, text=True
        )
        duration = float(result.stdout.strip()) if result.stdout.strip() else 0

        print(f"✅ 播客生成完成: {podcast_path}")
        print(f"📊 总时长: {duration:.1f}秒")

        return podcast_path


def main():
    parser = argparse.ArgumentParser(
        description='MiniMax AI 播客生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用方式:
  # 1. 直接输入主题（AI自动选择音色）
  python podcast_cli.py "人工智能如何改变未来"

  # 2. 从文件读取主题/要求
  python podcast_cli.py examples/podcast_auto_voices.txt

  # 3. 生成对话JSON（仅生成对话，不生成音频）
  python podcast_cli.py "AI话题" --generate-only

  # 4. 从JSON生成播客（直接提供对话）
  python podcast_cli.py output/logs/podcast_dialogue.json

  # 5. 自定义音色播客（指定角色和音色）
  python podcast_cli.py examples/podcast_custom_voices.txt

  # 6. 自定义选项
  python podcast_cli.py topic.txt --welcome-text "大家好！" -o ./podcast.mp3
        """
    )

    # 核心参数
    parser.add_argument('input', help='播客主题描述，或 .txt/.md/.json 文件路径')

    # 生成选项
    parser.add_argument('--generate-only', action='store_true',
                        help='仅生成对话JSON，不生成播客音频')
    parser.add_argument('--json-output', type=str,
                        help='对话JSON保存路径（仅--generate-only时生效）')
    parser.add_argument('--welcome-text', type=str, default="欢迎收听本期节目！",
                        help='自定义欢迎语')

    # 输出选项
    parser.add_argument('-o', '--output', type=str, help='播客输出文件路径')
    parser.add_argument('--templates', type=str, default="templates",
                        help='模板目录')

    args = parser.parse_args()

    generator = PodcastGenerator(templates_dir=args.templates)
    if args.output:
        generator.output_dir = Path(args.output).parent
        generator.editor.output_dir = generator.output_dir
        generator.audio_synth.output_dir = generator.output_dir

    # 判断输入类型：JSON文件 / txt/md文件 / 主题文本
    input_path = Path(args.input)
    if args.input.endswith('.json') and input_path.exists():
        # 模式2：从JSON生成（JSON中已有voice_id）
        output = generator.from_json(
            args.input,
            welcome_text=args.welcome_text,
            output_path=args.output
        )
    elif input_path.suffix in ['.txt', '.md'] and input_path.exists():
        # 从 txt/md 文件读取主题
        with open(input_path, 'r', encoding='utf-8') as f:
            topic = f.read()
        print(f"📄 从文件读取主题: {input_path}")
        if args.generate_only:
            dialogues = generator.dialogue_gen.generate(
                topic,
                args.json_output or "./output/logs/podcast_dialogue.json"
            )
            print(f"✅ 已生成 {len(dialogues)} 段对话")
            output = None
        else:
            output = generator.generate(
                topic,
                welcome_text=args.welcome_text,
                output_path=args.output
            )
    elif args.generate_only:
        # 模式3：仅生成对话
        dialogues = generator.dialogue_gen.generate(
            args.input,
            args.json_output or "./output/logs/podcast_dialogue.json"
        )
        print(f"✅ 已生成 {len(dialogues)} 段对话")
        output = None
    else:
        # 模式1：完整生成（主题 -> 对话 -> 音频 -> 播客）
        output = generator.generate(
            args.input,
            welcome_text=args.welcome_text,
            output_path=args.output
        )

    # 播放询问
    if output:
        try:
            play = input("\n🎵 是否播放播客? (y/n): ").strip().lower()
            if play == 'y':
                import platform
                system = platform.system()
                if system == "Windows":
                    subprocess.run(["start", output], shell=True)
                elif system == "Darwin":
                    subprocess.run(["afplay", output])
                elif system == "Linux":
                    subprocess.run(["mpg123", output])
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
