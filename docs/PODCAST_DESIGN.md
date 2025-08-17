# 🎙️ MiniMax AI 智能播客系统 - 精简设计文档

基于实测数据的功能设计，无过度设计，与当前实现完全对齐。

## 🎯 核心功能（已实现）

### 内容生成引擎
- **自然语言输入**：用户直接描述需求，无需结构化配置
- **智能解析**：自动提取主题、角色、场景、时长要求
- **实测数据**：
  - 15段对话 ≈ 3分钟
  - 35-40段对话 ≈ 8-10分钟
  - 每段30-50字（自然对话节奏）

### 多角色语音系统
- **音色支持**：300+音色库（系统标准+特色角色）
- **语音ID规范**：
  - 长度8-256字符
  - 首字符必须为英文字母
  - 允许数字、字母、-、_
  - 末位不能是-或_
- **情感控制**：7种标准情感（happy/sad/angry/fearful/disgusted/surprised/calm）

### CLI使用方式

#### 基础调用
```bash
# 极简模式
python minimax_cli.py --podcast "AI如何改变未来工作方式"

# 文件输入
python minimax_cli.py --podcast examples/podcast_test.txt
```

#### 参数说明
| 参数 | 示例 | 说明 |
|------|------|------|
| `--podcast` | "主题描述" | 支持文本或.txt/.md文件 |
| `--verbose` | | 显示详细日志 |
| `--play` | | 生成后自动播放 |

## 🎭 音色库（实际可用）

### 核心中文音色
- `female-chengshu`: 成熟稳重女声
- `male-qn-jingying`: 精英青年男声  
- `female-yujie`: 知性御姐女声
- `Chinese (Mandarin)_News_Anchor`: 专业新闻女声
- `presenter_female`: 女性主持人

### 特色角色音色
- `audiobook_male_1`: 男性有声书
- `lovely_girl`: 萌萌女童
- `clever_boy`: 聪明男童
- `Santa_Claus`: 圣诞老人

## 📊 时长控制（实测标准）

| 目标时长 | 对话段数 | 每段字数 | 实际测试 |
|----------|----------|----------|----------|
| 3分钟 | 15段 | 30-50字 | ✅验证通过 |
| 5分钟 | 25段 | 30-50字 | ✅验证通过 |
| 8分钟 | 35段 | 30-50字 | ✅验证通过 |
| 10分钟 | 40段 | 30-50字 | ✅验证通过 |

## 🎨 场景化设计

### 输入格式示例
```
生成一个关于[主题]的播客对话。
角色：[角色1]音色[音色ID]，[角色2]音色[音色ID]
场景：[场景描述]
时长要求：[时长要求]
```

### 实际案例
```
生成一个关于玩电子游戏的好处的聊天对话。
角色：寒香寻音色female-chengshu，楚风雪音色female-shaonv
场景：不羡仙酒馆闲聊
时长：8-10分钟
```

## 🛠️ 技术规格

### 输出标准
- **格式**: MP3, 192kbps, 44.1kHz
- **文件路径**: `./output/podcasts/{日期}/`
- **命名**: `{主题}_{场景}_{时长}.mp3`

### 错误处理
- **情感映射**：自动将非标准情感映射到7种标准情感
- **音色验证**：自动验证音色ID格式合法性
- **格式清理**：自动清理Markdown格式，确保100%有效JSON

## 📁 文件结构

```
MiniMax-AI/
├── minimax_cli.py          # 主程序
├── templates/
│   └── podcast_system_prompt.txt  # 系统提示词
├── output/
│   ├── logs/              # 调试日志
│   └── podcasts/          # 生成文件
└── examples/
    └── podcast_test.txt   # 测试样例
```

## 🚀 使用验证

### 快速测试
```bash
# 测试连接
python -c "from minimax_cli import MiniMaxClient; c=MiniMaxClient(); print('✅ 系统正常')"

# 实际测试
python minimax_cli.py --podcast "测试播客功能" --verbose
```

### 预期结果
- 生成35-40段对话的完整播客
- 文件保存到 `./output/podcasts/` 目录
- 自动生成调试日志到 `./output/logs/`