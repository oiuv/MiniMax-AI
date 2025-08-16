"""
音乐创作模块
基于MiniMax音乐API生成背景音乐
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
from .models.podcast_config import PodcastScene, MusicStyle

class MusicCreator:
    """背景音乐创作器"""
    
    # 音乐风格模板
    MUSIC_TEMPLATES = {
        MusicStyle.ELECTRONIC: {
            "prompt": "现代电子音乐，科技氛围，轻快节奏，适合工作场景",
            "lyrics": """[Intro]
电子节拍轻轻响起
[Verse]
科技的光芒照亮前方
创新的力量改变世界
我们在数字时代前行
[Chorus]
科技让生活更美好
未来由我们创造
[Bridge]
每一次创新都是进步
[Outro]
科技之光永远闪耀"""
        },
        MusicStyle.FOLK: {
            "prompt": "治愈民谣，温暖柔和，生活感悟，适合日常聆听",
            "lyrics": """[Intro]
吉他声轻轻响起
[Verse]
生活就像一首歌
有高潮也有低谷
我们在平凡中寻找美好
[Chorus]
温暖就在心中
幸福其实很简单
[Bridge]
感受生活的每一份感动
[Outro]
温柔时光静静流淌"""
        },
        MusicStyle.CLASSICAL: {
            "prompt": "轻古典音乐，优雅宁静，知识氛围，适合学习场景",
            "lyrics": """[Intro]
钢琴旋律优雅响起
[Verse]
知识如河流般流淌
智慧的光芒照亮前方
我们在学习中不断成长
[Chorus]
知识让世界更精彩
思考让人生更丰富
[Bridge]
每一次学习都是收获
[Outro]
优雅与智慧同行"""
        },
        MusicStyle.POP: {
            "prompt": "流行音乐，青春活力，积极向上，适合年轻人",
            "lyrics": """[Intro]
动感节拍活力四射
[Verse]
青春是最美的时光
梦想在心中闪耀
我们在奋斗中前行
[Chorus]
青春充满无限可能
梦想就在不远方
[Bridge]
活力让我们更强大
[Outro]
阳光永远灿烂辉煌"""
        },
        MusicStyle.AMBIENT: {
            "prompt": "氛围音乐，平和宁静，专注背景，适合冥想放松",
            "lyrics": """[Intro]
