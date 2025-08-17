#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniMax AI 安装脚本
"""

import subprocess
import sys
from pathlib import Path

def install():
    """一键安装"""
    print("🚀 安装MiniMax AI...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ 安装完成！")
    print("使用方法:")
    print("  python minimax_cli.py --interactive")
    print("  python minimax_cli.py --chat '你好'")

if __name__ == "__main__":
    install()