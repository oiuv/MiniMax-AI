# MiniMax AI 开发指导文档

该文档为AI开发者提供MiniMax API的核心技术规格和接口信息。

## 🔗 核心接口汇总

### 1. 文本生成（聊天）
**接口**: 文本-文本生成（聊天）  
**文档**: https://platform.minimaxi.com/document/对话?key=66701d281d57f38758d581d0  
**基础URL**: https://api.minimax.chat/v1

### 2. 语音合成
**同步接口**: https://platform.minimaxi.com/document/同步语音合成?key=66719005a427f0c8a5701643  
**异步接口**: https://platform.minimaxi.com/document/异步长文本语音合成?key=66b3559f290299a26b2347d2

### 3. 语音克隆
**快速复刻**: https://platform.minimaxi.com/document/快速复刻?key=66719032a427f0c8a570165b  
**音色设计**: https://platform.minimaxi.com/document/voice_design?key=669f5af198ff2c57eeb9a0f0

### 4. 视频生成
**视频生成**: https://platform.minimaxi.com/document/video_generation?key=66d1439376e52fcee2853049  
**视频生成Agent**: https://platform.minimaxi.com/document/template?key=68747c38b9b3965c7e4f72da

### 5. 音乐生成
**接口**: https://platform.minimaxi.com/document/Music%20Generation?key=667cd92e3be2027f69b723dd

### 6. 图像生成
**接口**: https://platform.minimaxi.com/document/vffrKguXhEQoELeH2hVECJnd?key=67b03bdcdd0f18b80647241

### 7. 文件管理
**接口**: https://platform.minimaxi.com/document/file?key=6685458335a2d55137ca9681

## 🤖 最新模型列表（2025年8月6日更新）

### 文本模型
- **MiniMax-M1**: 全球领先，80K思维链 × 1M输入
- **MiniMax-Text-01**: 全新架构，支持1M超长上下文

### 语音模型
- **speech-2.5-hd-preview**: 最新的HD模型（2025年8月6日发布），韵律表现出色，复刻相似度极佳
- **speech-2.5-turbo-preview**: 最新的Turbo模型（2025年8月6日发布），支持40个语种
- **speech-02-hd**: 出色韵律和稳定性，音质突出
- **speech-02-turbo**: 小语种能力增强
- **speech-01-hd**: 超高复刻相似度
- **speech-01-turbo**: 快速生成

### 视频模型
- **MiniMax-Hailuo-02**: 1080P超清，10秒视频
- **T2V-01-Director**: 文生视频导演版
- **I2V-01-Director**: 图生视频导演版
- **I2V-01-live**: 卡通/漫画风格增强
- **S2V-01**: 主体参考视频生成

### 图片模型
- **image-01**: 细腻画面，支持文生图/图生图
- **image-01-live**: 手绘/卡通画风增强

### 音乐模型
- **music-1.5**: 支持音乐描述和歌词生成
- **music-01**: 支持上传音乐文件生成

## ⚙️ 技术参数

### 通用配置
- **认证方式**: Bearer Token
- **基础URL**: https://api.minimax.chat/v1
- **超时设置**: 30-60秒
- **重试次数**: 3次

### 文本生成参数
- **max_tokens**: 100-2048
- **temperature**: 0.1-2.0
- **top_p**: 0.1-1.0
- **对话模式**: 单轮/多轮
- **流式输出**: 支持

### 语音合成参数
- **音频格式**: mp3, wav, pcm, aac
- **采样率**: 8kHz, 16kHz, 24kHz, 48kHz
- **语速**: 0.5-2.0倍速
- **音量**: 0.1-2.0倍

### 图像生成参数
- **分辨率**: 1024x1024, 1024x1792, 1792x1024
- **生成数量**: 1-4张
- **负面提示**: 支持
- **风格控制**: 支持

### 视频生成参数
- **分辨率**: 1080P
- **时长**: 5-10秒
- **镜头控制**: 推镜/拉镜/摇镜/移镜
- **风格**: 写实/卡通/漫画/手绘/赛博朋克

## 🛠️ 开发环境

### 必需环境变量
```bash
export MINIMAX_GROUP_ID="your_group_id"
export MINIMAX_API_KEY="your_api_key"
```

### 快速测试
```bash
# 测试API连接
curl -X POST https://api.minimax.chat/v1/text/chatcompletion \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"MiniMax-Text-01","messages":[{"role":"user","content":"测试"}]}'
```

---

**最后更新**: 2025年8月15日  
**文档版本**: 2.0 (开发专用版)