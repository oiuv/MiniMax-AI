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
    
    def chat(self, message: str, model: str = "MiniMax-M2.1",
             system_prompt: str = None,
             # M2-her 专属参数（暂时注释，等待 API BUG 修复）
             # user_system: str = None, group: str = None,
             # sample_user: str = None, sample_ai: str = None,
             temperature: float = 1.0, max_tokens: int = 2048, stream: bool = False,
             use_anthropic_api: bool = False, show_thinking: bool = False) -> str:
        """智能对话（支持 M2-her 和 Anthropic API 兼容接口）

        Args:
            message: 用户消息内容
            model: 模型名称，可选值：M2-her, MiniMax-M2.1, MiniMax-M2.1-lightning, MiniMax-M2
            system_prompt: 系统提示词（定义 AI 的角色和行为）
            # M2-her 专属参数（暂时注释）
            # user_system: 用户角色设定（用于角色扮演场景定义用户身份）
            # group: 对话分组名称（标识对话场景）
            # sample_user: 示例用户消息（引导模型理解期望的对话风格）
            # sample_ai: 示例 AI 回复（配合 sample_user 使用）
            temperature: 温度参数 (0.0, 1.0]，推荐 1.0
            max_tokens: 最大生成 token 数，M2-her 上限为 2048
            stream: 是否使用流式响应
            use_anthropic_api: 是否使用 Anthropic API 兼容接口
            show_thinking: 是否显示思考过程（仅 Anthropic API 支持）

        Returns:
            模型响应文本，如果 show_thinking=True 则返回包含思考过程的字典
        """
        # 模型映射：M2-her 为对话模型，MiniMax-M2 系列为文本生成模型
        model_mapping = {
            "MiniMax-M2.1": "MiniMax-M2.1",
            "MiniMax-M2.1-lightning": "MiniMax-M2.1-lightning",
            "MiniMax-M2": "MiniMax-M2",
            "M2-her": "M2-her"
        }
        model = model_mapping.get(model, model)

        # 选择 API 端点
        if use_anthropic_api:
            endpoint = "anthropic/v1/messages"
            base_url = "https://api.minimaxi.com/anthropic"
            self._log(f"🤖 使用 Anthropic API 兼容接口 (模型: {model})")
        else:
            endpoint = "text/chatcompletion_v2"
            base_url = self.base_url
            self._log(f"🤖 使用标准 MiniMax API (模型: {model})")

        # 构建请求数据
        if use_anthropic_api:
            # Anthropic API 格式
            messages = [{"role": "user", "content": [{"type": "text", "text": message}]}]
            data = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens
            }
            if system_prompt:
                data["system"] = system_prompt
            if temperature is not None:
                if temperature <= 0 or temperature > 1:
                    raise ValueError(f"temperature 必须在 (0.0, 1.0] 范围内，当前为 {temperature}")
                data["temperature"] = temperature
            if stream:
                data["stream"] = True
        else:
            # 标准 MiniMax API 格式
            messages = []

            # M2-her 支持高级角色类型
            if model == "M2-her":
                # system: 定义 AI 角色
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})

                # user_system, group, sample_user, sample_ai 已暂时注释，等待 API BUG 修复
                # if user_system:
                #     messages.append({"role": "user_system", "content": user_system})
                # if group:
                #     messages.append({"role": "group", "content": group})
                # if sample_user:
                #     messages.append({"role": "sample_message_user", "content": sample_user})
                # if sample_ai:
                #     messages.append({"role": "sample_message_ai", "content": sample_ai})

                # user: 用户消息
                messages.append({"role": "user", "content": message})

                # 构建请求数据
                data = {
                    "model": model,
                    "messages": messages
                }

                # M2-her 参数验证
                if max_tokens > 2048:
                    self._log(f"⚠️ max_tokens 超过 M2-her 上限 2048，已调整为 2048")
                    max_tokens = 2048

            else:
                # 原有模型格式（MiniMax-M2 系列）
                messages = [{"role": "user", "content": message}]
                data = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens
                }
                if system_prompt:
                    # 标准 API 将 system prompt 作为第一条消息
                    messages.insert(0, {"role": "system", "content": system_prompt})

            # 通用参数
            if temperature is not None:
                data["temperature"] = temperature
            if stream:
                data["stream"] = True

        # 发送请求
        if use_anthropic_api:
            # 使用自定义 base_url
            original_base_url = self.base_url
            self.base_url = base_url
            try:
                response = self._request("POST", endpoint, json=data)
            finally:
                self.base_url = original_base_url
        else:
            response = self._request("POST", endpoint, json=data)

        # 解析响应
        if use_anthropic_api:
            return self._parse_anthropic_response(response, show_thinking)
        else:
            # 检查响应是否包含 choices
            if 'choices' not in response or response['choices'] is None:
                self._log(f"❌ API 响应异常: {response}")
                raise ValueError(f"API 响应格式异常: {response}")

            content = response['choices'][0]['message']['content']
            self._log(f"📄 生成内容长度: {len(content)} 字符")
            return content

    def _parse_anthropic_response(self, response: dict, show_thinking: bool = False) -> str | dict:
        """解析 Anthropic API 格式的响应

        Args:
            response: API 响应数据
            show_thinking: 是否显示思考过程

        Returns:
            文本内容或包含思考过程的字典
        """
        # Anthropic API 格式：response.content 是一个列表
        if "content" not in response:
            raise ValueError("无效的 API 响应格式：缺少 content 字段")

        content_blocks = response["content"]
        thinking_text = ""
        response_text = ""

        for block in content_blocks:
            if block.get("type") == "thinking":
                thinking_text = block.get("thinking", "")
            elif block.get("type") == "text":
                response_text = block.get("text", "")

        if show_thinking:
            return {
                "thinking": thinking_text,
                "content": response_text,
                "full_response": content_blocks
            }
        else:
            self._log(f"📄 生成内容长度: {len(response_text)} 字符")
            return response_text
    
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
        success_count = int(metadata.get('success_count', len(result)))
        failed_count = int(metadata.get('failed_count', 0))

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
            elif model in ['MiniMax-Hailuo-2.3', 'MiniMax-Hailuo-02']:
                resolution = '768P'  # Hailuo系列默认768P以获得更好质量
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
        """获取模型支持的时长和分辨率组合（根据官方API文档）

        注意：不同模型在T2V（文生视频）和I2V（图生视频）中的支持度可能不同
        """
        combinations = {
            # Hailuo 系列（支持 T2V 和 I2V）
            "MiniMax-Hailuo-2.3": [(6, "768P"), (10, "768P"), (6, "1080P")],
            "MiniMax-Hailuo-2.3-Fast": [(6, "768P"), (10, "768P"), (6, "1080P")],  # 仅 I2V
            "MiniMax-Hailuo-02": [(6, "512P"), (6, "768P"), (10, "768P"), (6, "1080P")],  # I2V 支持 512P
            # T2V 专用模型
            "T2V-01-Director": [(6, "720P")],
            "T2V-01": [(6, "720P")],
            # I2V 专用模型
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

            # 检查文件大小 (统一20MB限制，API会根据用途自行验证)
            file_size = image_path.stat().st_size
            if file_size > 20 * 1024 * 1024:  # 20MB
                raise ValueError(f"图片文件过大: {file_size/1024/1024:.1f}MB (限制: 20MB，图生图建议10MB以内)")

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
            elif model in ['MiniMax-Hailuo-2.3', 'MiniMax-Hailuo-2.3-Fast', 'MiniMax-Hailuo-02']:
                resolution = '768P'  # Hailuo系列默认768P以获得更好质量
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
                - MiniMax-Hailuo-2.3: 全新模型，肢体动作、物理表现全面升级（支持T2V和I2V）
                - MiniMax-Hailuo-2.3-Fast: 图生视频快速模型（仅支持I2V）
                - MiniMax-Hailuo-02: 经典模型，指令遵循能力强（支持T2V和I2V，I2V支持512P）
                - T2V-01-Director: 导演版，支持运镜控制（T2V专用）
                - T2V-01: 基础文生视频模型（T2V专用）
                - I2V-01系列: 图生视频模型（I2V专用）
                - S2V-01: 主体参考视频生成模型
            first_frame_image: 首帧图片URL或路径（图生视频必需）
            last_frame_image: 尾帧图片URL或路径（首尾帧生成必需）
            subject_image: 主体参考图片URL或路径（主体参考生成必需）
            duration: 视频时长（秒）
            resolution: 分辨率 (512P/720P/768P/1080P，仅MiniMax-Hailuo-02的I2V支持512P)
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
        """查询视频生成状态

        Args:
            task_id: 视频生成任务ID

        Returns:
            包含任务状态的字典：
            - task_id: 任务ID
            - status: 状态
            - file_id: 文件ID（成功时）
            - video_width: 视频宽度（成功时）
            - video_height: 视频高度（成功时）
            - base_resp: 响应基础信息

        状态说明：
            - Preparing: 准备中
            - Queueing: 队列中
            - Processing: 生成中
            - Success: 成功
            - Fail: 失败
        """
        return self._request("GET", f"query/video_generation?task_id={task_id}")
    
    def download_video(self, file_id: str, filename: str = None) -> str:
        """下载视频文件

        Args:
            file_id: 视频文件ID（从视频状态查询接口获得）
            filename: 自定义文件名（可选），默认使用API返回的文件名

        Returns:
            下载后的视频文件本地路径

        文件信息字段：
            - file_id: 文件唯一标识符（整数）
            - bytes: 文件大小（字节）
            - created_at: 创建时间（Unix时间戳）
            - filename: 文件名称
            - purpose: 文件用途（如 video_generation）
            - download_url: 文件下载URL
        """
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

    def music(self, prompt: str = None, lyrics: str = None, stream: bool = False,
                output_format: str = "hex", sample_rate: int = 44100,
                bitrate: int = 256000, format: str = "mp3",
                aigc_watermark: bool = False, model: str = "music-2.5") -> str:
        """音乐生成 (music-2.5)

        Args:
            prompt: 音乐描述，用于指定风格、情绪和场景
                    - music-2.5: 可选，[0, 2000]字符
                    - 旧模型: 必填，[10, 2000]字符
            lyrics: 歌词内容，支持结构标签
                    - music-2.5: [1, 3500]字符（必填）
                    - 旧模型: [10, 3500]字符
            stream: 是否使用流式传输，默认false
            output_format: 音频返回格式，可选url/hex，默认hex
            sample_rate: 采样率，可选16000/24000/32000/44100，默认44100
            bitrate: 比特率，可选32000/64000/128000/256000，默认256000
            format: 音频编码格式，可选mp3/wav/pcm，默认mp3
            aigc_watermark: 是否在音频末尾添加水印，默认false（仅非流式生效）
            model: 音乐生成模型，默认music-2.5

        Returns:
            音频数据（hex编码或URL）
        """
        self._log("🎵 开始生成音乐...")
        import sys

        lyrics = lyrics.strip() if lyrics else ""

        # 模型特定的参数验证
        is_music_25 = model == "music-2.5"

        if is_music_25:
            # music-2.5: prompt可选 [0, 2000], lyrics必填 [1, 3500]
            if prompt:
                prompt = prompt.strip()
                if len(prompt) > 2000:
                    print(f"❌ prompt过长 ({len(prompt)}字符)")
                    print(f"💡 music-2.5模型: prompt长度限制[0, 2000]字符")
                    sys.exit(1)
            else:
                prompt = ""

            if not lyrics:
                print(f"❌ 歌词为必填参数")
                print(f"💡 music-2.5模型: 歌词长度限制[1, 3500]字符")
                print(f"📝 示例: '[Verse]\n街灯微亮晚风轻抚\n[Chorus]\n推开木门香气弥漫'")
                sys.exit(1)

            if len(lyrics) < 1:
                print(f"❌ 歌词过短 ({len(lyrics)}字符)")
                print(f"💡 music-2.5模型: 歌词长度限制[1, 3500]字符")
                sys.exit(1)

            if len(lyrics) > 3500:
                print(f"❌ 歌词过长 ({len(lyrics)}字符)")
                print(f"💡 music-2.5模型: 歌词长度限制[1, 3500]字符")
                sys.exit(1)
        else:
            # 旧模型: prompt必填 [10, 2000], lyrics [10, 3500]
            if not prompt:
                print(f"❌ prompt为必填参数（非music-2.5模型）")
                print(f"💡 旧模型: prompt长度限制[10, 2000]字符")
                print(f"📝 示例: '独立民谣,忧郁,内省,渴望,独自漫步,咖啡馆'")
                sys.exit(1)

            prompt = prompt.strip()
            if len(prompt) < 10:
                print(f"❌ prompt过短 ({len(prompt)}字符)")
                print(f"💡 旧模型: prompt长度限制[10, 2000]字符")
                print(f"📝 建议: 添加更多描述，如风格、情绪、场景")
                sys.exit(1)

            if len(prompt) > 2000:
                print(f"❌ prompt过长 ({len(prompt)}字符)")
                print(f"💡 旧模型: prompt长度限制[10, 2000]字符")
                sys.exit(1)

            if not lyrics or len(lyrics) < 10:
                print(f"❌ 歌词为必填参数")
                print(f"💡 旧模型: 歌词长度限制[10, 3500]字符")
                print(f"📝 示例: '[Verse]\n街灯微亮晚风轻抚\n[Chorus]\n推开木门香气弥漫'")
                sys.exit(1)

            if len(lyrics) > 3500:
                print(f"❌ 歌词过长 ({len(lyrics)}字符)")
                print(f"💡 旧模型: 歌词长度限制[10, 3500]字符")
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
            "model": model,
            "lyrics": lyrics,
            "stream": stream,
            "output_format": output_format,
            "audio_setting": {
                "sample_rate": sample_rate,
                "bitrate": bitrate,
                "format": format
            }
        }

        # music-2.5中prompt是可选的
        if prompt:
            data["prompt"] = prompt

        # 仅在非流式时添加水印
        if not stream and aigc_watermark:
            data["aigc_watermark"] = True

        self._log(f"📋 使用模型: {model}")
        self._log(f"🎵 音乐描述: {prompt[:100] + '...' if len(prompt) > 100 else prompt}")
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

    def generate_lyrics(self, mode: str = "write_full_song", prompt: str = None,
                      lyrics: str = None, title: str = None) -> Dict[str, Any]:
        """歌词生成 (lyrics_generation)

        Args:
            mode: 生成模式 [write_full_song, edit]
                - write_full_song: 写完整歌曲
                - edit: 编辑/续写歌词
            prompt: 提示词/指令，用于描述歌曲主题、风格或编辑方向。为空时随机生成。
            lyrics: 现有歌词内容，仅在 `edit` 模式下有效。可用于续写或修改已有歌词。
            title: 歌曲标题。传入后输出将保持该标题不变。

        Returns:
            包含生成结果的字典，包括：
                - song_title: 歌曲标题
                - style_tags: 风格标签
                - lyrics: 生成的歌词（含结构标签）
                - base_resp: 响应状态信息
        """
        self._log("🎵 开始生成歌词...")

        # 参数验证
        valid_modes = ["write_full_song", "edit"]
        if mode not in valid_modes:
            raise ValueError(f"无效的生成模式: {mode}，可选值: {valid_modes}")

        if prompt and len(prompt) > 2000:
            raise ValueError(f"提示词过长，最多支持2000字符，当前{len(prompt)}字符")

        if lyrics and len(lyrics) > 3500:
            raise ValueError(f"歌词过长，最多支持3500字符，当前{len(lyrics)}字符")

        # 构建请求数据
        data = {
            "mode": mode
        }

        if prompt:
            data["prompt"] = prompt.strip()

        if lyrics:
            data["lyrics"] = lyrics.strip()

        if title:
            data["title"] = title.strip()

        self._log(f"📋 生成模式: {mode}")
        if prompt:
            self._log(f"📝 提示词: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        if lyrics:
            self._log(f"🎤 现有歌词长度: {len(lyrics)}字符")
        if title:
            self._log(f"🎭 歌曲标题: {title}")

        response = self._request("POST", "lyrics_generation", json=data)

        # 处理响应
        self._log("✅ 歌词生成完成")

        result = {
            "song_title": response.get("song_title", ""),
            "style_tags": response.get("style_tags", ""),
            "lyrics": response.get("lyrics", ""),
            "base_resp": response.get("base_resp", {})
        }

        # 显示生成结果信息
        if result["song_title"]:
            self._log(f"🎵 歌曲标题: {result['song_title']}")

        if result["style_tags"]:
            self._log(f"🎨 风格标签: {result['style_tags']}")

        if result["lyrics"]:
            # 计算歌词行数和字符数
            lines = result["lyrics"].count("\n") + 1
            chars = len(result["lyrics"])
            self._log(f"📊 歌词统计: {lines}行，{chars}字符")

            # 显示前几行歌词预览
            preview = "\n".join(result["lyrics"].split("\n")[:5])
            if lines > 5:
                preview += "\n..."
            self._log(f"🎤 歌词预览:\n{preview}")

        return result

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

    def list_files(self, purpose: str) -> Dict[str, Any]:
        """
        列出文件列表

        Args:
            purpose: 文件分类（必填）
                - voice_clone: 快速复刻原始文件
                - prompt_audio: 音色复刻的示例音频
                - t2a_async_input: 异步长文本语音生成合成中音频

        Returns:
            包含文件列表的字典，每个文件包含：
            - file_id: 文件唯一标识符
            - bytes: 文件大小（字节）
            - created_at: 创建时间（Unix时间戳）
            - filename: 文件名称
            - purpose: 文件使用目的
        """
        try:
            # 参数验证
            valid_purposes = ["voice_clone", "prompt_audio", "t2a_async_input"]
            if purpose not in valid_purposes:
                raise ValueError(f"无效的purpose: {purpose}，可选值: {valid_purposes}")

            # 构建查询参数
            params = {'purpose': purpose}

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
                output_dir = self.base_dir / "downloads"
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

    def tts(self, text: str, voice_id: str = "female-chengshu", emotion: str = None,
               model: str = "speech-2.8-hd",
               speed: float = 1.0, vol: float = 1.0, pitch: int = 0,
               sample_rate: int = 32000, format: str = "mp3", bitrate: int = 128000,
               channel: int = 1, stream: bool = False, language_boost: str = None,
               subtitle_enable: bool = False, output_format: str = "hex",
               text_normalization: bool = False, latex_read: bool = False,
               force_cbr: bool = False, continuous_sound: bool = False,
               voice_modify: dict = None, aigc_watermark: bool = False) -> str:
        """文本转语音（支持8个模型和完整参数）

        Args:
            text: 需要合成语音的文本 (< 10000字符)
            voice_id: 音色ID (支持系统音色、复刻音色、文生音色)
            model: 语音模型 [speech-2.8-hd, speech-2.8-turbo, speech-2.6-hd, speech-2.6-turbo, speech-02-hd, speech-02-turbo]
            emotion: 情感控制 [happy, sad, angry, fearful, disgusted, surprised, calm, fluent, whisper]
                    fluent/whisper 仅对 speech-2.6-hd/speech-2.6-turbo 生效
            speed: 语速 [0.5, 2.0]，默认1.0
            vol: 音量 (0, 10]，默认1.0
            pitch: 语调 [-12, 12]，默认0
            sample_rate: 采样率 [8000,16000,22050,24000,32000,44100]，默认32000
            format: 音频格式 [mp3, pcm, flac, wav(仅非流式)]，默认mp3
            bitrate: 比特率 [32000,64000,128000,256000]，默认128000
            channel: 声道数 [1,2]，默认1
            stream: 是否流式输出，默认False
            language_boost: 语言增强 [Chinese, English, auto, 等40种语言]
            subtitle_enable: 是否启用字幕（仅非流式），默认False
            output_format: 输出格式 [url, hex]，流式仅支持hex
            text_normalization: 是否启用文本规范化，默认False
            latex_read: 是否朗读latex公式（需用$包裹），默认False
            force_cbr: 是否使用恒定比特率（仅流式+mp3生效），默认False
            continuous_sound: 子句衔接更自然（仅 speech-2.8 系列支持），默认False
            voice_modify: 声音效果器设置 {pitch, intensity, timbre, sound_effects}
            aigc_watermark: 添加音频水印（仅非流式），默认False

        Returns:
            音频数据URL或hex编码
        """
        self._log(f"🎤 开始语音合成 (模型: {model})...")

        # 模型验证（仅保留 speech-02 及以后的新模型）
        valid_models = ["speech-2.8-hd", "speech-2.8-turbo", "speech-2.6-hd", "speech-2.6-turbo",
                       "speech-02-hd", "speech-02-turbo"]
        if model not in valid_models:
            raise ValueError(f"模型必须是{valid_models}之一")

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

        # 情感验证（仅在指定 emotion 时验证）
        if emotion is not None:
            valid_emotions = ["happy", "sad", "angry", "fearful", "disgusted",
                             "surprised", "calm", "fluent", "whisper"]
            if emotion not in valid_emotions:
                raise ValueError(f"情感必须是{valid_emotions}之一")

            # fluent/whisper 仅对特定模型生效
            if emotion in ["fluent", "whisper"] and model not in ["speech-2.6-hd", "speech-2.6-turbo"]:
                self._log(f"⚠️ {emotion}情感仅对 speech-2.6-hd/speech-2.6-turbo 生效", "WARN")

        # output_format 验证
        if stream and output_format == "url":
            raise ValueError("流式输出仅支持hex格式")

        # 构建请求数据
        voice_settings = {
            "voice_id": voice_id,
            "speed": speed,
            "vol": vol,
            "pitch": pitch,
            "text_normalization": text_normalization,
            "latex_read": latex_read
        }

        # 仅在明确指定 emotion 时才添加（让模型自动匹配）
        if emotion is not None:
            voice_settings["emotion"] = emotion

        data = {
            "model": model,
            "text": text,
            "stream": stream,
            "voice_setting": voice_settings,
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

        # continuous_sound 仅对 2.8 系列生效
        if continuous_sound and model.startswith("speech-2.8"):
            data["continuous_sound"] = True

        # voice_modify 音效设置
        if voice_modify:
            data["voice_modify"] = voice_modify

        # aigc_watermark 仅在非流式时生效
        if aigc_watermark:
            data["aigc_watermark"] = True

        if stream:
            data["stream_options"] = {
                "exclude_aggregated_audio": False
            }
            # force_cbr 仅在流式+mp3时生效
            if format == "mp3" and force_cbr:
                data["audio_setting"]["force_cbr"] = True

        response = self._request("POST", "t2a_v2", json=data)

        # 处理响应
        if stream:
            # 流式响应处理
            self._log("📡 流式语音合成完成")
            # TODO: 实现流式音频合并
            return response.get('data', {}).get('audio', '')
        else:
            audio_data = response.get('data', {}).get('audio', '')
            subtitle_file = response.get('data', {}).get('subtitle_file', '')
            self._log("🗣️ 语音合成完成")

            # 显示字幕信息
            if subtitle_file:
                self._log(f"📝 字幕文件: {subtitle_file}")

            # 显示音频信息
            extra_info = response.get('extra_info', {})
            if extra_info:
                self._log(f"📊 音频信息: 时长{extra_info.get('audio_length', 0)//1000}秒, "
                         f"大小{extra_info.get('audio_size', 0)//1024}KB, "
                         f"字数{extra_info.get('word_count', 0)}")

            return audio_data

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
            "model": "speech-2.8-hd",
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
        
        # API支持的参数映射（根据官方文档）
        valid_types = {
            'system': 'system',
            'cloning': 'voice_cloning',
            'generation': 'voice_generation',
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

    def voice_clone(self, file_id: int, voice_id: str,
                   prompt_audio: int = None, prompt_text: str = None,
                   text: str = None, model: str = "speech-2.8-hd",
                   language_boost: str = None,
                   need_noise_reduction: bool = False,
                   need_volume_normalization: bool = False,
                   aigc_watermark: bool = False,
                   continuous_sound: bool = False) -> Dict[str, Any]:
        """音色快速复刻

        Args:
            file_id: 待复刻音频的 file_id（通过上传文件获得，purpose=voice_clone）
            voice_id: 克隆音色的ID
                - 自定义 voice_id 长度范围[8,256]
                - 首字符必须为英文字母
                - 允许数字、字母、-、_
                - 末位字符不可为 -、_
                - 不可与已有 id 重复
            prompt_audio: 示例音频的 file_id（通过上传文件获得，purpose=prompt_audio）
            prompt_text: 示例音频的对应文本
            text: 复刻试听文本（最多1000字符，支持语气词标签）
            model: 试听音频模型（speech-2.8-hd, speech-2.8-turbo, speech-2.6-hd, speech-02-hd等）
            language_boost: 语言增强（auto, Chinese等）
            need_noise_reduction: 是否开启降噪，默认False
            need_volume_normalization: 是否开启音量归一化，默认False
            aigc_watermark: 是否添加水印，默认False
            continuous_sound: 子句衔接更自然（仅 speech-2.8 系列支持），默认False

        Returns:
            包含 demo_audio 试听链接等信息的字典

        文件要求：
            - 复刻音频：mp3/m4a/wav，10秒-5分钟，≤20MB
            - 示例音频：mp3/m4a/wav，<8秒，≤20MB

        语气词标签（仅 speech-2.8 系列支持）：
            (laughs), (chuckle), (coughs), (clear-throat), (groans), (breath),
            (pant), (inhale), (exhale), (gasps), (sniffs), (sighs), (snorts),
            (burps), (lip-smacking), (humming), (hissing), (emm), (whistles),
            (sneezes), (crying), (applause)
        """
        self._log("🎤 开始音色快速复刻...")

        # 参数验证
        if not voice_id:
            raise ValueError("voice_id 不能为空")

        # 验证 voice_id 格式
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*[a-zA-Z0-9]$', voice_id):
            raise ValueError("voice_id 格式错误：首字符必须为英文字母，只允许数字、字母、-、_，末位不可为 - 或 _")

        if len(voice_id) < 8 or len(voice_id) > 256:
            raise ValueError("voice_id 长度必须在 8-256 之间")

        # 构建请求数据
        data = {
            "file_id": file_id,
            "voice_id": voice_id,
            "need_noise_reduction": need_noise_reduction,
            "need_volume_normalization": need_volume_normalization,
            "aigc_watermark": aigc_watermark
        }

        # 添加可选参数
        if prompt_audio and prompt_text:
            data["clone_prompt"] = {
                "prompt_audio": prompt_audio,
                "prompt_text": prompt_text
            }
            self._log("📝 使用示例音频增强音色相似度")

        if text:
            if not model:
                raise ValueError("提供试听文本时必须指定模型")
            data["text"] = text
            data["model"] = model
            self._log(f"🎧 生成试听音频（模型: {model}）")

        if language_boost:
            data["language_boost"] = language_boost
            self._log(f"🌍 语言增强: {language_boost}")

        # continuous_sound 仅对 speech-2.8 系列生效
        if continuous_sound and model and model.startswith("speech-2.8"):
            data["continuous_sound"] = True
            self._log("🔗 启用子句自然衔接")

        self._log(f"📁 复刻音频ID: {file_id}")
        self._log(f"🎭 目标音色ID: {voice_id}")

        response = self._request("POST", "voice_clone", json=data)

        # 处理响应
        demo_audio = response.get('demo_audio', '')
        if demo_audio:
            self._log("✅ 音色复刻成功")
            self._log(f"🎵 试听音频: {demo_audio}")
        else:
            self._log("✅ 音色复刻成功（无试听音频）")

        # 风控检查
        input_sensitive = response.get('input_sensitive', {})
        if input_sensitive:
            sensitive_type = input_sensitive.get('type', 0)
            if sensitive_type != 0:
                self._log(f"⚠️ 警告：输入音频命中风控（类型: {sensitive_type}）", "WARN")

        return response

    def voice_design(self, prompt: str, preview_text: str,
                    voice_id: str = None, aigc_watermark: bool = False) -> Dict[str, Any]:
        """音色设计 - 通过文本描述生成自定义音色

        Args:
            prompt: 音色描述（如：声音低沉富有磁性的播音员）
            preview_text: 试听音频文本（将收取2元/万字符费用）
            voice_id: 自定义音色ID（可选，不提供时自动生成）
            aigc_watermark: 是否添加水印，默认False

        Returns:
            包含 voice_id 和 trial_audio (hex编码) 的字典
        """
        self._log("🎨 开始音色设计...")

        # 参数验证
        if not prompt:
            raise ValueError("音色描述不能为空")
        if not preview_text:
            raise ValueError("试听文本不能为空")

        # 构建请求数据
        data = {
            "prompt": prompt,
            "preview_text": preview_text,
            "aigc_watermark": aigc_watermark
        }

        if voice_id:
            data["voice_id"] = voice_id
            self._log(f"🎭 目标音色ID: {voice_id}")
        else:
            self._log("🎭 音色ID: 自动生成")

        self._log(f"📝 音色描述: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        self._log(f"🎧 试听文本: {preview_text[:100]}{'...' if len(preview_text) > 100 else ''}")

        response = self._request("POST", "voice_design", json=data)

        # 处理响应
        result_voice_id = response.get('voice_id', '')
        trial_audio = response.get('trial_audio', '')

        self._log("✅ 音色设计成功")
        self._log(f"🎭 音色ID: {result_voice_id}")
        self._log(f"🎵 试听音频: {len(trial_audio)} 字符（hex编码）")

        return response

class FileManager:
    """文件管理"""
    
    def __init__(self):
        self.base_dir = Path('./output')
        self.base_dir.mkdir(exist_ok=True)

        for subdir in ['audio', 'images', 'videos', 'music', 'podcasts']:
            (self.base_dir / subdir).mkdir(exist_ok=True)

    def read_input(self, content: str, param_name: str = "内容") -> str:
        """读取输入内容，支持文本或文件路径

        Args:
            content: 输入内容（文本或文件路径）
            param_name: 参数名称（用于错误提示）

        Returns:
            读取的文本内容

        Raises:
            SystemExit: 文件不存在时退出
        """
        if content.endswith(('.txt', '.md')):
            if Path(content).exists():
                with open(content, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                print(f"❌ {param_name}文件不存在: {content}")
                sys.exit(1)
        return content

    def generate_timestamp(self) -> str:
        """生成时间戳字符串"""
        return datetime.now().strftime('%Y%m%d_%H%M%S')

    def save_file(self, data: str, filename: str, subdir: str) -> str:
        """保存文件（支持URL或十六进制数据）"""
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

    def save_text(self, content: str, filename: str, subdir: str) -> str:
        """保存文本内容到文件"""
        filepath = self.base_dir / subdir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(filepath)

    def get_path(self, subdir: str, filename: str = None) -> Path:
        """获取输出目录路径，可选带文件名"""
        path = self.base_dir / subdir
        path.mkdir(parents=True, exist_ok=True)
        return path / filename if filename else path
    
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
    generate_group.add_argument('-l', '--lyrics', metavar='歌词提示', help='AI歌词生成（支持完整创作或续写）')

    # ⚙️ 通用选项
    common_group = parser.add_argument_group('通用选项')
    common_group.add_argument('-I', '--interactive', action='store_true', help='交互模式')
    common_group.add_argument('-V', '--verbose', action='store_true', help='显示详细日志')
    common_group.add_argument('-P', '--play', action='store_true', help='生成后自动播放音频')

    # 🤖 文本生成/对话选项
    chat_group = parser.add_argument_group('文本生成/对话选项')
    chat_group.add_argument('--chat-model', default='MiniMax-M2.1',
                           choices=['M2-her', 'MiniMax-M2.1', 'MiniMax-M2.1-lightning', 'MiniMax-M2'],
                           help='模型选择：M2-her=对话/角色扮演, MiniMax-M2系列=编程/Agent工作流（需配合--anthropic-api）')
    chat_group.add_argument('--anthropic-api', action='store_true',
                           help='使用 Anthropic API 兼容接口（推荐用于 MiniMax-M2 系列，支持思考过程显示）')
    chat_group.add_argument('--show-thinking', action='store_true',
                           help='显示模型思考过程（仅 --anthropic-api 支持）')
    chat_group.add_argument('--system-prompt', type=str, help='系统提示词（定义AI角色和行为）')
    # M2-her 专属参数（暂时注释，等待 API BUG 修复）
    # chat_group.add_argument('--user-system', type=str, metavar='TEXT',
    #                        help='用户角色设定（用于角色扮演场景定义用户身份，M2-her专属）')
    # chat_group.add_argument('--group', type=str, metavar='NAME',
    #                        help='对话分组名称（标识对话场景，M2-her专属）')
    # chat_group.add_argument('--sample-user', type=str, metavar='TEXT',
    #                        help='示例用户消息（引导对话风格，M2-her专属）')
    # chat_group.add_argument('--sample-ai', type=str, metavar='TEXT',
    #                        help='示例AI回复（配合--sample-user使用，M2-her专属）')
    chat_group.add_argument('--temperature', type=float, default=1.0,
                           help='温度参数 (0.0-1.0]，默认1.0')
    chat_group.add_argument('--max-tokens', type=int, default=1024,
                           help='最大生成token数，M2-her上限2048，默认1024')

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
    voice_group.add_argument('--list-voices', choices=['system', 'cloning', 'generation', 'all'],
                            help='查询可用音色列表 (system:系统音色, cloning:快速复刻, generation:文生音色, all:全部)')
    voice_group.add_argument('-r', '--refresh-voices', action='store_true', help='强制刷新音色缓存')
    voice_group.add_argument('-f', '--filter-voices', type=str, help='过滤音色列表关键词')

    # 🎤 音色快速复刻
    clone_group = parser.add_argument_group('音色快速复刻')
    clone_group.add_argument('--clone', type=str, metavar='VOICE_ID',
                            help='音色快速复刻：指定目标音色ID')
    clone_group.add_argument('--clone-file-id', type=int, metavar='FILE_ID',
                            help='复刻音频的file_id（必填）')
    clone_group.add_argument('--prompt-audio', type=int, metavar='FILE_ID',
                            help='示例音频的file_id（用于增强相似度）')
    clone_group.add_argument('--prompt-text', type=str, metavar='TEXT',
                            help='示例音频对应的文本（需与prompt_audio同时提供）')
    clone_group.add_argument('--demo-text', type=str, metavar='TEXT',
                            help='复刻试听文本（最多1000字符）')
    clone_group.add_argument('--demo-model', default='speech-2.8-hd',
                            choices=['speech-2.8-hd', 'speech-2.8-turbo', 'speech-2.6-hd', 'speech-2.6-turbo',
                                    'speech-02-hd', 'speech-02-turbo'],
                            help='试听音频模型，默认speech-2.8-hd')
    clone_group.add_argument('--clone-language-boost', metavar='LANGUAGE',
                            help='语言增强（auto, Chinese, English等）')
    clone_group.add_argument('--noise-reduction', action='store_true',
                            help='开启音频降噪')
    clone_group.add_argument('--volume-normalization', action='store_true',
                            help='开启音量归一化')
    clone_group.add_argument('--continuous-sound', action='store_true',
                            help='启用子句自然衔接（仅 2.8 系列支持）')

    # 🎨 音色设计
    design_group = parser.add_argument_group('音色设计')
    design_group.add_argument('--design', type=str, metavar='VOICE_ID',
                             help='音色设计：指定目标音色ID（可选，不提供则自动生成）')
    design_group.add_argument('--design-prompt', type=str, metavar='PROMPT',
                             help='音色描述（必填），如：声音低沉富有磁性的播音员')
    design_group.add_argument('--preview-text', type=str, metavar='TEXT',
                             help='试听文本（必填），将收取2元/万字符费用')

    # 🎤 语音合成选项
    tts_group = parser.add_argument_group('语音合成选项')
    tts_group.add_argument('--voice', type=str, default="female-shaonv",
                          help='指定音色ID (如: male-qn-jingying, female-yujie, female-shaonv)')
    tts_group.add_argument('--tts-model', default='speech-2.8-hd',
                          choices=['speech-2.8-hd', 'speech-2.8-turbo', 'speech-2.6-hd', 'speech-2.6-turbo',
                                  'speech-02-hd', 'speech-02-turbo'],
                          help='语音合成模型：2.8系列=高精度/自然度，2.6系列=极速版，02系列=经典版，默认speech-2.8-hd')
    tts_group.add_argument('--emotion', default=None,
                          choices=['happy', 'sad', 'angry', 'fearful', 'disgusted',
                                  'surprised', 'calm', 'fluent', 'whisper'],
                          help='语音情感控制（默认不指定，让模型自动匹配）')
    tts_group.add_argument('--speed', type=float, default=1.0, help='语速 (0.5-2.0)，默认1.0')
    tts_group.add_argument('--vol', type=float, default=1.0, help='音量 (0.1-10.0)，默认1.0')
    tts_group.add_argument('--pitch', type=int, default=0, help='语调 (-12到12)，默认0')
    tts_group.add_argument('--sample-rate', type=int, default=32000,
                          choices=[8000, 16000, 22050, 24000, 32000, 44100],
                          help='采样率，默认32000')
    tts_group.add_argument('--format', default='mp3',
                          choices=['mp3', 'pcm', 'flac', 'wav'],
                          help='音频格式，默认mp3 (wav仅非流式)')
    tts_group.add_argument('--bitrate', type=int, default=128000,
                          choices=[32000, 64000, 128000, 256000],
                          help='比特率，默认128000')
    tts_group.add_argument('--channel', type=int, default=1, choices=[1, 2], help='声道数，默认1')
    tts_group.add_argument('--stream', action='store_true', help='启用流式输出')
    tts_group.add_argument('--language-boost', help='语言增强 (Chinese, English, auto等40种语言)')
    tts_group.add_argument('--subtitle', action='store_true', help='启用字幕生成（仅非流式）')
    tts_group.add_argument('--output-format', default='hex', choices=['hex', 'url'],
                          help='输出格式，默认hex (流式仅支持hex)')
    tts_group.add_argument('--text-normalization', action='store_true',
                          help='启用文本规范化（提升数字阅读性能）')
    tts_group.add_argument('--latex-read', action='store_true',
                          help='启用LaTeX公式朗读（公式需用$包裹）')
    tts_group.add_argument('--force-cbr', action='store_true',
                          help='使用恒定比特率（仅流式+mp3生效）')

    # 🎵 歌词生成选项
    lyrics_group = parser.add_argument_group('歌词生成选项')
    lyrics_group.add_argument('--lyrics-mode', default='write_full_song',
                           choices=['write_full_song', 'edit'],
                           help='生成模式：write_full_song=完整歌曲创作，edit=编辑/续写（默认write_full_song）')
    lyrics_group.add_argument('--lyrics-title', type=str, metavar='TITLE',
                           help='歌曲标题（可选，不提供时自动生成）')
    lyrics_group.add_argument('--lyrics-input', type=str, metavar='FILE',
                           help='现有歌词文件路径（仅在edit模式下使用）')

    # 🎵 音乐生成选项
    music_group = parser.add_argument_group('音乐生成')
    music_group.add_argument('--music-model', default='music-2.5', choices=['music-2.5'], help='音乐生成模型，默认music-2.5')
    music_group.add_argument('--music-lyrics', help='音乐歌词内容或文件路径(.txt/.md) [music-2.5: 1-3500字符]')
    music_group.add_argument('--music-stream', action='store_true', help='启用流式传输（仅支持hex格式）')
    music_group.add_argument('--music-format', default='hex', choices=['hex', 'url'], help='音频返回格式，默认hex')
    music_group.add_argument('--music-sample-rate', type=int, default=44100, choices=[16000, 24000, 32000, 44100], help='音频采样率，默认44100')
    music_group.add_argument('--music-bitrate', type=int, default=256000, choices=[32000, 64000, 128000, 256000], help='音频比特率，默认256000')
    music_group.add_argument('--music-encoding', default='mp3', choices=['mp3', 'wav', 'pcm'], help='音频编码格式，默认mp3')
    music_group.add_argument('--music-watermark', action='store_true', help='在音频末尾添加水印（仅非流式生效）')

    # 📺 视频管理
    video_group = parser.add_argument_group('视频管理')
    video_group.add_argument('-s', '--video-status', metavar='任务ID', help='查询视频状态（传入task_id）')
    video_group.add_argument('-d', '--download-video', metavar='文件ID', help='下载视频文件（传入file_id）')

    # 🎬 视频生成选项
    video_gen_group = parser.add_argument_group('视频生成选项')
    video_gen_group.add_argument('--video-model', default='MiniMax-Hailuo-2.3',
                                choices=[
                                    'MiniMax-Hailuo-2.3', 'MiniMax-Hailuo-02',
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

    # 📁 文件管理
    file_group = parser.add_argument_group('文件管理')
    file_group.add_argument('--upload-file', type=str, metavar='FILE_PATH', help='上传文件到MiniMax平台')
    file_group.add_argument('--file-purpose', default='voice_clone',
                           choices=['voice_clone', 'prompt_audio', 't2a_async_input'],
                           help='文件使用目的，默认voice_clone（用于上传和列出文件）')
    file_group.add_argument('--list-files', action='store_true',
                           help='列出指定分类的文件（需配合--file-purpose使用）')
    file_group.add_argument('--retrieve-file', type=str, metavar='FILE_ID', help='检索文件信息')
    file_group.add_argument('--download-file', type=str, metavar='FILE_ID', help='下载文件')
    file_group.add_argument('--save-path', type=str, metavar='PATH', help='下载文件保存路径')
    file_group.add_argument('--delete-file', type=str, metavar='FILE_ID', help='删除文件')
    file_group.add_argument('--delete-purpose', choices=['voice_clone', 'prompt_audio', 't2a_async', 't2a_async_input', 'video_generation'],
                           help='删除文件时指定的用途（必填）')
    
    args = parser.parse_args()
    
    client = MiniMaxClient()
    file_mgr = FileManager()
    
    if args.verbose:
        client.verbose = True
    
    if args.interactive:
        print("💬 MiniMax AI 交互模式 (输入 'quit' 退出)")
        while True:
            try:
                cmd = input("\n选择功能 [chat/image/video/music/lyrics/tts/quit]: ").strip()
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
                            filepath = file_mgr.save_file(url, f"image_{file_mgr.generate_timestamp()}.jpg", "images")
                            print(f"✅ 已保存: {filepath}")
                elif cmd == 'video':
                    prompt = input("描述: ")
                    task_id = client.video(prompt)
                    print(f"🎬 任务ID: {task_id}")
                    check = input("查询状态? (y/n): ")
                    if check.lower() == 'y':
                        status = client.video_status(task_id)
                        status_map = {
                            'Preparing': '📋 准备中',
                            'Queueing': '⏳ 队列中',
                            'Processing': '🎬 生成中',
                            'Success': '✅ 成功',
                            'Fail': '❌ 失败'
                        }
                        print(f"📊 状态: {status_map.get(status.get('status'), status.get('status'))}")
                        if status.get('status') == 'Success':
                            print(f"📐 分辨率: {status.get('video_width')}x{status.get('video_height')}")
                            print(f"📁 文件ID: {status.get('file_id')}")
                elif cmd == 'music':
                    prompt = input("音乐描述: ")
                    lyrics = input("歌词内容: ")
                    if not lyrics.strip():
                        print("❌ 音乐生成需要歌词内容")
                        continue
                    
                    audio = client.music(prompt, lyrics, model="music-2.5")
                    if audio:
                        filepath = file_mgr.save_file(audio, f"music_{file_mgr.generate_timestamp()}.mp3", "music")
                        print(f"✅ 音乐已保存: {filepath}")
                elif cmd == 'lyrics':
                    mode = input("生成模式 [write_full_song/edit]: ").strip() or 'write_full_song'
                    prompt = input("提示词 (可选): ").strip()
                    title = input("歌曲标题 (可选): ").strip()
                    lyrics = None
                    if mode == 'edit':
                        lyrics_path = input("现有歌词文件路径 (可选): ").strip()
                        if lyrics_path and Path(lyrics_path).exists():
                            with open(lyrics_path, 'r', encoding='utf-8') as f:
                                lyrics = f.read()
                        else:
                            lyrics = input("现有歌词内容 (可选): ").strip()

                    result = client.generate_lyrics(mode=mode, prompt=prompt, lyrics=lyrics, title=title)

                    if result.get("lyrics"):
                        lyrics_filepath = file_mgr.save_text(result["lyrics"], f"lyrics_{file_mgr.generate_timestamp()}.txt", "music")
                        print(f"✅ 歌词已保存: {lyrics_filepath}")

                        print(f"\n🎵 歌曲标题: {result.get('song_title', '未命名')}")
                        if result.get('style_tags'):
                            print(f"🎨 风格标签: {result.get('style_tags')}")
                        print(f"\n🎤 完整歌词:")
                        print(result["lyrics"])
                elif cmd == 'tts':
                    text = input("文本: ")
                    voice = input("音色ID (默认 female-chengshu): ").strip() or "female-chengshu"
                    audio = client.tts(text, voice)
                    if audio:
                        filepath = file_mgr.save_file(audio, f"tts_{file_mgr.generate_timestamp()}.mp3", "audio")
                        print(f"✅ 已保存: {filepath}")
            except KeyboardInterrupt:
                break
    
    elif args.chat:
        content = file_mgr.read_input(args.chat, "对话内容")

        # 调用更新后的 chat 方法
        response = client.chat(
            message=content,
            model=args.chat_model,
            system_prompt=args.system_prompt,
            # M2-her 专属参数已暂时注释
            # user_system=args.user_system,
            # group=args.group,
            # sample_user=args.sample_user,
            # sample_ai=args.sample_ai,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            use_anthropic_api=args.anthropic_api,
            show_thinking=args.show_thinking
        )

        # 显示响应
        if args.show_thinking and isinstance(response, dict):
            print("=== 🧠 思考过程 ===")
            print(response.get('thinking', ''))
            print("\n=== 📝 回复内容 ===")
            print(response.get('content', ''))
        else:
            print(response)
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
                    filepath = file_mgr.save_file(item, f"image2image_{file_mgr.generate_timestamp()}_{i+1}.jpg", "images")
                    print(f"✅ 图生图已保存: {filepath}")
                    print(f"🔗 图片URL: {item}")
                    if args.play:
                        import webbrowser
                        webbrowser.open(item)
                else:
                    import base64
                    try:
                        image_data = base64.b64decode(item)
                        filepath = file_mgr.get_path("images", f"image2image_{file_mgr.generate_timestamp()}_{i+1}.jpg")
                        filepath.parent.mkdir(exist_ok=True)
                        with open(filepath, 'wb') as f:
                            f.write(image_data)
                        print(f"✅ 图生图Base64已保存: {filepath}")
                        print(f"📊 图片大小: {len(image_data)} 字节")
                    except Exception as e:
                        print(f"❌ Base64图片保存失败: {e}")
    elif args.image:
        prompt = file_mgr.read_input(args.image, "图像描述")

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
                    filepath = file_mgr.save_file(item, f"image_{file_mgr.generate_timestamp()}_{i+1}.jpg", "images")
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
                        filepath = file_mgr.get_path("images", f"image_{file_mgr.generate_timestamp()}_{i+1}.jpg")
                        with open(filepath, 'wb') as f:
                            f.write(image_data)
                        print(f"✅ Base64图片已保存: {filepath}")
                        print(f"📊 图片大小: {len(image_data)} 字节")
                    except Exception as e:
                        print(f"❌ Base64图片保存失败: {e}")
                        print(f"🔗 Base64数据前50字符: {item[:50]}...")
    elif args.video:
        prompt = file_mgr.read_input(args.video, "视频描述")

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
            elif args.video_model in ['MiniMax-Hailuo-2.3', 'MiniMax-Hailuo-02']:
                resolution = '768P'  # Hailuo系列默认768P以获得更好质量
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
            elif args.i2v_model in ['MiniMax-Hailuo-2.3', 'MiniMax-Hailuo-2.3-Fast', 'MiniMax-Hailuo-02']:
                i2v_resolution = '768P'  # Hailuo系列默认768P以获得更好质量
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
        prompt = file_mgr.read_input(args.music, "音乐描述")

        # 歌词为必填
        if not args.music_lyrics:
            print("❌ 音乐生成需要歌词参数")
            print("💡 使用: --music-lyrics '歌词内容' 或 --music-lyrics lyrics.txt")
            print("📝 提示: 使用换行符分隔，支持[Intro][Verse][Chorus][Bridge][Outro]结构")
            sys.exit(1)

        lyrics = file_mgr.read_input(args.music_lyrics, "音乐歌词")
        
        # 使用新的音乐生成参数
        audio = client.music(
            prompt=prompt,
            lyrics=lyrics,
            stream=args.music_stream,
            output_format=args.music_format,
            sample_rate=args.music_sample_rate,
            bitrate=args.music_bitrate,
            format=args.music_encoding,
            aigc_watermark=args.music_watermark,
            model=args.music_model
        )

        if audio:
            # 根据返回格式处理音频
            if args.music_format == 'url':
                # URL格式：下载并保存
                ext = args.music_encoding
                filepath = file_mgr.save_file(audio, f"music_{file_mgr.generate_timestamp()}.{ext}", "music")
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
                    filepath = file_mgr.get_path("music", f"music_{file_mgr.generate_timestamp()}.{ext}")
                    with open(filepath, 'wb') as f:
                        f.write(audio_data)
                    print(f"✅ 音乐已保存: {filepath}")
                    print(f"📊 音频大小: {len(audio_data)} 字节")
                    if args.play:
                        file_mgr.play_audio(str(filepath))
                except Exception as e:
                    print(f"❌ 音频保存失败: {e}")
                    print(f"🔗 音频数据前50字符: {audio[:50]}...")
    elif args.lyrics:
        # 歌词生成处理
        prompt = file_mgr.read_input(args.lyrics, "歌词提示")

        # 处理现有歌词文件（仅在edit模式下使用）
        lyrics = None
        if args.lyrics_input:
            lyrics = file_mgr.read_input(args.lyrics_input, "现有歌词")

        # 调用歌词生成方法
        result = client.generate_lyrics(
            mode=args.lyrics_mode,
            prompt=prompt,
            lyrics=lyrics,
            title=args.lyrics_title
        )

        # 保存歌词到文件
        if result.get("lyrics"):
            timestamp = file_mgr.generate_timestamp()

            # 保存歌词文件
            lyrics_filepath = file_mgr.save_text(result["lyrics"], f"lyrics_{timestamp}.txt", "music")

            print(f"✅ 歌词已保存: {lyrics_filepath}")

            # 保存提示词文件（标题 + 风格标签），方便生成音乐时使用
            song_title = result.get('song_title', '')
            style_tags = result.get('style_tags', '')
            if song_title or style_tags:
                prompt_content = ""
                if song_title:
                    prompt_content += f"歌曲标题: {song_title}\n"
                if style_tags:
                    prompt_content += f"风格标签: {style_tags}\n"
                prompt_filepath = file_mgr.save_text(prompt_content, f"prompt_{timestamp}.txt", "music")
                print(f"✅ 提示词已保存: {prompt_filepath}")

            # 显示完整结果
            if song_title:
                print(f"\n🎵 歌曲标题: {song_title}")
            if style_tags:
                print(f"🎨 风格标签: {style_tags}")
            print(f"\n🎤 完整歌词:")
            print(result["lyrics"])
    elif args.tts:
        text = file_mgr.read_input(args.tts, "语音文本")

        # 使用更新后的TTS参数
        audio = client.tts(
            text=text,
            voice_id=args.voice,
            model=args.tts_model,
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
            output_format=args.output_format,
            text_normalization=args.text_normalization,
            latex_read=args.latex_read,
            force_cbr=args.force_cbr
        )

        if audio:
            # 根据格式决定文件扩展名
            ext = args.format
            if args.output_format == 'url':
                # 如果是URL格式，需要下载文件
                ext = 'mp3'  # URL通常是mp3

            filepath = file_mgr.save_file(audio, f"tts_{file_mgr.generate_timestamp()}.{ext}", "audio")
            print(filepath)
            if args.play:
                file_mgr.play_audio(filepath)
    elif args.video_status:
        status = client.video_status(args.video_status)

        # 状态映射
        status_map = {
            'Preparing': '📋 准备中',
            'Queueing': '⏳ 队列中',
            'Processing': '🎬 生成中',
            'Success': '✅ 成功',
            'Fail': '❌ 失败'
        }

        # 友好的状态显示
        print(f"🆔 任务ID: {status.get('task_id', args.video_status)}")
        print(f"📊 状态: {status_map.get(status.get('status'), status.get('status'))}")

        # 如果成功，显示视频信息
        if status.get('status') == 'Success':
            file_id = status.get('file_id')
            width = status.get('video_width')
            height = status.get('video_height')

            print(f"🎬 视频已生成！")
            print(f"📐 分辨率: {width}x{height}")
            print(f"📁 文件ID: {file_id}")
            print(f"📥 下载命令: python minimax_cli.py -d {file_id}")
        elif status.get('status') == 'Fail':
            print(f"❌ 生成失败")
            if 'base_resp' in status:
                print(f"错误信息: {status['base_resp'].get('status_msg', 'Unknown error')}")
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

    # 🎤 音色快速复刻
    elif args.clone:
        if not args.clone_file_id:
            print("❌ 音色复刻必须提供 --clone-file-id 参数")
            print("💡 提示：请先使用 --upload-file 上传复刻音频文件（--file-purpose voice_clone）")
            return

        voice_id = args.clone
        try:
            result = client.voice_clone(
                file_id=args.clone_file_id,
                voice_id=voice_id,
                prompt_audio=args.prompt_audio,
                prompt_text=args.prompt_text,
                text=args.demo_text,
                model=args.demo_model,
                language_boost=args.clone_language_boost,
                need_noise_reduction=args.noise_reduction,
                need_volume_normalization=args.volume_normalization,
                aigc_watermark=args.add_watermark,
                continuous_sound=args.continuous_sound
            )

            # 显示结果
            print(f"\n🎤 音色复刻完成")
            print("-" * 50)
            print(f"🎭 音色ID: {voice_id}")

            demo_audio = result.get('demo_audio', '')
            if demo_audio:
                print(f"🎵 试听音频: {demo_audio}")
            else:
                print("📝 未生成试听音频")

            # 风控检查
            input_sensitive = result.get('input_sensitive', {})
            if input_sensitive:
                sensitive_type = input_sensitive.get('type', 0)
                if sensitive_type != 0:
                    type_names = {
                        0: "正常", 1: "严重违规", 2: "色情", 3: "广告",
                        4: "违禁", 5: "谩骂", 6: "暴恐", 7: "其他"
                    }
                    print(f"⚠️ 警告：输入音频命中风控 - {type_names.get(sensitive_type, f'类型{sensitive_type}')}")

            print("\n💡 使用新音色:")
            print(f"   python minimax_cli.py -t \"你的文本\" --voice {voice_id}")

        except ValueError as e:
            print(f"❌ 参数错误: {e}")
        except Exception as e:
            print(f"❌ 音色复刻失败: {e}")

    # 🎨 音色设计功能
    elif args.design or args.design_prompt:
        # 验证必需参数
        if not args.design_prompt:
            print("❌ 错误：音色设计需要提供 --design-prompt 参数")
            print("💡 使用示例：")
            print('   python minimax_cli.py --design-prompt "声音低沉富有磁性的播音员" --preview-text "大家好"')
            return
        if not args.preview_text:
            print("❌ 错误：音色设计需要提供 --preview-text 参数")
            print("💡 使用示例：")
            print('   python minimax_cli.py --design-prompt "声音低沉富有磁性的播音员" --preview-text "大家好"')
            return

        try:
            result = client.voice_design(
                prompt=args.design_prompt,
                preview_text=args.preview_text,
                voice_id=args.design,
                aigc_watermark=args.add_watermark
            )

            # 检查响应格式
            if 'error' in result:
                print(f"❌ 音色设计失败: {result['error']}")
            elif 'base_resp' in result and result['base_resp']['status_code'] != 0:
                print(f"❌ 音色设计失败: {result['base_resp']['status_msg']}")
            else:
                voice_id = result.get('voice_id', '')
                trial_audio = result.get('trial_audio', '')

                print(f"\n🎨 音色设计完成")
                print("-" * 50)
                print(f"🎭 音色ID: {voice_id}")
                print(f"🎵 试听音频: {len(trial_audio)} 字符（hex编码）")

                # 保存试听音频
                if trial_audio:
                    import binascii
                    try:
                        audio_data = binascii.unhexlify(trial_audio)
                        filepath = file_mgr.save_file(trial_audio, f"voice_design_{voice_id}.mp3", "audio")
                        print(f"💾 试听音频已保存: {filepath}")
                    except Exception as e:
                        print(f"⚠️ 音频保存失败: {e}")

                print("\n💡 使用新音色:")
                print(f"   python minimax_cli.py -t \"你的文本\" --voice {voice_id}")

        except ValueError as e:
            print(f"❌ 参数错误: {e}")
        except Exception as e:
            print(f"❌ 音色设计失败: {e}")

    elif args.list_files:
        # list_files 现在需要 purpose 参数
        purpose = args.file_purpose  # 使用 --file-purpose 指定的分类
        result = client.list_files(purpose=purpose)

        if 'error' in result:
            print(f"❌ 获取文件列表失败: {result['error']}")
        elif 'files' in result and isinstance(result['files'], list):
            files = result['files']
            print(f"\n📁 文件列表 - {purpose} (共 {len(files)} 个文件)")
            print("-" * 80)

            for file_info in files:
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