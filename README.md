# MiniMax AI 工具包 🚀

功能完整的MiniMax AI统一命令行工具，支持所有最新AI功能，包括语音克隆、图像/视频/音乐生成、播客系统等。

## 🚀 快速开始

### 安装方式

#### 1. 传统方式（pip）
```bash
# 一键安装
python setup.py

# 或手动安装
pip install -r requirements.txt
```

#### 2. 现代方式（uv，推荐）
uv 是一个快速、现代的 Python 包管理器，提供更好的依赖管理和虚拟环境体验。

```bash
# 安装 uv（首次使用）
# Windows: winget install astral-sh.uv
# macOS: brew install uv
# Linux: cargo install uv

# 使用 uv 运行项目（自动管理依赖和虚拟环境）
uv run python minimax_cli.py --interactive
```

### 使用方式

#### 🌐 Web UI 模式（推荐，新手友好）
全新的图形化界面，支持所有功能，无需记忆命令参数。

```bash
# 直接启动Web UI
python minimax_web.py

# 或通过CLI启动
python minimax_cli.py --web

# 生成公网分享链接（可远程访问）
python minimax_web.py --share

# uv 方式
uv run python minimax_web.py
```

启动后访问 http://localhost:7860 即可使用。

#### 交互模式
```bash
# 传统方式
python minimax_cli.py --interactive

# uv 方式
uv run python minimax_cli.py --interactive
```

#### 命令行模式
```bash
# ========== 智能对话（支持最新 MiniMax-M2.1 系列）==========
# 基础对话（默认使用 MiniMax-M2.1 模型）
python minimax_cli.py -c "你好，MiniMax"

# 高级对话 - 使用 Anthropic API 兼容接口
python minimax_cli.py -c "解释量子计算" --anthropic-api --show-thinking

# 自定义系统提示词和温度
python minimax_cli.py -c "写一首关于春天的诗" \
    --chat-model MiniMax-M2.1 \
    --system-prompt "你是一位专业的诗人" \
    --temperature 0.9 \
    --max-tokens 2048

# 使用极速模型
python minimax_cli.py -c "快速回答: 1+1等于几?" --chat-model M2.1-lightning

# ========== 图像生成（支持高级参数）==========
python minimax_cli.py -i "樱花树下的猫" --n 2 --aspect-ratio 16:9

# 高级图像生成（新模型支持）
python minimax_cli.py -i "可爱的卡通人物" --image-model image-01-live --style-type 漫画
# 自定义尺寸生成
python minimax_cli.py -i "风景画" --width 1024 --height 768 --prompt-optimizer
# Base64格式输出
python minimax_cli.py -i "现代艺术" --response-format base64 --n 3
# 添加水印和风格
python minimax_cli.py -i "水彩画风格的山水" --style-type 水彩 --style-weight 0.9 --add-watermark

# 图生图（基于参考图片生成）
python minimax_cli.py -i2i person.jpg "该人物穿着古装，在古代建筑前"
# 图生图与风格化结合
python minimax_cli.py -i2i portrait.jpg "动漫风格的人物" --image-model image-01-live --style-type 漫画
# 高级图生图
python minimax_cli.py -i2i photo.jpg "油画风格的艺术肖像" --n 2 --seed 12345 --add-watermark

# 视频生成（支持运镜控制）
python minimax_cli.py -v "熊猫在竹林中漫步[推进]" --video-model MiniMax-Hailuo-2.3
# 导演模型（专业运镜）
python minimax_cli.py -v "主角[左摇]看夕阳，然后[拉远]显示全景" --video-model T2V-01-Director
# 镜头序列控制
python minimax_cli.py -v "动作场景" --camera-sequence '[{"action":"推进","timing":"开始"},{"action":"晃动","timing":"打斗"}]'
# 高质量长视频
python minimax_cli.py -v "自然风景[上升]俯瞰" --video-duration 10 --video-resolution 1080P --fast-preprocessing

# 图生视频（让静态图片动起来）
python minimax_cli.py -i2v image.jpg "人物开始微笑和眨眼" --i2v-model I2V-01-Director
# 卡通风格增强
python minimax_cli.py -i2v cartoon.png "角色开始跳舞" --i2v-model I2V-01-live
# 高质量图生视频
python minimax_cli.py -i2v photo.jpg "镜头[推进]展示细节" --i2v-model MiniMax-Hailuo-2.3 --i2v-duration 10

# 首尾帧视频生成（图片到图片的过渡动画）
python minimax_cli.py -se start.jpg end.jpg
# 高清首尾帧视频
python minimax_cli.py -se start.jpg end.jpg --se-duration 10 --se-resolution 1080P
# 添加水印和回调
python minimax_cli.py -se before.jpg after.jpg --add-watermark --callback-url https://example.com/callback

# 主体参考视频生成（基于人物图片生成视频）
python minimax_cli.py -s2v person.jpg "一个人跑步并微笑"
# 添加水印的高级生成
python minimax_cli.py -s2v character.jpg "角色走向镜头并眨眼" --add-watermark --no-prompt-optimizer

# 音乐生成（music-2.5）
python minimax_cli.py -m "轻松愉快的背景音乐" --lyrics "[Verse]\n阳光洒落\n[Chorus]\n快乐每一天"

# 高级音乐生成（music-2.5新功能）
python minimax_cli.py -m "独立民谣,忧郁,内省,渴望,独自漫步,咖啡馆" --lyrics "[verse]\n街灯微亮晚风轻抚\n[chorus]\n推开木门香气弥漫" --music-watermark
# 高质量音频输出
python minimax_cli.py -m "摇滚音乐,激情,充满力量" --lyrics "[verse]\n吉他声响起\n[chorus]\n燃烧的青春" --music-format wav --music-bitrate 256000 --music-sample-rate 44100
# 流式传输（hex格式）
python minimax_cli.py -m "电子音乐,未来感,科技" --lyrics "未来世界\n代码与梦想" --music-stream

# 文本转语音（支持6个最新模型）
python minimax_cli.py -t "你好，世界" --tts-model speech-2.6-hd --emotion happy --speed 1.2
# 高级语音合成
python minimax_cli.py -t "你好，世界" --format wav --sample-rate 44100 --channel 2
# 流式语音合成
python minimax_cli.py -t "你好，世界" --stream --output-format hex
# 文本规范化+LaTeX公式
python minimax_cli.py -t "公式：$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$" --latex-read --text-normalization
# 使用fluent/whisper情感（仅2.6模型）
python minimax_cli.py -t "生动讲述一个故事" --tts-model speech-2.6-hd --emotion fluent

# 查询音色列表
python minimax_cli.py --list-voices
```

