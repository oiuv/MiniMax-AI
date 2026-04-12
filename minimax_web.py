#!/usr/bin/env python3
"""
MiniMax AI Web UI
基于 Gradio 的图形化界面
"""

import gradio as gr
import os
import sys
import time
import json
import base64
import requests
from pathlib import Path
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from minimax_cli import MiniMaxClient, FileManager

# 初始化客户端
client = None
file_mgr = None


def init_client():
    """初始化 MiniMax 客户端"""
    global client, file_mgr
    try:
        client = MiniMaxClient()
        file_mgr = FileManager()
        return True, "✅ 连接成功"
    except Exception as e:
        return False, f"❌ 连接失败: {str(e)}"


# ==================== 对话模块 ====================
def create_chat_tab():
    """创建对话标签页"""
    with gr.TabItem("💬 对话"):
        gr.Markdown("## AI 对话聊天")

        with gr.Row():
            with gr.Column(scale=1):
                # 模型分类选择
                model_category = gr.Dropdown(
                    choices=[
                        ("编程/Agent (Anthropic API)", "anthropic"),
                        ("对话/角色扮演 (M2-her)", "m2her"),
                    ],
                    value="anthropic",
                    label="模型类别",
                )

                # Anthropic API 模型
                anthropic_model = gr.Dropdown(
                    choices=[
                        "MiniMax-M2.7",
                        "MiniMax-M2.7-highspeed",
                        "MiniMax-M2.5",
                        "MiniMax-M2.5-highspeed",
                        "MiniMax-M2.1",
                        "MiniMax-M2.1-highspeed",
                        "MiniMax-M2",
                    ],
                    value="MiniMax-M2.7",
                    label="模型",
                    visible=True,
                )

                # M2-her 模型（专用）
                m2her_model = gr.Dropdown(
                    choices=["M2-her"], value="M2-her", label="模型", visible=False
                )

                # 系统提示词（通用）
                system_prompt = gr.Textbox(
                    label="系统提示词 (system)",
                    placeholder="设定AI的角色和行为...",
                    lines=2,
                )

                # M2-her 专用参数
                with gr.Accordion(
                    "🎭 M2-her 角色设定", open=False, visible=False
                ) as m2her_settings:
                    user_system = gr.Textbox(
                        label="用户角色设定 (user_system)",
                        placeholder="设定用户的角色和人设...",
                        lines=2,
                    )
                    group_name = gr.Textbox(
                        label="对话分组名称 (group)",
                        placeholder="标识对话场景...",
                        lines=1,
                    )
                    with gr.Row():
                        ai_name = gr.Textbox(
                            label="AI名称", placeholder="如：MiniMax AI", lines=1
                        )
                        user_name = gr.Textbox(
                            label="用户名称", placeholder="如：用户", lines=1
                        )
                    with gr.Accordion("示例对话学习", open=False):
                        sample_user = gr.Textbox(
                            label="示例用户输入",
                            placeholder="示例用户说的话...",
                            lines=2,
                        )
                        sample_ai = gr.Textbox(
                            label="示例AI回复", placeholder="示例AI的回复...", lines=2
                        )

                # 高级参数
                with gr.Accordion("高级参数", open=False):
                    temperature = gr.Slider(
                        0.01, 1, value=1.0, step=0.05, label="Temperature (0-1]"
                    )
                    top_p = gr.Slider(0.01, 1, value=0.95, step=0.05, label="Top-p")
                    max_tokens = gr.Slider(
                        100, 8192, value=4096, step=100, label="Max Tokens"
                    )
                    use_anthropic = gr.Checkbox(
                        label="使用 Anthropic API 格式", value=True, visible=False
                    )

            with gr.Column(scale=2):
                # 对话区域
                chatbot = gr.Chatbot(label="对话历史", height=480)
                msg_input = gr.Textbox(
                    label="输入消息", placeholder="输入你想说的话..."
                )

                with gr.Row():
                    send_btn = gr.Button("🚀 发送", variant="primary")
                    clear_btn = gr.Button("🗑️ 清空")

        # 根据模型类别切换显示
        def on_category_change(category):
            if category == "anthropic":
                return {
                    anthropic_model: gr.Dropdown(visible=True),
                    m2her_model: gr.Dropdown(visible=False),
                    m2her_settings: gr.Accordion(visible=False),
                    use_anthropic: gr.Checkbox(value=True, visible=False),
                }
            else:
                return {
                    anthropic_model: gr.Dropdown(visible=False),
                    m2her_model: gr.Dropdown(visible=True),
                    m2her_settings: gr.Accordion(visible=True),
                    use_anthropic: gr.Checkbox(value=False, visible=False),
                }

        model_category.change(
            on_category_change,
            inputs=[model_category],
            outputs=[anthropic_model, m2her_model, m2her_settings, use_anthropic],
        )

        # 事件处理 - 流式响应
        def respond(
            message,
            chat_history,
            category,
            anthropic_m,
            m2her_m,
            system_prompt,
            user_system,
            group_name,
            ai_name,
            user_name,
            sample_user,
            sample_ai,
            temp,
            top_p,
            max_tok,
            use_anthropic,
        ):
            user_system = user_system or ""
            group_name = group_name or ""
            ai_name = ai_name or ""
            user_name = user_name or ""
            sample_user = sample_user or ""
            sample_ai = sample_ai or ""
            system_prompt = system_prompt or ""

            if not message.strip():
                return chat_history, ""

            model = anthropic_m if category == "anthropic" else m2her_m
            temp = max(0.01, min(temp, 1.0))
            top_p = max(0.01, min(top_p, 1.0))

            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": ""})

            try:
                if category == "m2her":
                    messages = []

                    if system_prompt.strip():
                        msg = {"role": "system", "content": system_prompt}
                        if ai_name.strip():
                            msg["name"] = ai_name
                        messages.append(msg)

                    if user_system.strip():
                        messages.append({"role": "user_system", "content": user_system})

                    if group_name.strip():
                        messages.append({"role": "group", "content": group_name})

                    if sample_user.strip() and sample_ai.strip():
                        messages.append(
                            {"role": "sample_message_user", "content": sample_user}
                        )
                        messages.append(
                            {"role": "sample_message_ai", "content": sample_ai}
                        )

                    for msg in chat_history[:-1]:
                        if isinstance(msg, dict):
                            role = msg.get("role", "user")
                            content = msg.get("content", "")
                            if role in ("user", "assistant"):
                                messages.append({"role": role, "content": content})

                    user_msg = {"role": "user", "content": message}
                    if user_name.strip():
                        user_msg["name"] = user_name
                    messages.append(user_msg)

                    max_completion_tokens = min(max_tok, 2048)

                    yield chat_history, ""
                    for chunk in client.chat_stream(
                        messages=messages,
                        model=model,
                        system_prompt=system_prompt,
                        temperature=temp,
                        max_tokens=max_completion_tokens,
                        use_anthropic_api=False,
                        show_thinking=False,
                    ):
                        if chunk["type"] == "error":
                            chat_history[-1]["content"] = f"❌ 错误: {chunk['content']}"
                            yield chat_history, ""
                            return

                        if chunk["type"] == "text":
                            chat_history[-1]["content"] += chunk["content"]
                            yield chat_history, ""

                else:
                    messages = []

                    if system_prompt.strip():
                        messages.append({"role": "system", "content": system_prompt})

                    for msg in chat_history[:-1]:
                        if isinstance(msg, dict):
                            role = msg.get("role", "user")
                            content = msg.get("content", "")
                            if role in ("user", "assistant"):
                                messages.append({"role": role, "content": content})

                    messages.append({"role": "user", "content": message})

                    yield chat_history, ""
                    for chunk in client.chat_stream(
                        messages=messages,
                        model=model,
                        system_prompt=system_prompt,
                        temperature=temp,
                        max_tokens=max_tok,
                        use_anthropic_api=True,
                        show_thinking=False,
                    ):
                        if chunk["type"] == "error":
                            chat_history[-1]["content"] = f"❌ 错误: {chunk['content']}"
                            yield chat_history, ""
                            return

                        if chunk["type"] == "text":
                            chat_history[-1]["content"] += chunk["content"]
                            yield chat_history, ""

            except Exception as e:
                chat_history[-1]["content"] = f"❌ 错误: {str(e)}"
                yield chat_history, ""

        def clear_chat():
            return [], ""

        send_btn.click(
            respond,
            inputs=[
                msg_input,
                chatbot,
                model_category,
                anthropic_model,
                m2her_model,
                system_prompt,
                user_system,
                group_name,
                ai_name,
                user_name,
                sample_user,
                sample_ai,
                temperature,
                top_p,
                max_tokens,
                use_anthropic,
            ],
            outputs=[chatbot, msg_input],
        )

        msg_input.submit(
            respond,
            inputs=[
                msg_input,
                chatbot,
                model_category,
                anthropic_model,
                m2her_model,
                system_prompt,
                user_system,
                group_name,
                ai_name,
                user_name,
                sample_user,
                sample_ai,
                temperature,
                top_p,
                max_tokens,
                use_anthropic,
            ],
            outputs=[chatbot, msg_input],
        )

        clear_btn.click(clear_chat, outputs=[chatbot, msg_input])


