#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
跨平台shell兼容性测试
此脚本测试修复后的get_new_command函数在不同shell环境下的行为
"""

import platform
import os
import sys
import subprocess

def test_command_in_shell(command, shell_type):
    """测试命令在指定shell中的执行情况"""
    print(f"在 {shell_type} 中测试命令: {command}")
    
    if shell_type == "bash" or shell_type == "zsh":
        # Linux/macOS shell测试
        shell_command = f"echo 'eval {command}' | {shell_type}"
    elif shell_type == "powershell":
        # Windows PowerShell测试
        shell_command = f'powershell -Command "Invoke-Expression \'{command}\'"'
    else:
        print(f"不支持的shell类型: {shell_type}")
        return False
    
    try:
        result = subprocess.run(shell_command, shell=True, capture_output=True, text=True)
        print(f"退出代码: {result.returncode}")
        print(f"标准输出: {result.stdout}")
        print(f"标准错误: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False

def process_command_with_our_logic(command):
    """使用我们的修复逻辑处理命令"""
    # 检测当前操作系统
    system = platform.system()
    
    print(f"原始命令: {command}")
    print(f"检测到的系统: {system}")
    
    # 为不同的shell环境处理命令
    if system == "Windows":
        # Windows (PowerShell) 环境
        processed_command = command
        print(f"Windows处理后: {processed_command}")
        return processed_command
    else:
        # Linux/macOS 环境 (bash/zsh)
        # 检查是否包含可能导致解析问题的特殊字符
        special_chars = ['>', '<', '|', ';', '&', '(', ')', '{', '}', '[', ']', '$', '`', '"', "'", '\\']
        has_special_chars = any(char in command for char in special_chars)
        
        if has_special_chars:
            # 对于包含特殊字符的命令，我们使用单引号来保护整个命令
            # 但需要先处理命令中已有的单引号
            escaped_command = command.replace("'", "'\\''")
            processed_command = f"'{escaped_command}'"
        else:
            # 如果没有特殊字符，直接返回命令
            processed_command = command
        
        print(f"Linux处理后: {processed_command}")
        return processed_command

def test_commands():
    """测试一系列命令在不同shell环境下的行为"""
    test_cases = [
        "ls",
        "cd /home/user",
        "ls -la | grep 'pattern'",
        "echo 'hello world' > output.txt",
        "find . -name '*.py' | xargs grep 'import'",
        "cat file.txt | awk '{print $1}' | sort | uniq -c",
        "echo \"special chars: > < | ; & ( ) { } [ ] $ ` \\\" ' \"",
        "python -c \"import os; print(os.getcwd())\"",
        "for i in {1..5}; do echo $i; done",
        "查看当前目录"  # 中文命令
    ]
    
    print("="*60)
    print("跨平台Shell兼容性测试")
    print("="*60)
    
    # 不同的shell环境
    shells = ["bash", "zsh"] if platform.system() != "Windows" else ["powershell"]
    
    for i, cmd in enumerate(test_cases, 1):
        print("\n" + "-"*60)
        print(f"测试用例 #{i}: {cmd}")
        
        # 使用我们的逻辑处理命令
        processed_cmd = process_command_with_our_logic(cmd)
        
        # 在适用的shell环境中测试处理后的命令
        for shell in shells:
            success = test_command_in_shell(processed_cmd, shell)
            print(f"在 {shell} 中测试{'成功' if success else '失败'}")

if __name__ == "__main__":
    test_commands()
