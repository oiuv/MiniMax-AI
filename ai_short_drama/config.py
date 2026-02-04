#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI短剧素材生成系统配置文件
"""

# 短剧生成标准配置
DRAMA_CONFIG = {
    # 视频规格
    "video": {
        "aspect_ratio": "9:16",       # 竖屏比例
        "width": 1080,                # 视频宽度
        "height": 1920,               # 视频高度
        "resolution": "1080P",        # 分辨率
        "duration_per_scene": 6,       # 每镜头时长（秒）
        "scenes_per_episode": 6,       # 每集镜头数
        "episode_duration": 240        # 每集总时长（秒）
    },
    
    # 音频规格
    "audio": {
        "sample_rate": 32000,          # 采样率
        "format": "mp3",              # 音频格式
        "bitrate": 128000,            # 比特率
        "channel": 1,                 # 单声道
        "speed": 1.2,                 # 语速（快节奏）
        "volume": 0.8                 # 音量
    },
    
    # 剧本规格
    "script": {
        "scenes_per_episode": [5, 8],  # 每集镜头数范围
        "scene_duration_range": [30, 60],  # 每镜头时长范围（秒）
        "hook_timing": 3,              # 钩子时间（秒）
        "twist_interval": 10,          # 反转间隔（秒）
        "compression_ratio": 0.7,       # 剧情压缩比例
        "min_conflict_level": 7         # 最低冲突强度
    },
    
    # 质量控制
    "quality": {
        "target_level": "合格线以上",    # 目标质量水平
        "auto_retry": True,            # 自动重试
        "max_retries": 3,              # 最大重试次数
        "parallel_processing": True     # 并行处理
    }
}

# 音色映射配置
VOICE_MAPPING = {
    "narrator": {
        "voice_id": "male-qn-qingse",
        "emotion": "fluent",
        "description": "说书人播音员"
    },
    "protagonist_male": {
        "voice_id": "male-qn-qingse",
        "emotion": "calm",
        "description": "青年男主角"
    },
    "protagonist_female": {
        "voice_id": "female-chengshu",
        "emotion": "calm",
        "description": "青年女主角"
    },
    "antagonist": {
        "voice_id": "male-qn-qingse",
        "emotion": "arrogant",
        "description": "反派角色"
    }
}

# 运镜映射配置
CAMERA_MAPPING = {
    "dialogue": "固定镜头",       # 对话场景
    "emotion_boost": "推进镜头",   # 情绪增强
    "scene_transition": "拉远镜头", # 场景转换
    "action": "跟随镜头",         # 动作场景
    "tension": "晃动镜头",        # 紧张时刻
    "reveal": "推进镜头"           # 揭示时刻
}

# 情绪类型配置
EMOTION_TYPES = {
    "爽": "爽快、满足、打脸",
    "甜": "甜蜜、温馨、浪漫",
    "紧张": "紧张、悬疑、心跳加速",
    "愤怒": "愤怒、不满、爆发",
    "期待": "期待、渴望、好奇"
}

# 模型配置
MODEL_CONFIG = {
    "image": {
        "model": "image-01",
        "response_format": "url"
    },
    "video": {
        "model": "I2V-01-Director",
        "resolution": "1080P"
    },
    "audio": {
        "model": "speech-2.6-hd",
        "output_format": "hex"
    }
}