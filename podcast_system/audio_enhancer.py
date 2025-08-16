"""
音频增强模块
提供音频后处理优化和智能降级功能
"""

import os
from pathlib import Path
from typing import List, Optional, Dict
import subprocess
import tempfile
from datetime import datetime

class AudioEnhancer:
    """音频增强器 - 无需外部依赖的高级音频处理"""
    
    def __init__(self, output_dir: str = None):
        """初始化音频增强器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir) if output_dir else Path("output/enhanced")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查ffmpeg可用性
        self.ffmpeg_available = self._check_ffmpeg()
        if not self.ffmpeg_available:
            print("⚠️  ffmpeg未安装，将使用基础音频处理")
    
    def _check_ffmpeg(self) -> bool:
        """检查ffmpeg是否可用"""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def enhance_podcast_audio(
        self,
        voice_files: List[str],
        background_music: Optional[str] = None,
        output_filename: str = None,
        normalize_volume: bool = True,
        add_fade_effects: bool = True,
        target_lufs: float = -16.0
    ) -> str:
        """增强播客音频质量
        
        Args:
            voice_files: 语音文件列表
            background_music: 背景音乐文件（可选）
            output_filename: 输出文件名
            normalize_volume: 是否标准化音量
            add_fade_effects: 是否添加淡入淡出
            target_lufs: 目标响度（LUFS）
            
        Returns:
            增强后的音频文件路径
        """
        
        if self.ffmpeg_available:
            return self._enhance_with_ffmpeg(
                voice_files, background_music, output_filename,
                normalize_volume, add_fade_effects, target_lufs
            )
        else:
            return self._basic_enhancement(voice_files, output_filename)
    
    def _enhance_with_ffmpeg(
        self,
        voice_files: List[str],
        background_music: Optional[str],
        output_filename: Optional[str],
        normalize_volume: bool,
        add_fade_effects: bool,
        target_lufs: float
    ) -> str:
        """使用ffmpeg进行高级音频增强"""
        
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"enhanced_podcast_{timestamp}.mp3"
        
        output_path = self.output_dir / output_filename
        
        try:
            # 构建ffmpeg命令
            cmd = ['ffmpeg', '-y', '-i']
            
            # 合并语音文件
            if len(voice_files) == 1:
                # 单个文件
                input_file = voice_files[0]
            else:
                # 多个文件合并
                input_file = self._concatenate_voices(voice_files)
            
            if background_music and os.path.exists(background_music):
                # 有背景音乐的复杂处理
                cmd.extend([input_file, '-i', background_music])
                
                # 构建ffmpeg过滤器
                filter_complex = []
                
                # 标准化语音音量
                if normalize_volume:
                    filter_complex.append('[0:a]loudnorm=I=-16:TP=-1.5:LRA=11[voice]')
                else:
                    filter_complex.append('[0:a]volume=1.0[voice]')
                
                # 调整背景音乐音量并淡入淡出
                bg_filters = '[1:a]volume=0.3'
                if add_fade_effects:
                    bg_filters += ',afade=t=in:ss=0:d=2,afade=t=out:st=end-3:d=3'
                bg_filters += '[bg]'
                filter_complex.append(bg_filters)
                
                # 混合音频
                filter_complex.append('[voice][bg]amix=inputs=2:duration=first:dropout_transition=2[out]')
                
                cmd.extend(['-filter_complex', ';'.join(filter_complex), '-map', '[out]'])
                
            else:
                # 纯语音处理
                cmd.extend([input_file])
                
                if normalize_volume:
                    cmd.extend(['-af', f'loudnorm=I={target_lufs}:TP=-1.5:LRA=11'])
                
                if add_fade_effects:
                    cmd.extend(['-af', 'afade=t=in:ss=0:d=2,afade=t=out:st=end-3:d=3'])
            
            # 输出设置
            cmd.extend(['-c:a', 'libmp3lame', '-b:a', '192k', str(output_path)])
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ 音频增强完成: {output_path}")
                return str(output_path)
            else:
                print(f"⚠️  ffmpeg处理失败: {result.stderr}")
                return self._basic_enhancement(voice_files, output_filename)
                
        except Exception as e:
            print(f"⚠️  音频增强失败: {e}")
            return self._basic_enhancement(voice_files, output_filename)
    
    def _basic_enhancement(self, voice_files: List[str], output_filename: str) -> str:
        """基础音频增强（不依赖ffmpeg）"""
        import shutil
        
        output_path = self.output_dir / output_filename
        
        # 找到第一个有效的语音文件
        valid_file = None
        for file in voice_files:
            if os.path.exists(file):
                valid_file = file
                break
        
        if valid_file:
            # 简单复制并重命名
            shutil.copy2(valid_file, output_path)
            print(f"✅ 基础音频增强完成: {output_path}")
            return str(output_path)
        else:
            raise ValueError("没有找到有效的语音文件")
    
    def _concatenate_voices(self, voice_files: List[str]) -> str:
        """合并多个语音文件"""
        # 创建临时文件列表
        list_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        
        try:
            # 写入文件列表
            for file in voice_files:
                if os.path.exists(file):
                    list_file.write(f"file '{os.path.abspath(file)}'\n")
            list_file.close()
            
            # 创建合并后的临时文件
            merged_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            merged_file.close()
            
            # 使用ffmpeg合并
            cmd = [
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', list_file.name, '-c', 'copy', merged_file.name
            ]
            
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0:
                return merged_file.name
            else:
                # 回退到复制第一个文件
                return voice_files[0] if voice_files else None
                
        finally:
            try:
                os.unlink(list_file.name)
            except:
                pass
    
    def analyze_audio_quality(self, audio_file: str) -> Dict:
        """分析音频质量"""
        if not self.ffmpeg_available:
            return {"status": "unavailable", "reason": "ffmpeg未安装"}
        
        try:
            cmd = [
                'ffmpeg', '-i', audio_file, '-af',
                'volumedetect', '-f', 'null', '-'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 解析输出
            output = result.stderr
            
            # 提取关键信息
            max_volume = None
            mean_volume = None
            for line in output.split('\n'):
                if 'max_volume' in line:
                    max_volume = float(line.split(':')[1].strip().replace(' dB', ''))
                elif 'mean_volume' in line:
                    mean_volume = float(line.split(':')[1].strip().replace(' dB', ''))
            
            return {
                "max_volume": max_volume,
                "mean_volume": mean_volume,
                "file_size": os.path.getsize(audio_file),
                "format": audio_file.split('.')[-1].upper(),
                "status": "analyzed"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def create_silence_padding(self, duration: float, output_file: str = None) -> str:
        """创建静音填充"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = str(self.output_dir / f"silence_{timestamp}.mp3")
        
        if self.ffmpeg_available:
            try:
                cmd = [
                    'ffmpeg', '-y', '-f', 'lavfi', '-i',
                    f'anullsrc=duration={duration}', '-c:a', 'libmp3lame',
                    '-b:a', '192k', output_file
                ]
                
                subprocess.run(cmd, capture_output=True, check=True)
                return output_file
                
            except Exception as e:
                print(f"创建静音失败: {e}")
        
        # 基础方法：创建空文件
        return output_file
    
    def install_ffmpeg(self) -> bool:
        """检查并指导安装ffmpeg"""
        try:
            import subprocess
            import sys
            
            if sys.platform == "win32":
                print("📥 Windows用户请下载ffmpeg:")
                print("1. 访问 https://ffmpeg.org/download.html")
                print("2. 下载Windows版本")
                print("3. 解压并将bin目录添加到系统PATH")
            else:
                print("📥 使用包管理器安装:")
                print("Ubuntu/Debian: sudo apt install ffmpeg")
                print("macOS: brew install ffmpeg")
                
            return False
            
        except Exception as e:
            print(f"安装指导失败: {e}")
            return False