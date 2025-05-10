import sys
import os
import requests
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, QComboBox
)

def get_env_variable(var_name: str) -> str:
    return os.getenv(var_name)

PURPOSE_OPTIONS = [
    ("retrieval", "知识库检索（pdf/docx/txt）"),
    ("fine-tune", "模型finetune（jsonl）"),
    ("fine-tune-result", "finetune训练结果"),
    ("voice_clone", "快速复刻原始文件（mp3/m4a/wav）"),
    ("prompt_audio", "音色复刻示例音频（mp3/m4a/wav）"),
    ("assistants", "助手（详见官方文档）"),
    ("role-recognition", "文本角色分类（txt/json，正文需为json格式）"),
    ("t2a_async_input", "异步超长文本语音生成（txt）"),
]

def format_upload_result(resp_json):
    """格式化上传结果"""
    if not isinstance(resp_json, dict):
        return "返回内容无法解析"
    file_info = resp_json.get("file", {})
    base_resp = resp_json.get("base_resp", {})
    lines = []
    lines.append("【文件信息】")
    lines.append(f"文件ID: {file_info.get('file_id', '-')}")
    lines.append(f"文件名: {file_info.get('filename', '-')}")
    lines.append(f"文件大小: {file_info.get('bytes', '-')} 字节")
    lines.append(f"用途: {file_info.get('purpose', '-')}")
    lines.append(f"创建时间: {file_info.get('created_at', '-')}")
    lines.append("")
    lines.append("【状态信息】")
    lines.append(f"状态码: {base_resp.get('status_code', '-')}")
    lines.append(f"状态详情: {base_resp.get('status_msg', '-')}")
    return "\n".join(lines)

def extract_status_from_text(text):
    """从非标准返回内容中提取状态码和详细错误信息，并返回中文提示"""
    code_map = {
        1000: "未知错误",
        1001: "超时",
        1002: "触发RPM限流",
        1004: "鉴权失败",
        1008: "余额不足",
        1013: "服务内部错误",
        1026: "输入内容错误",
        1027: "输出内容错误",
        1039: "触发TPM限流",
        2013: "输入格式信息不正常"
    }
    # 提取 status_code
    code_match = re.search(r'status[_\s]?code[\"\':： ]*([0-9]+)', text, re.IGNORECASE)
    # 提取 status_msg
    msg_match = re.search(r'status[_\s]?msg[\"\':： ]*([^\n\"}]+)', text, re.IGNORECASE)
    code = int(code_match.group(1)) if code_match else None
    zh_msg = code_map.get(code, "未知错误") if code else None
    detail_msg = msg_match.group(1).strip() if msg_match else None

    if code:
        result = f"【上传失败】\n状态码: {code}\n原因: {zh_msg}"
        if detail_msg:
            result += f"\n详情: {detail_msg}"
        return result
    return "【上传失败】\n未能识别状态码，请检查返回内容或联系管理员。"

class FileUploadWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MiniMax 文件上传工具")
        self.setMinimumSize(400, 300)
        self.file_path = None

        layout = QVBoxLayout()

        self.label = QLabel("请选择要上传的文件：")
        layout.addWidget(self.label)

        self.select_btn = QPushButton("选择文件")
        self.select_btn.clicked.connect(self.select_file)
        layout.addWidget(self.select_btn)

        self.purpose_label = QLabel("请选择文件用途（purpose）：")
        layout.addWidget(self.purpose_label)

        self.purpose_combo = QComboBox()
        for value, desc in PURPOSE_OPTIONS:
            self.purpose_combo.addItem(f"{value} - {desc}", value)
        layout.addWidget(self.purpose_combo)

        self.upload_btn = QPushButton("上传文件")
        self.upload_btn.clicked.connect(self.upload_file)
        self.upload_btn.setEnabled(False)
        layout.addWidget(self.upload_btn)

        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*)")
        if file_path:
            self.file_path = file_path
            self.label.setText(f"已选择文件: {os.path.basename(file_path)}")
            self.upload_btn.setEnabled(True)
        else:
            self.label.setText("请选择要上传的文件：")
            self.upload_btn.setEnabled(False)

    def upload_file(self):
        if not self.file_path or not os.path.isfile(self.file_path):
            QMessageBox.warning(self, "错误", "文件不存在，请重新选择。")
            return

        group_id = get_env_variable('MINIMAX_GROUP_ID')
        api_key = get_env_variable('MINIMAX_API_KEY')
        if not group_id or not api_key:
            QMessageBox.critical(self, "环境变量错误", "请确保已设置 MINIMAX_GROUP_ID 和 MINIMAX_API_KEY 环境变量。")
            return

        purpose = self.purpose_combo.currentData()
        if not purpose:
            QMessageBox.warning(self, "错误", "请选择文件用途（purpose）")
            return

        url = f"https://api.minimax.chat/v1/files/upload?GroupId={group_id}"
        payload = {'purpose': purpose}
        files = {'file': open(self.file_path, 'rb')}
        headers = {
            'authority': 'api.minimax.chat',
            'Authorization': f'Bearer {api_key}',
        }

        try:
            response = requests.post(url, headers=headers, data=payload, files=files)
            try:
                resp_json = response.json()
                result_text = format_upload_result(resp_json)
            except Exception:
                # 解析失败时，尝试提取状态码和状态信息
                result_text = extract_status_from_text(response.text)
            self.result_label.setText(result_text)
            QMessageBox.information(self, "上传完成", result_text)
        except Exception as e:
            QMessageBox.critical(self, "上传失败", f"上传过程中发生错误：{e}")

def main():
    app = QApplication(sys.argv)
    window = FileUploadWidget()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
