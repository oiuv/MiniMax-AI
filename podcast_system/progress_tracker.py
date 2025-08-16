"""
进度追踪模块
提供实时进度显示和状态更新
"""

import time
from typing import Dict, Optional, Callable
from pathlib import Path

class ProgressTracker:
    """播客生成进度追踪器"""
    
    def __init__(self, enable_progress: bool = True):
        """初始化进度追踪器
        
        Args:
            enable_progress: 是否启用进度显示
        """
        self.enable_progress = enable_progress
        self.current_step = 0
        self.total_steps = 6  # 总步骤数
        self.step_names = [
            "内容生成",
            "语音合成",
            "背景音乐",
            "音频混合",
            "质量增强",
            "完成"
        ]
        self.start_time = None
        
    def start(self, topic: str):
        """开始进度追踪"""
        if not self.enable_progress:
            return
        
        self.start_time = time.time()
        print(f"🎙️ 开始生成播客: {topic}")
        print("=" * 50)
        
    def update(self, step_name: str, status: str = "进行中"):
        """更新进度"""
        if not self.enable_progress:
            return
            
        # 找到步骤索引
        try:
            step_index = self.step_names.index(step_name)
            self.current_step = step_index + 1
        except ValueError:
            step_index = self.current_step
            
        progress = (self.current_step / self.total_steps) * 100
        bar_length = 30
        filled_length = int(bar_length * self.current_step // self.total_steps)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        print(f"\r[{bar}] {progress:.0f}% | {step_name}: {status}", end="")
        
    def complete(self, success: bool = True, file_path: str = None):
        """完成进度"""
        if not self.enable_progress:
            return
            
        if success:
            elapsed = time.time() - self.start_time if self.start_time else 0
            print(f"\n✅ 完成！耗时: {elapsed:.1f}秒")
            if file_path:
                print(f"📁 文件: {file_path}")
        else:
            print("\n❌ 生成失败")
            
    def get_estimated_time(self, duration: int) -> str:
        """获取估算时间"""
        base_time = 30
        content_time = duration * 2
        voice_time = duration * 3
        music_time = 60
        mix_time = 30
        
        total_seconds = base_time + content_time + voice_time + music_time + mix_time
        
        if total_seconds < 60:
            return f"{total_seconds}秒"
        elif total_seconds < 3600:
            return f"{total_seconds//60}分钟"
        else:
            return f"{total_seconds//3600}小时{total_seconds%3600//60}分钟"

class SimpleProgressBar:
    """简单进度条（无依赖）"""
    
    def __init__(self, total: int = 100):
        self.total = total
        self.current = 0
        
    def update(self, value: int):
        """更新进度"""
        self.current = value
        percentage = (self.current / self.total) * 100
        bar_length = 20
        filled_length = int(bar_length * self.current // self.total)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(f"\r[{bar}] {percentage:.0f}%", end="")
        
    def finish(self):
        """完成进度"""
        print()

class StepTimer:
    """步骤计时器"""
    
    def __init__(self):
        self.steps = {}
        self.start_time = time.time()
        
    def start_step(self, name: str):
        """开始步骤"""
        self.steps[name] = {"start": time.time()}
        
    def end_step(self, name: str):
        """结束步骤"""
        if name in self.steps:
            self.steps[name]["end"] = time.time()
            self.steps[name]["duration"] = self.steps[name]["end"] - self.steps[name]["start"]
            
    def get_report(self) -> Dict[str, float]:
        """获取步骤报告"""
        return {name: data["duration"] for name, data in self.steps.items() if "duration" in data}