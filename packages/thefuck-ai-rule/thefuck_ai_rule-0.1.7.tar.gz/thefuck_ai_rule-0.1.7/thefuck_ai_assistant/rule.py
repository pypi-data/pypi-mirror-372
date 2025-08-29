import os
import sys
import json
import re
import platform
import requests
import importlib.util
from pathlib import Path

# 检查thefuck是否已安装
def is_thefuck_installed():
    return importlib.util.find_spec("thefuck") is not None

# 如果thefuck已安装，导入settings
if is_thefuck_installed():
    try:
        from thefuck.conf import settings
    except ImportError:
        print("警告: 无法导入thefuck设置。请确保thefuck已正确安装。")

# 配置
AI_API_URL = os.environ.get('THEFUCK_AI_API_URL', 'https://api.siliconflow.cn/v1/chat/completions')
AI_API_KEY = os.environ.get('THEFUCK_AI_API_KEY', '')
AI_MODEL = os.environ.get('THEFUCK_AI_MODEL', 'deepseek-ai/DeepSeek-V3')
REQUEST_TIMEOUT = 10  # 秒

# 可选配置
enabled_by_default = True  # 默认启用
priority = 1000  # 优先级高于大多数内置规则，让AI规则先处理
requires_output = True  # 需要命令输出来分析错误

# 环境变量设置状态追踪
_env_setup_attempted = False

def check_env_setup():
    """检查环境变量设置并提示用户设置（如需要）"""
    global _env_setup_attempted, AI_API_KEY, AI_API_URL, AI_MODEL
    
    # 如果已经尝试过设置，或已经设置了API密钥，则跳过
    if _env_setup_attempted or AI_API_KEY:
        return
    
    _env_setup_attempted = True
    
    print("\n未设置AI助手所需的环境变量。")
    print("请设置以下环境变量以启用AI辅助功能:")
    
    from thefuck_ai_assistant.installer import prompt_api_key, prompt_api_url, prompt_api_model, set_environment_variable
    
    try:
        # 获取API密钥
        api_key = prompt_api_key()
        if not api_key:
            print("错误: 未提供API密钥，AI助手功能将被禁用。")
            return
        
        # 获取API URL和模型
        api_url = prompt_api_url()
        api_model = prompt_api_model()
        
        # 询问是否永久保存
        print("是否将这些设置永久保存到系统环境变量中? (y/n): ")
        permanent = input().strip().lower() == 'y'
        
        # 设置环境变量
        set_environment_variable("THEFUCK_AI_API_KEY", api_key, permanent)
        set_environment_variable("THEFUCK_AI_API_URL", api_url, permanent)
        set_environment_variable("THEFUCK_AI_MODEL", api_model, permanent)
        
        # 更新全局变量
        AI_API_KEY = api_key
        AI_API_URL = api_url
        AI_MODEL = api_model
        
        print("环境变量设置完成!")
    except Exception as e:
        print(f"设置环境变量失败: {str(e)}")