## ✨ 核心功能

| 功能 | 模型 | 描述 |
|---|---|---|
| **智能对话** | MiniMax-M2.5系列 | 最新M2.5/M2.5-lightning，支持Anthropic API，思维链可视化，M2-her角色扮演 |
| **图像生成** | image-01系列 | 支持1-9张图片，多种宽高比，风格控制 |
| **图生图** | image-01系列 | 基于参考图片生成，支持人像character类型 |
| **视频生成** | MiniMax-Hailuo-2.3 | 肢体动作、物理表现与指令遵循能力全面升级 |
| **图生视频** | I2V-01系列 | 静态图片转换为动态视频，支持运镜控制 |
| **首尾帧生成** | MiniMax-Hailuo-02 | 起始到结束图片的过渡动画，高清输出 |
| **主体参考生成** | S2V-01 | 基于人物主体图片生成视频，保持面部特征 |
| **音乐创作** | music-2.5 | 自定义歌词，支持流式传输和多种音频格式，prompt可选 |
| **语音合成** | speech-2.6系列 | 支持6个模型，9种情感，文本规范化，LaTeX朗读 |
| **语音克隆** | voice_clone | 3秒快速克隆音色 |
| **AI播客** | PodcastGenerator | 独立播客生成器，多角色对话、多音色合成 |
| **🌐 Web UI** | Gradio 6.0 | 全功能图形化界面，支持所有AI能力，无需命令行操作 |

