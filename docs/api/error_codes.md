# MiniMax AI 错误码全表

## 错误码速查表

| 错误码 | 含义 | 解决方法 |
|--------|------|----------|
| **1000** | 未知错误/系统默认错误 | 请稍后再试 |
| **1001** | 请求超时 | 请稍后再试 |
| **1002** | 请求频率超限 | 请稍后再试 |
| **1004** | 未授权/Token不匹配/Cookie缺失 | 请检查API Key |
| **1008** | 余额不足 | 请检查您的账户余额 |
| **1024** | 内部错误 | 请稍后再试 |
| **1026** | 输入内容涉敏 | 请调整输入内容 |
| **1027** | 输出内容涉敏 | 请调整输入内容 |
| **1033** | 系统错误/下游服务错误 | 请稍后再试 |
| **1039** | Token限制 | 请调整max_tokens |
| **1041** | 连接数限制 | 请联系我们 |
| **1042** | 不可见字符比例超限/非法字符超过10% | 请检查输入内容，是否包含不可见字符或非法字符 |
| **1043** | ASR相似度检查失败 | 请检查file_id与text_validation匹配度 |
| **1044** | 克隆提示词相似度检查失败 | 请检查克隆提示音频和提示词 |
| **2013** | 参数错误 | 请检查请求参数 |
| **20132** | 语音克隆样本或voice_id参数错误 | 请检查Voice Cloning 接口下的 file_id 和 T2A v2，T2A Large v2 接口下的 voice_id 参数 |
| **2037** | 语音时长不符合要求(太长或太短) | 请检查voice_clone file_id文件时长，最少应不低于10秒，最长应不超过5分钟 |
| **2038** | 用户语音克隆功能被禁用 | 使用语音克隆功能需要完成账户身份认证，请根据您的使用需求在账户系管理》账户信息中进行个人或企业认证 |
| **2039** | 语音克隆voice_id重复 | 请修改voice_id，确保未和已有voice_id重复 |
| **2042** | 无权访问该voice_id | 请确认是否为该voice_id创建者 |
| **2045** | 请求频率增长超限 | 请避免请求骤增骤减情况 |
| **2048** | 语音克隆提示音频太长 | 请调整prompt_audio音频文件时长（＜8s） |
| **2049** | 无效的API Key | 请检查API Key |

## 错误处理实用工具

### 错误码映射器
```python
ERROR_CODES = {
    1000: {
        "message": "未知错误/系统默认错误",
        "solution": "请稍后再试",
        "retry": True,
        "log_level": "ERROR"
    },
    1001: {
        "message": "请求超时",
        "solution": "请稍后再试",
        "retry": True,
        "log_level": "WARNING"
    },
    1002: {
        "message": "请求频率超限",
        "solution": "请稍后再试",
        "retry": True,
        "backoff": 2.0,
        "log_level": "WARNING"
    },
    1004: {
        "message": "未授权/Token不匹配/Cookie缺失",
        "solution": "请检查API Key",
        "retry": False,
        "log_level": "ERROR"
    },
    1008: {
        "message": "余额不足",
        "solution": "请检查您的账户余额",
        "retry": False,
        "log_level": "ERROR"
    },
    1026: {
        "message": "输入内容涉敏",
        "solution": "请调整输入内容",
        "retry": False,
        "log_level": "WARNING"
    },
    1027: {
        "message": "输出内容涉敏",
        "solution": "请调整输入内容",
        "retry": False,
        "log_level": "WARNING"
    },
    2013: {
        "message": "参数错误",
        "solution": "请检查请求参数",
        "retry": False,
        "log_level": "ERROR"
    },
    20132: {
        "message": "语音克隆样本或voice_id参数错误",
        "solution": "请检查Voice Cloning接口下的file_id和T2A v2，T2A Large v2接口下的voice_id参数",
        "retry": False,
        "log_level": "ERROR"
    },
    2037: {
        "message": "语音时长不符合要求",
        "solution": "请检查voice_clone file_id文件时长，最少应不低于10秒，最长应不超过5分钟",
        "retry": False,
        "log_level": "ERROR"
    },
    2038: {
        "message": "用户语音克隆功能被禁用",
        "solution": "使用语音克隆功能需要完成账户身份认证，请根据您的使用需求在账户系管理》账户信息中进行个人或企业认证",
        "retry": False,
        "log_level": "ERROR"
    },
    2039: {
        "message": "语音克隆voice_id重复",
        "solution": "请修改voice_id，确保未和已有voice_id重复",
        "retry": False,
        "log_level": "ERROR"
    },
    2042: {
        "message": "无权访问该voice_id",
        "solution": "请确认是否为该voice_id创建者",
        "retry": False,
        "log_level": "ERROR"
    },
    2049: {
        "message": "无效的API Key",
        "solution": "请检查API Key",
        "retry": False,
        "log_level": "ERROR"
    }
}
```

