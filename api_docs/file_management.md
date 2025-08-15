# 文件管理（File Management）API文档

## 功能概述
- ✅ 统一文件管理系统
- ✅ 支持5个核心操作：上传、列出、检索、删除、下载
- ✅ 多用途支持：知识库、微调、语音克隆、助手、角色识别等
- ✅ 大容量支持：总容量100GB，单文件512MB
- ✅ 多格式支持：pdf、docx、txt、jsonl、mp3、m4a、wav等

## 接口概览

### 5个核心接口
| 接口 | 地址 | 方法 | 功能 |
|------|------|------|------|
| **上传** | `/v1/files/upload` | POST | 上传文件到云端 |
| **列出** | `/v1/files/list` | GET | 查询所有文件 |
| **检索** | `/v1/files/retrieve` | GET | 获取单个文件信息 |
| **删除** | `/v1/files/delete` | POST | 删除指定文件 |
| **下载** | `/v1/files/retrieve_content` | GET | 下载文件内容 |

## 容量和限制

### 存储限制
| 限制项目 | 大小限制 | 说明 |
|----------|----------|------|
| **总容量** | 100GB | 每个账户总存储空间 |
| **单文件** | 512MB | 单个文件最大大小 |
| **文件数量** | 无限制 | 文件数量无上限 |

### 支持格式
| 使用目的 | 支持格式 | 说明 |
|----------|----------|------|
| **知识库检索** | pdf, docx, txt | 文档内容索引 |
| **模型微调** | jsonl | 训练数据格式 |
| **语音克隆** | mp3, m4a, wav | 音频文件 |
| **助手** | 多种格式 | 根据助手需求 |
| **角色识别** | txt, json | 文本角色分类 |

## 1. 上传接口（Upload）

### 接口地址
`POST https://api.minimaxi.com/v1/files/upload`

### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| **purpose** | string | ✅ | 文件使用目的 |
| **file** | file | ✅ | 需要上传的文件 |

### purpose参数说明
| 取值 | 支持格式 | 用途说明 |
|------|----------|----------|
| **retrieval** | pdf, docx, txt | 知识库检索 |
| **fine-tune** | jsonl | 模型微调训练 |
| **fine-tune-result** | - | 微调结果文件 |
| **voice_clone** | mp3, m4a, wav | 语音克隆音频 |
| **prompt_audio** | mp3, m4a, wav | 音色复刻示例 |
| **assistants** | 多种格式 | 助手文件 |
| **role-recognition** | txt, json | 文本角色分类 |
| **t2a_async_input** | - | 异步语音合成文本 |

### 基础上传示例
```python
import requests

api_key = "your_api_key"
url = "https://api.minimaxi.com/v1/files/upload"

headers = {
    'Authorization': f'Bearer {api_key}'
}

# 上传PDF文档用于知识库
files = {
    'file': open('document.pdf', 'rb')
}

data = {
    'purpose': 'retrieval'
}

response = requests.post(url, headers=headers, data=data, files=files)
result = response.json()

print(f"文件ID: {result['file']['file_id']}")
print(f"文件名: {result['file']['filename']}")
print(f"文件大小: {result['file']['bytes']} bytes")
```

### 不同用途上传示例
```python
class FileUploader:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.minimaxi.com/v1/files/upload"
    
    def upload_document(self, file_path: str, purpose: str = "retrieval"):
        """通用文件上传"""
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        files = {'file': open(file_path, 'rb')}
        data = {'purpose': purpose}
        
        response = requests.post(self.base_url, headers=headers, data=data, files=files)
        return response.json()
    
    def upload_knowledge_base(self, file_path: str):
        """上传知识库文档"""
        return self.upload_document(file_path, "retrieval")
    
    def upload_training_data(self, jsonl_path: str):
        """上传微调训练数据"""
        return self.upload_document(jsonl_path, "fine-tune")
    
    def upload_voice_sample(self, audio_path: str):
        """上传语音样本"""
        supported_formats = ['.mp3', '.m4a', '.wav']
        if any(audio_path.endswith(fmt) for fmt in supported_formats):
            return self.upload_document(audio_path, "voice_clone")
        else:
            raise ValueError("不支持的音频格式")

# 使用示例
uploader = FileUploader("your_api_key")

# 上传PDF文档
result = uploader.upload_knowledge_base("company_policy.pdf")

# 上传训练数据
result = uploader.upload_training_data("training_data.jsonl")

# 上传语音样本
result = uploader.upload_voice_sample("sample_voice.mp3")
```