# ==================== 图像生成模块 ====================
def create_image_tab():
    """创建图像生成标签页"""
    with gr.TabItem("🎨 图像"):
        gr.Markdown("## AI 图像生成")

        with gr.Row():
            with gr.Column(scale=1):
                prompt = gr.Textbox(
                    label="提示词", placeholder="描述你想要生成的图像...", lines=3
                )
                model = gr.Dropdown(
                    choices=["image-01", "image-01-live"],
                    value="image-01",
                    label="模型",
                )
                aspect_ratio = gr.Dropdown(
                    choices=["1:1", "16:9", "4:3", "3:2", "2:3", "3:4", "9:16", "21:9"],
                    value="1:1",
                    label="宽高比",
                )
                num_images = gr.Slider(1, 9, value=1, step=1, label="生成数量")
                ref_image = gr.Image(
                    label="参考图片（可选，用于图生图）", type="filepath"
                )

                generate_btn = gr.Button("🎨 生成图像", variant="primary")

            with gr.Column(scale=2):
                output_gallery = gr.Gallery(label="生成结果", columns=3, height=600)
                status_text = gr.Textbox(label="状态", interactive=False)

        def generate_image(prompt, model, aspect, num, ref_img):
            if not prompt.strip():
                return [], "请输入提示词"

            try:
                # 构建参数
                kwargs = {
                    "prompt": prompt,
                    "model": model,
                    "aspect_ratio": aspect,
                    "n": int(num),
                }

                if ref_img:
                    kwargs["reference_image"] = ref_img

                result = client.image(**kwargs)

                # 处理结果
                image_paths = []
                if isinstance(result, list):
                    # URL 列表
                    for i, url in enumerate(result):
                        if url.startswith("http"):
                            # 下载图片
                            img_path = file_mgr.get_path(
                                "images",
                                f"image_{file_mgr.generate_timestamp()}_{i}.png",
                            )
                            import urllib.request

                            urllib.request.urlretrieve(url, img_path)
                            image_paths.append(str(img_path))
                        else:
                            image_paths.append(url)

                return image_paths, f"✅ 成功生成 {len(image_paths)} 张图片"
            except Exception as e:
                return [], f"❌ 错误: {str(e)}"

        generate_btn.click(
            generate_image,
            inputs=[prompt, model, aspect_ratio, num_images, ref_image],
            outputs=[output_gallery, status_text],
        )


