#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniMax AI 工具安装脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """安装依赖"""
    print("正在安装依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def create_alias():
    """创建命令别名"""
    if os.name == 'nt':  # Windows
        # 创建批处理文件
        bat_file = Path.home() / "minimax.bat"
        with open(bat_file, 'w') as f:
            f.write(f'@echo off\npython "{Path.cwd() / "minimax_cli.py"}" %*')
        print(f"Windows批处理文件已创建: {bat_file}")
        print("请将以下路径添加到系统PATH环境变量:")
        print(Path.home())
    else:  # Unix-like
        alias_line = f'alias minimax="python3 {Path.cwd() / "minimax_cli.py"}"'
        shell_rc = Path.home() / '.bashrc'
        if Path.home() / '.zshrc':
            shell_rc = Path.home() / '.zshrc'
        
        with open(shell_rc, 'a') as f:
            f.write(f'\n{alias_line}\n')
        print(f"别名已添加到 {shell_rc}")
        print("请运行: source ~/.bashrc 或重新打开终端")

def main():
    print("🚀 MiniMax AI 工具安装向导")
    print("=" * 40)
    
    install_choice = input("是否安装依赖包? (y/n): ").lower()
    if install_choice == 'y':
        install_dependencies()
    
    alias_choice = input("是否创建命令别名? (y/n): ").lower()
    if alias_choice == 'y':
        create_alias()
    
    print("\n✅ 安装完成!")
    print("使用方法:")
    print("  交互模式: python minimax_cli.py --interactive")
    print("  命令模式: python minimax_cli.py --chat '你好'")
    print("  图像生成: python minimax_cli.py --image '一只可爱的猫'")

if __name__ == "__main__":
    main()