## 2. 列出接口（List）

### 接口地址
`GET https://api.minimaxi.com/v1/files/list`

### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| **purpose** | string | ❌ | 按用途筛选文件 |

### 列出文件示例
```python
import requests

class FileManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.minimaxi.com/v1/files"
    
    def list_files(self, purpose: str = None):
        """列出所有文件"""
        url = f"{self.base_url}/list"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        params = {}
        if purpose:
            params['purpose'] = purpose
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()
    
    def list_by_purpose(self, purpose: str):
        """按用途列出文件"""
        return self.list_files(purpose)
    
    def get_file_statistics(self):
        """获取文件统计信息"""
        result = self.list_files()
        files = result.get('files', [])
        
        stats = {
            'total_files': len(files),
            'total_size': sum(f['bytes'] for f in files),
            'by_purpose': {}
        }
        
        for file in files:
            purpose = file['purpose']
            stats['by_purpose'][purpose] = stats['by_purpose'].get(purpose, 0) + 1
        
        return stats

# 使用示例
manager = FileManager("your_api_key")

# 列出所有文件
all_files = manager.list_files()
print(f"共找到 {len(all_files['files'])} 个文件")

# 按用途筛选
pdf_files = manager.list_by_purpose("retrieval")
print(f"知识库文档: {len(pdf_files['files'])} 个")

# 获取统计信息
stats = manager.get_file_statistics()
print(f"总存储: {stats['total_size'] / (1024*1024):.2f} MB")
```

## 3. 检索接口（Retrieve）

### 接口地址
`GET https://api.minimaxi.com/v1/files/retrieve`

### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| **file_id** | string | ✅ | 文件唯一标识符 |

### 检索文件示例
```python
def get_file_info(self, file_id: str):
    """获取单个文件信息"""
    url = f"{self.base_url}/retrieve"
    headers = {
        'Authorization': f'Bearer {self.api_key}',
        'Content-Type': 'application/json'
    }
    
    params = {'file_id': file_id}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def find_file_by_name(self, filename: str):
    """通过文件名查找文件"""
    all_files = self.list_files()
    for file in all_files.get('files', []):
        if file['filename'] == filename:
            return self.get_file_info(file['file_id'])
    return None

# 使用示例
file_info = manager.get_file_info("file_12345")
print(f"文件: {file_info['file']['filename']}")
print(f"大小: {file_info['file']['bytes'] / (1024*1024):.2f} MB")
print(f"用途: {file_info['file']['purpose']}")
```

## 4. 删除接口（Delete）

### 接口地址
`POST https://api.minimaxi.com/v1/files/delete`

### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| **file_id** | string | ✅ | 要删除的文件ID |

### 删除文件示例
```python
def delete_file(self, file_id: str):
    """删除指定文件"""
    url = f"{self.base_url}/delete"
    headers = {
        'Authorization': f'Bearer {self.api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {'file_id': file_id}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def cleanup_by_purpose(self, purpose: str):
    """清理特定用途的所有文件"""
    files = self.list_by_purpose(purpose)
    deleted_count = 0
    
    for file in files.get('files', []):
        result = self.delete_file(file['file_id'])
        if result['base_resp']['status_code'] == 0:
            deleted_count += 1
            print(f"已删除: {file['filename']}")
    
    return deleted_count

def delete_old_files(self, days_old: int = 30):
    """删除旧文件"""
    import time
    from datetime import datetime, timedelta
    
    all_files = self.list_files()
    cutoff_time = datetime.now() - timedelta(days=days_old)
    deleted_count = 0
    
    for file in all_files.get('files', []):
        file_time = datetime.fromtimestamp(file['created_at'])
        if file_time < cutoff_time:
            result = self.delete_file(file['file_id'])
            if result['base_resp']['status_code'] == 0:
                deleted_count += 1
    
    return deleted_count

# 使用示例
result = manager.delete_file("file_12345")
if result['base_resp']['status_code'] == 0:
    print("文件删除成功")

# 清理知识库文档
deleted = manager.cleanup_by_purpose("retrieval")
print(f"共删除 {deleted} 个知识库文档")
```