# ==================== 视频生成模块 ====================
def create_video_tab():
    """创建视频生成标签页"""
    with gr.TabItem("🎬 视频"):
        gr.Markdown("## AI 视频生成")

        with gr.Tabs():
            # 文生视频
            with gr.TabItem("📝 文生视频"):
                with gr.Row():
                    with gr.Column(scale=1):
                        prompt = gr.Textbox(
                            label="视频描述",
                            placeholder="描述你想要生成的视频...",
                            lines=4,
                        )
                        model = gr.Dropdown(
                            choices=[
                                "MiniMax-Hailuo-2.3",
                                "T2V-01-Director",
                                "T2V-01",
                                "T2V-01-live",
                            ],
                            value="MiniMax-Hailuo-2.3",
                            label="模型",
                        )
                        duration = gr.Dropdown(
                            choices=[6, 10], value=6, label="时长（秒）"
                        )
                        resolution = gr.Dropdown(
                            choices=["512P", "720P", "768P", "1080P"],
                            value="768P",
                            label="分辨率",
                        )
                        generate_btn = gr.Button("🎬 生成视频", variant="primary")

                    with gr.Column(scale=2):
                        status = gr.Textbox(label="任务状态", value="等待生成...")
                        video_output = gr.Video(label="生成结果")

                def generate_text_video(prompt, model, duration, resolution):
                    if not prompt.strip():
                        return "请输入视频描述", None

                    try:
                        # 提交任务
                        task_id = client.video(
                            prompt=prompt,
                            model=model,
                            duration=int(duration),
                            resolution=resolution,
                        )

                        # 轮询状态
                        max_attempts = 60  # 最多等待10分钟
                        for i in range(max_attempts):
                            status_result = client.video_status(task_id)
                            task_status = status_result.get("status", "")

                            if task_status == "Success":
                                file_id = status_result.get("file_id")
                                if file_id:
                                    # 下载视频
                                    video_path = client.download_video(file_id)
                                    return f"✅ 视频生成成功！", video_path
                                else:
                                    return "✅ 视频生成成功，但无法获取文件", None
                            elif task_status == "Fail":
                                return "❌ 视频生成失败", None
                            elif task_status in ["Preparing", "Queueing", "Processing"]:
                                yield (
                                    f"⏳ 状态: {task_status} (等待 {i + 1} 秒)...",
                                    None,
                                )
                                time.sleep(10)
                            else:
                                yield (
                                    f"⏳ 状态: {task_status} (等待 {i + 1} 秒)...",
                                    None,
                                )
                                time.sleep(10)

                        return "⏱️ 等待超时，请稍后手动查询", None

                    except Exception as e:
                        return f"❌ 错误: {str(e)}", None

                generate_btn.click(
                    generate_text_video,
                    inputs=[prompt, model, duration, resolution],
                    outputs=[status, video_output],
                )

            # 图生视频
            with gr.TabItem("🖼️ 图生视频"):
                with gr.Row():
                    with gr.Column(scale=1):
                        first_frame = gr.Image(label="首帧图片", type="filepath")
                        prompt_img = gr.Textbox(
                            label="视频描述（可选）",
                            placeholder="描述视频内容...",
                            lines=3,
                        )
                        model_img = gr.Dropdown(
                            choices=[
                                "I2V-01-Director",
                                "I2V-01-live",
                                "I2V-01",
                                "MiniMax-Hailuo-2.3",
                            ],
                            value="I2V-01-Director",
                            label="模型",
                        )
                        duration_img = gr.Dropdown(
                            choices=[6, 10], value=6, label="时长（秒）"
                        )
                        generate_btn_img = gr.Button("🎬 生成视频", variant="primary")

                    with gr.Column(scale=2):
                        status_img = gr.Textbox(label="任务状态", value="等待生成...")
                        video_output_img = gr.Video(label="生成结果")

                def generate_image_video(first_frame, prompt, model, duration):
                    if not first_frame:
                        return "请上传首帧图片", None

                    try:
                        # 提交任务
                        task_id = client.image_to_video(
                            first_frame_image=first_frame,
                            prompt=prompt or "",
                            model=model,
                            duration=int(duration),
                        )

                        # 轮询状态
                        max_attempts = 60
                        for i in range(max_attempts):
                            status_result = client.video_status(task_id)
                            task_status = status_result.get("status", "")

                            if task_status == "Success":
                                file_id = status_result.get("file_id")
                                if file_id:
                                    video_path = client.download_video(file_id)
                                    return f"✅ 视频生成成功！", video_path
                                else:
                                    return "✅ 视频生成成功，但无法获取文件", None
                            elif task_status == "Fail":
                                return "❌ 视频生成失败", None
                            else:
                                yield (
                                    f"⏳ 状态: {task_status} (等待 {i + 1} 秒)...",
                                    None,
                                )
                                time.sleep(10)

                        return "⏱️ 等待超时，请稍后手动查询", None

                    except Exception as e:
                        return f"❌ 错误: {str(e)}", None

                generate_btn_img.click(
                    generate_image_video,
                    inputs=[first_frame, prompt_img, model_img, duration_img],
                    outputs=[status_img, video_output_img],
                )


