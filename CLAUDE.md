# CLAUDE.md

该文件为Claude Code (claude.ai/code) 提供本仓库的开发指导。

## 🚀 快速命令

### 环境准备
```bash
# 一键安装依赖
python setup.py

# 交互模式启动（推荐）
python minimax_cli.py --interactive

# 直接功能调用
python minimax_cli.py --chat "你好，MiniMax！"
python minimax_cli.py --image "月光下跳舞的猫，水墨画风格"
python minimax_cli.py --video "竹林中散步的熊猫，卡通风格"
python minimax_cli.py --music "春天的歌"
python minimax_cli.py --clone

# Windows用户一键启动
python start.bat
```

### 环境配置
- **API密钥**: `~/.minimax_env` 存储Group ID和API Key
- **自定义配置**: `~/.minimax_config` JSON格式配置文件
- **输出目录**: `~/minimax_outputs/` 自动生成分类文件夹

## 🏗️ 架构概览

### 核心模块
- **minimax_cli.py**: 统一CLI主程序，集成所有AI功能
- **MiniMaxClient**: 中央API客户端，处理认证、请求和错误
- **Legacy scripts**: 独立功能脚本（备份和调试用途）

### MiniMaxClient核心能力
- **认证管理**: 环境变量自动配置，首次使用引导设置
- **统一请求**: `_make_request()` 方法标准化所有API调用
- **错误处理**: 友好的错误提示和重试机制
- **流式支持**: 支持流式和非流式响应

## 🔗 核心接口文档

### 1. 文本生成（聊天）
- **接口地址**: https://platform.minimaxi.com/document/对话?key=66701d281d57f38758d581d0
- **接口地址**: https://api.minimaxi.com/v1/text/chatcompletion_v2
- **认证方式**: Bearer Token (MINIMAX_API_KEY)
- **模型列表**:
  - **MiniMax-M1**: 全球领先，80K思维链 × 1M输入
  - **MiniMax-Text-01**: 全新架构，支持1M超长上下文

### 2. 语音合成
- **同步接口**: https://api.minimaxi.com/v1/t2a_v2?GroupId={YOUR_GROUP_ID}
- **异步接口**: https://api.minimaxi.com/v1/t2a_async_v2?GroupId={YOUR_GROUP_ID}
- **最新模型** (2025年8月6日发布):
  - **speech-2.5-hd-preview**: 极致相似度，韵律表现出色
  - **speech-2.5-turbo-preview**: 支持40个语种
  - **speech-02-hd**: 出色韵律和稳定性
  - **speech-02-turbo**: 小语种能力增强
  - **speech-01-hd**: 超高复刻相似度
  - **speech-01-turbo**: 快速生成

### 测试规范（必须遵守）
**测试流程：**
1. **用户运行测试**：所有测试必须由用户在真实环境中运行
2. **结果确认**：测试后必须提供明确的成功/失败结果
3. **直接反馈**：不创建无意义的测试脚本

**播客功能测试步骤：**
```bash
# 测试1：基础播客生成
python minimax_cli.py --podcast "AI如何改变未来工作方式"

# 测试2：指定场景和音色
python minimax_cli.py --podcast "科技热点" --scene dialogue --voice male-qn-jingying --voice female-yujie

# 测试3：交互式播客生成
python minimax_cli.py --interactive  # 选择电台播客功能
```

**预期结果：**
- 成功：播客文件保存在 `./podcasts/` 目录
- 失败：提供具体错误信息

### 3. 语音克隆
- **快速复刻**: https://api.minimaxi.com/v1/voice_clone
- **音色设计**: https://api.minimaxi.com/v1/voice_design

### 4. 视频生成
- **视频生成**: https://api.minimaxi.com/v1/video_generation
- **视频生成Agent**: https://api.minimaxi.com/v1/video_template_generation
- **模型列表**:
  - **MiniMax-Hailuo-02**: 1080P超清，10秒视频
  - **T2V-01-Director**: 文生视频导演版
  - **I2V-01-Director**: 图生视频导演版
  - **I2V-01-live**: 卡通/漫画风格增强
  - **S2V-01**: 主体参考视频生成

### 5. 音乐生成
- **接口地址**: https://api.minimaxi.com/v1/music_generation
- **支持模型**: music-1.5, music-01

### 6. 图像生成
- **接口地址**: https://api.minimaxi.com/v1/image_generation
- **支持模型**: image-01, image-01-live

### 7. 文件管理
- **上传接口**: https://api.minimaxi.com/v1/files/upload
- **列出接口**: https://api.minimaxi.com/v1/files/list
- **检索接口**: https://api.minimaxi.com/v1/files/retrieve
- **删除接口**: https://api.minimaxi.com/v1/files/delete
- **下载接口**: https://api.minimaxi.com/v1/files/retrieve_content

## 📦 依赖配置

### 核心依赖
```
requests>=2.28.0      # HTTP客户端
inquirer>=3.1.0       # 交互式提示
rich>=13.0.0          # 终端UI/UX增强
openai>=1.0.0         # OpenAI兼容API
```

### 环境变量
```bash
export MINIMAX_GROUP_ID="your_group_id"
export MINIMAX_API_KEY="your_api_key"
```

## 🗂️ 项目结构

```
MiniMax-AI/
├── minimax_cli.py          # 统一CLI主程序
├── setup.py               # 一键安装脚本
├── requirements.txt       # 依赖列表
├── start.bat             # Windows一键启动
├── CLAUDE.md             # 本开发指导文档
├── QWEN.md               # 产品需求文档
├── README.md             # 用户说明文档
└── legacy/               # 原始独立脚本
    ├── minimax_*.py      # 各功能独立实现
    └── ...
```

## 🔧 开发最佳实践

### 代码风格
- **模块化**: 按功能模块组织代码
- **错误处理**: 用户友好的错误提示
- **配置管理**: 环境变量 + JSON配置文件
- **日志管理**: 详细的操作日志和错误日志

### API集成模式
- **统一封装**: 所有API调用通过MiniMaxClient
- **参数验证**: 输入参数合法性检查
- **重试机制**: 网络异常自动重试
- **结果缓存**: 合理缓存API响应

### 用户体验
- **交互模式**: 彩色界面 + 进度条
- **命令模式**: 简洁的参数解析
- **文件管理**: 自动生成分类目录
- **进度反馈**: 实时状态更新

## 📝 调试技巧

### 快速测试
```bash
# 测试API连接
python -c "from minimax_cli import MiniMaxClient; c=MiniMaxClient(); print('✅ API正常')"

# 测试特定功能
python minimax_cli.py --chat "测试连接" --model MiniMax-Text-01
```

### 日志查看
- **操作日志**: `~/minimax_outputs/logs/`
- **错误日志**: 控制台实时显示 + 文件保存
- **调试模式**: 添加 `--debug` 参数获取详细日志

## 🔄 版本管理
- **当前版本**: v2.1.0 (支持Speech 2.5模型)
- **最后更新**: 2025年8月15日
- **发布日期**: 2025年8月6日 (Speech 2.5模型支持)