## 🌐 Web UI 功能特性

全新的Web界面提供直观易用的操作体验，支持所有MiniMax AI能力：

### 核心功能模块
- **💬 智能对话**：双模型支持（MiniMax-M2.5系列通用模型/M2-her角色扮演模型），支持系统提示词、参数调整、思维链显示
- **🎨 图像生成**：文生图/图生图，支持多种分辨率、风格选择、批量生成
- **🎬 视频生成**：文生视频/图生视频/首尾帧/主体参考，自动状态轮询和视频下载
- **🎵 音频合成**：音乐生成+TTS语音合成，支持音色选择、情感调整、参数自定义
- **🎙️ 播客生成**：自动生成双人对话播客，多音色合成，一键下载
- **📁 文件管理**：文件上传/列表/下载/删除全功能，点击复制ID，自动命名防覆盖
- **🔊 音色管理**：系统音色列表查看、音色克隆、AI音色设计

### 界面优势
- ✅ 宽屏自适应布局，美观易用
- ✅ 所有功能可视化操作，无需记忆命令参数
- ✅ 媒体文件（图片/音频/视频）直接在线预览播放
- ✅ 一键生成公网分享链接，支持远程访问
- ✅ 响应式设计，支持移动端访问

## 🎙️ AI播客生成（独立工具）

播客功能已独立为 `podcast_cli.py`，提供更专业的播客生成体验。

```bash
# 基础播客生成
python podcast_cli.py "人工智能如何改变未来"

# 自定义欢迎语
python podcast_cli.py "AI技术播客" --welcome-text "听众朋友们好，欢迎收听本期节目！"

# 从文件读取主题
python podcast_cli.py topic.txt

# 指定输出目录
python podcast_cli.py topic.txt -o ./my_podcasts
```

### 播客功能特性
- **多角色对话**：支持生成多人对话播客
- **多音色合成**：自动匹配角色音色
- **情感控制**：每段对话可指定情感
- **背景音乐**：自动添加BGM
- **日志保存**：生成过程详细记录

### 文件结构
```
./output/podcasts/
└── podcasts/          # 播客文件
    └── podcast_20240206_120000.mp3
./output/logs/
└── podcast_dialogue_*.json   # 对话内容
└── podcast_error_*.json     # 错误日志
```

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

### 智能对话参数（支持 MiniMax-M2.1 系列）
```bash
python minimax_cli.py -c "对话内容" \
    --chat-model MiniMax-M2.1 \        # 对话模型 [MiniMax-M2.1, MiniMax-M2.1-lightning, MiniMax-M2]
    --system-prompt "你是一个助手" \  # 系统提示词
    --temperature 0.8 \                # 温度参数 (0.0-1.0]，默认1.0
    --max-tokens 2048 \                # 最大生成token数，默认1024
    --anthropic-api \                  # 使用 Anthropic API 兼容接口
    --show-thinking                    # 显示模型思考过程（仅 Anthropic API）

# Anthropic API 兼容模式 - 查看思考过程
python minimax_cli.py -c "解释量子纠缠原理" \
    --anthropic-api \
    --show-thinking \
    --temperature 0.7

# 使用极速模型 M2.1-lightning
python minimax_cli.py -c "快速生成一份代码大纲" \
    --chat-model M2.1-lightning \
    --max-tokens 4096
```

### 对话模型特性
| 模型 | 速度 | 特点 | 适用场景 |
|------|------|------|----------|
| **MiniMax-M2.5** | ~60 tps | 最新一代大模型，能力全面提升，多语言和编程能力更强 | 编程、复杂任务、通用场景 |
| **MiniMax-M2.5-lightning** | ~100 tps | 极速版，响应更快，成本更低 | 快速对话、实时应用 |
| **MiniMax-M2.1** | ~60 tps | 强大多语言能力，编程体验全面升级 | 兼容性需求 |
| **M2-her** | 标准 | 专为对话场景优化，支持角色扮演和情感交流 | 聊天、陪伴、角色扮演 |