# ==================== 音乐与音频模块 ====================
def create_audio_tab():
    """创建音乐与音频标签页"""
    with gr.TabItem("🎵 音乐"):
        gr.Markdown("## AI 音乐生成")

        with gr.Tabs():
            # 音乐生成
            with gr.TabItem("🎼 音乐创作"):
                with gr.Row():
                    with gr.Column(scale=1):
                        music_model = gr.Dropdown(
                            choices=["music-2.6", "music-cover"],
                            value="music-2.6",
                            label="模型",
                        )
                        music_instrumental = gr.Checkbox(
                            label="纯音乐模式（无人声）", value=False
                        )
                        music_prompt = gr.Textbox(
                            label="音乐描述/翻唱风格",
                            placeholder="文生音乐：描述风格、情绪、场景，如：流行音乐,欢快,适合派对...\n翻唱模式：描述目标翻唱风格，如：流行摇滚版，节奏更快",
                            lines=2,
                        )
                        music_lyrics = gr.Textbox(
                            label="歌词",
                            placeholder="[Verse]\n歌词内容...\n[Chorus]\n副歌内容...\n\n翻唱模式可留空，AI将自动从参考音频提取歌词",
                            lines=6,
                        )
                        music_lyrics_optimizer = gr.Checkbox(
                            label="自动生成歌词", value=False
                        )
                        
                        # 翻唱模式专属：参考音频
                        music_audio_url = gr.Textbox(
                            label="参考音频URL（翻唱模式）",
                            placeholder="https://example.com/reference_audio.mp3",
                            lines=2,
                        )

                        with gr.Accordion("音频参数", open=False):
                            music_sample_rate = gr.Dropdown(
                                [16000, 24000, 32000, 44100],
                                value=44100,
                                label="采样率",
                            )
                            music_bitrate = gr.Dropdown(
                                [32000, 64000, 128000, 256000],
                                value=256000,
                                label="比特率",
                            )
                            music_format_type = gr.Dropdown(
                                ["mp3", "wav", "pcm"], value="mp3", label="格式"
                            )

                        music_generate_btn = gr.Button("🎵 生成音乐", variant="primary")

                    with gr.Column(scale=2):
                        music_status = gr.Textbox(label="状态", value="等待生成...")
                        music_audio_output = gr.Audio(label="生成结果", type="filepath")

                def generate_music(
                    model,
                    instrumental,
                    prompt,
                    lyrics,
                    lyrics_opt,
                    audio_url,
                    sample_rate,
                    bitrate,
                    format_type,
                ):
                    try:
                        is_cover = model == "music-cover"
                        
                        # 校验翻唱模式
                        if is_cover:
                            if not audio_url and not prompt:
                                return "❌ 翻唱模式必须提供参考音频URL和目标风格描述", None
                        
                        # 校验非翻唱模式
                        if not is_cover:
                            if not instrumental and not lyrics_opt and not lyrics:
                                return "❌ 请输入歌词，或启用纯音乐模式/自动生成歌词", None

                        # 调用音乐生成
                        audio_data = client.music(
                            prompt=prompt if prompt else None,
                            lyrics=lyrics if lyrics else None,
                            model=model,
                            is_instrumental=instrumental and not is_cover,
                            lyrics_optimizer=lyrics_opt and not is_cover,
                            audio_url=audio_url if audio_url else None,
                            sample_rate=int(sample_rate),
                            bitrate=int(bitrate),
                            format=format_type,
                        )

                        # 保存音频文件
                        timestamp = file_mgr.generate_timestamp()
                        filename = f"music_{timestamp}.{format_type}"
                        filepath = file_mgr.save_file(audio_data, filename, "music")

                        return f"✅ 音乐生成成功！", filepath
                    except Exception as e:
                        return f"❌ 错误: {str(e)}", None

                music_generate_btn.click(
                    generate_music,
                    inputs=[
                        music_model,
                        music_instrumental,
                        music_prompt,
                        music_lyrics,
                        music_lyrics_optimizer,
                        music_audio_url,
                        music_sample_rate,
                        music_bitrate,
                        music_format_type,
                    ],
                    outputs=[music_status, music_audio_output],
                )

            # TTS
            with gr.TabItem("🗣️ 语音合成"):
                with gr.Row():
                    with gr.Column(scale=1):
                        text = gr.Textbox(
                            label="文本内容",
                            placeholder="输入要转换为语音的文本...",
                            lines=4,
                        )

                        # 加载音色列表
                        def load_voices():
                            try:
                                result = client.list_voices("system")
                                voices = result.get("voices", [])
                                if voices:
                                    choices = [v["voice_id"] for v in voices]
                                    return gr.Dropdown(
                                        choices=choices, value=choices[0]
                                    )
                                else:
                                    # 默认音色列表
                                    default_voices = [
                                        "female-chengshu",
                                        "male-chengshu",
                                        "female-yujie",
                                        "male-yujie",
                                        "female-tianmei",
                                    ]
                                    return gr.Dropdown(
                                        choices=default_voices, value="female-chengshu"
                                    )
                            except:
                                default_voices = [
                                    "female-chengshu",
                                    "male-chengshu",
                                    "female-yujie",
                                    "male-yujie",
                                    "female-tianmei",
                                ]
                                return gr.Dropdown(
                                    choices=default_voices, value="female-chengshu"
                                )

                        voice = gr.Dropdown(label="音色", choices=[])
                        tts_model = gr.Dropdown(
                            choices=[
                                "speech-2.8-hd",
                                "speech-2.8-turbo",
                                "speech-2.6-hd",
                                "speech-2.6-turbo",
                                "speech-02-hd",
                                "speech-02-turbo",
                            ],
                            value="speech-2.8-hd",
                            label="TTS模型",
                        )
                        emotion = gr.Dropdown(
                            choices=[
                                "happy",
                                "sad",
                                "angry",
                                "fearful",
                                "disgusted",
                                "surprised",
                                "calm",
                                "fluent",
                                "whisper",
                            ],
                            value="happy",
                            label="情感",
                        )
                        with gr.Row():
                            speed = gr.Slider(
                                0.5, 2.0, value=1.0, step=0.1, label="语速"
                            )
                            vol = gr.Slider(0, 10, value=1.0, step=0.1, label="音量")
                            pitch = gr.Slider(-12, 12, value=0, step=1, label="音高")

                        tts_btn = gr.Button("🗣️ 生成语音", variant="primary")

                    with gr.Column(scale=2):
                        tts_status = gr.Textbox(label="状态")
                        tts_audio = gr.Audio(label="生成结果", type="filepath")

                # 页面加载时加载音色列表
                def load_voices():
                    try:
                        result = client.list_voices("system")
                        voices = result.get("voices", [])
                        if voices:
                            choices = [v["voice_id"] for v in voices]
                            return gr.Dropdown(choices=choices, value=choices[0])
                        else:
                            # 默认音色列表
                            default_voices = [
                                "female-chengshu",
                                "male-chengshu",
                                "female-yujie",
                                "male-yujie",
                                "female-tianmei",
                            ]
                            return gr.Dropdown(
                                choices=default_voices, value="female-chengshu"
                            )
                    except:
                        default_voices = [
                            "female-chengshu",
                            "male-chengshu",
                            "female-yujie",
                            "male-yujie",
                            "female-tianmei",
                        ]
                        return gr.Dropdown(
                            choices=default_voices, value="female-chengshu"
                        )

                # 初始化音色列表
                voice.choices = load_voices().choices
                voice.value = load_voices().value

                def generate_tts(text, voice, model, emotion, speed, vol, pitch):
                    if not text.strip():
                        return "请输入文本", None

                    try:
                        audio_data = client.tts(
                            text=text,
                            voice_id=voice,
                            model=model,
                            emotion=emotion,
                            speed=speed,
                            vol=vol,
                            pitch=pitch,
                        )

                        # 保存音频
                        timestamp = file_mgr.generate_timestamp()
                        filename = f"tts_{timestamp}.mp3"
                        filepath = file_mgr.save_file(audio_data, filename, "audio")

                        return f"✅ 语音合成成功！", filepath
                    except Exception as e:
                        return f"❌ 错误: {str(e)}", None

                # 加载音色列表
                voice.choices = load_voices().choices
                voice.value = "female-chengshu"

                tts_btn.click(
                    generate_tts,
                    inputs=[text, voice, tts_model, emotion, speed, vol, pitch],
                    outputs=[tts_status, tts_audio],
                )