## 5. 下载接口（RetrieveContent）

### 接口地址
`GET https://api.minimaxi.com/v1/files/retrieve_content`

### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| **file_id** | string | ✅ | 要下载的文件ID |

### 下载文件示例
```python
import os

def download_file(self, file_id: str, output_path: str = None):
    """下载文件内容"""
    # 先获取文件信息
    file_info = self.get_file_info(file_id)
    if not file_info:
        return None
    
    filename = file_info['file']['filename']
    if not output_path:
        output_path = f"./downloads/{filename}"
    
    # 确保下载目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 下载文件内容
    url = f"{self.base_url}/retrieve_content"
    headers = {
        'Authorization': f'Bearer {self.api_key}'
    }
    
    response = requests.get(url, headers=headers, params={'file_id': file_id})
    
    # 保存文件
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    return output_path

def download_all_files(self, output_dir: str = "./downloads"):
    """下载所有文件"""
    all_files = self.list_files()
    downloaded_files = []
    
    for file in all_files.get('files', []):
        output_path = os.path.join(output_dir, file['filename'])
        downloaded = self.download_file(file['file_id'], output_path)
        if downloaded:
            downloaded_files.append(downloaded)
    
    return downloaded_files

# 使用示例
filepath = manager.download_file("file_12345", "./downloads/document.pdf")
print(f"文件已下载到: {filepath}")

# 批量下载
all_files = manager.download_all_files("./my_files")
print(f"共下载 {len(all_files)} 个文件")
```

## 高级应用示例

### 1. 完整文件管理类
```python
import json
import os
from datetime import datetime
from typing import List, Dict, Any

class MiniMaxFileManager:
    def __init__(self, api_key: str, group_id: str = None):
        self.api_key = api_key
        self.group_id = group_id
        self.base_url = f"https://api.minimaxi.com/v1"
    
    def upload_file(self, file_path: str, purpose: str) -> Dict[str, Any]:
        """上传文件"""
        url = f"{self.base_url}/files/upload"
        if self.group_id:
            url += f"?GroupId={self.group_id}"
        
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'purpose': purpose}
            response = requests.post(url, headers=headers, data=data, files=files)
        
        return response.json()
    
    def list_files(self, purpose: str = None) -> List[Dict[str, Any]]:
        """列出文件"""
        url = f"{self.base_url}/files/list"
        if self.group_id:
            url += f"?GroupId={self.group_id}"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        params = {}
        if purpose:
            params['purpose'] = purpose
        
        response = requests.get(url, headers=headers, params=params)
        return response.json().get('files', [])
    
    def get_file(self, file_id: str) -> Dict[str, Any]:
        """获取文件信息"""
        url = f"{self.base_url}/files/retrieve"
        if self.group_id:
            url += f"?GroupId={self.group_id}"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers, params={'file_id': file_id})
        return response.json()
    
    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """删除文件"""
        url = f"{self.base_url}/files/delete"
        if self.group_id:
            url += f"?GroupId={self.group_id}"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {'file_id': file_id}
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    
    def download_file(self, file_id: str, output_path: str = None) -> str:
        """下载文件"""
        file_info = self.get_file(file_id)
        filename = file_info['file']['filename']
        
        if not output_path:
            output_path = f"./downloads/{filename}"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        url = f"{self.base_url}/files/retrieve_content"
        if self.group_id:
            url += f"?GroupId={self.group_id}"
        
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response = requests.get(url, headers=headers, params={'file_id': file_id})
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return output_path
    
    def export_file_list(self, filename: str = None) -> str:
        """导出文件列表"""
        files = self.list_files()
        
        if not filename:
            filename = f"file_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(files, f, ensure_ascii=False, indent=2)
        
        return filename

# 使用示例
manager = MiniMaxFileManager("your_api_key", "your_group_id")
```