平和音乐缓缓流淌
[Verse]
宁静的氛围包围着我
专注让心灵更纯净
我们在平静中找到力量
[Chorus]
平和让思考更深入
宁静让心灵更宽广
[Bridge]
感受内心的每一份平静
[Outro]
平和心境永远相伴"""
        }
    }
    
    # 场景音乐映射
    SCENE_MUSIC_MAPPING = {
        PodcastScene.SOLO: MusicStyle.FOLK,
        PodcastScene.DIALOGUE: MusicStyle.POP,
        PodcastScene.PANEL: MusicStyle.ELECTRONIC,
        PodcastScene.NEWS: MusicStyle.CLASSICAL,
        PodcastScene.STORYTELLING: MusicStyle.FOLK,
        PodcastScene.INTERVIEW: MusicStyle.AMBIENT
    }
    
    def __init__(self, client, output_dir: str = None):
        """初始化音乐创作器
        
        Args:
            client: MiniMaxClient实例
            output_dir: 输出目录
        """
        self.client = client
        self.output_dir = Path(output_dir) if output_dir else Path("output/temp")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_background_music(
        self,
        topic: str,
        duration: int,
        scene: PodcastScene = None,
        style: MusicStyle = None,
        filename: str = None
    ) -> str:
        """创建背景音乐
        
        Args:
            topic: 播客主题
            duration: 播客时长(分钟)
            scene: 播客场景
            style: 音乐风格(可选)
            filename: 输出文件名
            
        Returns:
            生成的音乐文件路径
        """
        # 确定音乐风格
        if style is None:
            style = self.SCENE_MUSIC_MAPPING.get(scene, MusicStyle.AMBIENT)
        
        # 根据主题生成个性化提示
        personalized_prompt = self._generate_personalized_prompt(topic, style)
        personalized_lyrics = self._generate_personalized_lyrics(topic, style)
        
        # 计算音乐时长(播客时长的70%用于背景音乐)
        music_duration = min(duration * 0.7 * 60, 90)  # 不超过90秒
        
        try:
            # 调用音乐生成API（使用正确歌词）
            audio_data = self.client.generate_music(
                prompt=personalized_prompt,
                lyrics=personalized_lyrics
            )
            
            # 生成文件名
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_topic = topic[:15].replace(' ', '_').replace('/', '_')
                filename = f"bgm_{style.value}_{safe_topic}_{timestamp}.mp3"
            
            filepath = self.output_dir / filename
            
            # 处理音频数据
            if isinstance(audio_data, str):
                audio_bytes = bytes.fromhex(audio_data)
            else:
                audio_bytes = audio_data
            
            # 保存音乐文件
            with open(filepath, 'wb') as f:
                f.write(audio_bytes)
            
            return str(filepath)
            
        except Exception as e:
            print(f"❌ 背景音乐创建失败: {e}")
            raise
    
    def create_intent_music(self, intent: str, filename: str = None) -> str:
        """基于意图创建音乐
        
        Args:
            intent: 音乐意图描述
            filename: 输出文件名
            
        Returns:
            生成的音乐文件路径
        """
        try:
            print(f"🎵 正在创建意图音乐: {intent}")
            
            # 生成对应的歌词
            lyrics = self._generate_lyrics_from_intent(intent)
            
            audio_data = self.client.generate_music(
                prompt=intent,
                lyrics=lyrics
            )
            
            # 生成文件名
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_intent = intent[:15].replace(' ', '_').replace('/', '_')
                filename = f"intent_{safe_intent}_{timestamp}.mp3"
            
            filepath = self.output_dir / filename
            
            # 处理音频数据
            if isinstance(audio_data, str):
                audio_bytes = bytes.fromhex(audio_data)
            else:
                audio_bytes = audio_data
            
            # 保存音乐文件
            with open(filepath, 'wb') as f:
                f.write(audio_bytes)
            
            print(f"✅ 意图音乐创建完成: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ 意图音乐创建失败: {e}")
            raise
    
    def _generate_personalized_prompt(self, topic: str, style: MusicStyle) -> str:
        """生成个性化音乐提示
        
        Args:
            topic: 播客主题
            style: 音乐风格
            
        Returns:
            个性化音乐提示
        """
        base_template = self.MUSIC_TEMPLATES[style]
        
        # 根据主题关键词调整
        topic_lower = topic.lower()
        
        # 主题关键词映射
        keywords_mapping = {
            "科技": "科技,现代,创新",
            "商业": "商务,专业,成功", 
            "生活": "生活,日常,温馨",
            "教育": "教育,学习,成长",
            "娱乐": "娱乐,轻松,快乐",
            "情感": "情感,温暖,治愈",
            "新闻": "新闻,正式,权威"
        }
        
        additional_keywords = ""
        for keyword, music_desc in keywords_mapping.items():
            if keyword in topic_lower:
                additional_keywords = music_desc
                break
        
        return f"{base_template['prompt']},{additional_keywords}"
    
    def _generate_personalized_lyrics(self, topic: str, style: MusicStyle) -> str:
        """生成个性化歌词
        
        Args:
            topic: 播客主题
            style: 音乐风格
            
        Returns:
            个性化歌词
        """
        base_lyrics = self.MUSIC_TEMPLATES[style]["lyrics"]
        
        # 根据主题生成个性化歌词
        safe_topic = topic[:20]  # 限制长度
        
        # 生成主题相关的歌词
        personalized_lyrics = f"""[Intro]
关于{safe_topic}的美好音乐
[Verse]
让我们一起聊聊{safe_topic}
这个话题如此有趣
{base_lyrics}"""
        
        return personalized_lyrics
    
    def _generate_lyrics_from_intent(self, intent: str) -> str:
        """从意图生成歌词
        
        Args:
            intent: 音乐意图
            
        Returns:
            生成的歌词
        """
        return f"""[Intro]
背景音乐开始
[Verse]
{intent}的氛围
[Bridge]
音乐与主题融合
[Outro]
音乐渐渐结束"""
    
    def get_music_duration_estimate(self, podcast_duration: int) -> int:
        """计算背景音乐时长
        
        Args:
            podcast_duration: 播客时长(分钟)
            
        Returns:
            背景音乐时长(秒)
        """
        # 背景音乐时长为播客时长的70%，但不超过90秒
        bgm_duration = min(int(podcast_duration * 0.7 * 60), 90)
        return max(bgm_duration, 30)  # 最少30秒
    
    def list_music_styles(self) -> Dict[str, str]:
        """列出可用音乐风格"""
        return {
            style.value: template["prompt"].split(',')[0]
            for style, template in self.MUSIC_TEMPLATES.items()
        }
    
    def get_scene_music_recommendation(self, scene: PodcastScene) -> MusicStyle:
        """获取场景推荐的音乐风格"""
        return self.SCENE_MUSIC_MAPPING.get(scene, MusicStyle.AMBIENT)
    
    def create_music_for_scene(
        self, 
        topic: str, 
        scene: PodcastScene, 
        duration: int, 
        filename: str = None
    ) -> str:
        """为特定场景创建音乐
        
        Args:
            topic: 主题
            scene: 场景
            duration: 时长
            filename: 文件名
            
        Returns:
            音乐文件路径
        """
        style = self.get_scene_music_recommendation(scene)
        return self.create_background_music(
            topic=topic,
            duration=duration,
            scene=scene,
            style=style,
            filename=filename
        )
    
    def cleanup_music_files(self, file_paths: List[str]):
        """清理音乐文件"""
        for filepath in file_paths:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"🗑️ 已清理音乐文件: {filepath}")
            except Exception as e:
                print(f"清理音乐文件失败 {filepath}: {e}")