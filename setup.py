#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniMax AI 安装脚本
支持 pip 和 uv 两种安装方式
"""

import subprocess
import sys
from pathlib import Path
import sys

def install_with_pip():
    """使用 pip 安装"""
    print("🚀 使用 pip 安装 MiniMax AI...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ 安装完成！")

def install_with_uv():
    """使用 uv 安装"""
    print("🚀 使用 uv 安装 MiniMax AI...")
    try:
        # 检查 uv 是否已安装
        subprocess.run(["uv", "--version"], check=True, capture_output=True, text=True)
    except FileNotFoundError:
        print("❌ uv 命令未找到，请先安装 uv：")
        print("   Windows: winget install astral-sh.uv")
        print("   macOS: brew install uv")
        print("   Linux: cargo install uv")
        return False

    # 创建虚拟环境并安装依赖
    subprocess.run(["uv", "venv"], check=True)
    subprocess.run(["uv", "pip", "install", "-r", "requirements.txt"], check=True)
    print("✅ 安装完成！")
    print("使用方法:")
    print("  uv run python minimax_cli.py --interactive")
    print("  uv run python minimax_cli.py --chat '你好'")
    return True

def install():
    """一键安装（自动检测安装方式）"""
    # 检查是否使用 uv 环境
    if "VIRTUAL_ENV" in sys.environ and "uv" in sys.executable:
        install_with_uv()
    else:
        # 询问用户选择安装方式
        print("请选择安装方式：")
        print("1. 使用 pip（系统 Python）")
        print("2. 使用 uv（推荐，创建独立虚拟环境）")
        choice = input("请输入 1 或 2：").strip()

        if choice == "1":
            install_with_pip()
        elif choice == "2":
            install_with_uv()
        else:
            print("❌ 无效选择")
            return False

        print("\n使用方法:")
        if choice == "1":
            print("  python minimax_cli.py --interactive")
            print("  python minimax_cli.py --chat '你好'")
        else:
            print("  uv run python minimax_cli.py --interactive")
            print("  uv run python minimax_cli.py --chat '你好'")

    return True

if __name__ == "__main__":
    install()