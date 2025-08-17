# MiniMax AI 工具包 🚀

功能完整的MiniMax AI统一命令行工具，支持所有最新AI功能，包括播客系统、语音克隆、图像/视频/音乐生成等。

## 🚀 快速开始

### 一键安装
```bash
# 安装所有依赖
python setup.py

# 或手动安装
pip install -r requirements.txt
```

### 使用方式

#### 交互模式（推荐）
```bash
python minimax_cli.py --interactive
```

#### 命令行模式
```bash
# 智能对话
python minimax_cli.py -c "你好，MiniMax"

# 图像生成（支持高级参数）
python minimax_cli.py -i "樱花树下的猫" --n 2 --aspect-ratio 16:9

# 视频生成
python minimax_cli.py -v "熊猫在竹林中漫步"

# 音乐生成（需要歌词）
python minimax_cli.py -m "轻松愉快的背景音乐" --lyrics "[Verse]\n阳光洒落\n[Chorus]\n快乐每一天"

# 文本转语音
python minimax_cli.py -t "你好，世界" --voice female-chengshu

# AI播客生成
python minimax_cli.py -p "人工智能如何改变未来"

# 查询音色列表
python minimax_cli.py --list-voices
```

## ✨ 核心功能

| 功能 | 模型 | 描述 |
|---|---|---|
| **智能对话** | MiniMax-Text-01 | 支持超长上下文，思维链推理 |
| **图像生成** | image-01 | 支持1-9张图片，多种宽高比 |
| **视频生成** | MiniMax-Hailuo-02 | 1080P超清，10秒视频 |
| **音乐创作** | music-1.5 | 自定义歌词，支持多种风格 |
| **语音合成** | speech-2.5-hd-preview | 100+音色，情感控制 |
| **AI播客** | 多模型组合 | 多人对话，多音色播客 |
| **语音克隆** | voice_clone | 3秒快速克隆音色 |

## 📁 文件管理

所有输出自动保存到：
```
./output/
├── audio/          # 语音合成文件
├── images/         # 生成图片
├── videos/         # 生成视频
├── music/          # 生成音乐
└── podcasts/       # 播客文件
```

## ⚙️ 配置

首次使用自动引导配置：
- **API密钥**: 保存在 `~/.minimax_ai/config.json`
- **环境变量**: 也可设置 `MINIMAX_GROUP_ID` 和 `MINIMAX_API_KEY`

## 🎯 高级功能

### 图像生成参数
```bash
python minimax_cli.py -i "描述" \
    --n 3 \                    # 生成3张图片
    --aspect-ratio 16:9 \      # 16:9比例
    --seed 12345              # 固定随机种子
```

### 视频状态管理
```bash
# 提交视频生成
python minimax_cli.py -v "描述"

# 查询状态
python minimax_cli.py -s 任务ID

# 下载视频
python minimax_cli.py --download-video 文件ID
```

### 音色管理
```bash
# 查看所有音色
python minimax_cli.py --list-voices

# 过滤音色
python minimax_cli.py --list-voices --filter-voices "中文"

# 刷新音色缓存
python minimax_cli.py --list-voices --refresh-voices
```

## 📖 使用示例

### 基础使用
```python
from minimax_cli import MiniMaxClient

client = MiniMaxClient()

# 智能对话
response = client.chat("介绍一下人工智能的发展历史")
print(response)

# 生成图片
urls = client.image("月光下的猫，水墨画风格", n=2, aspect_ratio="16:9")
for url in urls:
    print(url)

# 生成音乐
audio = client.music(
    "轻松愉悦的背景音乐",
    "[Verse]\n阳光洒落大地\n[Chorus]\n快乐每一天"
)
print(f"音乐已生成: {audio}")

# 生成播客
podcast = client.podcast("人工智能如何改变未来")
print(f"播客已生成: {podcast}")
```

## 🔧 技术特性

- **统一API**: 所有功能集成在单个CLI工具
- **智能缓存**: 音色列表缓存2小时
- **错误恢复**: 自动重试和降级处理
- **日志系统**: 详细日志和调试模式
- **文件管理**: 自动生成分类目录
- **跨平台**: 支持Windows/macOS/Linux

## 📊 性能指标

- **响应时间**: 5分钟播客 ≤3分钟
- **成功率**: ≥95%
- **音频质量**: 192kbps MP3, 44.1kHz
- **图像质量**: 1080P高清

## 🚀 项目结构

```
MiniMax-AI/
├── minimax_cli.py          # 主CLI程序
├── setup.py               # 一键安装脚本
├── requirements.txt       # 依赖列表
├── start.bat             # Windows一键启动
├── README.md             # 项目说明
├── CLAUDE.md             # 开发指导
├── QWEN.md               # 产品需求
├── .gitignore            # Git忽略规则
├── examples/             # 示例文件
│   ├── tts_story.txt     # TTS测试文本
│   └── prompts/          # 提示词示例
├── output/               # 生成文件
│   ├── audio/
│   ├── images/
│   ├── videos/
│   ├── music/
│   └── podcasts/
└── legacy/               # 备份文件
    └── *.py
```

## 📞 支持

- **GitHub Issues**: 报告问题和功能请求
- **文档**: 详见 `CLAUDE.md` 开发指导
- **示例**: 查看 `examples/` 目录

简洁、高效、功能完整的MiniMax AI工具包！