"""
内容生成模块
基于MiniMax AI生成播客脚本内容
"""

import json
from typing import List, Dict, Tuple, Optional
from .models.podcast_config import PodcastConfig, PodcastScene

class ContentGenerator:
    """播客内容生成器"""
    
    # 场景提示模板
    SCENE_PROMPTS = {
        PodcastScene.SOLO: {
            "prompt": "你是一位专业的单人播客主播，请围绕{topic}创作一期{duration}分钟的播客节目。",
            "style": "亲切自然，像朋友聊天，温暖有深度",
            "structure": "开场白(30秒) → 主题引入(1分钟) → 深度分析(主体) → 总结思考(1分钟) → 温暖结尾(30秒)"
        },
        PodcastScene.DIALOGUE: {
            "prompt": "你是一个专业的双人对话播客，由{speaker_names}两位主播主持，请围绕{topic}进行{duration}分钟的对话讨论。",
            "style": "观点碰撞，互动自然，轻松有趣",
            "structure": "共同开场 → 观点分享 → 深入讨论 → 共同总结"
        },
        PodcastScene.PANEL: {
            "prompt": "你是一个专业的{speaker_count}人圆桌讨论，由{speaker_names}共同主持，请围绕{topic}进行{duration}分钟的专业讨论。",
            "style": "专业深入，观点多元，逻辑清晰",
            "structure": "主持人开场 → 嘉宾观点1 → 嘉宾观点2 → 嘉宾观点3 → 互动讨论 → 总结"
        },
        PodcastScene.NEWS: {
            "prompt": "你是一位专业新闻主播，请围绕{topic}进行{duration}分钟的新闻播报和解读。",
            "style": "正式权威，语速适中，信息准确",
            "structure": "新闻导语 → 事件详情 → 背景分析 → 影响解读 → 总结"
        },
        PodcastScene.STORYTELLING: {
            "prompt": "你是一位专业故事讲述者，请围绕{topic}创作一个{duration}分钟的情感故事。",
            "style": "情感丰富，节奏舒缓，画面感强",
            "structure": "故事开场 → 情节发展 → 高潮冲突 → 温暖结局 → 感悟分享"
        },
        PodcastScene.INTERVIEW: {
            "prompt": "你是一个专业访谈节目，主持人采访嘉宾关于{topic}，时长{duration}分钟。",
            "style": "专业提问，深入交流，自然对话",
            "structure": "开场介绍 → 背景了解 → 深入提问 → 观点碰撞 → 总结感谢"
        }
    }
    
    def __init__(self, client):
        """初始化内容生成器
        
        Args:
            client: MiniMaxClient实例
        """
        self.client = client
    
    def generate_script(self, config: PodcastConfig, role_names: List[str] = None) -> str:
        """生成播客脚本
        
        Args:
            config: 播客配置
            role_names: 角色名称列表，与speakers一一对应
            
        Returns:
            生成的播客脚本
        """
        scene_config = self.SCENE_PROMPTS[config.scene]
        speaker_count = len(config.speakers) if config.speakers else 1
        
        # 设置角色名称
        if role_names and len(role_names) == len(config.speakers):
            speaker_names = "和".join(role_names)
        else:
            # 使用默认角色名称
            if config.scene == PodcastScene.DIALOGUE:
                speaker_names = "李明和小雅"
            elif config.scene == PodcastScene.PANEL:
                speaker_names = "主持人李明、专家小雅和嘉宾"
            else:
                speaker_names = "主播"
        
        # 构建提示
        prompt = f"""{scene_config['prompt'].format(
            topic=config.topic,
            duration=config.duration,
            speaker_count=speaker_count,
            speaker_names=speaker_names
        )}

要求：
1. 风格：{scene_config['style']}
2. 结构：{scene_config['structure']}
3. 时长：{config.duration}分钟播客内容
4. 语言：自然口语化，避免书面语
5. 内容：围绕"{config.topic}"主题
6. 节奏：适合音频播报，段落清晰
7. 角色：使用"{speaker_names}"作为对话中的称呼

输出格式：
直接输出播客文本内容，不要添加任何格式标记或标题。
确保内容完整，适合{config.duration}分钟播报。
"""
        
        try:
            response = self.client.chat_completion(
                message=prompt,
                model=config.model_text
            )
            
            if not response or not response.strip():
                return self._get_fallback_script(config)
                
            return response.strip()
            
        except Exception as e:
            print(f"内容生成失败: {e}")
            return self._get_fallback_script(config)
    
    def split_dialogue(self, script: str, config: PodcastConfig) -> List[Tuple[str, str]]:
        """将脚本分割为对话段落
        
        Args:
            script: 完整脚本
            config: 播客配置
            
        Returns:
            [(speaker_id, text), ...] 的对话列表
        """
        speakers = [s.voice_id for s in config.speakers]
        if not speakers:
            # 使用默认音色
            if config.scene == PodcastScene.SOLO:
                speakers = ["female-chengshu"]
            elif config.scene == PodcastScene.DIALOGUE:
                speakers = ["male-qn-jingying", "female-yujie"]
            elif config.scene == PodcastScene.PANEL:
                speakers = ["male-qn-jingying", "female-chengshu", "male-qn-daxuesheng"]
            else:
                speakers = ["presenter_male"]
        
        # 计算内容量：每分钟约200字
        expected_chars = config.duration * 200
        actual_chars = len(script)
        
        if actual_chars > expected_chars * 1.5:
            # 内容过多，按比例截断
            script = script[:expected_chars]
            print(f"⚠️  内容过长，已截断至{expected_chars}字符")
        
        if len(speakers) == 1:
            # 单人播客 - 分割为多个短段落
            short_paragraphs = self._split_into_short_segments(script, max_length=250)
            return [(speakers[0], para) for para in short_paragraphs if para.strip()]
        
        # 多人播客 - 智能分割并维护角色对应关系
        # 首先尝试从脚本内容中识别说话人
        dialogue = self._parse_dialogue_with_roles(script, speakers)
        
        if not dialogue:
            # 如果无法识别角色，使用智能分配确保角色一致性
            cleaned_script = self._remove_speaker_prefixes(script)
            paragraphs = self._split_into_dialogue_segments(cleaned_script, len(speakers))
            dialogue = []
            
            # 使用智能角色分配：根据段落内容特点分配角色
            # 确保每个说话人按固定顺序发言，保持voice-speaker对应关系
            for i, para in enumerate(paragraphs):
                if para.strip():
                    # 使用固定顺序分配，确保角色与voice_id一一对应
                    # 按提供的音色顺序循环分配对话段落
                    speaker_idx = i % len(speakers)
                    speaker_id = speakers[speaker_idx]
                    dialogue.append((speaker_id, para.strip()))
        
        return dialogue

    def _parse_dialogue_with_roles(self, script: str, speakers: List[str]) -> List[Tuple[str, str]]:
        """从脚本中解析角色对话
        
        Args:
            script: 完整脚本内容
            speakers: 说话人列表
            
        Returns:
            [(speaker_id, text)] 的对话列表
        """
        import re
        
        dialogue = []
        lines = script.split('\n')
        
        # 尝试识别对话格式
        role_patterns = [
            r'^([\u4e00-\u9fff]+)：(.+)$',  # 李明：内容
            r'^([A-Z])：(.+)$',           # A：内容
            r'^主播[ABC]：(.+)$',         # 主播A：内容
            r'^([\u4e00-\u9fff]+)说：(.+)$',  # 李明说：内容
        ]
        
        current_speaker_idx = 0
        current_text = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            matched = False
            for pattern in role_patterns:
                match = re.match(pattern, line)
                if match:
                    # 找到角色标识，处理之前的内容
                    if current_text.strip():
                        speaker_id = speakers[current_speaker_idx % len(speakers)]
                        cleaned_text = self._remove_speaker_prefixes(current_text.strip())
                        if cleaned_text:
                            dialogue.append((speaker_id, cleaned_text))
                        current_speaker_idx += 1
                    
                    # 处理当前行
                    speaker_name = match.group(1) if len(match.groups()) > 1 else match.group(0)
                    content = match.group(2) if len(match.groups()) > 1 else match.group(1)
                    
                    speaker_id = speakers[current_speaker_idx % len(speakers)]
                    cleaned_content = self._remove_speaker_prefixes(content)
                    if cleaned_content:
                        dialogue.append((speaker_id, cleaned_content))
                    current_speaker_idx += 1
                    
                    matched = True
                    break
            
            if not matched:
                # 没有角色标识，累积到当前文本
                if current_text:
                    current_text += " " + line
                else:
                    current_text = line
        
        # 处理最后累积的内容
        if current_text.strip():
            speaker_id = speakers[current_speaker_idx % len(speakers)]
            cleaned_text = self._remove_speaker_prefixes(current_text.strip())
            if cleaned_text:
                dialogue.append((speaker_id, cleaned_text))
        
        return dialogue
    
    def _split_into_short_segments(self, text: str, max_length: int = 250) -> List[str]:
        """将长文本分割为短片段，适合语音合成"""
        segments = []
        current_segment = ""
        
        # 按句子分割
        sentences = text.replace('。', '。|').replace('！', '！|').replace('？', '？|').split('|')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_segment + sentence) <= max_length:
                if current_segment:
                    current_segment += " " + sentence
                else:
                    current_segment = sentence
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = sentence
                else:
                    # 单句太长，强制截断
                    segments.append(sentence[:max_length])
                    
        if current_segment:
            segments.append(current_segment)
            
        return segments
    
    def _remove_speaker_prefixes(self, text: str) -> str:
        """移除对话中的角色前缀，防止在语音合成中被读出"""
        import re
        
        # 移除常见的角色前缀格式
        # 匹配模式：李明：, 主播A：, A：, 小雅说：等
        patterns = [
            r'^\s*[A-Z]\s*：\s*',           # A：, B：
            r'^\s*[\u4e00-\u9fff]+\s*：\s*',  # 李明：, 小雅：
            r'^\s*主播[ABC]\s*：\s*',      # 主播A：, 主播B：
            r'^\s*[\u4e00-\u9fff]+说[：:]\s*',  # 李明说：, 小雅说：
            r'^\s*[A-Z]说[：:]\s*',       # A说：, B说：
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                for pattern in patterns:
                    line = re.sub(pattern, '', line)
                cleaned_lines.append(line)
        
        # 同时处理单行内的角色标签
        combined_text = ' '.join(cleaned_lines)
        for pattern in patterns:
            combined_text = re.sub(pattern, '', combined_text, flags=re.MULTILINE)
        
        return combined_text.strip()

    def _split_into_dialogue_segments(self, text: str, speaker_count: int) -> List[str]:
        """将文本分割为对话段落"""
        # 按段落分割，确保每个说话人2-3句话
        sentences = text.replace('。', '。|').replace('！', '！|').replace('？', '？|').split('|')
        segments = []
        
        # 每个说话人轮流说2-3句
        sentences_per_turn = 2
        current_segment = ""
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if i % sentences_per_turn == 0 and current_segment:
                segments.append(current_segment)
                current_segment = sentence
            else:
                if current_segment:
                    current_segment += " " + sentence
                else:
                    current_segment = sentence
        
        if current_segment:
            segments.append(current_segment)
            
        return segments
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """将文本分割为段落"""
        # 按换行符分割
        lines = text.split('\n')
        paragraphs = []
        current_para = ""
        
        for line in lines:
            line = line.strip()
            if line:
                if len(line) < 20:  # 短行可能是标题或分隔
                    if current_para:
                        paragraphs.append(current_para)
                        current_para = ""
                else:
                    if current_para:
                        current_para += " " + line
                    else:
                        current_para = line
        
        if current_para:
            paragraphs.append(current_para)
        
        # 如果段落太少，按句子分割
        if len(paragraphs) < 3:
            sentences = text.replace('。', '。|').replace('！', '！|').replace('？', '？|').split('|')
            paragraphs = [s.strip() for s in sentences if s.strip()]
        
        return paragraphs
    
    def _get_fallback_script(self, config: PodcastConfig) -> str:
        """获取备用脚本"""
        scene_name = config.scene.value
        topic = config.topic
        
        fallback_scripts = {
            PodcastScene.SOLO: f"""
大家好，欢迎收听本期播客。今天我们要聊的话题是{topic}。

在这个信息爆炸的时代，{topic}已经成为我们生活中不可忽视的一部分。
让我来为你深入分析这个话题。

首先，我们来看看{topic}对我们日常生活的实际影响。
无论是工作还是生活，这个主题都在悄悄地改变着我们的行为方式。

接下来，我想分享几个关于{topic}的有趣观点和案例。
这些真实的经历或许能让你对这个话题有更深的理解。

最后，让我们一起思考：面对{topic}带来的变化，
我们应该如何更好地适应和利用这些新的可能性。

感谢大家收听本期播客，希望这些内容对你有所启发。
我们下期再见！
""",
            PodcastScene.DIALOGUE: f"""
李明：大家好，欢迎收听本期对话播客，我是李明。

小雅：大家好，我是小雅，今天我们聊的话题是{topic}。

李明：没错，这个话题最近真的很火，我也一直在关注相关的讨论。

小雅：那我们就从最基本的开始吧，你觉得{topic}对我们最大的影响是什么？

李明：从我的观察来看，主要是改变了我们的生活习惯和思维方式。

小雅：确实如此，我也有类似的感受。不过我还想补充一点...

李明：小雅的这个观点很有意思，让我想到另一个角度...

小雅：今天的讨论很精彩，让我们总结一下今天的要点。

李明：感谢大家的收听，我们下期再见！
""",
            PodcastScene.NEWS: f"""
各位听众大家好，欢迎收听本期新闻播客。
今天我们要关注的话题是{topic}。

首先来看事件背景。{topic}近期引发了广泛关注，
这背后反映出了怎样的社会现象？

根据我们的了解，{topic}的发展经历了几个重要阶段。
从最初的探索到如今的普及应用，这个过程充满了挑战与机遇。

专家分析认为，{topic}的未来发展将呈现以下趋势：
技术创新将推动应用场景的不断拓展。

以上就是本期新闻播客的全部内容，感谢您的收听。
"""
        }
        
        return fallback_scripts.get(config.scene, fallback_scripts[PodcastScene.SOLO])
    
    def generate_content_summary(self, topic: str) -> Dict:
        """生成内容摘要用于背景音乐选择"""
        prompt = f"""请为播客主题"{topic}"生成一个简短的内容摘要，用于选择合适的背景音乐风格。

输出格式：
主题类型: [技术/生活/商业/娱乐/教育]
情绪基调: [轻松/严肃/温暖/激动/治愈]
适用场景: [工作/学习/休闲/运动]
关键词: [3-5个关键词]

请保持简洁，每行一个信息。"""
        
        try:
            response = self.client.chat_completion(
                message=prompt,
                model="MiniMax-Text-01"            )
            
            # 解析响应
            lines = response.strip().split('\n')
            summary = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    summary[key.strip()] = value.strip()
            
            return summary
            
        except Exception as e:
            print(f"内容摘要生成失败: {e}")
            return {
                "主题类型": "生活",
                "情绪基调": "温暖",
                "适用场景": "休闲",
                "关键词": "日常,轻松,有趣"
            }