### 2. 知识库管理
```python
class KnowledgeBaseManager:
    def __init__(self, file_manager: MiniMaxFileManager):
        self.file_manager = file_manager
    
    def upload_document(self, file_path: str):
        """上传知识库文档"""
        return self.file_manager.upload_file(file_path, "retrieval")
    
    def list_documents(self):
        """列出所有知识库文档"""
        return self.file_manager.list_files("retrieval")
    
    def cleanup_documents(self, max_files: int = 100):
        """清理旧文档，保持数量限制"""
        documents = self.list_documents()
        
        if len(documents) > max_files:
            # 按创建时间排序，删除最旧的
            documents.sort(key=lambda x: x['created_at'])
            files_to_delete = documents[:len(documents) - max_files]
            
            for file in files_to_delete:
                self.file_manager.delete_file(file['file_id'])
                print(f"已删除旧文档: {file['filename']}")
    
    def search_documents(self, keyword: str):
        """搜索文档"""
        documents = self.list_documents()
        return [doc for doc in documents if keyword.lower() in doc['filename'].lower()]

# 使用示例
kb_manager = KnowledgeBaseManager(manager)
documents = kb_manager.list_documents()
print(f"知识库共有 {len(documents)} 个文档")
```

### 3. 语音样本管理
```python
class VoiceSampleManager:
    def __init__(self, file_manager: MiniMaxFileManager):
        self.file_manager = file_manager
    
    def upload_voice_sample(self, audio_path: str, name: str = None):
        """上传语音样本"""
        result = self.file_manager.upload_file(audio_path, "voice_clone")
        
        if name:
            # 可以维护一个映射表
            mapping = self._load_mapping()
            mapping[name] = result['file']['file_id']
            self._save_mapping(mapping)
        
        return result
    
    def get_voice_sample(self, name: str):
        """获取语音样本ID"""
        mapping = self._load_mapping()
        return mapping.get(name)
    
    def list_voice_samples(self):
        """列出所有语音样本"""
        return self.file_manager.list_files("voice_clone")
    
    def _load_mapping(self):
        """加载名称映射"""
        try:
            with open('voice_mapping.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_mapping(self, mapping):
        """保存名称映射"""
        with open('voice_mapping.json', 'w') as f:
            json.dump(mapping, f, indent=2)

# 使用示例
voice_manager = VoiceSampleManager(manager)
result = voice_manager.upload_voice_sample("my_voice.mp3", "my_voice")
```

## 错误处理

### 错误码说明
| 状态码 | 含义 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | - |
| 1000 | 未知错误 | 重试或联系支持 |
| 1001 | 超时 | 重试请求 |
| 1002 | RPM限流 | 降低请求频率 |
| 1004 | 鉴权失败 | 检查API密钥 |
| 1008 | 余额不足 | 充值账户 |
| 1013 | 服务内部错误 | 稍后重试 |
| 1026 | 输入内容错误 | 检查文件内容 |
| 1027 | 输出内容错误 | 检查文件格式 |
| 1039 | TPM限流 | 降低并发 |
| 2013 | 输入格式异常 | 检查参数格式 |

### 错误处理示例
```python
def safe_file_operation(operation_func, *args, **kwargs):
    """安全文件操作"""
    try:
        result = operation_func(*args, **kwargs)
        
        if isinstance(result, dict) and 'base_resp' in result:
            status_code = result['base_resp']['status_code']
            if status_code == 0:
                return {'success': True, 'data': result}
            else:
                return {
                    'success': False,
                    'error': result['base_resp']['status_msg'],
                    'code': status_code
                }
        
        return {'success': True, 'data': result}
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'code': -1
        }

# 使用示例
result = safe_file_operation(manager.upload_file, 'test.pdf', 'retrieval')
if result['success']:
    print("上传成功")
else:
    print(f"错误: {result['error']}")
```

## 最佳实践

### 1. 文件命名规范
```python
def generate_filename(original_name: str, purpose: str) -> str:
    """生成规范的文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(original_name)
    return f"{purpose}_{timestamp}_{name}{ext}"
```

### 2. 自动清理策略
```python
def auto_cleanup_strategy(file_manager: MiniMaxFileManager, 
                         max_age_days: int = 30,
                         max_size_gb: float = 10):
    """自动清理策略"""
    files = file_manager.list_files()
    
    # 按创建时间清理
    old_files = [f for f in files 
                if (datetime.now() - datetime.fromtimestamp(f['created_at'])).days > max_age_days]
    
    # 按总大小清理
    total_size = sum(f['bytes'] for f in files)
    if total_size > max_size_gb * 1024 * 1024 * 1024:
        # 删除最旧的文件直到满足大小限制
        files.sort(key=lambda x: x['created_at'])
        for file in files:
            file_manager.delete_file(file['file_id'])
            total_size -= file['bytes']
            if total_size <= max_size_gb * 1024 * 1024 * 1024:
                break
```

