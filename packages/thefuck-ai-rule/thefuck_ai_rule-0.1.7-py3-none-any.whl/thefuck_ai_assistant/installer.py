import os
import sys
import json
import platform
import shutil
import subprocess
from pathlib import Path
import getpass

def check_thefuck_installed():
    """检查是否已安装thefuck"""
    # 首先尝试使用importlib检查
    try:
        import thefuck
        return True
    except ImportError:
        # 作为备选，尝试使用命令行工具
        try:
            subprocess.run(["thefuck", "--version"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE,
                          check=False)
            return True
        except FileNotFoundError:
            return False

def get_thefuck_rules_dir():
    """获取thefuck规则目录路径"""
    if platform.system() == "Windows":
        username = getpass.getuser()
        rules_dir = Path(f"C:/Users/{username}/.config/thefuck/rules")
    else:
        # Linux/macOS
        rules_dir = Path.home() / ".config" / "thefuck" / "rules"
    
    # 确保目录存在
    rules_dir.mkdir(parents=True, exist_ok=True)
    return rules_dir

def prompt_api_key():
    """提示用户输入API密钥"""
    print("您需要提供AI API密钥才能使用此功能。")
    api_key = input("请输入您的API密钥: ").strip()
    return api_key

def prompt_api_url():
    """提示用户输入API URL"""
    default_url = "https://api.siliconflow.cn/v1/chat/completions"
    print(f"请输入API URL (默认: {default_url}): ")
    api_url = input().strip()
    if not api_url:
        return default_url
    return api_url

def prompt_api_model():
    """提示用户输入API模型名称"""
    default_model = "Qwen/QwQ-32B"
    print(f"请输入要使用的AI模型名称 (默认: {default_model}): ")
    model = input().strip()
    if not model:
        return default_model
    return model

def set_environment_variable(name, value, permanent=False):
    """设置环境变量"""
    os.environ[name] = value
    
    if permanent:
        if platform.system() == "Windows":
            # Windows系统下永久设置环境变量
            subprocess.run(
                ["setx", name, value],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            print(f"已永久设置环境变量 {name}")
        else:
            # Linux/macOS系统下永久设置环境变量
            shell = os.environ.get("SHELL", "/bin/bash")
            if "bash" in shell:
                config_file = Path.home() / ".bashrc"
            elif "zsh" in shell:
                config_file = Path.home() / ".zshrc"
            else:
                config_file = Path.home() / ".profile"
                
            # 追加到配置文件
            with open(config_file, "a") as f:
                f.write(f'\nexport {name}="{value}"\n')
            print(f"已将环境变量 {name} 添加到 {config_file}")

def copy_rule_file():
    """复制规则文件到thefuck规则目录"""
    # 获取当前包目录
    current_dir = Path(__file__).parent
    rule_file = current_dir / "rule.py"
    
    # 目标目录
    target_dir = get_thefuck_rules_dir()
    target_file = target_dir / "ai_rule.py"
    
    # 复制文件
    shutil.copy2(rule_file, target_file)
    print(f"已复制规则文件到 {target_file}")

def setup_environment():
    """设置必要的环境变量"""
    # 检查环境变量是否已设置
    needs_setup = (
        "THEFUCK_AI_API_KEY" not in os.environ or
        not os.environ["THEFUCK_AI_API_KEY"]
    )
    
    if needs_setup:
        print("设置AI助手所需的环境变量...")
        
        # 获取API密钥
        api_key = prompt_api_key()
        if not api_key:
            print("错误: 必须提供API密钥才能使用AI助手功能。")
            return False
        
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
        
        print("环境变量设置完成!")
    
    return True

def install():
    """执行安装过程"""
    print("欢迎安装 TheFuck AI Assistant!")
    
    # 检查thefuck是否已安装
    if not check_thefuck_installed():
        print("错误: 未检测到thefuck已安装。此插件需要thefuck才能正常工作。")
        print("请先安装thefuck: pip install thefuck")
        return False
    
    # 复制规则文件
    try:
        copy_rule_file()
    except Exception as e:
        print(f"复制规则文件失败: {str(e)}")
        return False
    
    # 设置环境变量
    if not setup_environment():
        return False
    
    print("安装成功! 现在你可以使用 TheFuck AI Assistant 来智能修复命令了。")
    print("只需像往常一样使用 'fuck' 命令即可。")
    return True

def main():
    """命令行入口点"""
    success = install()
    if not success:
        sys.exit(1)
    
if __name__ == "__main__":
    main()
