# AGENTS.md - Development Guide for Agentic Coding Assistants

## Build/Test Commands

### Installation
```bash
python setup.py                    # One-click install all dependencies
pip install -r requirements.txt    # Manual install
```

### Running Tests
```bash
python test_simple.py               # Run all tests
python -m pytest test_simple.py    # Run with pytest (if installed)
```

### Running the Application
```bash
python minimax_cli.py --interactive  # Interactive mode
python minimax_cli.py -c "hello"     # Chat example
python minimax_cli.py --help          # Show all CLI options
```

## Code Style Guidelines

### File Structure
- **Shebang**: `#!/usr/bin/env python3` for all executable scripts
- **Encoding**: `# -*- coding: utf-8 -*-` for UTF-8 support
- **Docstrings**: Triple-quoted docstrings at module and function level
- **Single file preferred**: This codebase uses a monolithic architecture (minimax_cli.py ~3000 lines)

### Imports
```python
# Standard library first
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Third-party imports
import requests
import base64
import mimetypes
import argparse
```

### Type Hints
- Use type hints for all function parameters and return values
- Prefer explicit types over generic ones when possible
- Use `Optional[T]` for nullable types
- Example:
```python
def chat(self, message: str, model: str = "M2-her",
         temperature: float = 1.0, max_tokens: int = 1024,
         use_anthropic_api: bool = False) -> str:
```

### Naming Conventions
- **Classes**: `PascalCase` - `MiniMaxClient`, `FileManager`
- **Functions/Methods**: `snake_case` - `chat()`, `image()`, `video_status()`
- **Variables**: `snake_case` - `file_path`, `audio_data`, `task_id`
- **Constants**: `UPPER_SNAKE_CASE` (when applicable)
- **Private methods**: `_prefix` - `_setup_credentials()`, `_request()`

### Error Handling
```python
# Always validate parameters and raise ValueError with descriptive messages
if len(prompt) > 1500:
    raise ValueError(f"描述过长，最多支持1500字符，当前{len(prompt)}字符")

if not Path(file_path).exists():
    raise ValueError(f"文件不存在: {file_path}")

# Use try-except for external operations
try:
    response = requests.post(url, headers=headers, json=data, timeout=60)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.Timeout:
    raise Exception("请求超时，请检查网络连接")
except Exception as e:
    raise Exception(f"操作失败: {str(e)}")
```

### Logging and Output
- Use the `_log()` method for consistent output formatting
- Use emojis for visual clarity: `🚀`, `✅`, `❌`, `⚠️`, `💡`
- Log levels: INFO (default), WARN, ERROR
- Example:
```python
self._log(f"🚀 开始生成图像...")
self._log(f"⚠️ 参数警告", "WARN")
self._log(f"❌ 操作失败: {e}", "ERROR")
```

### API Request Pattern
- All API calls should go through the unified `_request()` method
- Handle `base_resp.status_code != 0` as errors
- Implement 3-retry mechanism with exponential backoff
- Example:
```python
response = self._request("POST", "image_generation", json=data)
if 'base_resp' in response and response['base_resp']['status_code'] != 0:
    raise Exception(f"API错误: {response['base_resp']['status_msg']}")
```

### Method Organization
In MiniMaxClient class, methods appear in this order:
1. `__init__` and setup methods
2. Core AI generation methods (chat, image, video, music, tts)
3. File management methods (upload, list, retrieve, download, delete)
4. Voice management methods (list_voices, voice_clone, voice_design)
5. Helper methods (_log, _request, _process_image_input, etc.)

### Code Documentation
- Docstrings should follow Google-style or similar
- Include parameter descriptions with type information
- Document return values and possible exceptions
- Example:
```python
def voice_clone(self, file_id: int, voice_id: str,
                prompt_audio: int = None, prompt_text: str = None) -> Dict[str, Any]:
    """音色快速复刻

    Args:
        file_id: 待复刻音频的 file_id（通过上传文件获得，purpose=voice_clone）
        voice_id: 克隆音色的ID，长度范围[8,256]，首字符必须为英文字母
        prompt_audio: 示例音频的 file_id（通过上传文件获得，purpose=prompt_audio）
        prompt_text: 示例音频的对应文本

    Returns:
        包含 demo_audio 试听链接等信息的字典
    """
```

### Configuration Management
- Store API credentials in `~/.minimax_ai/config.json`
- Support environment variables: `MINIMAX_GROUP_ID`, `MINIMAX_API_KEY`
- Use interactive setup wizard for first-time users
- Never hardcode credentials

### Output File Management
- Use `FileManager` class for saving generated content
- Organize outputs in `./output/` subdirectories: audio/, images/, videos/, music/, podcasts/
- Generate timestamped filenames: `tts_20260203_143025.mp3`
- Handle both URL and hex/Base64 formats appropriately

## Key Architecture Decisions

1. **Monolithic Design**: All functionality in single minimax_cli.py file (~3000 lines)
2. **Unified API Client**: Centralized `_request()` method handles authentication and retries
3. **Smart Parameter Resolution**: Model-specific validation in each method
4. **Progressive Enhancement**: Fallback handling for different API response formats
5. **Caching Strategy**: Voice list cached for 2 hours to reduce API calls

## Testing Strategy

- Use simple test files (e.g., test_simple.py)
- Test API connectivity before complex operations
- Mock external dependencies when writing unit tests
- Test both success and error paths

## Special Notes for AI Agents

- **No inline comments**: Codebase is intentionally concise
- **No garbage code**: Keep implementations minimal and focused
- **User experience first**: Provide clear error messages and usage hints
- **Emoji-enhanced output**: Use emojis for better CLI UX
- **Chinese language**: Documentation and user-facing text in Chinese