def ask_ai_if_command_failed(command):
    """使用AI判断命令是否执行失败"""
    system_info = get_system_info()
    
    # 净化命令和输出，移除敏感信息
    sanitized_script = sanitize_command(command.script)
    sanitized_output = sanitize_output(command.output)
    
    # 准备发送给AI的消息，用于判断命令是否失败
    messages = [
        {
            "role": "system",
            "content": "你是一个命令行错误检测助手。你的任务是判断用户提供的命令执行是否失败。只需回答 'yes' 如果命令失败，或 'no' 如果命令成功执行。"
        },
        {
            "role": "user",
            "content": f"""
命令: {sanitized_script}
命令输出: {sanitized_output}
系统信息: {json.dumps(system_info)}

请判断上面的命令是否执行失败，只回答 'yes' 或 'no'。
"""
        }
    ]
    
    try:
        # 准备API请求
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {AI_API_KEY}'
        }
        
        payload = {
            'model': AI_MODEL,
            'messages': messages,
            'temperature': 0.1,  # 非常低的温度，让回答更确定
            'max_tokens': 10     # 限制回复长度，只需要yes/no
        }
        
        # 发送请求到AI API
        response = requests.post(
            AI_API_URL,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        
        # 解析响应
        if response.status_code == 200:
            response_data = response.json()
            ai_response = response_data['choices'][0]['message']['content'].strip().lower()
            
            # 判断AI的回答是否表示命令执行失败
            return 'yes' in ai_response
        else:
            print(f"AI API请求失败: 状态码 {response.status_code}")
            return fallback_command_failure_detection(command)
            
    except Exception as e:
        # AI判断失败，使用传统的关键词判断作为备选
        print(f"AI判断命令执行状态失败: {str(e)}，将使用备选方法")
        return fallback_command_failure_detection(command)


def fallback_command_failure_detection(command):
    """备选的命令失败检测方法，使用关键词匹配"""
    # 错误指示词列表
    error_indicators = [
        'error', 'exception', 'failed', 'not found', 'invalid', 'cannot',
        'permission denied', 'syntax error', 'command not found', 'no such file',
        'undefined', 'unrecognized', 'unexpected', 'unknown', 'missing',
        '错误', '异常', '失败', '未找到', '无效', '不能', '权限被拒绝', '语法错误'
    ]
    
    output_lower = command.output.lower()
    has_error = any(indicator in output_lower for indicator in error_indicators)
    
    # 如果输出中没有错误指示词且输出较短，可能是成功执行的命令
    if not has_error and len(command.output) < 200:
        return False
    
    return has_error


def match(command):
    """匹配条件很宽松，几乎尝试修复所有命令
    但有一些条件：
    1. 需要有API密钥
    2. 不处理空命令
    3. 不处理已成功的命令（由AI判断）
    """
    # 检查thefuck是否已安装
    if not is_thefuck_installed():
        print("错误: thefuck未安装。此规则需要thefuck才能正常工作。")
        return False
    
    # 检查是否配置了API密钥，如果没有则提示用户设置
    if not AI_API_KEY:
        check_env_setup()
        # 再次检查API密钥
        if not AI_API_KEY:
            print("未配置AI API密钥，跳过AI辅助修正")
            return False
    
    # 检查命令是否为空
    if not command.script or not command.script.strip():
        return False
    
    # 如果命令没有输出或输出很短（可能是成功执行的命令），不处理
    if not command.output or len(command.output) < 10:
        return False
    
    # 使用AI判断命令是否执行失败
    return ask_ai_if_command_failed(command)


def get_system_info():
    """获取系统信息作为上下文"""
    info = {
        'os': platform.system(),
        'os_version': platform.version(),
        'platform': platform.platform(),
        'shell': os.environ.get('SHELL', os.environ.get('COMSPEC', 'unknown')),
    }
    return info


def sanitize_command(command_text):
    """
    净化命令，移除可能包含的敏感信息
    - 移除明显的密码和令牌模式
    - 掩盖绝对路径中的用户名
    """
    # 替换常见的密码和令牌模式
    sanitized = re.sub(r'(password|passwd|pwd|token|secret|key|credential)s?\s*[=:]\s*["\']?[\w\-\.]+["\']?', 
                       r'\1=***REDACTED***', 
                       command_text, 
                       flags=re.IGNORECASE)
    
    # 替换可能的主目录绝对路径 (~/用户名/ 或 /home/用户名/ 或 C:\Users\用户名\)
    sanitized = re.sub(r'(/home/[\w\-]+|~/[\w\-]*|C:\\Users\\[\w\-]+)', 
                       r'/home/user', 
                       sanitized)
    
    return sanitized

def sanitize_output(output_text):
    """
    净化输出，移除可能包含的敏感信息
    - 限制输出长度
    - 移除IP地址、主机名、邮件地址等
    - 移除绝对路径中的用户名
    """
    # 限制输出长度，避免发送过多数据
    if len(output_text) > 500:
        output_text = output_text[:500] + "... [输出被截断]"
    
    # 替换IP地址
    sanitized = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', 
                       r'xxx.xxx.xxx.xxx', 
                       output_text)
    
    # 替换邮箱地址
    sanitized = re.sub(r'[\w\.-]+@[\w\.-]+', 
                       r'user@example.com', 
                       sanitized)
    
    # 替换可能的主目录绝对路径
    sanitized = re.sub(r'(/home/[\w\-]+|~/[\w\-]*|C:\\Users\\[\w\-]+)', 
                       r'/home/user', 
                       sanitized)
    
    # 替换主机名
    sanitized = re.sub(r'(on|at|@)\s+[\w\-\.]+', 
                       r'\1 hostname', 
                       sanitized)
    
    return sanitized