# ==================== 播客模块 ====================
def create_podcast_tab():
    """创建播客生成标签页"""
    with gr.TabItem("🎙️ 播客"):
        gr.Markdown("## AI 播客生成")

        with gr.Row():
            with gr.Column(scale=1):
                topic = gr.Textbox(
                    label="播客主题",
                    placeholder="输入播客主题，如：AI创作短剧会成为新风口吗？",
                    lines=2,
                )
                welcome_text = gr.Textbox(
                    label="欢迎语", value="欢迎收听本期节目！", lines=1
                )
                with gr.Accordion("对话编辑（高级）", open=False):
                    dialogue_json = gr.Code(
                        label="对话 JSON（可选，用于自定义）", language="json", lines=10
                    )

                generate_btn = gr.Button("🎙️ 生成播客", variant="primary")

            with gr.Column(scale=2):
                progress = gr.Textbox(label="生成进度", value="等待开始...")
                podcast_audio = gr.Audio(label="生成结果", type="filepath")

        def generate_podcast(topic, welcome_text, dialogue_json):
            if not topic.strip():
                return "请输入播客主题", None

            try:
                # 这里需要调用播客生成功能
                # 由于播客生成涉及多个步骤，简化处理
                yield "📝 正在生成对话脚本...", None

                # 使用 chat 方法生成对话
                system_prompt = """你是一个专业的播客制作助手。请生成一个自然流畅的双人对话播客，围绕用户提供的主题展开。
对话要求：
1. 包含两位主播：主持人（活泼开朗，引导话题）和嘉宾（专业人士，分享观点）
2. 对话形式自然，有互动和讨论，不是单方面讲解
3. 总长度控制在10-15轮对话
4. 输出严格为JSON数组，每个元素包含：
   - speaker: "主持人"或"嘉宾"
   - text: 对话内容（口语化，自然）
   - voice_id: 主持人用"female-tianmei"（甜美女声），嘉宾用"male-chengshu"（成熟男声）
   - emotion: 根据内容选择合适的情感，如happy、calm、excited等"""

                messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f'请生成关于"{topic}"的播客对话，开头必须包含欢迎语：{welcome_text}',
                    },
                ]

                response = client._request(
                    "POST",
                    "text/chatcompletion_v2",
                    json={
                        "model": "MiniMax-M2.5",
                        "messages": messages,
                        "temperature": 0.8,
                        "max_completion_tokens": 2048,
                    },
                )

                dialogue_text = response["choices"][0]["message"]["content"]

                # 尝试解析JSON
                try:
                    # 提取JSON部分
                    import re

                    json_match = re.search(r"\[.*\]", dialogue_text, re.DOTALL)
                    if json_match:
                        dialogue_data = json.loads(json_match.group())
                    else:
                        dialogue_data = json.loads(dialogue_text)
                except:
                    return "❌ 对话生成失败，无法解析JSON", None

                yield f"🎤 正在合成语音（共{len(dialogue_data)}段对话）...", None

                # 合成每段语音并合并
                audio_segments = []
                for i, item in enumerate(dialogue_data):
                    text = item.get("text", "")
                    voice_id = item.get("voice_id", "female-chengshu")
                    emotion = item.get("emotion", "happy")

                    if text:
                        try:
                            audio_data = client.tts(
                                text=text,
                                voice_id=voice_id,
                                emotion=emotion,
                                speed=1.0,
                                vol=1.0,
                            )
                            audio_segments.append(audio_data)
                            yield f"🎤 合成进度: {i + 1}/{len(dialogue_data)}", None
                        except:
                            continue

                # 合并音频（简化处理，实际应该使用音频处理库）
                # 这里只保存第一段作为示例
                if audio_segments:
                    timestamp = file_mgr.generate_timestamp()
                    filename = f"podcast_{timestamp}.mp3"
                    filepath = file_mgr.save_file(
                        audio_segments[0], filename, "podcasts"
                    )
                    return f"✅ 播客生成成功（示例，仅第一段）！", filepath
                else:
                    return "❌ 语音合成失败", None

            except Exception as e:
                return f"❌ 错误: {str(e)}", None

        generate_btn.click(
            generate_podcast,
            inputs=[topic, welcome_text, dialogue_json],
            outputs=[progress, podcast_audio],
        )