### Anthropic API 兼容性说明
- **端点**: `https://api.minimaxi.com/anthropic`
- **支持参数**: model, messages, max_tokens, stream, system, temperature, tool_choice, tools, top_p, thinking, metadata
- **不支持参数**: top_k, stop_sequences, service_tier, mcp_servers, context_management, container
- **消息类型支持**: text, tool_use, tool_result, thinking
- **消息类型不支持**: image, document

### 语音合成参数（支持6个模型）
```bash
python minimax_cli.py -t "文本内容" \
    --tts-model speech-2.6-hd \     # 语音模型 [speech-2.6-hd, speech-2.6-turbo, speech-02-hd, speech-02-turbo, speech-01-hd, speech-01-turbo]
    --voice female-chengshu \       # 音色选择（300+系统音色）
    --emotion happy \               # 情感控制 [happy, sad, angry, fearful, disgusted, surprised, calm, fluent, whisper]
                                    # fluent/whisper 仅对 speech-2.6-hd/speech-2.6-turbo 生效
    --speed 1.2 \                   # 语速 [0.5-2.0]
    --vol 1.5 \                     # 音量 (0, 10]
    --pitch 5 \                     # 语调 [-12到12]
    --format wav \                  # 音频格式 [mp3, pcm, flac, wav]，wav仅非流式
    --sample-rate 44100 \           # 采样率 [8000,16000,22050,24000,32000,44100]
    --bitrate 256000 \              # 比特率 [32000,64000,128000,256000]
    --channel 2 \                   # 声道数 [1,2]
    --stream \                      # 流式输出
    --language-boost Chinese \      # 语言增强（40种语言）
    --subtitle \                    # 启用字幕（仅非流式）
    --output-format hex \           # 输出格式 [hex, url]，流式仅支持hex
    --text-normalization \          # 启用文本规范化（提升数字阅读性能）
    --latex-read \                  # 启用LaTeX公式朗读（公式需用$包裹）
    --force-cbr                     # 使用恒定比特率（仅流式+mp3生效）

# 使用最新模型
python minimax_cli.py -t "你好世界" --tts-model speech-2.6-hd --emotion happy

# 使用fluent情感（生动讲述）
python minimax_cli.py -t "这是一个精彩的故事" --tts-model speech-2.6-hd --emotion fluent

# LaTeX公式朗读
python minimax_cli.py -t "公式是 $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$" --latex-read

# 文本规范化（优化数字阅读）
python minimax_cli.py -t "电话号码是13800138000" --text-normalization
```

### 语音合成模型特性
| 模型 | 特点 | 适用场景 |
|------|------|----------|
| **speech-2.6-hd** | 高质量，支持所有情感包括fluent/whisper | 高质量语音合成、生动讲述 |
| **speech-2.6-turbo** | 快速，支持fluent/whisper | 实时语音合成、快速对话 |
| **speech-02-hd** | 高质量标准模型 | 通用高质量语音 |
| **speech-02-turbo** | 快速标准模型 | 通用快速语音 |
| **speech-01-hd** | 基础高质量 | 兼容性需求 |
| **speech-01-turbo** | 基础快速 | 轻量级应用 |

### 图像生成参数
```bash
python minimax_cli.py -i "描述" \
    --image-model image-01 \          # 图像生成模型 [image-01, image-01-live]
    --n 3 \                           # 生成3张图片
    --aspect-ratio 16:9 \             # 16:9比例 [1:1, 16:9, 4:3, 3:2, 2:3, 3:4, 9:16, 21:9]
    --width 1024 --height 768 \      # 自定义尺寸（仅image-01模型，512-2048且8的倍数）
    --seed 12345 \                    # 固定随机种子
    --response-format url \           # 返回格式 [url, base64]
    --prompt-optimizer \              # 启用prompt优化
    --add-watermark \                 # 添加水印
    --style-type 漫画 \               # 风格类型（仅image-01-live）：[漫画, 元气, 中世纪, 水彩]
    --style-weight 0.8                # 风格权重 (0-1]
```

