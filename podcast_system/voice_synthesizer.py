"""
语音合成模块
基于MiniMax TTS API将文本转换为语音
"""

import os
import base64
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict
import tempfile

class VoiceSynthesizer:
    """语音合成器"""
    
    # 官方音色映射
    OFFICIAL_VOICES = {
        # 中文女声
        "female-chengshu": "成熟女声",
        "female-yujie": "御姐女声", 
        "female-shaonv": "少女女声",
        "female-tianmei": "甜美女声",
        "presenter_female": "女主播",
        "audiobook_female_1": "有声书女声1",
        "audiobook_female_2": "有声书女声2",
        
        # 中文男声
        "male-qn-qingse": "青年男声",
        "male-qn-jingying": "精英男声",
        "male-qn-badao": "霸道男声",
        "male-qn-daxuesheng": "大学生男声",
        "presenter_male": "男主播",
        "audiobook_male_1": "有声书男声1",
        "audiobook_male_2": "有声书男声2",
        
        # 特色音色
        "clever_boy": "聪明男孩",
        "cute_boy": "可爱男孩",
        "lovely_girl": "可爱女孩",
        "Santa_Claus": "圣诞老人",
        "Charming_Santa": "魅力圣诞老人"
    }
    
    def __init__(self, client, output_dir: str = None):
        """初始化语音合成器
        
        Args:
            client: MiniMaxClient实例
            output_dir: 输出目录
        """
        self.client = client
        self.output_dir = Path(output_dir) if output_dir else Path("output/temp")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def synthesize_text(
        self, 
        text: str, 
        voice_id: str = "female-chengshu",
        model: str = "speech-2.5-hd-preview",
        speed: float = 1.0,
        volume: float = 3.0,
        pitch: int = 0,
        filename: str = None
    ) -> str:
        """将文本转换为语音
        
        Args:
            text: 要转换的文本
            voice_id: 音色ID
            model: 语音模型
            speed: 语速(0.5-2.0)
            volume: 音量(0.1-10.0)
            pitch: 音调(-12到12)
            filename: 输出文件名
            
        Returns:
            生成的音频文件路径
        """
        if not text or not text.strip():
            raise ValueError("文本内容不能为空")
        
        # 限制文本长度，避免API截断
        max_chars = 300  # 限制单次合成字符数
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
            print(f"⚠️  文本过长，已截断至{max_chars}字符")
        
        # 直接使用提供的音色ID，让API自行验证
        print(f"🎤 使用音色: {voice_id}")
        
        try:
            print(f"🎤 正在生成语音: {voice_id} - {len(text)}字符")
            
            # 调用TTS API
            audio_data = self.client.text_to_speech(
                text=text.strip(),
                voice_id=voice_id,
                model=model
            )
            
            # 生成文件名
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_text = text[:20].replace(' ', '_').replace('/', '_')
                filename = f"voice_{voice_id}_{safe_text}_{timestamp}.mp3"
            
            filepath = self.output_dir / filename
            
            # 处理音频数据 - 增强兼容性
            audio_bytes = None
            if isinstance(audio_data, str):
                # 处理十六进制字符串
                try:
                    audio_bytes = bytes.fromhex(audio_data)
                except ValueError:
                    # 尝试base64解码
                    try:
                        import base64
                        audio_bytes = base64.b64decode(audio_data)
                    except:
                        raise ValueError("无法解析音频数据格式")
            elif isinstance(audio_data, bytes):
                audio_bytes = audio_data
            else:
                raise ValueError(f"未知的音频数据类型: {type(audio_data)}")
            
            # 验证音频数据完整性
            if not audio_bytes or len(audio_bytes) < 1000:
                raise ValueError("音频数据过小，可能不完整")
            
            # 保存音频文件
            with open(filepath, 'wb') as f:
                f.write(audio_bytes)
            
            # 验证文件完整性
            if filepath.stat().st_size < 1000:
                raise ValueError("生成的音频文件过小")
            
            print(f"✅ 语音生成完成: {filepath} ({len(audio_bytes)} bytes)")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ 语音生成失败: {e}")
            raise
    
    def synthesize_dialogue(
        self, 
        dialogue: List[Tuple[str, str]], 
        model: str = "speech-2.5-hd-preview"
    ) -> List[str]:
        """合成对话音频
        
        Args:
            dialogue: [(voice_id, text), ...] 的对话列表
            model: 语音模型
            
        Returns:
            生成的音频文件路径列表
        """
        audio_files = []
        
        for i, (voice_id, text) in enumerate(dialogue):
            try:
                # 添加延迟避免API频率限制
                import time
                if i > 0:
                    time.sleep(1.5)
                    
                filename = f"dialogue_{i+1}_{voice_id}.mp3"
                filepath = self.synthesize_text(
                    text=text,
                    voice_id=voice_id,
                    model=model,
                    filename=filename
                )
                audio_files.append(filepath)
                
            except Exception as e:
                print(f"对话片段 {i+1} 生成失败: {e}")
                # 使用备用方案
                fallback_voice = "female-chengshu"
                filepath = self.synthesize_text(
                    text=text,
                    voice_id=fallback_voice,
                    model=model,
                    filename=f"dialogue_{i+1}_fallback.mp3"
                )
                audio_files.append(filepath)
        
        return audio_files
    
    def batch_synthesize(
        self, 
        texts: List[str], 
        voices: List[str],
        model: str = "speech-2.5-hd-preview"
    ) -> List[str]:
        """批量合成语音
        
        Args:
            texts: 文本列表
            voices: 音色列表（循环使用）
            model: 语音模型
            
        Returns:
            音频文件路径列表
        """
        audio_files = []
        
        for i, text in enumerate(texts):
            voice_id = voices[i % len(voices)]
            try:
                filepath = self.synthesize_text(
                    text=text,
                    voice_id=voice_id,
                    model=model,
                    filename=f"batch_{i+1}_{voice_id}.mp3"
                )
                audio_files.append(filepath)
            except Exception as e:
                print(f"批量合成第{i+1}个失败: {e}")
                continue
        
        return audio_files
    
    def get_voice_info(self, voice_id: str) -> Dict:
        """获取音色信息"""
        return {
            "voice_id": voice_id,
            "name": self.OFFICIAL_VOICES.get(voice_id, "未知音色"),
            "is_official": voice_id in self.OFFICIAL_VOICES
        }
    
    def list_available_voices(self) -> Dict[str, str]:
        """列出可用音色"""
        return self.OFFICIAL_VOICES.copy()
    
    def estimate_duration(self, text: str, speed: float = 1.0) -> float:
        """估算文本朗读时长（秒）
        
        Args:
            text: 文本内容
            speed: 语速系数
            
        Returns:
            估算时长（秒）
        """
        # 中文字符平均每分钟约200-250字
        char_count = len(text)
        base_duration = char_count / 200  # 分钟
        return base_duration * 60 / speed  # 转换为秒，考虑语速
    
    def validate_voice_id(self, voice_id: str) -> bool:
        """验证音色ID是否有效"""
        return voice_id in self.OFFICIAL_VOICES
    
    def get_recommended_voices(self, scene: str, count: int = 1) -> List[str]:
        """根据场景推荐音色"""
        recommendations = {
            "solo": ["female-chengshu", "presenter_female", "audiobook_female_1"],
            "dialogue": ["male-qn-jingying", "female-yujie"],
            "panel": ["male-qn-jingying", "female-chengshu", "male-qn-daxuesheng"],
            "news": ["presenter_male", "presenter_female"],
            "storytelling": ["audiobook_female_1", "audiobook_male_1"],
            "interview": ["presenter_male", "female-yujie"]
        }
        
        voices = recommendations.get(scene, ["female-chengshu"])
        return voices[:count]
    
    def cleanup_temp_files(self, file_paths: List[str]):
        """清理临时语音文件"""
        for filepath in file_paths:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"🗑️ 已清理: {filepath}")
            except Exception as e:
                print(f"清理文件失败 {filepath}: {e}")