# ==================== 文件管理模块 ====================
def create_file_tab():
    """创建文件管理标签页"""
    with gr.TabItem("📁 文件"):
        gr.Markdown("## 文件管理")

        with gr.Row():
            file_purpose = gr.Dropdown(
                choices=["voice_clone", "prompt_audio", "t2a_async_input"],
                value="voice_clone",
                label="文件用途",
                scale=3,
            )
            refresh_btn = gr.Button("🔄 刷新列表", scale=1)

        files_state = gr.State([])

        file_table = gr.Dataframe(
            headers=["ID", "文件名", "用途", "大小", "创建时间"],
            label="文件列表",
            interactive=False,
        )

        with gr.Accordion("📤 上传文件", open=False):
            with gr.Row():
                upload_file = gr.File(label="选择文件", file_count="single")
                with gr.Column(scale=1):
                    gr.HTML("<br>")
                    upload_btn = gr.Button("⬆️ 上传", variant="primary")

        with gr.Accordion("📥 下载/删除文件", open=False):
            with gr.Row():
                download_file_id = gr.Textbox(
                    label="文件ID",
                    placeholder="点击列表自动填充...",
                    scale=3,
                )
                download_btn = gr.Button("⬇️ 下载", variant="secondary", scale=1)
                delete_btn = gr.Button("🗑️ 删除", variant="stop", scale=1)

            download_status = gr.Textbox(label="状态", interactive=False)

        def refresh_files(purpose):
            try:
                result = client.list_files(purpose)
                files = result.get("files", [])

                data = []
                for f in files:
                    created_at = f.get("created_at", 0)
                    created_str = (
                        datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M:%S")
                        if created_at
                        else ""
                    )
                    data.append(
                        [
                            str(f.get("file_id", "")),  # 确保ID是字符串
                            f.get("filename", ""),
                            f.get("purpose", ""),
                            f"{f.get('bytes', 0) / 1024:.1f} KB",
                            created_str,
                        ]
                    )

                table_data = data if data else [["", "暂无文件", "", "", ""]]
                return table_data, data  # 同时返回表格显示数据和完整数据
            except Exception as e:
                error_data = [["", f"错误: {str(e)}", "", "", ""]]
                return error_data, error_data

        def upload_new_file(file_obj, purpose):
            if not file_obj:
                error_data = [["", "请选择文件", "", "", ""]]
                return error_data, error_data

            try:
                result = client.upload_file(file_obj, purpose)
                return refresh_files(purpose)
            except Exception as e:
                error_data = [["", f"上传失败: {str(e)}", "", "", ""]]
                return error_data, error_data

        def download_file(file_id):
            if not file_id.strip():
                return "请输入文件ID"

            try:
                filepath = client.download_file(file_id.strip())
                if Path(filepath).exists():
                    return f"✅ 文件下载成功: {filepath}"
                else:
                    return "❌ 下载失败: 文件不存在"
            except Exception as e:
                return f"❌ 下载失败: {str(e)}"

        def delete_file(file_id, purpose):
            if not file_id.strip():
                table_data, files_data = refresh_files(purpose)
                return "请输入文件ID", table_data, files_data

            try:
                # 调用删除方法
                result = client.delete_file(file_id.strip(), purpose)
                if "base_resp" in result and result["base_resp"]["status_code"] == 0:
                    table_data, files_data = refresh_files(purpose)
                    return f"✅ 文件 {file_id} 删除成功", table_data, files_data
                else:
                    error_msg = result.get("base_resp", {}).get(
                        "status_msg", "未知错误"
                    )
                    table_data, files_data = refresh_files(purpose)
                    return f"❌ 删除失败: {error_msg}", table_data, files_data
            except Exception as e:
                table_data, files_data = refresh_files(purpose)
                return f"❌ 删除失败: {str(e)}", table_data, files_data

        # 点击表格行任意位置自动填充该文件的ID
        def on_select_file(selected_data: gr.SelectData, files_data):
            # 获取选中行的索引
            if selected_data.index is not None and files_data:
                row_index = selected_data.index[0]
                if 0 <= row_index < len(files_data):
                    # 返回该行第一列的文件ID
                    return files_data[row_index][0]
            return ""

        file_table.select(
            on_select_file, inputs=[files_state], outputs=[download_file_id]
        )

        refresh_btn.click(
            refresh_files, inputs=[file_purpose], outputs=[file_table, files_state]
        )
        upload_btn.click(
            upload_new_file,
            inputs=[upload_file, file_purpose],
            outputs=[file_table, files_state],
        )
        download_btn.click(
            download_file,
            inputs=[download_file_id],
            outputs=[download_status],
        )
        delete_btn.click(
            delete_file,
            inputs=[download_file_id, file_purpose],
            outputs=[download_status, file_table, files_state],
        )

        # 初始加载
        # file_table.value = refresh_files("voice_clone")