### 图生图参数
```bash
python minimax_cli.py -i2i reference.jpg "描述" \
    --image-model image-01 \          # 图像生成模型 [image-01, image-01-live]
    --n 2 \                           # 生成2张图片
    --style-type 漫画 \               # 风格类型（仅image-01-live）
    --add-watermark \                 # 添加水印
    --seed 12345 \                    # 固定随机种子
    --response-format url             # 返回格式 [url, base64]
```

### 图生图特性
- **参考类型**: 当前仅支持 character (人像) 类型
- **图片要求**: JPG/JPEG/PNG，小于10MB，建议单人正面照片
- **输入方式**: 本地文件路径或公网URL
- **兼容性**: 与所有图像生成参数兼容（风格、尺寸、优化等）

### 图像模型特性
- **image-01**: 基础模型，支持自定义尺寸、prompt优化、水印
- **image-01-live**: 风格化模型，支持漫画、元气、中世纪、水彩四种风格

### 视频生成参数
```bash
python minimax_cli.py -v "描述" \
    --video-model MiniMax-Hailuo-2.3 \    # 视频生成模型
    --video-duration 6 \                  # 视频时长（秒）
    --video-resolution auto \             # 分辨率 [auto, 720P, 768P, 1080P]
    --first-frame image.jpg \             # 首帧图片
    --last-frame end.jpg \                # 尾帧图片
    --subject-image character.jpg \        # 主体参考图片
    --video-name my_video \               # 视频文件名
    --no-prompt-optimizer \               # 禁用prompt优化
    --fast-preprocessing \                # 快速预处理
    --add-watermark \                     # 添加水印
    --callback-url https://example.com/callback \  # 回调URL
    --camera-sequence '[{"action":"推进","timing":"开始"},{"action":"左摇","timing":"中间"}]' # 镜头序列
```

### 镜头控制（15种运镜指令）
```bash
# 直接在prompt中使用镜头指令
python minimax_cli.py -v "一个人[推进]看书，然后[左摇]看窗外"

# 使用JSON镜头序列
python minimax_cli.py -v "故事场景" \
    --camera-sequence '[{"action":"推进","timing":"开始"},{"action":"固定","timing":"对话"}]'

# 支持的运镜指令
[左移] [右移] [左摇] [右摇] [推进] [拉远]
[上升] [下降] [上摇] [下摇] [变焦推近] [变焦拉远]
[晃动] [跟随] [固定]
```

### 图生视频参数
```bash
python minimax_cli.py -i2v image.jpg "描述" \
    --i2v-model I2V-01-Director \         # 图生视频模型
    --i2v-duration 6 \                    # 视频时长（秒）
    --i2v-resolution auto \               # 分辨率 [auto, 512P, 720P, 768P, 1080P]
    --no-prompt-optimizer \               # 禁用prompt优化
    --fast-preprocessing \                # 快速预处理
    --add-watermark \                     # 添加水印
    --callback-url https://example.com/callback \  # 回调URL
```

### 首尾帧生成参数
```bash
python minimax_cli.py -se start.jpg end.jpg \
    --se-duration 6 \              # 视频时长（秒）[6, 10]
    --se-resolution 768P \         # 分辨率 [768P, 1080P]
    --no-prompt-optimizer \        # 禁用prompt优化
    --add-watermark \              # 添加水印
    --callback-url https://example.com/callback  # 回调URL
```

### 首尾帧生成特性
- **专用模型**: 仅支持 MiniMax-Hailuo-02 模型
- **高分辨率**: 仅支持 768P 和 1080P 高清输出（**不支持 512P**）
- **精确过渡**: 起始图片到结束图片的平滑过渡动画
- **时长限制**: 支持6秒和10秒两种时长（1080P仅支持6秒）
- **图片尺寸**: ⚠️ 生成视频尺寸遵循首帧图片
- **尺寸不一致处理**: ⚠️ 当首帧和尾帧尺寸不一致时，模型将参考首帧对尾帧图片进行裁剪
- **图片要求**: 与图生视频相同的格式和尺寸要求

