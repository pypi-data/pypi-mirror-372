# 将源文件复制到包中
import shutil
import os
from pathlib import Path

def copy_ai_assistant():
    # 源文件路径
    src_file = Path(__file__).parent.parent / "ai_assistant.py"
    # 目标文件路径
    dest_file = Path(__file__).parent / "ai_assistant.py"
    
    # 复制文件
    if src_file.exists():
        shutil.copy2(src_file, dest_file)
        print(f"已将 {src_file} 复制到 {dest_file}")
    else:
        print(f"错误: 源文件 {src_file} 不存在")

if __name__ == "__main__":
    copy_ai_assistant()
