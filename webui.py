#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniMax AI Web UI
Flask-based chat-style interface with SSE streaming
"""

import os
import sys
import json
import uuid
import requests
from pathlib import Path
from typing import Generator, Optional, Dict, Any, List

from flask import (
    Flask,
    render_template,
    request,
    Response,
    jsonify,
    stream_with_context,
)

sys.path.insert(0, str(Path(__file__).parent))
from minimax_cli import MiniMaxClient, FileManager

app = Flask(__name__)
app.secret_key = os.urandom(24)

client: Optional[MiniMaxClient] = None
file_mgr: Optional[FileManager] = None
api_key: Optional[str] = None
group_id: Optional[str] = None

CHAT_MODELS = [
    {
        "id": "MiniMax-M2.7",
        "name": "MiniMax-M2.7",
        "desc": "最新旗舰 (~60 TPS)",
        "context": "204,800",
    },
    {
        "id": "MiniMax-M2.7-highspeed",
        "name": "MiniMax-M2.7-highspeed",
        "desc": "极速版 (~100 TPS)",
        "context": "204,800",
    },
    {
        "id": "MiniMax-M2.5",
        "name": "MiniMax-M2.5",
        "desc": "性价比 (~60 TPS)",
        "context": "65,536",
    },
    {
        "id": "MiniMax-M2.5-highspeed",
        "name": "MiniMax-M2.5-highspeed",
        "desc": "极速版 (~100 TPS)",
        "context": "65,536",
    },
    {
        "id": "MiniMax-M2.1",
        "name": "MiniMax-M2.1",
        "desc": "多语言编程 (~60 TPS)",
        "context": "65,536",
    },
    {
        "id": "MiniMax-M2.1-highspeed",
        "name": "MiniMax-M2.1-highspeed",
        "desc": "极速版 (~100 TPS)",
        "context": "65,536",
    },
    {
        "id": "MiniMax-M2",
        "name": "MiniMax-M2",
        "desc": "Agent 工作流",
        "context": "65,536",
    },
    {"id": "M2-her", "name": "M2-her", "desc": "角色扮演/对话", "context": "32,768"},
]

sessions: Dict[str, List[Dict]] = {}


def init_client():
    global client, file_mgr, api_key, group_id
    try:
        client = MiniMaxClient()
        file_mgr = FileManager()
        api_key = client.api_key
        group_id = client.group_id
        return True
    except Exception as e:
        print(f"Init failed: {e}")
        return False


def get_or_create_session(session_id: str) -> List[Dict]:
    if session_id not in sessions:
        sessions[session_id] = []
    return sessions[session_id]


def get_headers() -> Dict[str, str]:
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


@app.route("/")
def index():
    return render_template("webui.html", models=CHAT_MODELS)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    model = data.get("model", "MiniMax-M2.7")
    system_prompt = data.get("system_prompt", "")
    temperature = data.get("temperature", 1.0)
    max_tokens = data.get("max_tokens", 2048)
    session_id = data.get("session_id", str(uuid.uuid4()))
    stream = data.get("stream", True)

    if not client:
        return jsonify({"error": "Client not initialized"}), 500

    if not message.strip():
        return jsonify({"error": "Message is empty"}), 400

    history = get_or_create_session(session_id)

    def generate() -> Generator[str, None, None]:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(history)
            messages.append({"role": "user", "content": message})

            full_response = ""

            req_data = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream,
            }

            url = f"https://api.minimaxi.com/v1/text/chatcompletion_v2"

            if stream:
                response = requests.post(
                    url, headers=get_headers(), json=req_data, stream=True, timeout=60
                )
                response.raise_for_status()

                for line in response.iter_lines():
                    if not line:
                        continue
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        chunk = line[6:]
                        if chunk == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(chunk)
                            if "choices" in chunk_data and chunk_data["choices"]:
                                delta = chunk_data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    full_response += content
                                    yield f"data: {json.dumps({'content': content})}\n\n"
                        except json.JSONDecodeError:
                            continue
            else:
                response = requests.post(
                    url, headers=get_headers(), json=req_data, timeout=60
                )
                response.raise_for_status()
                result = response.json()
                if "choices" in result and result["choices"]:
                    full_response = result["choices"][0]["message"]["content"]
                    yield f"data: {json.dumps({'content': full_response})}\n\n"

            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": full_response})

            yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@app.route("/api/chat/anthropic", methods=["POST"])
def chat_anthropic():
    data = request.json
    message = data.get("message", "")
    model = data.get("model", "MiniMax-M2.7")
    system_prompt = data.get("system_prompt", "")
    temperature = data.get("temperature", 1.0)
    max_tokens = data.get("max_tokens", 2048)
    session_id = data.get("session_id", str(uuid.uuid4()))
    show_thinking = data.get("show_thinking", False)

    if not client:
        return jsonify({"error": "Client not initialized"}), 500

    history = get_or_create_session(session_id)

    def generate() -> Generator[str, None, None]:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(history)
            messages.append({"role": "user", "content": message})

            full_response = ""
            thinking_content = ""

            req_data = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True,
            }

            if show_thinking:
                req_data["thinking"] = {"type": "enabled", "budget_tokens": 10000}

            url = "https://api.minimaxi.com/anthropic/v1/messages"
            headers = get_headers()
            headers["anthropic-version"] = "2023-06-01"

            response = requests.post(
                url, headers=headers, json=req_data, stream=True, timeout=120
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    chunk = line[6:]
                    try:
                        event = json.loads(chunk)
                        event_type = event.get("type", "")

                        if event_type == "content_block_delta":
                            delta = event.get("delta", {})
                            block_type = delta.get("type", "text_delta")
                            text = delta.get("text", "")
                            if text:
                                if block_type == "thinking_delta":
                                    thinking_content += text
                                    yield f"data: {json.dumps({'thinking': text})}\n\n"
                                else:
                                    full_response += text
                                    yield f"data: {json.dumps({'content': text})}\n\n"

                        elif event_type == "content_block_start":
                            block = event.get("content_block", {})
                            if block.get("type") == "thinking":
                                yield f"data: {json.dumps({'thinking_start': True})}\n\n"

                        elif event_type == "content_block_stop":
                            yield f"data: {json.dumps({'block_stop': True})}\n\n"

                    except json.JSONDecodeError:
                        continue

            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": full_response})

            yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@app.route("/api/clear", methods=["POST"])
def clear_session():
    session_id = request.json.get("session_id", "")
    if session_id in sessions:
        del sessions[session_id]
    return jsonify({"success": True})


@app.route("/api/models")
def get_models():
    return jsonify(CHAT_MODELS)


@app.route("/api/image", methods=["POST"])
def generate_image():
    if not client:
        return jsonify({"error": "Client not initialized"}), 500

    data = request.json
    prompt = data.get("prompt", "")
    model = data.get("model", "image-01")
    aspect_ratio = data.get("aspect_ratio", "1:1")
    n = data.get("n", 1)

    try:
        result = client.image(
            prompt=prompt, model=model, aspect_ratio=aspect_ratio, n=n
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/video", methods=["POST"])
def generate_video():
    if not client:
        return jsonify({"error": "Client not initialized"}), 500

    data = request.json
    prompt = data.get("prompt", "")
    model = data.get("model", "MiniMax-Hailuo-2.3")
    first_frame = data.get("first_frame_image")

    try:
        result = client.video(prompt=prompt, model=model)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/video/status/<task_id>")
def video_status(task_id):
    if not client:
        return jsonify({"error": "Client not initialized"}), 500

    try:
        result = client.video_status(task_id=task_id)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/music", methods=["POST"])
def generate_music():
    if not client:
        return jsonify({"error": "Client not initialized"}), 500

    data = request.json
    prompt = data.get("prompt", "")
    lyrics = data.get("lyrics", "")

    try:
        result = client.music(prompt=prompt, lyrics=lyrics)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tts", methods=["POST"])
def generate_tts():
    if not client:
        return jsonify({"error": "Client not initialized"}), 500

    data = request.json
    text = data.get("text", "")
    voice_id = data.get("voice_id", "female-shaonv")
    model = data.get("model", "speech-2.6-hd")
    emotion = data.get("emotion", "happy")
    speed = data.get("speed", 1.0)

    try:
        result = client.tts(
            text=text, voice_id=voice_id, model=model, emotion=emotion, speed=speed
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/voices")
def list_voices():
    if not client:
        return jsonify({"error": "Client not initialized"}), 500

    try:
        result = client.list_voices()
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/status")
def status():
    return jsonify({"initialized": client is not None, "session_count": len(sessions)})


if __name__ == "__main__":
    print("🚀 Initializing MiniMax AI WebUI...")
    if init_client():
        print("✅ Client initialized successfully")
        print("🌐 Starting server at http://localhost:5000")
        app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
    else:
        print("❌ Failed to initialize client. Please check your API credentials.")
        sys.exit(1)
