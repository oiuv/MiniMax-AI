#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频下载工具 - 用于下载已生成的视频
使用方法: python download_video.py <file_id> [输出文件名]
"""
import os
import requests
import sys
from datetime import datetime

def download_video(file_id, filename=None):
    """下载视频文件"""
    api_key = os.getenv('MINIMAX_API_KEY')
    if not api_key:
        print("请先设置 MINIMAX_API_KEY 环境变量")
        return
    
    if not filename:
        filename = f"video_{file_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    
    url = f"https://api.minimax.chat/v1/files/retrieve?file_id={file_id}"
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        print("获取下载链接...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        download_url = result['file']['download_url']
        
        print(f"开始下载: {filename}")
        video_data = requests.get(download_url).content
        
        with open(filename, 'wb') as f:
            f.write(video_data)
        
        print(f"下载完成: {os.path.abspath(filename)}")
        return filename
        
    except Exception as e:
        print(f"下载失败: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python download_video.py <file_id> [输出文件名]")
        sys.exit(1)
    
    file_id = sys.argv[1]
    filename = sys.argv[2] if len(sys.argv) > 2 else None
    download_video(file_id, filename)