### 主体参考视频生成参数
```bash
python minimax_cli.py -s2v subject.jpg "描述" \
    --s2v-prompt-optimizer \     # 启用prompt优化（默认启用）
    --no-prompt-optimizer \      # 禁用prompt优化
    --add-watermark \            # 添加水印
    --callback-url https://example.com/callback  # 回调URL
```

### 主体参考视频生成特性
- **专用模型**: 仅支持 S2V-01 模型
- **主体类型**: 当前仅支持 character (人物面部)
- **保持特征**: 生成视频时保持人物面部特征
- **图片要求**: 与图生视频相同的格式和尺寸要求
- **描述限制**: 视频描述最多2000字符

### 音乐生成参数
```bash
python minimax_cli.py -m "独立民谣,忧郁,内省" \
    --music-model music-2.5 \      # 音乐生成模型 [music-2.5]
    --lyrics "[verse]\n街灯微亮晚风轻抚\n[chorus]\n推开木门香气弥漫" \
    --music-stream \               # 启用流式传输（仅支持hex格式）
    --music-format hex \            # 返回格式 [hex, url]，默认hex
    --music-sample-rate 44100 \     # 采样率 [16000, 24000, 32000, 44100]
    --music-bitrate 256000 \        # 比特率 [32000, 64000, 128000, 256000]
    --music-encoding mp3 \          # 音频格式 [mp3, wav, pcm]
    --music-watermark              # 添加音频水印（仅非流式生效）
```

### 音乐生成特性
- **最新模型**: music-2.5，支持更高音乐质量和更丰富风格
- **长度限制**: prompt可选[0, 2000]字符，歌词必填[1, 3500]字符
- **结构标签**: 支持[Intro][Verse][Pre Chorus][Chorus][Interlude][Bridge][Outro][Post Chorus][Transition][Break][Hook][Build Up][Inst][Solo]优化音乐结构
- **输出格式**: 支持hex和url两种格式，url有效期24小时
- **音频质量**: 支持16-44.1kHz采样率，32-256kbps比特率
- **流式传输**: 支持实时生成，hex格式输出
- **水印功能**: 可选择在音频末尾添加水印

### 图生视频模型特性
- **I2V-01-Director**: 导演版，支持15种运镜指令，专业控制
- **I2V-01-live**: 卡通/漫画风格增强，适合动画内容
- **I2V-01**: 基础图生视频模型，稳定可靠
- **MiniMax-Hailuo系列**: 也可用于图生视频，支持更高质量输出

### 图片格式要求
- **支持格式**: JPG, JPEG, PNG, WebP
- **文件大小**: 小于20MB
- **尺寸要求**: 短边像素大于300px，长宽比2:5到5:2之间
- **输入方式**: 本地文件路径、公网URL、Base64 Data URL

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

### 🎤 音色快速复刻
```bash
# 第一步：上传复刻音频（10秒-5分钟，mp3/m4a/wav，≤20MB）
python minimax_cli.py --upload-file voice_sample.mp3 --file-purpose voice_clone
# 输出：文件ID，例如 123456789

# 第二步：执行音色复刻
python minimax_cli.py --clone my_custom_voice --clone-file-id 123456789

# 使用示例音频增强相似度（可选）
python minimax_cli.py --clone my_custom_voice \
    --clone-file-id 123456789 \
    --prompt-audio 987654321 \
    --prompt-text "This voice sounds natural and pleasant."

# 生成试听音频（可选）
python minimax_cli.py --clone my_custom_voice \
    --clone-file-id 123456789 \
    --demo-text "欢迎使用这个全新的音色。" \
    --demo-model speech-2.6-hd

# 开启音频处理
python minimax_cli.py --clone my_custom_voice \
    --clone-file-id 123456789 \
    --noise-reduction \
    --volume-normalization

# 使用新复刻的音色
python minimax_cli.py -t "你好，这是用新音色合成的语音。" --voice my_custom_voice
```

### 音色复刻参数说明
- **--clone**: 自定义音色ID（必填）
  - 长度范围：[8, 256]
  - 首字符必须是英文字母
  - 允许数字、字母、-、_
  - 末位字符不可为 - 或_
