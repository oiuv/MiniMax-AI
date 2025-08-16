"""
播客生成器主类
集成所有模块，实现完整的播客生成功能
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .content_generator import ContentGenerator
from .voice_synthesizer import VoiceSynthesizer
from .music_creator import MusicCreator
from .audio_mixer import AudioMixer
from .audio_enhancer import AudioEnhancer
from .progress_tracker import ProgressTracker
from .models.podcast_config import PodcastConfig, PodcastScene

class PodcastGenerator:
    """播客生成器主类"""
    
    def __init__(self, client):
        """初始化播客生成器
        
        Args:
            client: MiniMaxClient实例
        """
        self.client = client
        
        # 初始化各个模块
        self.content_gen = ContentGenerator(client)
        self.voice_synth = VoiceSynthesizer(client)
        self.music_creator = MusicCreator(client)
        self.audio_mixer = AudioMixer()
        self.audio_enhancer = AudioEnhancer()
        self.progress_tracker = ProgressTracker()
        
        # 设置输出目录
        self.output_dir = Path("output/podcasts")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 临时文件目录
        self.temp_dir = Path("output/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        (self.temp_dir / "voices").mkdir(exist_ok=True)
        (self.temp_dir / "music").mkdir(exist_ok=True)
    
    def generate_podcast(
        self,
        topic: str,
        scene: str = "solo",
        duration: int = 5,
        voices: List[str] = None,
        role_names: List[str] = None,
        music_style: str = None,
        output_filename: str = None,
        show_progress: bool = True
    ) -> str:
        """生成完整播客
        
        Args:
            topic: 播客主题
            scene: 场景类型(solo, dialogue, panel, news, storytelling, interview)
            duration: 时长(分钟)
            voices: 音色列表
            music_style: 音乐风格
            output_filename: 输出文件名
            
        Returns:
            生成的播客文件路径
        """
        try:
            # 设置进度追踪
            self.progress_tracker.enable_progress = show_progress
            self.progress_tracker.start(topic)
            
            if show_progress:
                estimated = self.progress_tracker.get_estimated_time(duration)
                print(f"⏱️  预计耗时: {estimated}")
            
            # 1. 创建配置
            config = self._create_config(topic, scene, duration, voices, music_style)
            
            # 2. 生成内容
            self.progress_tracker.update("内容生成", "进行中")
            script = self.content_gen.generate_script(config, role_names=role_names)
            
            # 3. 分割对话
            self.progress_tracker.update("语音合成", "准备中")
            dialogue = self.content_gen.split_dialogue(script, config)
            
            # 4. 合成语音
            self.progress_tracker.update("语音合成", "进行中")
            voice_files = self.voice_synth.synthesize_dialogue(
                dialogue, 
                model=config.model_voice
            )
            
            if not voice_files:
                raise ValueError("语音合成失败")
            
            # 5. 创建背景音乐（带智能降级）
            music_file = None
            try:
                self.progress_tracker.update("背景音乐", "进行中")
                music_file = self.music_creator.create_music_for_scene(
                    topic=topic,
                    scene=config.scene,
                    duration=duration,
                    filename=f"bgm_{config.scene.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
                )
                self.progress_tracker.update("背景音乐", "完成")
            except Exception as e:
                self.progress_tracker.update("背景音乐", "跳过")
                music_file = None
            
            # 6. 音频混合
            self.progress_tracker.update("音频混合", "进行中")
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_topic = topic[:20].replace(' ', '_').replace('/', '_')
                output_filename = f"podcast_{config.scene.value}_{safe_topic}_{timestamp}.mp3"
            
            if music_file and os.path.exists(music_file):
                # 有背景音乐：混合
                mixed_file = self.audio_mixer.mix_audio_tracks(
                    voice_files=voice_files,
                    background_music=music_file,
                    output_filename=f"mixed_{output_filename}",
                    music_volume=config.music_volume
                )
                
                # 音频增强
                self.progress_tracker.update("质量增强", "进行中")
                final_file = self.audio_enhancer.enhance_podcast_audio(
                    voice_files=[mixed_file],
                    output_filename=output_filename,
                    normalize_volume=True,
                    add_fade_effects=True
                )
            else:
                # 无背景音乐：直接增强
                self.progress_tracker.update("质量增强", "进行中")
                final_file = self.audio_enhancer.enhance_podcast_audio(
                    voice_files=voice_files,
                    output_filename=output_filename,
                    normalize_volume=True,
                    add_fade_effects=True
                )
            
            # 7. 清理和完成
            self._cleanup_temp_files(voice_files + [music_file])
            self.progress_tracker.update("完成", "成功")
            self.progress_tracker.complete(True, final_file)
            return final_file
            
        except Exception as e:
            print(f"❌ 播客生成失败: {e}")
            raise
    
    def generate_solo_podcast(
        self,
        topic: str,
        duration: int = 5,
        voice: str = "female-chengshu",
        output_filename: str = None
    , show_progress: bool = True) -> str:
        """生成单人播客"""
        return self.generate_podcast(
            topic=topic,
            scene="solo",
            duration=duration,
            voices=[voice],
            output_filename=output_filename,
            show_progress=show_progress
        )
    
    def generate_dialogue_podcast(
        self,
        topic: str,
        duration: int = 8,
        voice1: str = "male-qn-jingying",
        voice2: str = "female-yujie",
        output_filename: str = None
    , show_progress: bool = True) -> str:
        """生成双人对话播客"""
        return self.generate_podcast(
            topic=topic,
            scene="dialogue",
            duration=duration,
            voices=[voice1, voice2],
            output_filename=output_filename,
            show_progress=show_progress
        )
    
    def generate_news_podcast(
        self,
        topic: str,
        duration: int = 3,
        output_filename: str = None
    , show_progress: bool = True) -> str:
        """生成新闻播客"""
        return self.generate_podcast(
            topic=topic,
            scene="news",
            duration=duration,
            voices=["presenter_male"],
            output_filename=output_filename,
            show_progress=show_progress
        )
    
    def _create_config(
        self,
        topic: str,
        scene: str,
        duration: int,
        voices: List[str] = None,
        music_style: str = None
    ) -> PodcastConfig:
        """创建播客配置"""
        scene_enum = PodcastScene(scene)
        
        config = PodcastConfig(
            topic=topic,
            scene=scene_enum,
            duration=duration
        )
        
        # 添加说话人
        if voices:
            for voice_id in voices:
                config.add_speaker(voice_id)
        else:
            # 使用默认音色
            default_voices = {
                "solo": ["female-chengshu"],
                "dialogue": ["male-qn-jingying", "female-yujie"],
                "panel": ["male-qn-jingying", "female-chengshu", "male-qn-daxuesheng"],
                "news": ["presenter_male"],
                "storytelling": ["audiobook_female_1"],
                "interview": ["presenter_male", "female-yujie"]
            }
            for voice_id in default_voices.get(scene, ["female-chengshu"]):
                config.add_speaker(voice_id)
        
        return config
    
    def get_available_voices(self) -> dict:
        """获取可用音色"""
        return self.voice_synth.list_available_voices()
    
    def get_music_styles(self) -> dict:
        """获取可用音乐风格"""
        return self.music_creator.list_music_styles()
    
    def estimate_generation_time(self, duration: int) -> int:
        """估算生成时间（秒）"""
        # 基于经验估算
        base_time = 30  # 基础时间
        content_time = duration * 2  # 内容生成
        voice_time = duration * 3  # 语音合成
        music_time = 60  # 音乐生成
        mix_time = 30  # 音频混合
        
        return base_time + content_time + voice_time + music_time + mix_time
    
    def _cleanup_temp_files(self, file_paths: List[str]):
        """清理临时文件"""
        # 语音合成器清理语音文件
        self.voice_synth.cleanup_temp_files(file_paths)
        
        # 音乐创作器清理音乐文件
        self.music_creator.cleanup_music_files(file_paths)
        
        # 音频混合器清理其他临时文件
        self.audio_mixer.cleanup_files(file_paths)
    
    def validate_inputs(
        self,
        topic: str,
        scene: str,
        duration: int,
        voices: List[str] = None
    ) -> bool:
        """验证输入参数"""
        if not topic or not topic.strip():
            print("❌ 主题不能为空")
            return False
        
        if scene not in [s.value for s in PodcastScene]:
            print(f"❌ 无效的场景: {scene}")
            return False
        
        if not (1 <= duration <= 30):
            print("❌ 时长必须在1-30分钟之间")
            return False
        
        # 不再验证音色ID，让API端处理
        
        return True
    
    def quick_demo(self, topic: str = "人工智能如何改变生活", show_progress: bool = True) -> str:
        """快速演示"""
        if show_progress:
            print("🚀 开始播客快速演示...")
        return self.generate_podcast(
            topic=topic,
            scene="solo",
            duration=3,
            voices=["female-chengshu"],
            show_progress=show_progress
        )