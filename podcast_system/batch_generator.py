"""
批量播客生成模块
支持一次生成多个播客主题
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

class BatchPodcastGenerator:
    """批量播客生成器"""
    
    def __init__(self, podcast_generator):
        """初始化批量生成器
        
        Args:
            podcast_generator: PodcastGenerator实例
        """
        self.generator = podcast_generator
        self.results = []
        
    def generate_batch(
        self,
        topics: List[Dict],
        max_workers: int = 3,
        output_dir: str = None
    ) -> List[Dict]:
        """批量生成播客
        
        Args:
            topics: 主题列表，每个主题包含：
                {
                    "topic": "主题内容",
                    "scene": "solo/dialogue/panel",
                    "duration": 分钟数,
                    "voices": [音色列表],
                    "output_filename": 可选输出文件名
                }
            max_workers: 最大并发数
            output_dir: 输出目录
            
        Returns:
            生成结果列表
        """
        print(f"🚀 开始批量生成 {len(topics)} 个播客...")
        
        if output_dir:
            self.generator.output_dir = Path(output_dir)
            self.generator.output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_topic = {
                executor.submit(self._generate_single, topic): topic
                for topic in topics
            }
            
            # 收集结果
            for future in as_completed(future_to_topic):
                topic = future_to_topic[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"✅ 完成: {topic.get('topic', '未知主题')}")
                except Exception as e:
                    print(f"❌ 失败: {topic.get('topic', '未知主题')} - {e}")
                    results.append({
                        "topic": topic.get("topic"),
                        "status": "failed",
                        "error": str(e)
                    })
        
        # 生成报告
        self._generate_report(results)
        
        print(f"📊 批量生成完成: {len([r for r in results if r['status'] == 'success'])}/{len(topics)} 成功")
        return results
    
    def _generate_single(self, topic_config: Dict) -> Dict:
        """生成单个播客"""
        try:
            # 验证参数
            if not self.generator.validate_inputs(
                topic=topic_config.get("topic", ""),
                scene=topic_config.get("scene", "solo"),
                duration=topic_config.get("duration", 5),
                voices=topic_config.get("voices")
            ):
                raise ValueError("参数验证失败")
            
            # 估算生成时间
            estimated_time = self.generator.estimate_generation_time(
                topic_config.get("duration", 5)
            )
            
            # 生成播客
            start_time = datetime.now()
            
            output_file = self.generator.generate_podcast(
                topic=topic_config.get("topic"),
                scene=topic_config.get("scene", "solo"),
                duration=topic_config.get("duration", 5),
                voices=topic_config.get("voices"),
                output_filename=topic_config.get("output_filename")
            )
            
            end_time = datetime.now()
            actual_time = (end_time - start_time).total_seconds()
            
            return {
                "topic": topic_config.get("topic"),
                "scene": topic_config.get("scene", "solo"),
                "duration": topic_config.get("duration", 5),
                "output_file": output_file,
                "status": "success",
                "estimated_time": estimated_time,
                "actual_time": actual_time,
                "file_size": os.path.getsize(output_file) if output_file else 0
            }
            
        except Exception as e:
            return {
                "topic": topic_config.get("topic"),
                "status": "failed",
                "error": str(e)
            }
    
    def generate_from_file(self, config_file: str, max_workers: int = 3) -> List[Dict]:
        """从配置文件批量生成
        
        Args:
            config_file: JSON配置文件路径
            max_workers: 最大并发数
            
        Returns:
            生成结果列表
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            topics = config.get("topics", [])
            output_dir = config.get("output_dir")
            
            return self.generate_batch(topics, max_workers, output_dir)
            
        except Exception as e:
            print(f"❌ 读取配置文件失败: {e}")
            return []
    
    def save_batch_config(self, topics: List[Dict], output_file: str = None) -> str:
        """保存批量配置到文件
        
        Args:
            topics: 主题配置列表
            output_file: 输出配置文件路径
            
        Returns:
            配置文件路径
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"batch_config_{timestamp}.json"
        
        config = {
            "created_at": datetime.now().isoformat(),
            "topics": topics,
            "total_count": len(topics),
            "description": "播客批量生成配置"
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 配置文件已保存: {output_file}")
        return output_file
    
    def create_sample_batch_config(self) -> str:
        """创建示例批量配置"""
        sample_topics = [
            {
                "topic": "AI如何改变我们的日常生活",
                "scene": "solo",
                "duration": 5,
                "voices": ["female-chengshu"]
            },
            {
                "topic": "远程工作的利与弊",
                "scene": "dialogue",
                "duration": 8,
                "voices": ["male-qn-jingying", "female-yujie"]
            },
            {
                "topic": "2024年科技趋势展望",
                "scene": "panel",
                "duration": 12,
                "voices": ["male-qn-jingying", "female-chengshu", "presenter_male"]
            },
            {
                "topic": "健康饮食的新观念",
                "scene": "interview",
                "duration": 10,
                "voices": ["presenter_female", "female-chengshu"]
            }
        ]
        
        return self.save_batch_config(sample_topics)
    
    def _generate_report(self, results: List[Dict]) -> str:
        """生成批量生成报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"batch_report_{timestamp}.json"
        
        success_count = len([r for r in results if r.get("status") == "success"])
        failed_count = len([r for r in results if r.get("status") == "failed"])
        
        total_time = sum([r.get("actual_time", 0) for r in results if r.get("status") == "success"])
        total_size = sum([r.get("file_size", 0) for r in results if r.get("status") == "success"])
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_topics": len(results),
                "successful": success_count,
                "failed": failed_count,
                "success_rate": success_count / len(results) if results else 0,
                "total_generation_time": total_time,
                "total_file_size": total_size
            },
            "details": results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📊 详细报告已保存: {report_file}")
        return report_file
    
    def get_progress_summary(self, results: List[Dict]) -> Dict:
        """获取进度摘要"""
        success_count = len([r for r in results if r.get("status") == "success"])
        failed_count = len([r for r in results if r.get("status") == "failed"])
        
        return {
            "total": len(results),
            "successful": success_count,
            "failed": failed_count,
            "success_rate": f"{success_count/len(results)*100:.1f}%" if results else "0%"
        }