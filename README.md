# MiniMax AI 统一工具包 🚀

一个用户友好的MiniMax AI API封装工具，提供统一的命令行界面，支持智能对话、图像生成、视频制作、音乐创作和语音克隆等功能。

## ✨ 功能特性

- **🎯 统一界面** - 告别20+个零散脚本，一个工具搞定所有功能
- **💬 智能对话** - 基于MiniMax官方API，支持最新MiniMax-Text-01和MiniMax-M1模型（最大token数1,000,192）
- **🎨 AI绘画** - 文本生成高质量图像，支持多种宽高比
- **🎬 视频制作** - 文本生成视频内容，实时进度显示
- **🎵 音乐创作** - 根据歌词生成原创音乐，支持参考音色
- **🎤 语音克隆** - 快速复刻任意音色，支持试听功能
- **📁 文件管理** - 自动生成目录结构，统一管理所有内容
- **🎮 交互友好** - 彩色界面、进度条、智能提示、错误处理
- ⚙️ **零配置启动** - 首次使用自动引导API配置
- 🛡️ **健壮性** - 完善的错误处理和重试机制

## 🚀 快速开始

### 1. 安装

```bash
# 克隆项目
git clone <your-repo-url>
cd MiniMax-AI

# 一键安装
python setup.py
```

### 2. 配置API密钥

首次运行时会自动引导配置：
- Group ID
- API Key

配置信息会保存在 `~/.minimax_env`

### 3. 使用方式

#### 一键启动 (Windows用户)
```bash
# 双击 start.bat 直接启动交互界面
# 或命令行运行：
python start.bat
```

#### 交互模式 (推荐)
```bash
python minimax_cli.py --interactive
# 或简写
python minimax_cli.py -i
```

#### 命令行模式
```bash
# 智能对话 (支持中文)
python minimax_cli.py --chat "你好，请介绍一下MiniMax AI"

# 图像生成
python minimax_cli.py --image "一只在月光下跳舞的猫，水墨画风格"

# 视频生成
python minimax_cli.py --video "一只熊猫在竹林中散步，卡通风格"

# 音乐生成
python minimax_cli.py --music "写一首关于春天的歌"

# 语音克隆
python minimax_cli.py --clone
```

## 🎯 交互模式使用指南

### 主菜单
启动交互模式后，会看到功能菜单：

```
请选择功能:
  💬 智能对话
  🎨 图像生成
  🎬 视频生成
  🎵 音乐生成
  🎤 语音克隆
  📁 文件管理
  ❌ 退出
```

### 功能示例

#### 💬 智能对话
- 支持4种模型选择：abab6.5s-chat/6.5-chat/5.5s-chat/5.5-chat
- 连续对话，保持上下文
- 实时显示用量统计
- 输入 `exit` 或 `退出` 返回主菜单

#### 🎨 图像生成
- 输入图像描述
- 选择宽高比 (1:1, 16:9, 9:16, 4:3)
- 选择生成数量 (1-4张)
- 显示生成图像的URL和保存路径

#### 🎬 视频生成
- 输入视频描述
- 实时显示生成进度 (准备中/队列中/生成中/完成)
- 完成后提供下载链接和本地保存

#### 🎵 音乐生成
- 输入歌词或描述
- 支持参考音色和风格选择
- 自动播放和保存MP3文件

#### 🎤 语音克隆
- 输入音频文件ID进行音色复刻
- 支持试听功能
- 生成个性化语音

## 📁 文件管理

所有生成的内容会自动保存到：
```
~/minimax_outputs/
├── images/          # 生成的图像
├── videos/          # 生成的视频
├── music/           # 生成的音乐
├── voices/          # 克隆的语音
└── logs/            # 操作日志
```

## 🔧 高级配置

### 环境变量
```bash
export MINIMAX_GROUP_ID="your_group_id"
export MINIMAX_API_KEY="your_api_key"
```

### 自定义保存路径
在 `~/.minimax_config` 中配置：
```json
{
    "output_dir": "/custom/path",
    "auto_save": true,
    "max_history": 100
}
```

## 🛠️ 开发指南

### 项目结构
```
MiniMax-AI/
├── minimax_cli.py      # 主程序
├── setup.py           # 安装脚本
├── requirements.txt   # 依赖列表
├── README.md          # 说明文档
└── legacy/            # 原始脚本（备份）
```

### 添加新功能
1. 在 `MiniMaxClient` 类中添加方法
2. 在交互界面中添加对应菜单
3. 更新命令行参数解析

### 依赖安装
```bash
pip install -r requirements.txt
```

## 🐛 常见问题

### Q: 首次运行提示缺少依赖
A: 运行 `python setup.py` 自动安装

### Q: API调用失败
A: 检查网络连接和API密钥配置

### Q: 生成的文件在哪里
A: 默认保存在 `~/minimax_outputs/`

### Q: 如何更新
A: 直接拉取最新代码，依赖通常向后兼容

## 📞 技术支持

- 提交Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 文档更新: 欢迎PR改进文档
- 功能建议: 通过Issue提交新功能需求

## 📝 更新日志

### v2.0.0 (当前)
- ✅ **重大更新**: 从20+个零散脚本升级为统一CLI工具
- ✅ **官方API**: 基于MiniMax官方文档，支持abab全系列模型
- ✅ **用户体验**: 彩色界面、进度条、智能提示
- ✅ **零配置**: 首次使用自动引导API配置
- ✅ **双重模式**: 交互模式和命令行模式
- ✅ **错误处理**: 完善的异常处理和用户提示
- ✅ **文件管理**: 自动生成目录结构，统一管理输出
- ✅ **跨平台**: 支持Windows一键启动

### v1.0.0 (历史)
- 原始零散脚本版本

### 开发计划
- [ ] 批量处理功能
- [ ] 模板系统
- [ ] Web界面
- [ ] 插件系统
- [ ] 云端同步
- [ ] 语音对话模式

---

**享受AI创作的乐趣吧！** 🎉