### 智能错误处理器
```python
import time
import random
from typing import Dict, Any, Optional

class MiniMaxErrorHandler:
    def __init__(self):
        self.retry_config = {
            1000: {"max_retries": 3, "backoff": 1.5},
            1001: {"max_retries": 3, "backoff": 2.0},
            1002: {"max_retries": 5, "backoff": 2.0},
            1039: {"max_retries": 2, "backoff": 1.0}
        }
    
    def handle_error(self, error_code: int, error_msg: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理错误并返回处理建议"""
        
        error_info = ERROR_CODES.get(error_code, {
            "message": f"未知错误码: {error_code}",
            "solution": "请联系技术支持",
            "retry": False,
            "log_level": "ERROR"
        })
        
        response = {
            "error_code": error_code,
            "message": error_info["message"],
            "solution": error_info["solution"],
            "retry": error_info.get("retry", False),
            "retry_config": self.retry_config.get(error_code),
            "context": context or {}
        }
        
        # 特殊错误处理逻辑
        if error_code == 1008:
            response["action"] = "请充值账户余额"
        elif error_code == 1026:
            response["suggestion"] = "尝试调整输入内容，避免敏感词汇"
        elif error_code == 2037:
            response["requirements"] = {
                "min_duration": "10秒",
                "max_duration": "5分钟"
            }
        
        return response
    
    def should_retry(self, error_code: int) -> bool:
        """判断是否应该重试"""
        return ERROR_CODES.get(error_code, {}).get("retry", False)
    
    def get_retry_delay(self, error_code: int, attempt: int) -> float:
        """计算重试延迟"""
        config = self.retry_config.get(error_code, {"backoff": 2.0})
        return config["backoff"] ** attempt + random.uniform(0.1, 0.5)
    
    def validate_parameters(self, params: Dict[str, Any], api_type: str) -> Optional[Dict[str, str]]:
        """参数预验证"""
        
        validation_rules = {
            "voice_clone": {
                "required": ["audio_duration"],
                "constraints": {
                    "audio_duration": {"min": 10, "max": 300, "unit": "seconds"}
                }
            },
            "text_generation": {
                "required": ["prompt"],
                "constraints": {
                    "prompt": {"max_length": 2000}
                }
            }
        }
        
        rules = validation_rules.get(api_type)
        if not rules:
            return None
        
        errors = {}
        for field, rule in rules["constraints"].items():
            if field in params:
                value = params[field]
                if "min" in rule and value < rule["min"]:
                    errors[field] = f"{field}不能小于{rule['min']}{rule.get('unit', '')}"
                if "max" in rule and value > rule["max"]:
                    errors[field] = f"{field}不能大于{rule['max']}{rule.get('unit', '')}"
                if "max_length" in rule and len(str(value)) > rule["max_length"]:
                    errors[field] = f"{field}长度不能超过{rule['max_length']}"
        
        return errors if errors else None

# 使用示例
error_handler = MiniMaxErrorHandler()
```

### API调用包装器
```python
import functools
import logging

class MiniMaxAPIWrapper:
    def __init__(self, api_key: str, max_retries: int = 3):
        self.api_key = api_key
        self.max_retries = max_retries
        self.error_handler = MiniMaxErrorHandler()
        self.logger = logging.getLogger(__name__)
    
    def safe_api_call(self, func, *args, **kwargs):
        """安全的API调用包装器"""
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                
                # 检查返回结果中的错误
                if isinstance(result, dict) and 'base_resp' in result:
                    error_code = result['base_resp']['status_code']
                    if error_code != 0:
                        error_msg = result['base_resp']['status_msg']
                        
                        # 处理错误
                        error_info = self.error_handler.handle_error(
                            error_code, error_msg, {
                                "function": func.__name__,
                                "attempt": attempt,
                                "args": str(args),
                                "kwargs": str(kwargs)
                            }
                        )
                        
                        self.logger.error(f"API错误: {error_info}")
                        
                        # 检查是否应该重试
                        if not error_info['retry'] or attempt == self.max_retries:
                            return error_info
                        
                        # 计算重试延迟
                        delay = self.error_handler.get_retry_delay(error_code, attempt)
                        time.sleep(delay)
                        continue
                
                return {"success": True, "data": result}
                
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"API调用异常: {e}")
                
                if attempt == self.max_retries:
                    return {
                        "success": False,
                        "error": f"API调用失败: {last_error}",
                        "retry": False
                    }
                
                time.sleep(2 ** attempt)
    
    def retry_with_backoff(self, func, *args, **kwargs):
        """带指数退避的重试机制"""
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                
                # 检查是否需要重试
                if isinstance(result, dict) and 'base_resp' in result:
                    error_code = result['base_resp']['status_code']
                    
                    if error_code == 0:
                        return {"success": True, "data": result}
                    
                    if not self.error_handler.should_retry(error_code):
                        return self.error_handler.handle_error(
                            error_code, 
                            result['base_resp']['status_msg']
                        )
                    
                    delay = self.error_handler.get_retry_delay(error_code, attempt)
                    self.logger.warning(f"重试 {attempt + 1}: {error_code}, 等待 {delay:.1f}秒")
                    time.sleep(delay)
                    continue
                
                return {"success": True, "data": result}
                
            except Exception as e:
                if attempt == self.max_retries:
                    return {"success": False, "error": str(e)}
                
                delay = 2 ** attempt + random.uniform(0.1, 0.5)
                self.logger.warning(f"重试 {attempt + 1}: 异常 {e}, 等待 {delay:.1f}秒")
                time.sleep(delay)

# 使用示例
wrapper = MiniMaxAPIWrapper("your_api_key")
```

