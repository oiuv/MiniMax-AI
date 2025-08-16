"""
音频混合模块
将多个音频文件混合为最终播客
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional, Dict
import subprocess

class AudioMixer:
    """音频混合器"""
    
    def __init__(self, output_dir: str = None):
        """初始化音频混合器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir) if output_dir else Path("output/podcasts")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 临时目录
        self.temp_dir = Path("output/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查是否安装了pydub
        try:
            from pydub import AudioSegment
            self.pydub_available = True
        except ImportError:
            self.pydub_available = False
            print("⚠️  pydub未安装，将使用基础音频合并")
    
    def mix_audio_tracks(
        self,
        voice_files: List[str],
        background_music: str,
        output_filename: str = None,
        music_volume: float = 0.3,
        fade_in: float = 2.0,
        fade_out: float = 3.0
    ) -> str:
        """混合音频轨道
        
        Args:
            voice_files: 语音文件列表
            background_music: 背景音乐文件
            output_filename: 输出文件名
            music_volume: 背景音乐音量比例(0.0-1.0)
            fade_in: 淡入时长(秒)
            fade_out: 淡出时长(秒)
            
        Returns:
            混合后的音频文件路径
        """
        if self.pydub_available:
            return self._mix_with_pydub(
                voice_files, background_music, output_filename, 
                music_volume, fade_in, fade_out
            )
        else:
            return self._basic_concat(voice_files, background_music, output_filename)
    
    def _mix_with_pydub(
        self,
        voice_files: List[str],
        background_music: str,
        output_filename: Optional[str],
        music_volume: float,
        fade_in: float,
        fade_out: float
    ) -> str:
        """使用pydub混合音频"""
        from pydub import AudioSegment
        
        try:
            print("🎛️  正在混合音频轨道...")
            
            # 合并所有语音文件
            combined_voice = AudioSegment.empty()
            for voice_file in voice_files:
                if os.path.exists(voice_file):
                    audio = AudioSegment.from_file(voice_file)
                    combined_voice += audio
                else:
                    print(f"⚠️  语音文件不存在: {voice_file}")
            
            if len(combined_voice) == 0:
                raise ValueError("没有有效的语音文件")
            
            # 加载背景音乐
            if os.path.exists(background_music):
                bg_music = AudioSegment.from_file(background_music)
                
                # 调整背景音乐长度
                if len(bg_music) < len(combined_voice):
                    # 循环背景音乐
                    loops_needed = len(combined_voice) // len(bg_music) + 1
                    extended_bg = bg_music * loops_needed
                    bg_music = extended_bg[:len(combined_voice)]
                else:
                    # 裁剪背景音乐
                    bg_music = bg_music[:len(combined_voice)]
                
                # 调整音量
                bg_music = bg_music - (20 * (1 - music_volume))
                
                # 添加淡入淡出
                bg_music = bg_music.fade_in(int(fade_in * 1000)).fade_out(int(fade_out * 1000))
                
                # 混合音频
                final_audio = combined_voice.overlay(bg_music)
                
            else:
                print("⚠️  背景音乐文件不存在，仅使用语音")
                final_audio = combined_voice
            
            # 标准化音量
            final_audio = final_audio.normalize()
            
            # 生成输出文件名
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"podcast_mixed_{timestamp}.mp3"
            
            output_path = self.output_dir / output_filename
            
            # 导出音频
            final_audio.export(
                output_path,
                format="mp3",
                bitrate="192k",
                parameters=["-q:a", "2"]
            )
            
            print(f"✅ 音频混合完成: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ 音频混合失败: {e}")
            raise
    
    def _basic_concat(
        self,
        voice_files: List[str],
        background_music: str,
        output_filename: Optional[str]
    ) -> str:
        """基础音频合并（无背景音乐混合）"""
        
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"podcast_basic_{timestamp}.mp3"
        
        output_path = self.output_dir / output_filename
        
        # 过滤存在的文件
        valid_files = [f for f in voice_files if os.path.exists(f)]
        if not valid_files:
            raise ValueError("没有有效的音频文件")
        
        # 使用ffmpeg合并所有音频文件
        try:
            import subprocess
            
            # 创建临时文件列表
            temp_list = self.temp_dir / "concat_list.txt"
            temp_list.parent.mkdir(parents=True, exist_ok=True)
            
            with open(temp_list, 'w', encoding='utf-8') as f:
                for file_path in valid_files:
                    f.write(f"file '{os.path.abspath(file_path)}'\n")
            
            # 使用ffmpeg合并
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', str(temp_list),
                '-c', 'copy', str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='ignore')
            
            if result.returncode != 0:
                print(f"⚠️  ffmpeg合并失败: {result.stderr}")
                # 回退到pydub基础合并
                return self._fallback_concat(valid_files, output_path)
            
            print(f"✅ 基础音频合并完成: {output_path}")
            
            # 清理临时文件
            try:
                temp_list.unlink()
            except:
                pass
                
            return str(output_path)
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # ffmpeg不可用，回退到基础方法
            return self._fallback_concat(valid_files, output_path)
    
    def _fallback_concat(self, valid_files: List[str], output_path: Path) -> str:
        """回退合并方法"""
        import shutil
        
        # 检查pydub是否可用
        if self.pydub_available:
            return self._concat_with_pydub(valid_files, str(output_path), 0.0)
        else:
            # 最后回退：只复制第一个文件
            if valid_files:
                shutil.copy2(valid_files[0], output_path)
                print(f"⚠️  仅使用第一个音频文件: {output_path}")
                return str(output_path)
            else:
                raise ValueError("没有有效的音频文件")
    
    def concatenate_audio_files(
        self,
        audio_files: List[str],
        output_filename: str = None,
        crossfade: float = 0.5
    ) -> str:
        """连接多个音频文件
        
        Args:
            audio_files: 音频文件列表
            output_filename: 输出文件名
            crossfade: 交叉淡化时长(秒)
            
        Returns:
            连接后的音频文件路径
        """
        if not audio_files:
            raise ValueError("音频文件列表为空")
        
        if self.pydub_available:
            return self._concat_with_pydub(audio_files, output_filename, crossfade)
        else:
            return self._basic_concat(audio_files, None, output_filename)
    
    def _concat_with_pydub(
        self,
        audio_files: List[str],
        output_filename: Optional[str],
        crossfade: float
    ) -> str:
        """使用pydub连接音频文件"""
        from pydub import AudioSegment
        
        try:
            print("🔗 正在连接音频文件...")
            
            combined = AudioSegment.empty()
            
            for audio_file in audio_files:
                if os.path.exists(audio_file):
                    audio = AudioSegment.from_file(audio_file)
                    if len(combined) == 0:
                        combined = audio
                    else:
                        combined = combined.append(audio, crossfade=int(crossfade * 1000))
                else:
                    print(f"⚠️  音频文件不存在: {audio_file}")
            
            if len(combined) == 0:
                raise ValueError("没有有效的音频文件")
            
            # 生成输出文件名
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"concatenated_{timestamp}.mp3"
            
            output_path = self.output_dir / output_filename
            
            # 导出音频
            combined.export(
                output_path,
                format="mp3",
                bitrate="192k"
            )
            
            print(f"✅ 音频连接完成: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ 音频连接失败: {e}")
            raise
    
    def adjust_audio_levels(
        self,
        audio_file: str,
        target_volume: float = -16.0,
        output_filename: str = None
    ) -> str:
        """调整音频音量
        
        Args:
            audio_file: 输入音频文件
            target_volume: 目标音量(dB)
            output_filename: 输出文件名
            
        Returns:
            调整后的音频文件路径
        """
        if not self.pydub_available:
            print("⚠️  pydub不可用，跳过音量调整")
            return audio_file
        
        try:
            from pydub import AudioSegment
            from pydub.effects import normalize
            
            audio = AudioSegment.from_file(audio_file)
            
            # 调整音量
            change_in_dBFS = target_volume - audio.dBFS
            adjusted_audio = audio.apply_gain(change_in_dBFS)
            
            # 生成输出文件名
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"normalized_{timestamp}.mp3"
            
            output_path = self.output_dir / output_filename
            
            # 导出音频
            adjusted_audio.export(
                output_path,
                format="mp3",
                bitrate="192k"
            )
            
            print(f"✅ 音量调整完成: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ 音量调整失败: {e}")
            return audio_file
    
    def get_audio_info(self, audio_file: str) -> Dict:
        """获取音频信息
        
        Args:
            audio_file: 音频文件路径
            
        Returns:
            音频信息字典
        """
        if not self.pydub_available:
            return {"error": "pydub不可用"}
        
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(audio_file)
            
            return {
                "duration": round(len(audio) / 1000, 2),  # 秒
                "channels": audio.channels,
                "sample_rate": audio.frame_rate,
                "bitrate": audio.frame_width * 8,
                "file_size": os.path.getsize(audio_file),
                "format": audio_file.split('.')[-1].upper()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup_files(self, file_paths: List[str]):
        """清理音频文件"""
        for filepath in file_paths:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"🗑️  已清理音频文件: {filepath}")
            except Exception as e:
                print(f"清理音频文件失败 {filepath}: {e}")
    
    def install_pydub(self) -> bool:
        """检查并尝试安装pydub"""
        try:
            import subprocess
            import sys
            
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pydub"])
            print("✅ pydub安装成功")
            self.pydub_available = True
            return True
            
        except Exception as e:
            print(f"❌ pydub安装失败: {e}")
            return False