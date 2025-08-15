#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniMax AI 电台播客生成系统
基于真实MiniMax音色ID实现多场景播客自动生成
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class PodcastGenerator:
    """播客生成器 - 集成真实MiniMax音色系统"""
    
    # 真实音色映射表（基于voice_list_1768538055993475850.json）
    VOICE_CATEGORIES = {
        "中文女声": {
            "female-shaonv": "少女音",
            "female-yujie": "御姐音", 
            "female-chengshu": "成熟女声",
            "female-tianmei": "甜美女声",
            "presenter_female": "女主播",
            "audiobook_female_1": "有声书女声1",
            "audiobook_female_2": "有声书女声2",
            "female-shaonv-jingpin": "少女音精品",
            "female-yujie-jingpin": "御姐音精品",
            "female-chengshu-jingpin": "成熟女声精品",
            "female-tianmei-jingpin": "甜美女声精品"
        },
        "中文男声": {
            "male-qn-qingse": "青年音",
            "male-qn-jingying": "精英音",
            "male-qn-badao": "霸道总裁",
            "male-qn-daxuesheng": "大学生",
            "presenter_male": "男主播",
            "audiobook_male_1": "有声书男声1",
            "audiobook_male_2": "有声书男声2",
            "male-qn-qingse-jingpin": "青年音精品",
            "male-qn-jingying-jingpin": "精英音精品",
            "male-qn-badao-jingpin": "霸道总裁精品",
            "male-qn-daxuesheng-jingpin": "大学生精品"
        },
        "特色音色": {
            "clever_boy": "聪明男孩",
            "cute_boy": "可爱男孩",
            "lovely_girl": "可爱女孩",
            "cartoon_pig": "卡通猪",
            "bingjiao_didi": "病娇弟弟",
            "junlang_nanyou": "俊朗男友",
            "chunzhen_xuedi": "纯真学弟",
            "lengdan_xiongzhang": "冷淡兄丈",
            "badao_shaoye": "霸道少爷",
            "tianxin_xiaoling": "甜心小玲",
            "qiaopi_mengmei": "俏皮萌妹",
            "wumei_yujie": "妩媚御姐",
            "diadia_xuemei": "嗲嗲学妹",
            "danya_xuejie": "淡雅学姐"
        }
    }
    
    # 播客场景配置
    PODCAST_SCENES = {
        "solo": {
            "name": "单人主播",
            "description": "温暖亲切的独白式播客",
            "default_voice": "female-chengshu",
            "backup_voices": ["presenter_female", "audiobook_female_1"],
            "style": "亲切自然，像朋友聊天"
        },
        "dialogue": {
            "name": "双人对话",
            "description": "两个主播的轻松对话",
            "default_voices": ["male-qn-jingying", "female-yujie"],
            "backup_voices": ["presenter_male", "presenter_female"],
            "style": "观点碰撞，互动自然"
        },
        "panel": {
            "name": "多人圆桌",
            "description": "三人以上的专业讨论",
            "default_voices": ["male-qn-jingying", "female-chengshu", "male-qn-daxuesheng"],
            "backup_voices": ["presenter_male", "presenter_female", "audiobook_male_1"],
            "style": "专业深入，观点多元"
        },
        "news": {
            "name": "新闻播报",
            "description": "正式权威的新闻播客",
            "default_voice": "presenter_male",
            "backup_voices": ["presenter_female", "audiobook_male_1"],
            "style": "正式权威，语速适中"
        },
        "storytelling": {
            "name": "故事讲述",
            "description": "情感丰富的故事播客",
            "default_voice": "audiobook_female_1",
            "backup_voices": ["audiobook_male_1", "female-yujie"],
            "style": "情感丰富，节奏舒缓"
        }
    }
    
    def __init__(self, client):
        self.client = client
        # 使用项目目录而不是系统目录
        self.output_dir = Path(__file__).parent / "podcasts"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_voice_recommendations(self, scene: str, count: int = 1) -> List[str]:
        """根据场景推荐音色"""
        scene_config = self.PODCAST_SCENES[scene]
        
        if count == 1:
            # 单人播客
            return [scene_config["default_voice"]]
        elif count == 2:
            # 双人播客
            return scene_config["default_voices"][:2]
        else:
            # 多人播客
            return scene_config["default_voices"][:count]
    
    def generate_script(self, topic: str, scene: str, duration: int = 10) -> str:
        """生成播客脚本"""
        scene_config = self.PODCAST_SCENES[scene]
        
        # 确保主题不为空
        if not topic or not topic.strip():
            topic = "科技与生活"
        
        prompt = f"""
你是一位专业的{scene_config['name']}播客主播，请围绕"{topic}"创作一期{duration}分钟的播客节目。

要求：
1. {scene_config['style']}
2. 开场白：30秒引人入胜的开场
3. 主体内容：分3-4个自然段落
4. 互动环节：{'提问讨论' if scene != 'solo' else '思考引导'}
5. 结束语：30秒温暖结尾
6. 语气：{scene_config['description']}
7. 语言：自然口语化，避免书面语

请直接输出播客文本内容，不要添加任何格式标记。
确保内容完整，字数适中，适合{duration}分钟播报。
"""
        
        try:
            response = self.client.chat_completion(prompt)
            # 确保返回内容不为空
            if not response or not response.strip():
                return f"大家好，欢迎收听本期播客。今天我们要聊的话题是{topic}。人工智能正在以前所未有的方式改变我们的生活和工作方式。从智能家居到自动驾驶，从医疗诊断到教育辅导，AI的应用无处不在。让我们一起探讨这个激动人心的主题。"
            return response.strip()
        except Exception as e:
            print(f"脚本生成失败: {e}")
            return f"大家好，欢迎收听本期播客。今天我们要聊的话题是{topic}。人工智能正在深刻改变着我们的世界，从工作方式到生活习惯，每一个领域都在发生变革。让我们一起来看看这些变化吧。"
    
    def split_script_by_speakers(self, script: str, scene: str, speaker_count: int) -> List[Tuple[str, str]]:
        """将脚本分割为不同说话人"""
        if speaker_count == 1:
            return [(self.PODCAST_SCENES[scene]["default_voice"], script)]
        
        # 简单的对话分割逻辑
        lines = script.split('\n')
        speakers = self.get_voice_recommendations(scene, speaker_count)
        
        dialogue_parts = []
        current_speaker_idx = 0
        current_text = ""
        
        for line in lines:
            if line.strip():
                if len(line.strip()) > 50:  # 长段落分配给当前说话人
                    if current_text:
                        dialogue_parts.append((speakers[current_speaker_idx], current_text))
                        current_text = line
                        current_speaker_idx = (current_speaker_idx + 1) % speaker_count
                    else:
                        current_text = line
                else:
                    if current_text:
                        current_text += " " + line
                    else:
                        current_text = line
        
        if current_text:
            dialogue_parts.append((speakers[current_speaker_idx], current_text))
        
        return dialogue_parts
    
    def generate_audio_segments(self, dialogue_parts: List[Tuple[str, str]], 
                              model: str = "speech-2.5-hd-preview") -> List[str]:
        """生成音频片段"""
        audio_files = []
        
        for i, (voice_id, text) in enumerate(dialogue_parts):
            try:
                # 确保文本不为空
                if not text or not text.strip():
                    text = "感谢您的收听，这是播客的一段内容。"
                
                print(f"正在生成第{i+1}段音频 ({voice_id})...")
                audio_data = self.client.text_to_speech(
                    text=text.strip(),
                    voice_id=voice_id,
                    model=model,
                    speed=1.0
                )
                
                # 保存音频文件
                filename = f"segment_{i+1}_{voice_id}_{datetime.now().strftime('%H%M%S')}.mp3"
                filepath = self.output_dir / filename
                
                # 处理音频数据（可能是base64字符串或字节数据）
                import base64
                try:
                    # 尝试base64解码
                    decoded_data = base64.b64decode(audio_data)
                except:
                    # 如果已经是字节数据，直接使用
                    if isinstance(audio_data, str):
                        decoded_data = base64.b64decode(audio_data)
                    else:
                        decoded_data = audio_data
                
                with open(filepath, 'wb') as f:
                    f.write(decoded_data)
                
                audio_files.append(str(filepath))
                print(f"✓ 已保存: {filepath}")
                
            except Exception as e:
                print(f"音频生成失败 ({voice_id}): {e}")
                continue
        
        return audio_files
    
    def merge_audio_files(self, audio_files: List[str], output_filename: str) -> str:
        """合并音频文件"""
        try:
            from pydub import AudioSegment
            
            combined = AudioSegment.empty()
            for file in audio_files:
                if os.path.exists(file):
                    audio = AudioSegment.from_mp3(file)
                    combined += audio
            
            output_path = self.output_dir / output_filename
            combined.export(output_path, format="mp3", bitrate="192k")
            
            # 清理临时文件
            for file in audio_files:
                if os.path.exists(file):
                    os.remove(file)
            
            return str(output_path)
            
        except ImportError:
            print("需要安装 pydub: pip install pydub")
            print("将使用第一个音频文件作为最终结果")
            return audio_files[0] if audio_files else None
        except Exception as e:
            print(f"音频合并失败: {e}")
            return audio_files[0] if audio_files else None
    
    def generate_podcast(self, topic: str, scene: str = "solo", 
                        custom_voices: List[str] = None, 
                        duration: int = 10, 
                        model: str = "speech-2.5-hd-preview") -> str:
        """一键生成完整播客"""
        print(f"🎙️ 正在生成{self.PODCAST_SCENES[scene]['name']}播客：{topic}")
        
        # 1. 生成脚本
        print("📄 正在生成播客脚本...")
        script = self.generate_script(topic, scene, duration)
        
        # 2. 确定说话人数量
        speaker_count = len(custom_voices) if custom_voices else (2 if scene in ["dialogue"] else 1)
        if scene == "panel":
            speaker_count = 3
        
        # 3. 确定音色
        if custom_voices:
            voices = custom_voices[:speaker_count]
        else:
            voices = self.get_voice_recommendations(scene, speaker_count)
        
        print(f"🎭 使用音色: {', '.join(voices)}")
        
        # 4. 分割脚本
        dialogue_parts = self.split_script_by_speakers(script, scene, speaker_count)
        
        # 5. 生成音频
        audio_files = self.generate_audio_segments(dialogue_parts, model)
        
        # 6. 合并音频
        if audio_files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"podcast_{scene}_{timestamp}.mp3"
            final_path = self.merge_audio_files(audio_files, output_filename)
            
            if final_path:
                print(f"✅ 播客生成完成: {final_path}")
                return final_path
        
        return None
    
    def list_available_voices(self) -> Dict[str, List[str]]:
        """列出可用音色"""
        return self.VOICE_CATEGORIES
    
    def interactive_voice_selection(self, scene: str) -> List[str]:
        """交互式音色选择"""
        try:
            import inquirer
            
            scene_config = self.PODCAST_SCENES[scene]
            speaker_count = 1 if scene == "solo" else (2 if scene == "dialogue" else 3)
            
            selected_voices = []
            
            for i in range(speaker_count):
                # 为每个说话人选择音色
                choices = []
                for category, voices in self.VOICE_CATEGORIES.items():
                    for voice_id, desc in voices.items():
                        choices.append(f"{desc} ({voice_id})")
                
                question = [
                    inquirer.List(f'speaker_{i+1}',
                                message=f"选择说话人{i+1}的音色",
                                choices=choices)
                ]
                
                answer = inquirer.prompt(question)
                voice_choice = answer[f'speaker_{i+1}']
                voice_id = voice_choice.split('(')[-1].rstrip(')')
                selected_voices.append(voice_id)
            
            return selected_voices
            
        except ImportError:
            print("需要安装 inquirer: pip install inquirer")
            return self.get_voice_recommendations(scene, speaker_count)


def main():
    """测试播客生成功能"""
    from minimax_cli import MiniMaxClient
    
    client = MiniMaxClient()
    generator = PodcastGenerator(client)
    
    # 测试单人播客
    result = generator.generate_podcast(
        topic="人工智能如何改变我们的生活",
        scene="solo",
        duration=5
    )
    
    if result:
        print(f"播客已生成: {result}")


if __name__ == "__main__":
    main()