- **--clone-file-id**: 复刻音频的文件ID（必填）
- **--prompt-audio**: 示例音频文件ID（可选，用于增强相似度）
- **--prompt-text**: 示例音频对应的文本（需与prompt_audio同时提供）
- **--demo-text**: 试听文本（最多1000字符）
- **--demo-model**: 试听音频模型（默认speech-2.6-hd）
- **--clone-language-boost**: 语言增强（auto, Chinese, English等）
- **--noise-reduction**: 开启音频降噪
- **--volume-normalization**: 开启音量归一化

### 文件要求
**复刻音频**：
- 格式：mp3, m4a, wav
- 时长：10秒 - 5分钟
- 大小：≤20MB

**示例音频**（可选）：
- 格式：mp3, m4a, wav
- 时长：<8秒
- 大小：≤20MB

### 🎨 音色设计（AI生成音色）

通过文本描述生成自定义音色，无需提供音频样本。

```bash
# 基础音色设计（自动生成音色ID）
python minimax_cli.py \
  --design-prompt "声音低沉富有磁性的男播音员" \
  --preview-text "大家好，欢迎收听今天的节目"

# 指定音色ID
python minimax_cli.py \
  --design my narrator_voice \
  --design-prompt "温柔知性的女声，适合讲故事" \
  --preview-text "很久很久以前，有一个美丽的童话故事"

# 添加水印
python minimax_cli.py \
  --design-prompt "充满活力的年轻男声" \
  --preview-text "大家好，我是今天的主持人" \
  --add-watermark

# 使用设计的音色
python minimax_cli.py -t "这是用AI设计的音色合成的语音。" --voice my_narrator_voice
```

### 音色设计参数说明
- **--design**: 目标音色ID（可选，不提供则自动生成）
  - 长度范围：[8, 256]
  - 首字符必须是英文字母
  - 允许数字、字母、-、_
  - 末位字符不可为 - 或_
- **--design-prompt**: 音色描述（必填）
  - 长度范围：[10, 300]
  - 描述声音特征，如年龄、性别、音色、风格等
- **--preview-text**: 试听文本（必填）
  - 长度范围：[10, 300]
  - 将收取2元/万字符费用

### 音色设计提示词建议
```bash
# 男声示例
"声音低沉富有磁性的中年男播音员"
"充满活力的年轻男声，适合体育解说"
"稳重厚重的男声，适合新闻播报"

# 女声示例
"温柔知性的女声，适合讲故事"
"活泼可爱的年轻女声，适合配音"
"清澈甜美的少女音"

# 风格示例
"幽默风趣的脱口秀主持人"
"严肃专业的纪录片旁白"
"亲切温暖的客服声音"
```


## 📖 使用示例