### 错误监控和告警
```python
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

class ErrorMonitor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.error_counts = {}
        self.error_handler = MiniMaxErrorHandler()
    
    def log_error(self, error_code: int, context: Dict[str, Any]):
        """记录错误并触发告警"""
        
        # 更新错误计数
        self.error_counts[error_code] = self.error_counts.get(error_code, 0) + 1
        
        # 高频率错误告警
        if self.error_counts[error_code] > 10:
            self.send_alert(error_code, context)
        
        # 记录到日志文件
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - 错误码: {error_code}, 上下文: {json.dumps(context, ensure_ascii=False)}\n")
    
    def send_alert(self, error_code: int, context: Dict[str, Any]):
        """发送告警通知"""
        error_info = self.error_handler.handle_error(error_code, "", context)
        
        # 这里可以集成邮件、短信、钉钉等通知
        alert_message = f"""
        MiniMax API 高频率错误告警
        
        错误码: {error_code}
        含义: {error_info['message']}
        建议: {error_info['solution']}
        
        上下文: {json.dumps(context, ensure_ascii=False, indent=2)}
        """
        
        print(f"告警: {alert_message}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误统计摘要"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_breakdown": self.error_counts,
            "top_errors": sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }

# 使用示例
monitor = ErrorMonitor("your_api_key")
```

### CLI错误检查工具
```python
import argparse
import json

def error_cli():
    """错误码查询CLI工具"""
    parser = argparse.ArgumentParser(description='MiniMax错误码查询工具')
    
    parser.add_argument('error_code', type=int, help='错误码')
    parser.add_argument('--context', help='错误上下文信息')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    handler = MiniMaxErrorHandler()
    error_info = handler.handle_error(args.error_code, args.context or "")
    
    print(f"错误码: {error_info['error_code']}")
    print(f"含义: {error_info['message']}")
    print(f"解决方法: {error_info['solution']}")
    
    if args.verbose:
        print(f"\n详细信息:")
        print(json.dumps(error_info, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    error_cli()
```

## 错误处理最佳实践

### 1. 统一错误处理接口
```python
def handle_api_response(response, context=None):
    """统一API响应处理"""
    
    if not isinstance(response, dict):
        return {"success": True, "data": response}
    
    # 检查标准错误格式
    if 'base_resp' in response:
        error_code = response['base_resp']['status_code']
        error_msg = response['base_resp']['status_msg']
        
        if error_code == 0:
            return {"success": True, "data": response}
        
        error_handler = MiniMaxErrorHandler()
        return error_handler.handle_error(error_code, error_msg, context)
    
    return {"success": True, "data": response}
```

### 2. 重试装饰器
```python
def retry_on_error(max_retries=3, backoff_factor=2.0):
    """重试装饰器"""
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            handler = MiniMaxErrorHandler()
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    error_check = handle_api_response(result)
                    
                    if error_check['success']:
                        return error_check['data']
                    
                    if not error_check.get('retry', False):
                        return error_check
                    
                    if attempt < max_retries:
                        delay = backoff_factor ** attempt + random.uniform(0.1, 0.5)
                        time.sleep(delay)
                        
                except Exception as e:
                    if attempt == max_retries:
                        raise e
                    time.sleep(backoff_factor ** attempt)
            
            return {"error": f"重试{max_retries}次后仍然失败"}
        
        return wrapper
    return decorator

# 使用示例
@retry_on_error(max_retries=3)
def safe_api_call(api_function, *args, **kwargs):
    return api_function(*args, **kwargs)
```