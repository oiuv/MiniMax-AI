# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Quick Start Commands

### Environment Setup
```bash
# Install dependencies
python setup.py

# Interactive mode (recommended)
python minimax_cli.py --interactive

# Quick CLI commands
python minimax_cli.py --chat "Hello, MiniMax!"
python minimax_cli.py --list-files  # Test file management
python minimax_cli.py -t "Hello world"  # Test TTS
```

### Configuration
- **API Keys**: Stored in `~/.minimax_ai/config.json` via interactive setup
- **Environment Variables**: `MINIMAX_GROUP_ID`, `MINIMAX_API_KEY`
- **Output Directory**: `~/minimax_outputs/` with auto-categorized subdirectories

## 🏗️ Architecture Overview

### Core Structure
- **minimax_cli.py**: Single-file CLI application containing all functionality (~2400 lines)
- **MiniMaxClient**: Central API client class with unified request handling
- **ArgumentParser**: CLI interface with comprehensive parameter groups
- **File Management**: Automatic output organization in `~/minimax_outputs/`

### Key Design Patterns
- **Unified API Client**: All MiniMax API calls go through `_request()` method
- **Smart Parameter Resolution**: Automatic model-specific parameter validation
- **Progressive Enhancement**: Fallback handling for different API response formats
- **Interactive Setup**: First-run configuration wizard for API credentials

### Request Handling Architecture
```python
# Central request pattern
def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
    # URL construction with GroupId for specific endpoints
    # Bearer token authentication
    # 3-retry mechanism with exponential backoff
    # base_resp status code validation
```

## 🎯 Core MiniMax APIs

### API Endpoint Patterns
- **Base URL**: `https://api.minimaxi.com/v1`
- **Authentication**: Bearer token + GroupId query parameter for specific endpoints
- **Response Format**: JSON with `base_resp` wrapper containing status codes

### Key Model Families
- **Text Generation** (编程/Agent工作流):
  - `MiniMax-M2.1` - 强大多语言编程能力，~60 tps
  - `MiniMax-M2.1-lightning` - 极速版，~100 tps
  - `MiniMax-M2` - 高效编码与 Agent 工作流
  - **API**: Anthropic SDK 兼容 (`/anthropic/v1/messages`)
  - **Features**: Interleaved Thinking, show_thinking

- **Text Chat** (对话/角色扮演):
  - `M2-her` - 专为对话场景优化，支持角色扮演和多轮对话
  - **API**: OpenAI SDK 兼容 (`/v1/text/chatcompletion_v2`)
  - **Features**: user_system, group, sample_message_*

- **Speech**: speech-2.8-hd, speech-2.8-turbo, speech-2.6-hd, speech-2.6-turbo, speech-02-hd, speech-02-turbo
  - **Features**: 40 languages, voice modification, continuous_sound (2.8+), latex_read, subtitle_enable
- **Video**: MiniMax-Hailuo-2.3, T2V-01-Director, I2V-01 series
- **Image**: image-01, image-01-live (with styles)
- **Music**: 
  - `music-2.6` - 文本生成音乐（支持 is_instrumental、lyrics_optimizer）
  - `music-cover` - 翻唱模式（需提供参考音频 audio_url 或 audio_base64）
- **Files**: Upload/list/retrieve/delete management system

### Implementation Critical Points
- **GroupId Handling**: Required for TTS, voice cloning, music generation endpoints
- **Camera Controls**: Video generation supports 15 movement directives in prompt text
- **Resolution Validation**: Different video models support different resolution sets
- **File Purpose Validation**: Strict validation for upload/delete operations

## 🛠️ Development Commands

### Dependencies
```bash
# Install requirements
pip install -r requirements.txt
# Core dependency: requests>=2.28.0
```

### Testing Patterns
```bash
# API connectivity test
python minimax_cli.py --list-files  # Tests auth + file API

# Feature-specific tests
python minimax_cli.py -t "test"  # TTS test
python minimax_cli.py --chat "hello"  # Chat test
```

### Debugging
- **Log Level**: Built-in request/response logging
- **Error Handling**: All API calls return structured error responses
- **Configuration**: Interactive setup for first-time users

## 📁 Key Implementation Files

### Single-File Architecture
- **minimax_cli.py**: Complete CLI application (~2400 lines)
  - MiniMaxClient class with all API methods
  - ArgumentParser with comprehensive CLI groups
  - File management and output handling
  - Interactive mode implementation

### Method Organization (in order of appearance)
```python
# Core infrastructure
class MiniMaxClient:
    def __init__(self)           # Setup and auth
    def _request()              # Unified API caller
    def _setup_credentials()    # Interactive config

# AI Generation methods
    def chat()                  # Text generation (M2-her for dialogue, MiniMax-M2 for general)
    def tts()                   # Text-to-speech (speech-2.6-hd)
    def image()                 # Image generation (image-01)
    def video()                 # Video generation (Hailuo-2.3)
    def music()                 # Music generation (music-2.6 / music-cover)

# File Management (complete CRUD)
    def upload_file()           # Upload with multipart
    def list_files()            # List with pagination
    def retrieve_file()         # Get file details
    def download_file()         # Download binary content
    def delete_file()           # Delete with purpose validation

# Utility methods
    def list_voices()           # Voice catalog
    def podcast()               # Multi-voice generation
```

## 🎯 Implementation Notes

### Critical Implementation Details
- **Response Format Flexibility**: Handles both `data` and `files` keys in API responses
- **Smart Parameter Resolution**: Model-specific parameter validation
- **Base64 Image Processing**: Automatic local file encoding for image inputs
- **File Purpose Validation**: Strict enums for file operations
- **Camera Movement Parsing**: Text-based video direction controls

### CLI Architecture
- **Argument Groups**: Organized by function type (text, image, video, music, files)
- **Help System**: Comprehensive help for all parameters
- **Output Management**: Automatic file organization in categorized directories

### Error Handling Patterns
```python
# Standard API response validation
if 'base_resp' in result and result['base_resp']['status_code'] != 0:
    raise Exception(f"API错误: {result['base_resp']['status_msg']}")

# File operation fallbacks
if 'data' in result and isinstance(result['data'], list):
    files = result['data']
elif 'files' in result and isinstance(result['files'], list):
    files = result['files']
```