#!/usr/bin/env python3
"""
播客系统使用指南
提供详细的CLI命令和交互式使用说明
"""

import os
from pathlib import Path

def show_podcast_usage():
    """显示播客系统使用指南"""
    
    usage_text = """
🎙️ MiniMax AI 播客系统 - 使用指南

========================================

📋 快速开始

1. 安装依赖
   pip install -r requirements.txt

2. 配置API密钥
   python minimax_cli.py --interactive
   # 按提示输入 Group ID 和 API Key

3. 生成为你的第一个播客
   python minimax_cli.py --podcast "人工智能如何改变生活"

========================================

🚀 CLI命令模式

基础播客生成：
  python minimax_cli.py --podcast "主题内容"

高级参数：
  --scene           播客场景类型
    - solo:        单人主播 (默认)
    - dialogue:    双人对话
    - panel:       多人圆桌
    - news:        新闻播报
    - storytelling: 故事讲述
    - interview:   访谈节目

  --duration        播客时长(分钟，1-30，默认5分钟)
  --voice           自定义音色(可多次使用)
  --music-style     背景音乐风格
    - electronic:  电子音乐
    - folk:        民谣治愈
    - classical:   古典优雅
    - pop:         流行青春
    - ambient:     氛围音乐

  --output          输出文件名
  --no-music        禁用背景音乐(纯语音)
  --no-progress     禁用进度条显示

========================================

🎯 实用示例

# 单人播客 - 3分钟科技主题
python minimax_cli.py --podcast "AI如何改变未来工作方式" --scene solo --duration 3

# 双人对话 - 8分钟深度讨论
python minimax_cli.py --podcast "远程工作的优缺点" --scene dialogue --duration 8 \
  --voice male-qn-jingying --voice female-yujie

# 新闻播报 - 正式风格
python minimax_cli.py --podcast "今日科技资讯" --scene news --duration 2 \
  --music-style classical --output daily_news.mp3

# 无背景音乐播客
python minimax_cli.py --podcast "冥想指导" --scene solo --duration 5 --no-music

========================================

🎨 交互式模式

启动交互界面：
  python minimax_cli.py --interactive

交互流程：
1. 选择 "🎙️ 电台播客"
2. 选择播客场景
3. 输入播客主题
4. 设置时长
5. 选择音色(可选)
6. 选择语音模型
7. 自动生成并播放

========================================

🗣️ 推荐音色组合

单人播客：
  - female-chengshu (成熟女声)
  - male-qn-jingying (精英男声)

双人对话：
  - male-qn-jingying + female-yujie
  - male-qn-daxuesheng + female-chengshu

多人圆桌：
  - male-qn-jingying + female-chengshu + male-qn-daxuesheng

========================================

⚡ 批量生成模式

创建配置文件 batch_config.json:
[
  {
    "topic": "AI助手如何提高效率",
    "scene": "solo",
    "duration": 3,
    "voices": ["female-chengshu"]
  },
  {
    "topic": "远程工作vs办公室工作", 
    "scene": "dialogue",
    "duration": 5,
    "voices": ["male-qn-jingying", "female-yujie"]
  }
]

运行批量生成：
python -c "
from podcast_system.batch_generator import BatchPodcastGenerator
from podcast_system.podcast_generator import PodcastGenerator
from minimax_cli import MiniMaxClient
client = MiniMaxClient()
generator = PodcastGenerator(client)
batch_gen = BatchPodcastGenerator(generator)
import json
with open('batch_config.json') as f:
    configs = json.load(f)
results = batch_gen.generate_batch(configs)
print(f'批量生成完成: {len([r for r in results if r[\"status\"]==\"success\"])}/{len(configs)} 成功')
"

========================================

📁 文件位置

输出目录：
  Windows: C:\Users\\[用户名]\\minimax_outputs\\podcasts\\
  macOS/Linux: ~/minimax_outputs/podcasts/

临时文件：
  output/temp/ - 语音和音乐临时文件

========================================

🔧 故障排除

常见问题：
1. API密钥错误 → 检查 ~/.minimax_env 文件
2. 网络超时 → 检查网络连接，可重试
3. 音乐生成失败 → 使用 --no-music 跳过背景音乐
4. 内存不足 → 降低播客时长或分批生成

调试模式：
  添加环境变量: DEBUG=1 python minimax_cli.py ...

========================================

📞 获取帮助

查看详细文档：
  python -c "import podcast_help; podcast_help.show_podcast_usage()"

查看最新音色列表：
  python -c "
from minimax_cli import MiniMaxClient
from podcast_system.podcast_generator import PodcastGenerator
client = MiniMaxClient()
generator = PodcastGenerator(client)
print('可用音色:', generator.get_available_voices())
"

========================================
    """
    
    print(usage_text)

if __name__ == "__main__":
    show_podcast_usage()