# ==================== 音色管理模块 ====================
def create_voice_tab():
    """创建音色管理标签页"""
    with gr.TabItem("🔊 音色"):
        gr.Markdown("## 音色管理")

        with gr.Tabs():
            with gr.TabItem("📋 音色列表"):
                voice_type = gr.Dropdown(
                    choices=["all", "system", "cloning", "generation"],
                    value="all",
                    label="音色类型",
                )
                refresh_voice_btn = gr.Button("🔄 刷新列表")
                voice_list = gr.Dataframe(
                    headers=["ID", "名称", "类型", "描述"], label="可用音色"
                )

                def refresh_voices(vtype):
                    try:
                        result = client.list_voices(vtype)
                        data = []

                        # 按类型获取音色列表
                        type_mapping = {
                            "all": [
                                "system_voice",
                                "voice_cloning",
                                "voice_generation",
                                "music_generation",
                            ],
                            "system": ["system_voice"],
                            "cloning": ["voice_cloning"],
                            "generation": ["voice_generation"],
                        }

                        target_types = type_mapping.get(vtype, ["system_voice"])

                        for t in target_types:
                            if t in result:
                                for v in result[t]:
                                    voice_type = t.replace("_voice", "").replace(
                                        "voice_", ""
                                    )
                                    # 提取描述信息
                                    desc = v.get(
                                        "desc",
                                        v.get("description", v.get("remarks", "")),
                                    )
                                    if isinstance(desc, list):
                                        desc = " ".join(desc)
                                    data.append(
                                        [
                                            v.get("voice_id", ""),
                                            v.get(
                                                "name",
                                                v.get(
                                                    "voice_name", v.get("voice_id", "")
                                                ),
                                            ),
                                            voice_type,
                                            desc,
                                        ]
                                    )

                        return data if data else [["", "暂无音色", "", ""]]
                    except Exception as e:
                        return [["", f"错误: {str(e)}", "", ""]]

                refresh_voice_btn.click(
                    refresh_voices, inputs=[voice_type], outputs=[voice_list]
                )

                # 保存刷新函数到全局，方便页面加载时调用
                global refresh_voices_global
                refresh_voices_global = refresh_voices
                global voice_type_global
                voice_type_global = voice_type
                global voice_list_global
                voice_list_global = voice_list

            with gr.TabItem("🎤 克隆音色"):
                with gr.Row():
                    with gr.Column():
                        clone_audio = gr.Audio(label="上传音频样本", type="filepath")
                        voice_id_input = gr.Textbox(
                            label="音色ID", placeholder="自定义音色标识..."
                        )
                        clone_btn = gr.Button("🎤 开始克隆", variant="primary")
                    with gr.Column():
                        clone_status = gr.Textbox(label="状态")

                def clone_voice(audio_file, voice_id):
                    if not audio_file:
                        return "请上传音频文件"
                    if not voice_id:
                        return "请输入音色ID"

                    try:
                        # 先上传文件
                        upload_result = client.upload_file(audio_file, "voice_clone")
                        file_id = upload_result.get("file", {}).get("file_id")

                        if not file_id:
                            return "文件上传失败"

                        # 克隆音色
                        result = client.voice_clone(
                            file_id=file_id,
                            voice_id=voice_id,
                            text="这是音色克隆的试听音频",
                        )

                        demo_audio = result.get("demo_audio", "")
                        if demo_audio:
                            return f"✅ 音色克隆成功！试听链接: {demo_audio[:100]}..."
                        else:
                            return "✅ 音色克隆成功！"
                    except Exception as e:
                        return f"❌ 错误: {str(e)}"

                clone_btn.click(
                    clone_voice,
                    inputs=[clone_audio, voice_id_input],
                    outputs=[clone_status],
                )

            with gr.TabItem("✨ 设计音色"):
                with gr.Row():
                    with gr.Column():
                        voice_desc = gr.Textbox(
                            label="音色描述",
                            placeholder="描述你想要的音色特征...",
                            lines=3,
                        )
                        preview_text = gr.Textbox(
                            label="预览文本",
                            value="这是一段测试语音，用于试听设计的音色效果。",
                            lines=2,
                        )
                        design_btn = gr.Button("✨ 生成音色", variant="primary")
                    with gr.Column():
                        design_status = gr.Textbox(label="状态")
                        design_audio = gr.Audio(label="试听")

                def design_voice(desc, preview):
                    if not desc.strip():
                        return "请输入音色描述", None

                    try:
                        result = client.voice_design(prompt=desc, preview_text=preview)

                        voice_id = result.get("voice_id", "")
                        trial_audio = result.get("trial_audio", "")

                        if trial_audio:
                            # 保存试听音频
                            timestamp = file_mgr.generate_timestamp()
                            filename = f"voice_design_{timestamp}.mp3"
                            filepath = file_mgr.save_file(
                                trial_audio, filename, "audio"
                            )
                            return f"✅ 音色设计成功！ID: {voice_id}", filepath
                        else:
                            return f"✅ 音色设计成功！ID: {voice_id}", None
                    except Exception as e:
                        return f"❌ 错误: {str(e)}", None

                design_btn.click(
                    design_voice,
                    inputs=[voice_desc, preview_text],
                    outputs=[design_status, design_audio],
                )