def query_ai_for_correction(command):
    """向AI API发送请求，获取修正建议"""
    system_info = get_system_info()
    
    # 净化命令和输出，移除敏感信息
    sanitized_script = sanitize_command(command.script)
    sanitized_output = sanitize_output(command.output)
    
    # 准备发送给AI的消息
    messages = [
        {
            "role": "system",
            "content": "你是一个命令行修复助手。用户会提供一个错误的命令及其输出。你的任务是分析错误并只提供修正后的命令，不要添加任何解释。只返回一个修正后的命令字符串。"
        },
        {
            "role": "user",
            "content": f"""
错误命令: {sanitized_script}
命令输出: {sanitized_output}
系统信息: {json.dumps(system_info)}

请分析上面的错误命令和输出，只返回一个修正后的命令字符串，不要添加任何解释或其他文本。
"""
        }
    ]
    
    try:
        # 准备API请求
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {AI_API_KEY}'
        }
        
        payload = {
            'model': AI_MODEL,
            'messages': messages,
            'temperature': 0.3,  # 较低的温度，让回答更确定
            'max_tokens': 100     # 限制回复长度
        }
        
        # 发送请求到AI API
        response = requests.post(
            AI_API_URL,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        
        # 解析响应
        if response.status_code == 200:
            response_data = response.json()
            corrected_command = response_data['choices'][0]['message']['content'].strip()
            
            # 确保我们只返回命令，不包含解释
            if '\n' in corrected_command:
                # 如果有多行，取第一行作为命令
                corrected_command = corrected_command.split('\n')[0].strip()
            
            # 如果AI返回了引号包裹的命令，去掉引号
            if (corrected_command.startswith('"') and corrected_command.endswith('"')) or \
               (corrected_command.startswith("'") and corrected_command.endswith("'")):
                corrected_command = corrected_command[1:-1]
            
            # 如果修正的命令与原命令相同，说明AI没有提供有用的修正
            if corrected_command == command.script:
                return None
            
            return corrected_command
        else:
            print(f"AI API请求失败: 状态码 {response.status_code}")
            return None
            
    except Exception as e:
        # 记录错误但不中断程序流程
        print(f"AI修正请求失败: {str(e)}")
        return None


def get_new_command(command):
    """获取修正后的命令"""
    corrected_command = query_ai_for_correction(command)
    
    # 如果AI未能提供有用的修正，返回None让其他规则处理
    if not corrected_command:
        return None
    
    # 在标准错误流上打印消息，不影响命令本身
    # 使用简单的输出格式，避免特殊字符
    print("AI rule: 找到修复命令", file=sys.stderr)
    
    # 检测当前操作系统
    system = platform.system()
    
    # 为不同的shell环境处理命令
    if system == "Windows":
        # Windows (PowerShell) 环境
        # 在PowerShell中，命令被传递给Invoke-Expression (iex)
        return corrected_command
    else:
        # Linux/macOS 环境 (bash/zsh)
        # 在这些环境中，命令通过eval执行
        # 需要确保命令中的特殊字符不会被错误解释
        
        # 检查是否包含可能导致解析问题的特殊字符
        special_chars = ['>', '<', '|', ';', '&', '(', ')', '{', '}', '[', ']', '$', '`', '"', "'", '\\']
        has_special_chars = any(char in corrected_command for char in special_chars)
        
        if has_special_chars:
            # 对于包含特殊字符的命令，我们使用单引号来保护整个命令
            # 但需要先处理命令中已有的单引号
            # 在bash/zsh中，单引号内的内容不会被解释，除了单引号本身
            escaped_command = corrected_command.replace("'", "'\\''")
            return f"'{escaped_command}'"
        else:
            # 如果没有特殊字符，直接返回命令
            return corrected_command
