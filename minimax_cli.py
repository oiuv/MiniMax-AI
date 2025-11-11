#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniMax AI 统一命令行工具
简洁高效，无垃圾代码版本
"""

import os
import sys
import json
import time
import requests
import base64
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import argparse

class MiniMaxClient:
    """精简版MiniMax客户端"""
    
    def __init__(self):
        self.group_id = os.getenv('MINIMAX_GROUP_ID')
        self.api_key = os.getenv('MINIMAX_API_KEY')
        self.base_url = "https://api.minimaxi.com/v1"
        self.verbose = False
        
        if not self.group_id or not self.api_key:
            self._setup_credentials()
    
    def _log(self, message: str, level: str = "INFO"):
        """日志输出"""
        print(f"[{level}] {message}")
    
    def _log_request(self, method: str, endpoint: str, data: dict = None):
        """请求日志"""
        self._log(f"🚀 {method} {endpoint}")
        if self.verbose and data:
            self._log(f"📤 请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    def _setup_credentials(self):
        """配置向导"""
        config_file = Path.home() / '.minimax_ai' / 'config.json'
        config_file.parent.mkdir(exist_ok=True)
        
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                    self.group_id = config.get('group_id')
                    self.api_key = config.get('api_key')
                    if self.group_id and self.api_key:
                        return
            except Exception:
                pass
        
        print("⚠️  需要配置API密钥")
        group_id = input("请输入Group ID: ").strip()
        api_key = input("请输入API Key: ").strip()
        
        if not group_id or not api_key:
            print("❌ Group ID和API Key不能为空")
            sys.exit(1)
        
        with open(config_file, 'w') as f:
            json.dump({'group_id': group_id, 'api_key': api_key}, f, indent=2)
        
        print(f"✅ 配置已保存到 {config_file}")
        print("请重新运行程序")
        sys.exit(0)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """统一请求"""
        url = f"{self.base_url}/{endpoint}"
        if any(k in endpoint for k in ['t2a_v2', 'voice_clone', 'music_generation']):
            url += f"?GroupId={self.group_id}"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        self._log_request(method, endpoint, kwargs.get('json'))
        
        for attempt in range(3):
            try:
                response = requests.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                result = response.json()
                
                self._log(f"📥 响应状态: {response.status_code}")
                
                if 'base_resp' in result and result['base_resp']['status_code'] != 0:
                    self._log(f"⚠️ API错误: {result['base_resp']['status_msg']}", "ERROR")
                    if result['base_resp']['status_code'] == 1002 and attempt < 2:
                        time.sleep(2 * (attempt + 1))
                        continue
                    raise Exception(f"API错误: {result['base_resp']['status_msg']}")
                
                self._log(f"✅ 请求成功")
                return result
                
            except Exception as e:
                if attempt == 2:
                    self._log(f"❌ 请求失败: {e}", "ERROR")
                    sys.exit(1)
                self._log(f"🔄 重试第{attempt+1}次...", "WARN")
                time.sleep(1)
    
    def chat(self, message: str, model: str = "MiniMax-M2") -> str:
        """智能对话"""
        self._log("🤖 开始生成对话内容...")
        data = {
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "max_tokens": 1024
        }
        response = self._request("POST", "text/chatcompletion_v2", json=data)
        content = response['choices'][0]['message']['content']
        self._log(f"📄 生成内容长度: {len(content)} 字符")
        return content
    
    def image(self, prompt: str, model: str = "image-01", n: int = 1,
                aspect_ratio: str = "1:1", width: int = None, height: int = None,
                seed: int = None, response_format: str = "url",
                prompt_optimizer: bool = False, aigc_watermark: bool = False,
                style_type: str = None, style_weight: float = 0.8,
                reference_image: str = None) -> list:
        """图像生成（文生图/图生图）

        Args:
            prompt: 图像的文本描述，最长1500字符
            model: 模型名称，可选值：image-01, image-01-live
            n: 单次请求生成的图片数量，取值范围[1, 9]，默认为1
            aspect_ratio: 图像宽高比，默认为1:1，可选值：1:1, 16:9, 4:3, 3:2, 2:3, 3:4, 9:16, 21:9
            width: 生成图片的宽度（像素），仅当model为image-01时生效，取值范围[512, 2048]，且必须是8的倍数
            height: 生成图片的高度（像素），仅当model为image-01时生效，取值范围[512, 2048]，且必须是8的倍数
            seed: 随机种子，用于复现结果
            response_format: 返回图片的形式，默认为url，可选值：url, base64
            prompt_optimizer: 是否开启prompt自动优化，默认为False
            aigc_watermark: 是否在生成的图片中添加水印，默认为False
            style_type: 画风风格类型，仅当model为image-01-live时生效，可选值：漫画, 元气, 中世纪, 水彩
            style_weight: 画风权重，取值范围(0, 1]，默认0.8
            reference_image: 参考图片路径或URL，用于图生图（仅支持人像character类型）

        Returns:
            图片URL列表或Base64编码列表
        """
        # 检测生成模式
        if reference_image:
            self._log(f"🎨 开始图生图...")
            generation_mode = "图生图"
        else:
            self._log(f"🎨 开始文生图...")
            generation_mode = "文生图"

        # 参数验证
        if len(prompt) > 1500:
            raise ValueError(f"图像描述过长，最多支持1500字符，当前{len(prompt)}字符")

        if n < 1 or n > 9:
            raise ValueError(f"图片数量必须在1-9之间，当前为{n}")

        # width和height必须同时设置
        if (width is not None) != (height is not None):
            raise ValueError("width和height必须同时设置")

        if width is not None:
            if width < 512 or width > 2048 or width % 8 != 0:
                raise ValueError(f"width必须在512-2048之间且为8的倍数，当前为{width}")
            if height < 512 or height > 2048 or height % 8 != 0:
                raise ValueError(f"height必须在512-2048之间且为8的倍数，当前为{height}")
            if model != "image-01":
                raise ValueError("width和height参数仅当model为image-01时生效")

        if style_type and model != "image-01-live":
            raise ValueError("style_type参数仅当model为image-01-live时生效")

        data = {
            "model": model,
            "prompt": prompt,
            "response_format": response_format,
            "n": n,
            "prompt_optimizer": prompt_optimizer
        }

        # 图生图专用参数
        if reference_image:
            # 处理参考图片
            processed_ref_image = self._process_image_input(reference_image)
            data["subject_reference"] = [
                {
                    "type": "character",
                    "image_file": processed_ref_image
                }
            ]
            self._log(f"📷 参考图片: {reference_image}")

        # 优先使用aspect_ratio，如果设置了width和height则使用它们
        if width is not None and height is not None:
            data["width"] = width
            data["height"] = height
        else:
            data["aspect_ratio"] = aspect_ratio

        # 可选参数
        if seed is not None:
            data["seed"] = seed

        if aigc_watermark:
            data["aigc_watermark"] = True

        # 风格设置（仅对image-01-live生效）
        if style_type:
            data["style"] = {
                "style_type": style_type,
                "style_weight": style_weight
            }

        self._log(f"📋 使用模型: {model}")
        self._log(f"🎭 图片数量: {n}")
        self._log(f"📐 尺寸设置: {width}x{height}" if width else f"📐 宽高比: {aspect_ratio}")
        if style_type:
            self._log(f"🎨 风格设置: {style_type} (权重: {style_weight})")

        response = self._request("POST", "image_generation", json=data)

        # 根据response_format返回不同格式的数据
        if response_format == "url":
            result = response.get('data', {}).get('image_urls', [])
        else:
            result = response.get('data', {}).get('image_base64', [])

        # 显示生成统计
        metadata = response.get('metadata', {})
        success_count = metadata.get('success_count', len(result))
        failed_count = metadata.get('failed_count', 0)

        self._log(f"📸 {generation_mode}成功生成: {success_count} 张")
        if failed_count > 0:
            self._log(f"⚠️ 内容安全拦截: {failed_count} 张")

        return result
    
    def video(self, prompt: str, model: str = "MiniMax-Hailuo-2.3", duration: int = 6,
                 resolution: str = None, prompt_optimizer: bool = True,
                 fast_pretreatment: bool = False, aigc_watermark: bool = False,
                 callback_url: str = None) -> str:
        """视频生成 - 支持镜头控制和高级参数

        Args:
            prompt: 视频文本描述（最多2000字符），支持运镜指令如[推进]、[左移]等
            model: 视频生成模型
                - MiniMax-Hailuo-2.3: 最新模型，支持运镜控制
                - MiniMax-Hailuo-02: 经典模型，支持运镜控制
                - T2V-01-Director: 导演版，支持运镜控制
                - T2V-01: 基础模型
            duration: 视频时长（秒），根据模型和分辨率不同有不同限制
            resolution: 视频分辨率 [720P, 768P, 1080P]
            prompt_optimizer: 是否自动优化prompt，默认True
            fast_pretreatment: 是否缩短prompt优化耗时，仅对Hailuo模型生效
            aigc_watermark: 是否添加水印，默认False
            callback_url: 回调URL用于接收任务状态通知

        Returns:
            task_id: 视频生成任务ID
        """
        self._log(f"🎬 开始生成视频...")
        self._log(f"📋 使用模型: {model}")

        # 智能选择默认分辨率
        if resolution is None:
            if model in ['T2V-01-Director', 'T2V-01', 'I2V-01-Director', 'I2V-01-live', 'I2V-01']:
                resolution = '720P'
            elif model in ['MiniMax-Hailuo-2.3', 'MiniMax-Hailuo-2.3-Fast']:
                resolution = '768P'  # 默认使用768P以获得更好质量
            elif model == 'MiniMax-Hailuo-02':
                resolution = '768P'  # Hailuo-02支持512P，默认768P
            else:
                resolution = '720P'
            self._log(f"🎯 自动选择分辨率: {resolution}")

        # 参数验证
        if len(prompt) > 2000:
            raise ValueError("Prompt长度不能超过2000字符")

        # 验证时长和分辨率的组合是否有效
        valid_combinations = self._get_valid_duration_resolution(model)
        if (duration, resolution) not in valid_combinations:
            self._log(f"⚠️ 警告: 时长{duration}s和分辨率{resolution}组合可能不被支持")
            self._log(f"💡 建议组合: {valid_combinations[:3]}")

        # 检测运镜指令
        camera_moves = self._detect_camera_moves(prompt)
        if camera_moves:
            self._log(f"🎥 检测到运镜指令: {', '.join(camera_moves)}")

        data = {
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "resolution": resolution,
            "prompt_optimizer": prompt_optimizer,
            "aigc_watermark": aigc_watermark
        }

        # 添加可选参数
        if fast_pretreatment and model in ["MiniMax-Hailuo-2.3", "MiniMax-Hailuo-02"]:
            data["fast_pretreatment"] = fast_pretreatment
            self._log("⚡ 启用快速预处理")

        if callback_url:
            data["callback_url"] = callback_url
            self._log(f"📞 设置回调URL: {callback_url}")

        response = self._request("POST", "video_generation", json=data)
        task_id = response.get('task_id', '')
        self._log(f"🎯 视频任务ID: {task_id}")
        return task_id

    def _get_valid_duration_resolution(self, model: str) -> list:
        """获取模型支持的时长和分辨率组合"""
        combinations = {
            # T2V (文生视频) 模型
            "MiniMax-Hailuo-2.3": [(6, "768P"), (10, "768P"), (6, "1080P")],
            "MiniMax-Hailuo-2.3-Fast": [(6, "768P"), (10, "768P"), (6, "1080P")],
            "MiniMax-Hailuo-02": [(6, "512P"), (6, "768P"), (10, "768P"), (6, "1080P")],
            "T2V-01-Director": [(6, "720P")],
            "T2V-01": [(6, "720P")],
            # I2V (图生视频) 模型
            "I2V-01-Director": [(6, "720P")],
            "I2V-01-live": [(6, "720P")],
            "I2V-01": [(6, "720P")]
        }
        return combinations.get(model, [(6, "720P")])

    def _detect_camera_moves(self, prompt: str) -> list:
        """检测prompt中的运镜指令"""
        camera_moves = [
            "[左移]", "[右移]", "[左摇]", "[右摇]", "[推进]", "[拉远]",
            "[上升]", "[下降]", "[上摇]", "[下摇]", "[变焦推近]",
            "[变焦拉远]", "[晃动]", "[跟随]", "[固定]"
        ]

        detected = []
        for move in camera_moves:
            if move in prompt:
                detected.append(move.strip("[]"))

        return detected

    def video_with_camera_control(self, prompt: str, camera_sequence: list = None,
                                        **kwargs) -> str:
        """带镜头控制的视频生成

        Args:
            prompt: 视频描述文本
            camera_sequence: 镜头序列，如 [{"action": "推进", "timing": "开始"}, {"action": "左摇", "timing": "中间"}]
            **kwargs: 其他视频参数

        Returns:
            task_id: 视频生成任务ID
        """
        if camera_sequence:
            # 将镜头序列转换为prompt中的运镜指令
            camera_prompt = prompt
            for i, camera in enumerate(camera_sequence):
                action = camera.get("action", "")
                timing = camera.get("timing", "")

                # 映射自然语言到指令
                action_map = {
                    "左移": "左移", "右移": "右移", "左摇": "左摇", "右摇": "右摇",
                    "推进": "推进", "拉远": "拉远", "上升": "上升", "下降": "下降",
                    "上摇": "上摇", "下摇": "下摇", "变焦推近": "变焦推近",
                    "变焦拉远": "变焦拉远", "晃动": "晃动", "跟随": "跟随", "固定": "固定"
                }

                instruction = action_map.get(action, action)
                if instruction:
                    if i == 0:
                        camera_prompt = f"[{instruction}] " + camera_prompt
                    else:
                        camera_prompt += f", 然后[{instruction}]"

            prompt = camera_prompt
            self._log(f"🎥 应用镜头序列: {len(camera_sequence)}个镜头")

        return self.video(prompt, **kwargs)

    def _process_image_input(self, image_input: str) -> str:
        """处理图片输入，支持本地路径和URL，转换为Base64或验证URL

        Args:
            image_input: 图片路径、URL或Base64 Data URL

        Returns:
            str: 处理后的图片URL或Base64 Data URL
        """
        # 如果已经是Data URL格式，直接返回
        if image_input.startswith('data:image/'):
            return image_input

        # 如果是URL，进行简单验证
        if image_input.startswith(('http://', 'https://')):
            self._log(f"🌐 使用图片URL: {image_input}")
            return image_input

        # 处理本地文件
        try:
            image_path = Path(image_input)
            if not image_path.exists():
                raise FileNotFoundError(f"图片文件不存在: {image_path}")

            # 检查文件大小 (20MB限制)
            file_size = image_path.stat().st_size
            if file_size > 20 * 1024 * 1024:  # 20MB
                raise ValueError(f"图片文件过大: {file_size/1024/1024:.1f}MB (限制: 20MB)")

            # 检查文件格式
            mime_type, _ = mimetypes.guess_type(str(image_path))
            if mime_type not in ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']:
                raise ValueError(f"不支持的图片格式: {mime_type}")

            # 读取并编码为Base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                data_url = f"data:{mime_type};base64,{base64_data}"

            self._log(f"📷 图片已编码: {image_path.name} ({len(image_data)/1024:.1f}KB)")
            return data_url

        except Exception as e:
            self._log(f"❌ 图片处理失败: {e}", "ERROR")
            raise

    def image_to_video(self, first_frame_image: str, prompt: str = "",
                              model: str = "I2V-01", duration: int = 6,
                              resolution: str = None, prompt_optimizer: bool = True,
                              fast_pretreatment: bool = False, aigc_watermark: bool = False,
                              callback_url: str = None) -> str:
        """图生视频 - 将静态图片转换为动态视频

        Args:
            first_frame_image: 首帧图片（路径、URL或Base64 Data URL）
            prompt: 视频描述文本（最多2000字符），支持运镜指令
            model: 图生视频模型
                - I2V-01-Director: 导演版，支持运镜控制
                - I2V-01-live: 卡通/漫画风格增强
                - I2V-01: 基础图生视频模型
                - MiniMax-Hailuo-2.3/2.3-Fast/02: 也支持图生视频
            duration: 视频时长（秒）
            resolution: 视频分辨率，None为自动选择
            prompt_optimizer: 是否自动优化prompt
            fast_pretreatment: 快速预处理（仅Hailuo模型）
            aigc_watermark: 是否添加水印
            callback_url: 回调URL

        Returns:
            task_id: 视频生成任务ID
        """
        self._log(f"🎬 开始图生视频...")
        self._log(f"📋 使用模型: {model}")

        # 处理图片输入
        processed_image = self._process_image_input(first_frame_image)

        # 智能选择默认分辨率
        if resolution is None:
            if model in ['I2V-01-Director', 'I2V-01-live', 'I2V-01']:
                resolution = '720P'
            elif model in ['MiniMax-Hailuo-2.3', 'MiniMax-Hailuo-2.3-Fast']:
                resolution = '768P'
            elif model == 'MiniMax-Hailuo-02':
                resolution = '768P'  # Hailuo-02默认768P，支持512P
            else:
                resolution = '720P'
            self._log(f"🎯 自动选择分辨率: {resolution}")

        # 验证参数
        if prompt and len(prompt) > 2000:
            raise ValueError("Prompt长度不能超过2000字符")

        # 验证时长和分辨率组合
        valid_combinations = self._get_valid_duration_resolution(model)
        if (duration, resolution) not in valid_combinations:
            self._log(f"⚠️ 警告: 时长{duration}s和分辨率{resolution}组合可能不被支持")
            self._log(f"💡 建议组合: {valid_combinations[:3]}")

        # 检测运镜指令
        if prompt:
            camera_moves = self._detect_camera_moves(prompt)
            if camera_moves:
                self._log(f"🎥 检测到运镜指令: {', '.join(camera_moves)}")

        # 构建请求数据
        data = {
            "model": model,
            "first_frame_image": processed_image,
            "duration": duration,
            "resolution": resolution,
            "prompt_optimizer": prompt_optimizer,
            "aigc_watermark": aigc_watermark
        }

        # 添加可选参数
        if prompt:
            data["prompt"] = prompt

        if fast_pretreatment and model in ["MiniMax-Hailuo-2.3", "MiniMax-Hailuo-2.3-Fast", "MiniMax-Hailuo-02"]:
            data["fast_pretreatment"] = fast_pretreatment
            self._log("⚡ 启用快速预处理")

        if callback_url:
            data["callback_url"] = callback_url
            self._log(f"📞 设置回调URL: {callback_url}")

        response = self._request("POST", "video_generation", json=data)
        task_id = response.get('task_id', '')
        self._log(f"🎯 图生视频任务ID: {task_id}")
        return task_id

    def start_end_to_video(self, first_frame_image: str, last_frame_image: str,
                                prompt: str = "", duration: int = 6,
                                resolution: str = None, prompt_optimizer: bool = True,
                                aigc_watermark: bool = False,
                                callback_url: str = None) -> str:
        """首尾帧生成视频 - 在指定首尾帧之间生成过渡视频

        Args:
            first_frame_image: 起始帧图片（路径、URL或Base64 Data URL）
            last_frame_image: 结束帧图片（路径、URL或Base64 Data URL）
            prompt: 视频过渡描述文本（最多2000字符），支持运镜指令
            duration: 视频时长（秒），6或10秒
            resolution: 视频分辨率，768P或1080P
            prompt_optimizer: 是否自动优化prompt
            aigc_watermark: 是否添加水印
            callback_url: 回调URL

        Returns:
            task_id: 视频生成任务ID
        """
        self._log(f"🎬 开始首尾帧视频生成...")
        self._log(f"📋 使用模型: MiniMax-Hailuo-02 (首尾帧专用)")

        # 处理图片输入
        processed_first_frame = self._process_image_input(first_frame_image)
        processed_last_frame = self._process_image_input(last_frame_image)

        # 智能选择默认分辨率（首尾帧仅支持768P和1080P）
        if resolution is None:
            resolution = '768P'  # 默认使用768P以获得更好质量
            self._log(f"🎯 自动选择分辨率: {resolution}")

        # 验证分辨率限制
        if resolution not in ['768P', '1080P']:
            raise ValueError("首尾帧视频生成仅支持768P和1080P分辨率")

        # 验证时长和分辨率组合
        if resolution == '1080P' and duration != 6:
            raise ValueError("1080P分辨率仅支持6秒时长")
        if duration not in [6, 10]:
            raise ValueError("首尾帧视频生成仅支持6秒或10秒时长")

        # 验证参数
        if prompt and len(prompt) > 2000:
            raise ValueError("Prompt长度不能超过2000字符")

        # 检测运镜指令
        if prompt:
            camera_moves = self._detect_camera_moves(prompt)
            if camera_moves:
                self._log(f"🎥 检测到运镜指令: {', '.join(camera_moves)}")

        # 构建请求数据
        data = {
            "model": "MiniMax-Hailuo-02",
            "first_frame_image": processed_first_frame,
            "last_frame_image": processed_last_frame,
            "duration": duration,
            "resolution": resolution,
            "prompt_optimizer": prompt_optimizer,
            "aigc_watermark": aigc_watermark
        }

        # 添加可选参数
        if prompt:
            data["prompt"] = prompt

        if callback_url:
            data["callback_url"] = callback_url
            self._log(f"📞 设置回调URL: {callback_url}")

        response = self._request("POST", "video_generation", json=data)
        task_id = response.get('task_id', '')
        self._log(f"🎯 首尾帧视频任务ID: {task_id}")

        # 显示关键信息
        self._log(f"📐 分辨率: {resolution}")
        self._log(f"⏱️ 时长: {duration}秒")
        self._log(f"🖼️ 首尾帧尺寸将根据首帧自动调整")

        return task_id

    def video_advanced(self, prompt: str = "", model: str = "MiniMax-Hailuo-2.3",
                             first_frame_image: str = None, last_frame_image: str = None,
                             subject_image: str = None, duration: int = 10,
                             resolution: str = "1080P", video_name: str = None,
                             prompt_optimizer: bool = True, aigc_watermark: bool = False,
                             callback_url: str = None) -> str:
        """高级视频生成，支持多种模式

        Args:
            prompt: 视频生成描述文本
            model: 视频生成模型
                - MiniMax-Hailuo-2.3: 全新模型，肢体动作、物理表现全面升级
                - MiniMax-Hailuo-2.3-Fast: 图生视频快速模型，性价比高
                - MiniMax-Hailuo-02: 经典模型，指令遵循能力强
                - S2V-01: 主体参考视频生成模型
            first_frame_image: 首帧图片URL或路径（图生视频必需）
            last_frame_image: 尾帧图片URL或路径（首尾帧生成必需）
            subject_image: 主体参考图片URL或路径（主体参考生成必需）
            duration: 视频时长（秒）
            resolution: 分辨率 (720P/768P/1080P)
            video_name: 视频文件名
            prompt_optimizer: 是否自动优化prompt
            aigc_watermark: 是否添加水印
            callback_url: 回调URL

        Returns:
            task_id: 视频生成任务ID

        Note:
            主体参考生成：提供subject_image且model为S2V-01时，调用主体参考生成方法
            首尾帧生成：同时提供first_frame_image和last_frame_image时，将调用首尾帧专用方法
            图生视频：仅提供first_frame_image时，将调用图生视频方法
            文生视频：都不提供时，将调用基础视频生成方法
        """
        # 智能判断生成模式并调用相应方法
        if subject_image and model == "S2V-01":
            # 主体参考视频生成模式
            self._log("👤 检测到主体参考图片和S2V-01模型，使用主体参考生成模式")
            return self.subject_reference_to_video(
                subject_image=subject_image,
                prompt=prompt,
                prompt_optimizer=prompt_optimizer,
                aigc_watermark=aigc_watermark,
                callback_url=callback_url
            )
        elif first_frame_image and last_frame_image:
            # 首尾帧生成模式
            self._log("🔗 检测到首尾帧图片，使用首尾帧生成模式")
            return self.start_end_to_video(
                first_frame_image=first_frame_image,
                last_frame_image=last_frame_image,
                prompt=prompt,
                duration=duration,
                resolution=resolution,
                prompt_optimizer=prompt_optimizer,
                aigc_watermark=aigc_watermark,
                callback_url=callback_url
            )
        elif first_frame_image:
            # 图生视频模式
            self._log("🖼️ 检测到首帧图片，使用图生视频模式")
            return self.image_to_video(
                first_frame_image=first_frame_image,
                prompt=prompt,
                model=model,
                duration=duration,
                resolution=resolution,
                prompt_optimizer=prompt_optimizer,
                aigc_watermark=aigc_watermark,
                callback_url=callback_url
            )
        else:
            # 文生视频模式
            self._log("📝 使用文本视频生成模式")
            return self.video(
                prompt=prompt,
                model=model,
                duration=duration,
                resolution=resolution,
                prompt_optimizer=prompt_optimizer,
                aigc_watermark=aigc_watermark,
                callback_url=callback_url
            )

    def video_status(self, task_id: str) -> Dict[str, Any]:
        """查询视频状态"""
        return self._request("GET", f"query/video_generation?task_id={task_id}")
    
    def download_video(self, file_id: str, filename: str = None) -> str:
        """下载视频文件"""
        self._log(f"📥 开始下载视频...")

        # 获取文件信息
        file_response = self._request("GET", f"files/retrieve?file_id={file_id}")

        if 'file' not in file_response:
            raise Exception(f"无法获取文件信息: {file_response}")

        file_info = file_response['file']
        download_url = file_info['download_url']

        # 使用API返回的文件名，或自定义文件名
        if not filename:
            original_name = file_info.get('filename', f'video_{file_id}.mp4')
            # 确保文件扩展名为.mp4
            if not original_name.endswith('.mp4'):
                original_name += '.mp4'
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{original_name}"

        # 显示文件信息
        file_size = file_info.get('bytes', 0)
        created_time = file_info.get('created_at', 0)

        self._log(f"📁 文件ID: {file_id}")
        if file_size > 0:
            file_size_mb = file_size / (1024 * 1024)
            self._log(f"📊 文件大小: {file_size_mb:.1f} MB")
        self._log(f"📅 创建时间: {datetime.fromtimestamp(created_time).strftime('%Y-%m-%d %H:%M:%S')}" if created_time else "")

        # 下载文件
        import urllib.request
        filepath = Path('./output/videos') / filename
        filepath.parent.mkdir(exist_ok=True)
        self._log(f"🎯 正在下载: {filename}")
        urllib.request.urlretrieve(download_url, filepath)
        self._log(f"✅ 下载完成: {filepath}")
        return str(filepath)

    def subject_reference_to_video(self, subject_image: str, prompt: str,
                                   prompt_optimizer: bool = True,
                                   aigc_watermark: bool = False,
                                   callback_url: str = None) -> str:
        """主体参考视频生成

        基于提供的人物主体图片生成视频，保持人物面部特征

        Args:
            subject_image: 主体参考图片路径或URL
            prompt: 视频的文本描述，最大2000字符
            prompt_optimizer: 是否自动优化prompt，默认True
            aigc_watermark: 是否添加水印，默认False
            callback_url: 回调URL

        Returns:
            视频生成任务ID

        Raises:
            ValueError: 参数验证失败时抛出
        """
        self._log("👤 开始主体参考视频生成...")

        # 参数验证
        if not subject_image:
            raise ValueError("主体参考图片为必填参数")

        if not prompt:
            raise ValueError("视频描述为必填参数")

        if len(prompt) > 2000:
            raise ValueError(f"视频描述过长，最多支持2000字符，当前{len(prompt)}字符")

        # 处理主体参考图片
        processed_image = self._process_image_input(subject_image)

        # 构建请求数据
        data = {
            "model": "S2V-01",
            "prompt": prompt.strip(),
            "prompt_optimizer": prompt_optimizer,
            "subject_reference": [
                {
                    "type": "character",
                    "image": [processed_image]
                }
            ]
        }

        # 可选参数
        if aigc_watermark:
            data["aigc_watermark"] = True

        if callback_url:
            data["callback_url"] = callback_url

        self._log(f"🎭 使用模型: S2V-01")
        self._log(f"📝 视频描述: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        self._log(f"👤 主体图片: {subject_image}")

        # 发送请求
        response = self._request("POST", "video_generation", json=data)

        task_id = response.get("task_id", "")
        self._log(f"✅ 主体参考视频生成任务已提交，任务ID: {task_id}")

        return task_id

    def music(self, prompt: str, lyrics: str, stream: bool = False,
                output_format: str = "hex", sample_rate: int = 44100,
                bitrate: int = 256000, format: str = "mp3",
                aigc_watermark: bool = False) -> str:
        """音乐生成 (music-2.0)

        Args:
            prompt: 音乐描述，用于指定风格、情绪和场景，长度限制[10, 2000]字符
            lyrics: 歌词内容，长度限制[10, 3000]字符，支持结构标签
            stream: 是否使用流式传输，默认false
            output_format: 音频返回格式，可选url/hex，默认hex
            sample_rate: 采样率，可选16000/24000/32000/44100，默认44100
            bitrate: 比特率，可选32000/64000/128000/256000，默认256000
            format: 音频编码格式，可选mp3/wav/pcm，默认mp3
            aigc_watermark: 是否在音频末尾添加水印，默认false（仅非流式生效）

        Returns:
            音频数据（hex编码或URL）
        """
        self._log("🎵 开始生成音乐...")
        import sys

        # 严格校验长度
        prompt = prompt.strip()
        lyrics = lyrics.strip()

        # 验证prompt长度 [10, 2000]
        if len(prompt) < 10:
            print(f"❌ prompt过短 ({len(prompt)}字符)")
            print(f"💡 建议: 添加更多描述，如风格、情绪、场景")
            print(f"📝 示例: '独立民谣,忧郁,内省,渴望,独自漫步,咖啡馆'")
            sys.exit(1)

        if len(prompt) > 2000:
            print(f"❌ prompt过长 ({len(prompt)}字符)")
            print(f"💡 建议: prompt内容请控制在2000字符以内")
            print(f"📊 当前长度: {len(prompt)}字符，超出限制: {len(prompt) - 2000}字符")
            print(f"📝 提示: 可以精简描述或使用更精确的关键词")
            sys.exit(1)

        # 验证lyrics长度 [10, 3000]
        if not lyrics or not lyrics.strip():
            print(f"❌ 歌词为必填参数")
            print(f"💡 建议: 提供歌词内容或文件路径")
            print(f"📝 示例: '[Verse]\n街灯微亮晚风轻抚\n[Chorus]\n推开木门香气弥漫'")
            sys.exit(1)

        if len(lyrics) < 10:
            print(f"❌ 歌词过短 ({len(lyrics)}字符)")
            print(f"💡 建议: 歌词内容请控制在10-3000字符")
            print(f"📝 示例: '[Verse]\n街灯微亮晚风轻抚\n[Chorus]\n推开木门香气弥漫'")
            sys.exit(1)

        if len(lyrics) > 3000:
            print(f"❌ 歌词过长 ({len(lyrics)}字符)")
            print(f"💡 建议: 歌词内容请控制在3000字符以内")
            print(f"📊 当前长度: {len(lyrics)}字符，超出限制: {len(lyrics) - 3000}字符")
            print(f"📝 提示: 可以精简歌词或分段生成")
            sys.exit(1)

        # 验证参数组合
        if stream and output_format == "url":
            print(f"❌ 流式传输仅支持hex格式")
            print(f"💡 建议: 使用 --output-format hex 或设置 stream=false")
            sys.exit(1)

        # 验证音频设置参数
        valid_sample_rates = [16000, 24000, 32000, 44100]
        valid_bitrates = [32000, 64000, 128000, 256000]
        valid_formats = ["mp3", "wav", "pcm"]

        if sample_rate not in valid_sample_rates:
            print(f"❌ 无效采样率: {sample_rate}")
            print(f"💡 可选值: {valid_sample_rates}")
            sys.exit(1)

        if bitrate not in valid_bitrates:
            print(f"❌ 无效比特率: {bitrate}")
            print(f"💡 可选值: {valid_bitrates}")
            sys.exit(1)

        if format not in valid_formats:
            print(f"❌ 无效音频格式: {format}")
            print(f"💡 可选值: {valid_formats}")
            sys.exit(1)

        data = {
            "model": "music-2.0",
            "prompt": prompt,
            "lyrics": lyrics,
            "stream": stream,
            "output_format": output_format,
            "audio_setting": {
                "sample_rate": sample_rate,
                "bitrate": bitrate,
                "format": format
            }
        }

        # 仅在非流式时添加水印
        if not stream and aigc_watermark:
            data["aigc_watermark"] = True

        self._log(f"📋 使用模型: music-2.0")
        self._log(f"🎵 音乐描述: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        self._log(f"🎤 歌词长度: {len(lyrics)}字符")
        self._log(f"📊 音频设置: {format}, {sample_rate}Hz, {bitrate//1000}kbps")
        self._log(f"🌊 流式传输: {'是' if stream else '否'}")
        self._log(f"🔗 返回格式: {output_format}")

        response = self._request("POST", "music_generation", json=data)

        # 检查音乐生成状态
        music_data = response.get('data', {})
        status = music_data.get('status', 0)

        if status == 1:
            self._log(f"⏳ 音乐合成中，请稍候...")
            # TODO: 可以添加轮询机制来等待完成
        elif status == 2:
            self._log(f"✅ 音乐生成完成")

        audio_data = music_data.get('audio', '')

        # 显示额外信息
        extra_info = response.get('extra_info', {})
        if extra_info:
            duration_ms = extra_info.get('music_duration', 0)
            duration_sec = duration_ms / 1000 if duration_ms > 0 else 0
            music_size = extra_info.get('music_size', 0)
            music_size_kb = music_size / 1024 if music_size > 0 else 0

            self._log(f"⏱️  音乐时长: {duration_sec:.1f}秒")
            if music_size > 0:
                self._log(f"📊 文件大小: {music_size_kb:.1f}KB")

        return audio_data

    def upload_file(self, file_path: str, purpose: str) -> Dict[str, Any]:
        """上传文件到MiniMax平台

        Args:
            file_path: 文件路径
            purpose: 文件使用目的 [voice_clone, prompt_audio, t2a_async_input]

        Returns:
            上传响应，包含file_id等信息

        Raises:
            ValueError: 参数验证失败时抛出
        """
        self._log(f"📤 开始上传文件: {file_path}")

        # 参数验证
        valid_purposes = ["voice_clone", "prompt_audio", "t2a_async_input"]
        if purpose not in valid_purposes:
            raise ValueError(f"无效的purpose: {purpose}，可选值: {valid_purposes}")

        if not Path(file_path).exists():
            raise ValueError(f"文件不存在: {file_path}")

        # 检查文件大小（建议限制为100MB）
        file_size = Path(file_path).stat().st_size
        max_size = 100 * 1024 * 1024  # 100MB
        if file_size > max_size:
            raise ValueError(f"文件过大 ({file_size/1024/1024:.1f}MB)，最大支持{max_size/1024/1024}MB")

        # 验证文件格式
        file_ext = Path(file_path).suffix.lower()
        if purpose in ["voice_clone", "prompt_audio"]:
            valid_formats = [".mp3", ".m4a", ".wav"]
            if file_ext not in valid_formats:
                raise ValueError(f"voice_clone/prompt_audio仅支持音频文件，当前格式: {file_ext}")
        elif purpose == "t2a_async_input":
            valid_formats = [".text", ".zip"]
            if file_ext not in valid_formats:
                raise ValueError(f"t2a_async_input仅支持文本文件，当前格式: {file_ext}")

        # 构建multipart/form-data请求
        import requests

        url = f"{self.base_url}/files/upload"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }

        # 准备文件数据
        with open(file_path, 'rb') as f:
            files = {
                'file': (Path(file_path).name, f, 'application/octet-stream'),
                'purpose': (None, purpose)
            }

            self._log(f"📋 文件用途: {purpose}")
            self._log(f"📊 文件大小: {file_size/1024:.1f} KB")
            self._log(f"📄 文件格式: {file_ext}")

            try:
                response = requests.post(url, headers=headers, files=files, timeout=60)
                response.raise_for_status()
                result = response.json()

                if 'base_resp' in result and result['base_resp']['status_code'] != 0:
                    error_msg = result['base_resp'].get('status_msg', 'Unknown error')
                    raise Exception(f"文件上传失败: {error_msg}")

                file_info = result.get('file', {})
                file_id = file_info.get('file_id', '')
                filename = file_info.get('filename', '')
                bytes_size = file_info.get('bytes', 0)
                created_at = file_info.get('created_at', 0)

                self._log(f"✅ 文件上传成功")
                self._log(f"📁 文件ID: {file_id}")
                self._log(f"📄 文件名: {filename}")
                self._log(f"📊 大小: {bytes_size/1024:.1f} KB")
                self._log(f"📅 上传时间: {datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S')}" if created_at else "")

                return result

            except requests.exceptions.Timeout:
                raise Exception("文件上传超时，请检查网络连接")
            except Exception as e:
                raise Exception(f"文件上传失败: {str(e)}")

    def list_files(self, limit: int = 10, after: str = None, order: str = None) -> Dict[str, Any]:
        """
        列出文件列表

        Args:
            limit: 返回文件数量限制 (10-100)，默认10
            after: 分页游标，用于获取下一页数据
            order: 排序方式，created_at获取最新创建文件，file_size按文件大小排序

        Returns:
            包含文件列表和分页信息的字典
        """
        try:
            # 构建查询参数
            params = {'limit': limit}
            if after:
                params['after'] = after
            if order:
                params['order'] = order

            return self._request(
                'GET',
                '/files/list',
                params=params
            )
        except Exception as e:
            return {'error': str(e)}

    def retrieve_file(self, file_id: str) -> Dict[str, Any]:
        """
        检索文件信息

        Args:
            file_id: 文件的唯一标识符

        Returns:
            包含文件详细信息的字典
        """
        try:
            params = {'file_id': file_id}
            return self._request(
                'GET',
                '/files/retrieve',
                params=params
            )
        except Exception as e:
            return {'error': str(e)}

    def download_file(self, file_id: str, save_path: str = None) -> str:
        """
        下载文件

        Args:
            file_id: 需要下载的文件ID
            save_path: 保存路径，如果为None则使用默认路径

        Returns:
            下载文件的本地路径
        """
        try:
            import requests
            import os
            from pathlib import Path

            # 首先获取文件信息
            file_info = self.retrieve_file(file_id)
            if 'error' in file_info:
                raise Exception(f"获取文件信息失败: {file_info['error']}")

            file_data = file_info.get('file', {})
            filename = file_data.get('filename', f'file_{file_id}')

            # 构建下载URL
            params = {'file_id': file_id}
            download_url = f"{self.base_url}/files/retrieve_content"
            headers = {'Authorization': f'Bearer {self.api_key}'}

            self._log(f"📥 开始下载文件: {filename}")

            response = requests.get(download_url, headers=headers, params=params, stream=True, timeout=300)
            response.raise_for_status()

            # 确定保存路径
            if save_path is None:
                output_dir = Path.home() / "minimax_outputs" / "downloads"
                output_dir.mkdir(parents=True, exist_ok=True)
                save_path = output_dir / filename
            else:
                save_path = Path(save_path)
                save_path.parent.mkdir(parents=True, exist_ok=True)

            # 写入文件
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            file_size = save_path.stat().st_size
            self._log(f"✅ 文件下载成功: {save_path}")
            self._log(f"📊 文件大小: {file_size/1024/1024:.2f} MB")

            return str(save_path)

        except Exception as e:
            error_msg = f"文件下载失败: {str(e)}"
            self._log(error_msg)
            return error_msg

    def delete_file(self, file_id: str, purpose: str) -> Dict[str, Any]:
        """
        删除文件

        Args:
            file_id: 文件的唯一标识符
            purpose: 文件使用目的 [voice_clone, prompt_audio, t2a_async, t2a_async_input, video_generation]

        Returns:
            删除操作的结果
        """
        try:
            # 参数验证
            valid_purposes = ["voice_clone", "prompt_audio", "t2a_async", "t2a_async_input", "video_generation"]
            if purpose not in valid_purposes:
                raise ValueError(f"无效的purpose: {purpose}，可选值: {valid_purposes}")

            data = {
                'file_id': file_id,
                'purpose': purpose
            }

            self._log(f"🗑️  开始删除文件: {file_id}")

            result = self._request(
                'POST',
                '/files/delete',
                json=data
            )

            if 'base_resp' in result and result['base_resp']['status_code'] == 0:
                self._log(f"✅ 文件删除成功: {file_id}")
            else:
                error_msg = result.get('base_resp', {}).get('status_msg', 'Unknown error')
                self._log(f"❌ 文件删除失败: {error_msg}")

            return result

        except Exception as e:
            error_msg = f"文件删除失败: {str(e)}"
            self._log(error_msg)
            return {'error': error_msg}

    def tts(self, text: str, voice_id: str = "female-chengshu", emotion: str = "calm",
               speed: float = 1.0, vol: float = 1.0, pitch: int = 0,
               sample_rate: int = 32000, format: str = "mp3", bitrate: int = 128000,
               channel: int = 1, stream: bool = False, language_boost: str = None,
               subtitle_enable: bool = False, output_format: str = "hex") -> str:
        """文本转语音，支持完整的高级参数控制

        Args:
            text: 需要合成语音的文本 (< 10000字符)
            voice_id: 音色ID (支持300+系统音色)
            emotion: 情感控制 [happy, sad, angry, fearful, disgusted, surprised, calm, fluent]
            speed: 语速 [0.5, 2.0]，默认1.0
            vol: 音量 (0, 10]，默认1.0
            pitch: 语调 [-12, 12]，默认0
            sample_rate: 采样率 [8000,16000,22050,24000,32000,44100]，默认32000
            format: 音频格式 [mp3, pcm, flac, wav(仅非流式)]，默认mp3
            bitrate: 比特率 [32000,64000,128000,256000]，默认128000
            channel: 声道数 [1,2]，默认1
            stream: 是否流式输出，默认False
            language_boost: 语言增强 [Chinese, English, auto, 等40种语言]
            subtitle_enable: 是否启用字幕，默认False
            output_format: 输出格式 [url, hex]，默认hex

        Returns:
            音频数据URL或hex编码
        """
        self._log("🎤 开始语音合成...")

        # 参数验证
        if len(text) > 10000:
            raise ValueError("文本长度不能超过10000字符")
        if speed < 0.5 or speed > 2.0:
            raise ValueError("语速参数必须在0.5-2.0之间")
        if vol <= 0 or vol > 10:
            raise ValueError("音量参数必须在(0,10]之间")
        if pitch < -12 or pitch > 12:
            raise ValueError("语调参数必须在-12到12之间")
        if sample_rate not in [8000, 16000, 22050, 24000, 32000, 44100]:
            raise ValueError("采样率必须是8000,16000,22050,24000,32000,44100之一")
        if format not in ["mp3", "pcm", "flac", "wav"]:
            raise ValueError("音频格式必须是mp3,pcm,flac,wav之一")
        if format == "wav" and stream:
            raise ValueError("wav格式仅支持非流式输出")
        if bitrate not in [32000, 64000, 128000, 256000]:
            raise ValueError("比特率必须是32000,64000,128000,256000之一")
        if channel not in [1, 2]:
            raise ValueError("声道数必须是1或2")

        # 构建请求数据
        data = {
            "model": "speech-2.6-hd",
            "text": text,
            "stream": stream,
            "voice_setting": {
                "voice_id": voice_id,
                "emotion": emotion,
                "speed": speed,
                "vol": vol,
                "pitch": pitch
            },
            "audio_setting": {
                "sample_rate": sample_rate,
                "format": format,
                "bitrate": bitrate,
                "channel": channel
            },
            "subtitle_enable": subtitle_enable,
            "output_format": output_format
        }

        # 添加可选参数
        if language_boost:
            data["language_boost"] = language_boost

        if stream:
            data["stream_options"] = {
                "exclude_aggregated_audio": False
            }

        response = self._request("POST", "t2a_v2", json=data)

        # 处理响应
        if stream:
            # 流式响应处理
            self._log("📡 流式语音合成完成")
            # TODO: 实现流式音频合并
            return response.get('data', {}).get('audio', '')
        else:
            audio_url = response.get('data', {}).get('audio', '')
            self._log("🗣️ 语音合成完成")

            # 显示音频信息
            extra_info = response.get('extra_info', {})
            if extra_info:
                self._log(f"📊 音频信息: 时长{extra_info.get('audio_length', 0)//1000}秒, "
                         f"大小{extra_info.get('audio_size', 0)//1024}KB, "
                         f"字数{extra_info.get('word_count', 0)}")

            return audio_url

    def tts_advanced(self, text: str, voice_id: str = "female-chengshu",
                           pronunciation_dict: dict = None,
                           timber_weights: list = None,
                           voice_modify: dict = None,
                           aigc_watermark: bool = False,
                           text_normalization: bool = False,
                           latex_read: bool = False) -> str:
        """高级文本转语音，支持音色混合、发音字典、音效等高级功能

        Args:
            text: 需要合成语音的文本
            voice_id: 基础音色ID
            pronunciation_dict: 发音字典 {"tone": ["处理/(chu3)(li3)", "omg/oh my god"]}
            timber_weights: 音色混合 [{"voice_id": "female-chengshu", "weight": 30}, ...]
            voice_modify: 音效设置 {"pitch": 50, "intensity": -30, "timbre": 20, "sound_effects": "robotic"}
            aigc_watermark: 是否添加音频水印
            text_normalization: 是否启用文本规范化
            latex_read: 是否朗读latex公式

        Returns:
            音频数据URL或hex编码
        """
        self._log("🎨 开始高级语音合成...")

        # 构建请求数据
        data = {
            "model": "speech-2.6-hd",
            "text": text,
            "stream": False,
            "voice_setting": {
                "voice_id": voice_id if not timber_weights else "",  # 混合音色时voice_id为空
                "emotion": "calm",
                "speed": 1.0,
                "vol": 1.0,
                "pitch": 0,
                "text_normalization": text_normalization,
                "latex_read": latex_read
            },
            "audio_setting": {
                "sample_rate": 32000,
                "format": "mp3",
                "bitrate": 128000,
                "channel": 1
            },
            "aigc_watermark": aigc_watermark,
            "output_format": "hex"
        }

        # 添加可选参数
        if pronunciation_dict:
            data["pronunciation_dict"] = pronunciation_dict

        if timber_weights:
            data["timber_weights"] = timber_weights

        if voice_modify:
            data["voice_modify"] = voice_modify

        response = self._request("POST", "t2a_v2", json=data)
        audio_url = response.get('data', {}).get('audio', '')
        self._log("🎭 高级语音合成完成")

        # 显示高级功能信息
        if timber_weights:
            self._log(f"🎵 音色混合: {len(timber_weights)}种音色")
        if pronunciation_dict:
            self._log(f"📝 发音字典: {len(pronunciation_dict.get('tone', []))}个自定义发音")
        if voice_modify:
            self._log(f"🎛️ 音效处理: {list(voice_modify.keys())}")

        return audio_url

    def tts_stream(self, text: str, voice_id: str = "female-chengshu",
                         callback_func=None, **kwargs) -> str:
        """流式文本转语音

        Args:
            text: 需要合成语音的文本
            voice_id: 音色ID
            callback_func: 流式数据回调函数
            **kwargs: 其他TTS参数

        Returns:
            最终合并的音频数据
        """
        self._log("📡 开始流式语音合成...")

        kwargs["stream"] = True
        if "output_format" not in kwargs:
            kwargs["output_format"] = "hex"  # 流式仅支持hex格式

        # 使用基础TTS方法进行流式调用
        audio_chunks = []
        # TODO: 实现真正的流式处理和回调

        return self.tts(text, voice_id, **kwargs)

    def list_voices(self, voice_type: str = "all") -> Dict[str, Any]:
        """查询可用音色列表"""
        self._log("🔍 查询可用音色列表...")
        
        # 检查缓存
        cache_file = Path("./cache/voices.json")
        cache_file.parent.mkdir(exist_ok=True)
        
        # 缓存有效期：2小时
        cache_valid = False
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    if cache_data.get('voice_type') == voice_type:
                        cache_time = datetime.fromisoformat(cache_data.get('timestamp', ''))
                        if (datetime.now() - cache_time).total_seconds() < 7200:  # 2小时
                            self._log("📋 使用缓存数据")
                            return cache_data.get('data', {})
            except Exception:
                pass
        
        # API支持的参数映射
        valid_types = {
            'system': 'system',
            'cloning': 'voice_cloning',
            'generation': 'voice_generation',
            'music': 'music_generation',
            'all': 'all'
        }
        
        # 使用有效的API参数
        api_param = valid_types.get(voice_type, 'all')
        
        # 调用API获取最新数据
        url = "https://api.minimaxi.com/v1/get_voice"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {'voice_type': api_param}
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # 缓存结果
            cache_data = {
                'voice_type': voice_type,
                'timestamp': datetime.now().isoformat(),
                'data': result
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self._log("✅ 音色列表已更新并缓存")
            return result
            
        except Exception as e:
            # 如果API失败，尝试使用缓存（即使过期也显示提示）
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                        self._log("⚠️ 使用过期缓存数据，建议稍后刷新", "WARN")
                        return cache_data.get('data', {})
                except Exception:
                    pass
            
            self._log(f"❌ 获取音色列表失败: {e}", "ERROR")
            return {}
    
    def podcast(self, user_input: str) -> str:
        """智能播客生成 - 完全自然语言输入"""
        self._log("🎙️ 开始生成智能播客...")
        
        # 读取系统提示词模板
        template_path = Path("templates/podcast_system_prompt.txt")
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
        else:
            system_prompt = "你是一个智能播客生成助手，请根据用户描述生成JSON格式对话。"
        
        # 定义JSON schema确保格式正确
        json_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "speaker": {"type": "string", "description": "说话人姓名"},
                    "text": {"type": "string", "description": "说话内容"},
                    "voice_id": {"type": "string", "description": "音色ID"},
                    "emotion": {"type": "string", "enum": ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm"], "description": "情感类型"}
                },
                "required": ["speaker", "text", "voice_id", "emotion"],
                "additionalProperties": False
            },
            "minItems": 2
        }
        
        # 构建消息结构
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # 使用标准格式请求，避免response_format参数
        data = {
            "model": "MiniMax-M2",
            "messages": messages,
            "max_tokens": 20480,
            "temperature": 0.8
        }
        
        response = self._request("POST", "text/chatcompletion_v2", json=data)
        content = response['choices'][0]['message']['content']
        
        # 保存原始响应到本地文件
        log_dir = Path('./output/logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存完整的API响应
        response_log = {
            "timestamp": timestamp,
            "user_input": user_input,
            "response": content,
            "dialogue_count": None,
            "status": "success"
        }
        
        try:
            # 清理可能的Markdown格式并解析JSON
            cleaned_content = content.strip()
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()
            
            dialogues = json.loads(cleaned_content)
            response_log["dialogue_count"] = len(dialogues)
            
            # 保存解析后的JSON文件
            json_file = log_dir / f"podcast_dialogue_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(dialogues, f, ensure_ascii=False, indent=2)
            
            # 保存完整响应日志
            log_file = log_dir / f"podcast_response_{timestamp}.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(response_log, f, ensure_ascii=False, indent=2)
            
            self._log(f"📝 对话内容已保存: {json_file}")
            self._log(f"🎭 成功解析对话：{len(dialogues)} 段")
            
            # 为每段生成音频
            audio_segments = []
            for dialogue in dialogues:
                speaker = dialogue.get('speaker', '未知')
                text = dialogue.get('text', '')
                voice_id = dialogue.get('voice_id', 'female-chengshu')
                emotion = dialogue.get('emotion', 'calm')
                
                if text and len(text.strip()) > 5:
                    # 验证并修正情感类型
                    valid_emotions = ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm"]
                    corrected_emotion = emotion.lower()
                    if corrected_emotion not in valid_emotions:
                        # 智能映射到有效情感
                        emotion_mapping = {
                            "excited": "happy",
                            "joyful": "happy",
                            "delighted": "happy",
                            "cheerful": "happy",
                            "upset": "sad",
                            "depressed": "sad",
                            "disappointed": "sad",
                            "mad": "angry",
                            "furious": "angry",
                            "irritated": "angry",
                            "scared": "fearful",
                            "terrified": "fearful",
                            "anxious": "fearful",
                            "shocked": "surprised",
                            "amazed": "surprised",
                            "startled": "surprised",
                            "disgusted": "disgusted",
                            "revolted": "disgusted",
                            "neutral": "calm",
                            "thoughtful": "calm",
                            "curious": "surprised",
                            "concerned": "fearful",
                            "nostalgic": "sad",
                            "proud": "happy",
                            "confident": "happy"
                        }
                        corrected_emotion = emotion_mapping.get(corrected_emotion, "calm")
                        self._log(f"⚠️ 情感映射: {emotion} → {corrected_emotion}")
                    
                    self._log(f"🗣️ {speaker}({voice_id}): {text[:50]}...")
                    audio = self.tts(text.strip(), voice_id, corrected_emotion)
                    audio_segments.append(audio)
            
            if audio_segments:
                # 合并所有音频
                combined_audio = "".join(audio_segments)
                self._log("✅ 播客生成完成")
                return combined_audio
            else:
                self._log("❌ 没有有效音频内容", "ERROR")
                return ""
                
        except json.JSONDecodeError as e:
            response_log["status"] = "error"
            response_log["error"] = str(e)
            
            # 保存错误日志
            log_file = log_dir / f"podcast_error_{timestamp}.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(response_log, f, ensure_ascii=False, indent=2)
                
            self._log(f"❌ JSON解析失败: {e}", "ERROR")
            self._log(f"📝 错误日志已保存: {log_file}")
            if self.verbose:
                self._log(f"📝 原始内容: {content}")
            return ""

class FileManager:
    """文件管理"""
    
    def __init__(self):
        self.base_dir = Path('./output')
        self.base_dir.mkdir(exist_ok=True)
        
        for subdir in ['audio', 'images', 'videos', 'music', 'podcasts']:
            (self.base_dir / subdir).mkdir(exist_ok=True)
    
    def save_file(self, data: str, filename: str, subdir: str) -> str:
        """保存文件"""
        filepath = self.base_dir / subdir / filename
        
        if data.startswith('http'):
            # 下载URL
            import urllib.request
            urllib.request.urlretrieve(data, filepath)
        else:
            # 保存十六进制数据
            with open(filepath, 'wb') as f:
                f.write(bytes.fromhex(data))
        
        return str(filepath)
    
    def play_audio(self, filepath: str):
        """自动播放音频文件"""
        import subprocess
        import platform
        
        try:
            system = platform.system()
            if system == "Windows":
                subprocess.run(["start", filepath], shell=True, check=True)
            elif system == "Darwin":  # macOS
                subprocess.run(["afplay", filepath], check=True)
            elif system == "Linux":
                subprocess.run(["mpg123", filepath], check=True)
            else:
                print(f"📁 音频已保存，请手动播放: {filepath}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"📁 音频已保存，请手动播放: {filepath}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='MiniMax AI 工具')
    
    # 🎯 核心功能（参数支持内容或.txt/.md文件路径）
    generate_group = parser.add_argument_group('核心功能（参数支持内容或.txt/.md文件路径）')
    generate_group.add_argument('-c', '--chat', metavar='对话内容', help='AI智能对话')
    generate_group.add_argument('-i', '--image', metavar='图像描述', help='AI图像生成')
    generate_group.add_argument('-v', '--video', metavar='视频描述', help='AI视频生成')
    generate_group.add_argument('-m', '--music', metavar='音乐描述', help='AI音乐生成')
    generate_group.add_argument('-t', '--tts', metavar='语音文本', help='文本转语音')
    generate_group.add_argument('-p', '--podcast', metavar='播客主题', help='AI播客生成')
    
    # 🎨 图像生成选项
    image_group = parser.add_argument_group('图像生成选项')
    image_group.add_argument('--n', type=int, default=1, choices=range(1, 10), help='生成图片数量 (1-9)，默认1')
    image_group.add_argument('--aspect-ratio', default='1:1', choices=['1:1', '16:9', '4:3', '3:2', '2:3', '3:4', '9:16', '21:9'], help='图像宽高比，默认1:1')
    image_group.add_argument('--seed', type=int, help='随机种子，相同种子生成相似图片')
    image_group.add_argument('--width', type=int, help='图像宽度(像素)，512-2048且8的倍数，需与height同时设置')
    image_group.add_argument('--height', type=int, help='图像高度(像素)，512-2048且8的倍数，需与width同时设置')
    image_group.add_argument('--response-format', default='url', choices=['url', 'base64'], help='返回格式，默认url')
    image_group.add_argument('--prompt-optimizer', action='store_true', help='启用prompt自动优化')
    image_group.add_argument('--add-watermark', action='store_true', help='添加图片水印')

    # 🎨 图像风格选项（仅image-01-live模型）
    style_group = parser.add_argument_group('图像风格选项')
    style_group.add_argument('--image-model', default='image-01', choices=['image-01', 'image-01-live'], help='图像生成模型，默认image-01')
    style_group.add_argument('--style-type', choices=['漫画', '元气', '中世纪', '水彩'], help='画风风格类型，仅image-01-live模型生效')
    style_group.add_argument('--style-weight', type=float, default=0.8, help='画风权重(0-1]，默认0.8')

    # 📷 图生图选项
    i2i_group = parser.add_argument_group('图生图选项')
    i2i_group.add_argument('-i2i', '--image-to-image', nargs=2, metavar=('REFERENCE_IMAGE', 'PROMPT'),
                          help='图生图: 参考图片路径/URL + 描述文本')
    i2i_group.add_argument('--ref-image', help='参考图片路径或URL（用于图生图）')
    
    # 🎭 音色管理
    voice_group = parser.add_argument_group('音色管理')
    voice_group.add_argument('--voice', type=str, default="female-chengshu", 
                            help='指定音色ID (如: male-qn-jingying, female-yujie)')
    voice_group.add_argument('-l', '--list-voices', choices=['system', 'cloning', 'generation', 'music', 'all'], 
                            help='查询可用音色列表')
    voice_group.add_argument('-r', '--refresh-voices', action='store_true', help='强制刷新音色缓存')
    voice_group.add_argument('-f', '--filter-voices', type=str, help='过滤音色列表关键词')

    # 📁 文件管理
    file_group = parser.add_argument_group('文件管理')
    file_group.add_argument('--upload-file', type=str, metavar='FILE_PATH', help='上传文件到MiniMax平台')
    file_group.add_argument('--file-purpose', default='voice_clone',
                           choices=['voice_clone', 'prompt_audio', 't2a_async_input'],
                           help='文件使用目的，默认voice_clone')
    file_group.add_argument('--list-files', action='store_true', help='列出已上传的文件')
    file_group.add_argument('--file-limit', type=int, default=10, help='文件列表返回数量限制(10-100)，默认10')
    file_group.add_argument('--file-order', choices=['created_at', 'file_size'], help='文件排序方式')
    file_group.add_argument('--retrieve-file', type=str, metavar='FILE_ID', help='检索文件信息')
    file_group.add_argument('--download-file', type=str, metavar='FILE_ID', help='下载文件')
    file_group.add_argument('--save-path', type=str, metavar='PATH', help='下载文件保存路径')
    file_group.add_argument('--delete-file', type=str, metavar='FILE_ID', help='删除文件')
    file_group.add_argument('--delete-purpose', choices=['voice_clone', 'prompt_audio', 't2a_async', 't2a_async_input', 'video_generation'], help='删除文件时指定的用途')

    # 🎵 音乐生成
    music_group = parser.add_argument_group('音乐生成')
    music_group.add_argument('--lyrics', help='音乐歌词内容或文件路径(.txt/.md) [必填: 10-3000字符]')
    music_group.add_argument('--music-stream', action='store_true', help='启用流式传输（仅支持hex格式）')
    music_group.add_argument('--music-format', default='hex', choices=['hex', 'url'], help='音频返回格式，默认hex')
    music_group.add_argument('--music-sample-rate', type=int, default=44100, choices=[16000, 24000, 32000, 44100], help='音频采样率，默认44100')
    music_group.add_argument('--music-bitrate', type=int, default=256000, choices=[32000, 64000, 128000, 256000], help='音频比特率，默认256000')
    music_group.add_argument('--music-encoding', default='mp3', choices=['mp3', 'wav', 'pcm'], help='音频编码格式，默认mp3')
    music_group.add_argument('--music-watermark', action='store_true', help='在音频末尾添加水印（仅非流式生效）')

    # 🎤 语音合成高级选项
    tts_group = parser.add_argument_group('语音合成选项')
    tts_group.add_argument('--emotion', default='calm',
                          choices=['happy', 'sad', 'angry', 'fearful', 'disgusted', 'surprised', 'calm', 'fluent'],
                          help='语音情感控制，默认calm')
    tts_group.add_argument('--speed', type=float, default=1.0, help='语速 (0.5-2.0)，默认1.0')
    tts_group.add_argument('--vol', type=float, default=1.0, help='音量 (0.1-10.0)，默认1.0')
    tts_group.add_argument('--pitch', type=int, default=0, help='语调 (-12到12)，默认0')
    tts_group.add_argument('--sample-rate', type=int, default=32000,
                          choices=[8000, 16000, 22050, 24000, 32000, 44100],
                          help='采样率，默认32000')
    tts_group.add_argument('--format', default='mp3',
                          choices=['mp3', 'pcm', 'flac', 'wav'],
                          help='音频格式，默认mp3')
    tts_group.add_argument('--bitrate', type=int, default=128000,
                          choices=[32000, 64000, 128000, 256000],
                          help='比特率，默认128000')
    tts_group.add_argument('--channel', type=int, default=1, choices=[1, 2], help='声道数，默认1')
    tts_group.add_argument('--stream', action='store_true', help='启用流式输出')
    tts_group.add_argument('--language-boost', help='语言增强 (Chinese, English, auto等)')
    tts_group.add_argument('--subtitle', action='store_true', help='启用字幕生成')
    tts_group.add_argument('--output-format', default='hex', choices=['hex', 'url'], help='输出格式，默认hex')
    
    # 📺 视频管理
    video_group = parser.add_argument_group('视频管理')
    video_group.add_argument('-s', '--video-status', metavar='任务ID', help='查询视频状态（传入task_id）')
    video_group.add_argument('-d', '--download-video', metavar='文件ID', help='下载视频文件（传入file_id）')

    # 🎬 视频生成选项
    video_gen_group = parser.add_argument_group('视频生成选项')
    video_gen_group.add_argument('--video-model', default='MiniMax-Hailuo-2.3',
                                choices=[
                                    'MiniMax-Hailuo-2.3', 'MiniMax-Hailuo-2.3-Fast', 'MiniMax-Hailuo-02',
                                    'T2V-01-Director', 'T2V-01',  # 文生视频
                                    'I2V-01-Director', 'I2V-01-live', 'I2V-01',  # 图生视频
                                    'S2V-01'  # 主体参考视频生成
                                ],
                                help='视频生成模型，默认MiniMax-Hailuo-2.3')
    video_gen_group.add_argument('--video-duration', type=int, default=6, help='视频时长（秒），默认6')
    video_gen_group.add_argument('--video-resolution', default='auto', choices=['auto', '720P', '768P', '1080P'], help='视频分辨率，默认auto（根据模型自动选择）')
    video_gen_group.add_argument('--first-frame', help='首帧图片URL或路径（图生视频/首尾帧生成必需）')
    video_gen_group.add_argument('--last-frame', help='尾帧图片URL或路径（首尾帧生成必需）')
    video_gen_group.add_argument('--subject-image', help='主体参考图片URL或路径')
    video_gen_group.add_argument('--video-name', help='视频文件名')

    # 🔗 首尾帧生成专用参数
    se_group = parser.add_argument_group('首尾帧生成选项')
    se_group.add_argument('-se', '--start-end', nargs=2, metavar=('START_IMAGE', 'END_IMAGE'),
                       help='首尾帧生成: 起始图片 + 结束图片')
    se_group.add_argument('--se-duration', type=int, default=6, choices=[6, 10], help='首尾帧视频时长（秒），默认6')
    se_group.add_argument('--se-resolution', default='768P', choices=['768P', '1080P'], help='首尾帧视频分辨率，默认768P')

    # 🖼️ 图生视频专用参数
    i2v_group = parser.add_argument_group('图生视频选项')
    i2v_group.add_argument('-i2v', '--image-to-video', nargs=2, metavar=('IMAGE', 'PROMPT'),
                           help='图生视频: 图片路径/URL + 描述文本')
    i2v_group.add_argument('--i2v-model', default='I2V-01',
                         choices=['I2V-01-Director', 'I2V-01-live', 'I2V-01',
                                 'MiniMax-Hailuo-2.3', 'MiniMax-Hailuo-2.3-Fast', 'MiniMax-Hailuo-02'],
                         help='图生视频模型，默认I2V-01')
    i2v_group.add_argument('--i2v-duration', type=int, default=6, help='图生视频时长（秒），默认6')
    i2v_group.add_argument('--i2v-resolution', default='auto', choices=['auto', '512P', '720P', '768P', '1080P'],
                         help='图生视频分辨率，默认auto')

    # 👤 主体参考视频生成专用参数
    s2v_group = parser.add_argument_group('主体参考视频选项')
    s2v_group.add_argument('-s2v', '--subject-reference', nargs=2, metavar=('SUBJECT_IMAGE', 'PROMPT'),
                          help='主体参考视频生成: 主体图片 + 描述文本')
    s2v_group.add_argument('--s2v-prompt-optimizer', action='store_true', help='启用prompt优化（默认启用）')

    # 🎥 高级视频选项
    video_adv_group = parser.add_argument_group('高级视频选项')
    video_adv_group.add_argument('--no-prompt-optimizer', action='store_true', help='禁用prompt自动优化')
    video_adv_group.add_argument('--fast-preprocessing', action='store_true', help='启用快速预处理（仅Hailuo模型）')
    video_adv_group.add_argument('--video-watermark', action='store_true', help='添加视频水印')
    video_adv_group.add_argument('--callback-url', help='任务状态回调URL')
    video_adv_group.add_argument('--camera-sequence', help='镜头序列JSON，如[{"action":"推进","timing":"开始"}]')
    
    # ⚙️ 通用选项
    common_group = parser.add_argument_group('通用选项')
    common_group.add_argument('-I', '--interactive', action='store_true', help='交互模式')
    common_group.add_argument('-V', '--verbose', action='store_true', help='显示详细日志')
    common_group.add_argument('-P', '--play', action='store_true', help='生成后自动播放音频')
    
    args = parser.parse_args()
    
    client = MiniMaxClient()
    file_mgr = FileManager()
    
    if args.verbose:
        client.verbose = True
    
    if args.interactive:
        print("💬 MiniMax AI 交互模式 (输入 'quit' 退出)")
        while True:
            try:
                cmd = input("\n选择功能 [chat/image/video/music/tts/quit]: ").strip()
                if cmd == 'quit':
                    break
                elif cmd == 'chat':
                    message = input("消息: ")
                    print(client.chat(message))
                elif cmd == 'image':
                    prompt = input("描述: ")
                    urls = client.image(prompt)
                    for url in urls:
                        print(url)
                        save = input("保存文件? (y/n): ")
                        if save.lower() == 'y':
                            filepath = file_mgr.save_file(url, f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg", "images")
                            print(f"✅ 已保存: {filepath}")
                elif cmd == 'video':
                    prompt = input("描述: ")
                    task_id = client.video(prompt)
                    print(f"🎬 任务ID: {task_id}")
                    check = input("查询状态? (y/n): ")
                    if check.lower() == 'y':
                        status = client.video_status(task_id)
                        print(f"状态: {status}")
                elif cmd == 'music':
                    prompt = input("音乐描述: ")
                    lyrics = input("歌词内容: ")
                    if not lyrics.strip():
                        print("❌ 音乐生成需要歌词内容")
                        continue
                    
                    audio = client.music(prompt, lyrics)
                    if audio:
                        filepath = file_mgr.save_file(audio, f"music_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3", "music")
                        print(f"✅ 音乐已保存: {filepath}")
                elif cmd == 'tts':
                    text = input("文本: ")
                    voice = input("音色ID (默认 female-chengshu): ").strip() or "female-chengshu"
                    audio = client.tts(text, voice)
                    if audio:
                        filepath = file_mgr.save_file(audio, f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3", "audio")
                        print(f"✅ 已保存: {filepath}")
                elif cmd == 'podcast':
                    user_input = input("播客描述: ")
                    audio = client.podcast(user_input)
                    if audio:
                        filepath = file_mgr.save_file(audio, f"podcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3", "podcasts")
                        print(f"✅ 播客已保存: {filepath}")
            except KeyboardInterrupt:
                break
    
    elif args.chat:
        content = args.chat
        if content.endswith(('.txt', '.md')) and Path(content).exists():
            with open(content, 'r', encoding='utf-8') as f:
                content = f.read()
        print(client.chat(content))
    elif args.image_to_image:
        # 图生图处理
        reference_image, prompt = args.image_to_image

        result = client.image(
            prompt=prompt,
            model=args.image_model,
            n=args.n,
            aspect_ratio=args.aspect_ratio,
            width=args.width,
            height=args.height,
            seed=args.seed,
            response_format=args.response_format,
            prompt_optimizer=args.prompt_optimizer,
            aigc_watermark=args.add_watermark,
            style_type=args.style_type,
            style_weight=args.style_weight,
            reference_image=reference_image
        )

        # 处理图生图结果
        if result:
            for i, item in enumerate(result):
                if args.response_format == 'url':
                    filepath = file_mgr.save_file(item, f"image2image_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}.jpg", "images")
                    print(f"✅ 图生图已保存: {filepath}")
                    print(f"🔗 图片URL: {item}")
                    if args.play:
                        import webbrowser
                        webbrowser.open(item)
                else:
                    import base64
                    try:
                        image_data = base64.b64decode(item)
                        filepath = Path('./output/images') / f"image2image_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}.jpg"
                        filepath.parent.mkdir(exist_ok=True)
                        with open(filepath, 'wb') as f:
                            f.write(image_data)
                        print(f"✅ 图生图Base64已保存: {filepath}")
                        print(f"📊 图片大小: {len(image_data)} 字节")
                    except Exception as e:
                        print(f"❌ Base64图片保存失败: {e}")
    elif args.image:
        prompt = args.image
        if prompt.endswith(('.txt', '.md')) and Path(prompt).exists():
            with open(prompt, 'r', encoding='utf-8') as f:
                prompt = f.read()

        # 使用新的图像生成参数
        result = client.image(
            prompt=prompt,
            model=args.image_model,
            n=args.n,
            aspect_ratio=args.aspect_ratio,
            width=args.width,
            height=args.height,
            seed=args.seed,
            response_format=args.response_format,
            prompt_optimizer=args.prompt_optimizer,
            aigc_watermark=args.add_watermark,
            style_type=args.style_type,
            style_weight=args.style_weight,
            reference_image=args.ref_image
        )

        if result:
            for i, item in enumerate(result):
                if args.response_format == 'url':
                    # URL格式：下载并保存
                    filepath = file_mgr.save_file(item, f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}.jpg", "images")
                    print(f"✅ 图片已保存: {filepath}")
                    print(f"🔗 图片URL: {item}")
                    if args.play:
                        import webbrowser
                        webbrowser.open(item)
                else:
                    # Base64格式：保存为文件
                    import base64
                    try:
                        # 解码Base64数据
                        image_data = base64.b64decode(item)
                        filepath = Path('./output/images') / f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}.jpg"
                        filepath.parent.mkdir(exist_ok=True)
                        with open(filepath, 'wb') as f:
                            f.write(image_data)
                        print(f"✅ Base64图片已保存: {filepath}")
                        print(f"📊 图片大小: {len(image_data)} 字节")
                    except Exception as e:
                        print(f"❌ Base64图片保存失败: {e}")
                        print(f"🔗 Base64数据前50字符: {item[:50]}...")
    elif args.video:
        prompt = args.video
        if prompt.endswith(('.txt', '.md')) and Path(prompt).exists():
            with open(prompt, 'r', encoding='utf-8') as f:
                prompt = f.read()

        # 处理镜头序列
        camera_sequence = None
        if args.camera_sequence:
            try:
                camera_sequence = json.loads(args.camera_sequence)
                print(f"🎥 镜头序列: {len(camera_sequence)}个镜头")
            except json.JSONDecodeError:
                print(f"❌ 镜头序列JSON格式错误: {args.camera_sequence}")

        # 智能选择分辨率
        resolution = args.video_resolution
        if resolution == 'auto':
            # 根据模型自动选择最佳分辨率
            if args.video_model in ['T2V-01-Director', 'T2V-01', 'I2V-01-Director', 'I2V-01-live', 'I2V-01']:
                resolution = '720P'
            elif args.video_model in ['MiniMax-Hailuo-2.3', 'MiniMax-Hailuo-2.3-Fast']:
                resolution = '768P'  # 默认使用768P以获得更好质量
            elif args.video_model == 'MiniMax-Hailuo-02':
                resolution = '768P'  # Hailuo-02支持512P，默认768P
            else:
                resolution = '720P'
            print(f"🎯 自动选择分辨率: {resolution}")

        # 检查是否使用高级视频生成参数
        if any([args.first_frame, args.last_frame, args.subject_image, args.camera_sequence,
                args.no_prompt_optimizer, args.fast_preprocessing, args.video_watermark,
                args.callback_url, args.video_model != 'MiniMax-Hailuo-2.3',
                args.video_duration != 6, args.video_resolution != 'auto', args.video_name]):

            # 使用高级视频生成方法
            task_id = client.video_advanced(
                prompt=prompt,
                model=args.video_model,
                first_frame_image=args.first_frame,
                last_frame_image=args.last_frame,
                subject_image=args.subject_image,
                duration=args.video_duration,
                resolution=resolution,
                video_name=args.video_name,
                prompt_optimizer=not args.no_prompt_optimizer,
                aigc_watermark=args.video_watermark,
                callback_url=args.callback_url
            )

            # 如果有镜头序列，且不是主体参考视频，使用专门的镜头控制方法
            if camera_sequence and args.video_model != 'S2V-01':
                task_id = client.video_with_camera_control(
                    prompt=prompt,
                    camera_sequence=camera_sequence,
                    model=args.video_model,
                    duration=args.video_duration,
                    resolution=resolution,
                    prompt_optimizer=not args.no_prompt_optimizer,
                    fast_pretreatment=args.fast_preprocessing,
                    aigc_watermark=args.video_watermark,
                    callback_url=args.callback_url
                )
        else:
            # 使用基础视频生成（默认参数）
            task_id = client.video(prompt, model=args.video_model)

        print(f"🎬 视频生成任务已提交")
        print(f"📊 任务ID: {task_id}")
        print(f"🎭 使用模型: {args.video_model}")
        print(f"⏱️  预计3-8分钟完成，可多次查询状态")
        print(f"💡 查询状态: python minimax_cli.py -s {task_id}")
    elif args.image_to_video:
        # 图生视频处理
        image_path, prompt = args.image_to_video

        # 智能选择分辨率
        i2v_resolution = args.i2v_resolution
        if i2v_resolution == 'auto':
            if args.i2v_model in ['I2V-01-Director', 'I2V-01-live', 'I2V-01']:
                i2v_resolution = '720P'
            elif args.i2v_model in ['MiniMax-Hailuo-2.3', 'MiniMax-Hailuo-2.3-Fast']:
                i2v_resolution = '768P'
            elif args.i2v_model == 'MiniMax-Hailuo-02':
                i2v_resolution = '768P'
            else:
                i2v_resolution = '720P'
            print(f"🎯 自动选择分辨率: {i2v_resolution}")

        task_id = client.image_to_video(
            first_frame_image=image_path,
            prompt=prompt,
            model=args.i2v_model,
            duration=args.i2v_duration,
            resolution=i2v_resolution,
            prompt_optimizer=not args.no_prompt_optimizer,
            fast_pretreatment=args.fast_preprocessing,
            aigc_watermark=args.video_watermark,
            callback_url=args.callback_url
        )

        print(f"🖼️ 图生视频任务已提交")
        print(f"📊 任务ID: {task_id}")
        print(f"🎭 使用模型: {args.i2v_model}")
        print(f"📷 图片: {image_path}")
        print(f"⏱️  预计3-8分钟完成，可多次查询状态")
        print(f"💡 查询状态: python minimax_cli.py -s {task_id}")
    elif args.subject_reference:
        # 主体参考视频生成处理
        subject_image, prompt = args.subject_reference

        task_id = client.subject_reference_to_video(
            subject_image=subject_image,
            prompt=prompt,
            prompt_optimizer=not args.no_prompt_optimizer,
            aigc_watermark=args.video_watermark,
            callback_url=args.callback_url
        )

        print(f"👤 主体参考视频任务已提交")
        print(f"📊 任务ID: {task_id}")
        print(f"🎭 使用模型: S2V-01")
        print(f"👤 主体图片: {subject_image}")
        print(f"📝 视频描述: {prompt}")
        print(f"💡 查询状态: python minimax_cli.py -s {task_id}")
    elif args.start_end:
        # 首尾帧生成处理
        start_image, end_image = args.start_end

        task_id = client.start_end_to_video(
            first_frame_image=start_image,
            last_frame_image=end_image,
            duration=args.se_duration,
            resolution=args.se_resolution,
            prompt_optimizer=not args.no_prompt_optimizer,
            aigc_watermark=args.video_watermark,
            callback_url=args.callback_url
        )

        print(f"🔗 首尾帧视频任务已提交")
        print(f"📊 任务ID: {task_id}")
        print(f"🎭 使用模型: MiniMax-Hailuo-02")
        print(f"📷 起始图片: {start_image}")
        print(f"📷 结束图片: {end_image}")
        print(f"⏱️  时长: {args.se_duration}秒")
        print(f"📐 分辨率: {args.se_resolution}")
        print(f"💡 查询状态: python minimax_cli.py -s {task_id}")
    elif args.music:
        # 处理文件路径或文本内容
        prompt = args.music
        if prompt.endswith(('.txt', '.md')) and Path(prompt).exists():
            with open(prompt, 'r', encoding='utf-8') as f:
                prompt = f.read()
        
        # 歌词为必填
        if not args.lyrics:
            print("❌ 音乐生成需要歌词参数")
            print("💡 使用: --lyrics '歌词内容' 或 --lyrics lyrics.txt")
            print("📝 提示: 使用换行符分隔，支持[Intro][Verse][Chorus][Bridge][Outro]结构")
            sys.exit(1)
        
        lyrics = args.lyrics
        if lyrics.endswith(('.txt', '.md')) and Path(lyrics).exists():
            with open(lyrics, 'r', encoding='utf-8') as f:
                lyrics = f.read()
        
        # 使用新的音乐生成参数
        audio = client.music(
            prompt=prompt,
            lyrics=lyrics,
            stream=args.music_stream,
            output_format=args.music_format,
            sample_rate=args.music_sample_rate,
            bitrate=args.music_bitrate,
            format=args.music_encoding,
            aigc_watermark=args.music_watermark
        )

        if audio:
            # 根据返回格式处理音频
            if args.music_format == 'url':
                # URL格式：下载并保存
                ext = args.music_encoding
                filepath = file_mgr.save_file(audio, f"music_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}", "music")
                print(filepath)
                if args.play:
                    file_mgr.play_audio(filepath)
            else:
                # Hex格式：保存为文件
                import base64
                try:
                    # 解码hex数据
                    audio_data = bytes.fromhex(audio)
                    ext = args.music_encoding
                    filepath = Path('./output/music') / f"music_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                    filepath.parent.mkdir(exist_ok=True)
                    with open(filepath, 'wb') as f:
                        f.write(audio_data)
                    print(f"✅ 音乐已保存: {filepath}")
                    print(f"📊 音频大小: {len(audio_data)} 字节")
                    if args.play:
                        file_mgr.play_audio(str(filepath))
                except Exception as e:
                    print(f"❌ 音频保存失败: {e}")
                    print(f"🔗 音频数据前50字符: {audio[:50]}...")
    elif args.tts:
        text = args.tts
        if text.endswith(('.txt', '.md')) and Path(text).exists():
            with open(text, 'r', encoding='utf-8') as f:
                text = f.read()

        # 使用新的高级TTS参数
        audio = client.tts(
            text=text,
            voice_id=args.voice,
            emotion=args.emotion,
            speed=args.speed,
            vol=args.vol,
            pitch=args.pitch,
            sample_rate=args.sample_rate,
            format=args.format,
            bitrate=args.bitrate,
            channel=args.channel,
            stream=args.stream,
            language_boost=args.language_boost,
            subtitle_enable=args.subtitle,
            output_format=args.output_format
        )

        if audio:
            # 根据格式决定文件扩展名
            ext = args.format
            if args.output_format == 'url':
                # 如果是URL格式，需要下载文件
                ext = 'mp3'  # URL通常是mp3

            filepath = file_mgr.save_file(audio, f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}", "audio")
            print(filepath)
            if args.play:
                file_mgr.play_audio(filepath)
    elif args.podcast:
        user_input = args.podcast
        if user_input.endswith(('.txt', '.md')) and Path(user_input).exists():
            with open(user_input, 'r', encoding='utf-8') as f:
                user_input = f.read()
        audio = client.podcast(user_input)
        if audio:
            filepath = file_mgr.save_file(audio, f"podcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3", "podcasts")
            print(filepath)
            if args.play:
                file_mgr.play_audio(filepath)
    elif args.video_status:
        status = client.video_status(args.video_status)
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
        # 如果成功，提供下载链接
        if status.get('status') == 'Success':
            file_id = status.get('file_id')
            print(f"🎬 视频已生成，文件ID: {file_id}")
            print(f"📥 下载命令: python minimax_cli.py --download-video {file_id}")
    elif args.download_video:
        filepath = client.download_video(args.download_video)
        print(f"✅ 视频已下载: {filepath}")
    elif args.list_voices or args.refresh_voices:
        voice_type = args.list_voices or "all"
        
        if args.refresh_voices:
            # 强制刷新缓存
            cache_file = Path("./cache/voices.json")
            if cache_file.exists():
                cache_file.unlink()
                print("🔄 已清除音色缓存")
        
        voices_data = client.list_voices(voice_type)
        if not voices_data:
            print("❌ 无法获取音色列表")
            return
            
        filter_keyword = args.filter_voices
        
        # 格式化输出
        def format_voices(voice_list, title):
            if not voice_list:
                return
            
            print(f"\n🎭 {title}")
            for voice in voice_list:
                voice_id = voice.get('voice_id', '')
                name = voice.get('voice_name', voice_id)
                desc = " ".join(voice.get('description', [])) if isinstance(voice.get('description'), list) else str(voice.get('description', ''))
                
                # 过滤关键词
                if filter_keyword and filter_keyword.lower() not in f"{voice_id} {name} {desc}".lower():
                    continue
                    
                print(f"├─ {voice_id:<20} {name:<15} [{desc}]")
        
        # 系统音色
        format_voices(voices_data.get('system_voice', []), "系统音色")
        format_voices(voices_data.get('voice_cloning', []), "克隆音色")
        format_voices(voices_data.get('voice_generation', []), "生成音色")
        format_voices(voices_data.get('music_generation', []), "音乐音色")
        
        total_count = sum(len(voices_data.get(k) or []) for k in ['system_voice', 'voice_cloning', 'voice_generation', 'music_generation'])
        print(f"\n📊 总计: {total_count} 个音色")

    # 📁 文件管理功能
    elif args.upload_file:
        result = client.upload_file(args.upload_file, args.file_purpose)
        if 'error' in result:
            print(f"❌ 上传失败: {result['error']}")
        else:
            file_info = result.get('file', {})
            print(f"✅ 文件上传成功!")
            print(f"📁 文件ID: {file_info.get('file_id', '')}")
            print(f"📄 文件名: {file_info.get('filename', '')}")
            print(f"📊 大小: {file_info.get('bytes', 0)/1024:.1f} KB")
            print(f"🎯 用途: {file_info.get('purpose', '')}")

    elif args.list_files:
        result = client.list_files(limit=args.file_limit, order=args.file_order)
        if 'error' in result:
            print(f"❌ 获取文件列表失败: {result['error']}")
        elif 'files' in result and isinstance(result['files'], list):
            files = result['files']
            # 限制显示的文件数量以符合用户要求
            display_files = files[:args.file_limit]
            print(f"\n📁 文件列表 (显示前 {len(display_files)} 个，总共 {len(files)} 个文件)")
            print("-" * 80)

            for file_info in display_files:
                file_id = file_info.get('file_id', '')
                filename = file_info.get('filename', '')
                bytes_size = file_info.get('bytes', 0)
                purpose = file_info.get('purpose', '')
                created_at = file_info.get('created_at', 0)

                size_str = f"{bytes_size/1024:.1f} KB" if bytes_size > 0 else "未知大小"
                time_str = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S') if created_at else "未知时间"

                print(f"📄 {filename}")
                print(f"   📁 ID: {file_id}")
                print(f"   📊 大小: {size_str}")
                print(f"   🎯 用途: {purpose}")
                print(f"   📅 上传时间: {time_str}")
                print("-" * 40)

            # 显示分页信息
            if 'has_more' in result:
                print(f"\n📄 还有更多文件可获取")
        else:
            print("❌ 响应格式异常")

    # 📁 文件检索功能
    elif args.retrieve_file:
        result = client.retrieve_file(args.retrieve_file)
        if 'error' in result:
            print(f"❌ 检索文件失败: {result['error']}")
        elif 'file' in result:
            file_info = result['file']
            print(f"\n📄 文件详细信息")
            print("-" * 50)
            print(f"📁 文件ID: {file_info.get('file_id', '')}")
            print(f"📄 文件名: {file_info.get('filename', '')}")
            print(f"📊 大小: {file_info.get('bytes', 0)/1024:.1f} KB")
            print(f"🎯 用途: {file_info.get('purpose', '')}")
            if 'download_url' in file_info and file_info['download_url']:
                print(f"🔗 下载链接: {file_info['download_url']}")

            created_at = file_info.get('created_at', 0)
            if created_at:
                time_str = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S')
                print(f"📅 创建时间: {time_str}")
        else:
            print("❌ 响应格式异常")

    # 📁 文件下载功能
    elif args.download_file:
        download_path = client.download_file(args.download_file, args.save_path)
        if download_path.startswith('❌') or download_path.startswith('文件下载失败'):
            print(f"❌ {download_path}")
        else:
            print(f"✅ 文件已下载到: {download_path}")

    # 📁 文件删除功能
    elif args.delete_file:
        if not args.delete_purpose:
            print("❌ 删除文件时必须指定 --delete-purpose 参数")
            print("可选用途: voice_clone, prompt_audio, t2a_async, t2a_async_input, video_generation")
        else:
            result = client.delete_file(args.delete_file, args.delete_purpose)
            if 'error' in result:
                print(f"❌ {result['error']}")
            elif 'base_resp' in result:
                if result['base_resp']['status_code'] == 0:
                    print(f"✅ 文件删除成功: {args.delete_file}")
                else:
                    status_msg = result['base_resp'].get('status_msg', 'Unknown error')
                    print(f"❌ 文件删除失败: {status_msg}")
            else:
                print("❌ 响应格式异常")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()