# ==================== 主应用 ====================
def create_app():
    """创建主应用"""
    # 初始化
    connected, msg = init_client()

    with gr.Blocks(title="MiniMax AI 创意工作室", fill_width=True) as app:
        gr.Markdown(
            f"# 🎨 MiniMax AI 创意工作室 <span style='font-size: 14px; color: #666; margin-left: 10px;'>{msg}</span>"
        )
        gr.Markdown("基于 MiniMax API 的多功能 AI 创作平台")

        if not connected:
            gr.Markdown("""
            ⚠️ **连接失败**

            请确保已配置 MiniMax API 密钥。可以通过以下方式配置：
            1. 环境变量：`MINIMAX_API_KEY` 和 `MINIMAX_GROUP_ID`
            2. 运行命令：`python minimax_cli.py --setup`
            """)

        # 主标签页
        with gr.Tabs():
            create_chat_tab()
            create_image_tab()
            create_video_tab()
            create_audio_tab()
            create_podcast_tab()
            create_file_tab()
            create_voice_tab()

        # 页面加载事件
        def on_load():
            # 初始化音色列表
            try:
                if client:
                    result = client.list_voices("all")
                    voices = result.get("voices", [])
                    data = []
                    for v in voices:
                        data.append(
                            [
                                v.get("voice_id", ""),
                                v.get("name", v.get("voice_id", "")),
                                v.get("type", "system"),
                            ]
                        )
                    return data if data else [["", "暂无音色", ""]]
            except:
                return [["", "加载失败", ""]]

        app.load(on_load, outputs=[voice_list_global])

        # 底部
        gr.Markdown("---")
        gr.Markdown("Made with ❤️ using Gradio & MiniMax API")

    return app


# ==================== 入口 ====================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MiniMax AI Web UI")
    parser.add_argument("--host", default="0.0.0.0", help="服务器地址")
    parser.add_argument("--port", type=int, default=7860, help="服务器端口")
    parser.add_argument("--share", action="store_true", help="生成公网分享链接")
    args = parser.parse_args()

    app = create_app()
    app.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        show_error=True,
        theme=gr.themes.Soft(),
    )