### 3. 监控和日志
```python
import logging

class FileMonitor:
    def __init__(self, file_manager: MiniMaxFileManager):
        self.file_manager = file_manager
        self.logger = logging.getLogger('file_monitor')
    
    def log_upload(self, file_path: str, purpose: str, result: dict):
        """记录上传日志"""
        if result['success']:
            self.logger.info(f"上传成功: {file_path} -> {result['data']['file']['file_id']}")
        else:
            self.logger.error(f"上传失败: {file_path} - {result['error']}")
    
    def monitor_usage(self):
        """监控使用情况"""
        files = self.file_manager.list_files()
        total_size = sum(f['bytes'] for f in files)
        
        self.logger.info(f"总文件数: {len(files)}")
        self.logger.info(f"总存储: {total_size / (1024*1024):.2f} MB")
        self.logger.info(f"使用率: {(total_size / (100*1024*1024*1024)) * 100:.1f}%")
```

## 集成应用示例

### 1. CLI文件管理工具
```python
import argparse

def file_cli():
    """文件管理CLI工具"""
    parser = argparse.ArgumentParser(description='MiniMax文件管理工具')
    subparsers = parser.add_subparsers(dest='command')
    
    # 上传命令
    upload_parser = subparsers.add_parser('upload')
    upload_parser.add_argument('file_path', help='文件路径')
    upload_parser.add_argument('--purpose', default='retrieval', help='文件用途')
    
    # 列出命令
    list_parser = subparsers.add_parser('list')
    list_parser.add_argument('--purpose', help='按用途筛选')
    
    # 删除命令
    delete_parser = subparsers.add_parser('delete')
    delete_parser.add_argument('file_id', help='文件ID')
    
    # 下载命令
    download_parser = subparsers.add_parser('download')
    download_parser.add_argument('file_id', help='文件ID')
    download_parser.add_argument('--output', help='输出路径')
    
    args = parser.parse_args()
    
    manager = MiniMaxFileManager("your_api_key")
    
    if args.command == 'upload':
        result = manager.upload_file(args.file_path, args.purpose)
        print(f"上传成功，文件ID: {result['file']['file_id']}")
    
    elif args.command == 'list':
        files = manager.list_files(args.purpose)
        for file in files:
            print(f"{file['file_id']}: {file['filename']} ({file['purpose']})")
    
    elif args.command == 'delete':
        result = manager.delete_file(args.file_id)
        print("删除成功" if result['base_resp']['status_code'] == 0 else "删除失败")
    
    elif args.command == 'download':
        path = manager.download_file(args.file_id, args.output)
        print(f"下载完成: {path}")

if __name__ == "__main__":
    file_cli()
```

### 2. Web应用集成
```python
from flask import Flask, request, jsonify

app = Flask(__name__)
manager = MiniMaxFileManager("your_api_key")

@app.route('/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    purpose = request.form.get('purpose', 'retrieval')
    
    # 保存临时文件
    temp_path = f"./temp/{file.filename}"
    file.save(temp_path)
    
    result = manager.upload_file(temp_path, purpose)
    os.remove(temp_path)
    
    return jsonify(result)

@app.route('/files', methods=['GET'])
def list_files():
    """文件列表接口"""
    purpose = request.args.get('purpose')
    files = manager.list_files(purpose)
    return jsonify({'files': files})

@app.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """文件下载接口"""
    try:
        path = manager.download_file(file_id)
        return send_file(path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True)
```

## 注意事项

### 使用限制
1. **容量监控**: 定期检查总容量使用情况
2. **文件格式**: 确保上传文件格式符合要求
3. **敏感内容**: 避免上传包含敏感信息的文件
4. **有效期**: 注意文件URL的9小时有效期
5. **并发限制**: 遵守RPM和TPM限制

### 最佳实践
1. **文件命名**: 使用有意义的文件名
2. **定期清理**: 建立自动清理机制
3. **备份策略**: 重要文件本地备份
4. **监控告警**: 设置容量使用告警
5. **权限控制**: 合理控制文件访问权限