### 基础使用
```python
from minimax_cli import MiniMaxClient

client = MiniMaxClient()

# ========== 智能对话（支持 MiniMax-M2.1）==========
# 基础对话
response = client.chat("介绍一下人工智能的发展历史")
print(response)

# 使用最新模型
response = client.chat(
    "解释量子计算的原理",
    model="MiniMax-M2.1",
    temperature=0.7,
    max_tokens=2048
)
print(response)

# Anthropic API 兼容模式（查看思考过程）
result = client.chat(
    "如何证明勾股定理？",
    model="MiniMax-M2.1",
    use_anthropic_api=True,
    show_thinking=True
)
if isinstance(result, dict):
    print("思考过程:", result['thinking'])
    print("回答:", result['content'])
else:
    print(result)

# 极速模式
response = client.chat(
    "1+1等于几？",
    model="M2.1-lightning"
)
print(response)

# ========== 图像生成（基础）==========
urls = client.image("月光下的猫，水墨画风格", n=2, aspect_ratio="16:9")
for url in urls:
    print(url)

# 高级图像生成
漫画风格_urls = client.image(
    "可爱的卡通人物",
    model="image-01-live",
    n=3,
    style_type="漫画",
    style_weight=0.9,
    aigc_watermark=True
)

自定义尺寸_urls = client.image(
    "风景画",
    model="image-01",
    width=1024,
    height=768,
    prompt_optimizer=True,
    seed=12345
)

# 图生图
portrait_urls = client.image(
    "该人物穿着古装，在古代建筑前",
    model="image-01",
    n=2,
    reference_image="person.jpg",
    aigc_watermark=True
)

# 风格化图生图
漫画风格_urls = client.image(
    "动漫风格的人物",
    model="image-01-live",
    reference_image="portrait.jpg",
    style_type="漫画",
    style_weight=0.9,
    n=3
)

# 生成音乐（基础）
audio = client.music(
    "轻松愉悦的背景音乐",
    "[Verse]\n阳光洒落大地\n[Chorus]\n快乐每一天",
    model="music-2.5"
)
print(f"音乐已生成: {audio}")

# 高级音乐生成（music-2.5新功能）
高质量_audio = client.music(
    "独立民谣,忧郁,内省,渴望,独自漫步,咖啡馆",
    "[verse]\n街灯微亮晚风轻抚\n[chorus]\n推开木门香气弥漫",
    aigc_watermark=True,
    sample_rate=44100,
    bitrate=256000,
    format="wav",
    output_format="url",
    model="music-2.5"
)

# 流式音乐生成
流式音频 = client.music(
    "电子音乐,未来感,科技,节奏感强",
    "未来世界正在到来\n代码与梦想交织\n[Chorus]\n创造新纪元",
    stream=True,
    output_format="hex",
    sample_rate=32000,
    format="mp3",
    model="music-2.5"
)

# 生成播客（使用独立工具）
# python podcast_cli.py "人工智能如何改变未来"

# 首尾帧视频生成
task_id = client.start_end_to_video(
    first_frame_image="start.jpg",
    last_frame_image="end.jpg",
    duration=6,
    resolution="768P"
)
print(f"首尾帧视频已生成: {task_id}")

# 主体参考视频生成
task_id = client.subject_reference_to_video(
    subject_image="person.jpg",
    prompt="A girl runs toward the camera and winks with a smile",
    prompt_optimizer=True,
    aigc_watermark=False
)
print(f"主体参考视频已生成: {task_id}")

# ========== 音色快速复刻 ==========
# 上传复刻音频
upload_result = client.upload_file(
    file_path="voice_sample.mp3",
    purpose="voice_clone"
)
file_id = upload_result.get('file_id')
print(f"音频已上传，文件ID: {file_id}")

# 执行音色复刻
clone_result = client.voice_clone(
    file_id=file_id,
    voice_id="my_custom_voice",
    demo_text="你好，这是我的自定义音色。",
    language_boost="auto",
    need_noise_reduction=True,
    need_volume_normalization=True
)
voice_id = clone_result.get('voice_id')
print(f"音色复刻成功，音色ID: {voice_id}")

# ========== 音色设计（AI生成音色）==========
# 通过文本描述生成音色
design_result = client.voice_design(
    prompt="声音低沉富有磁性的男播音员",
    preview_text="大家好，欢迎收听今天的节目",
    aigc_watermark=False
)
new_voice_id = design_result.get('voice_id')
trial_audio_hex = design_result.get('trial_audio')
print(f"音色设计成功，音色ID: {new_voice_id}")
print(f"试听音频（hex编码）: {len(trial_audio_hex)} 字符")

# 保存试听音频
if trial_audio_hex:
    import binascii
    audio_data = binascii.unhexlify(trial_audio_hex)
    with open("voice_design_trial.mp3", "wb") as f:
        f.write(audio_data)
    print("试听音频已保存到 voice_design_trial.mp3")

# 使用设计的音色进行语音合成
tts_result = client.tts(
    text="这是用AI设计的音色合成的语音。",
    voice_id=new_voice_id,
    model="speech-2.6-hd"
)
print(f"语音已合成: {tts_result}")
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

- **GitHub Issues**: 报告问题和功能请求
- **文档**: 详见 `CLAUDE.md` 开发指导
- **示例**: 查看 `examples/` 目录

简洁、高效、功能完整的MiniMax AI工具包！