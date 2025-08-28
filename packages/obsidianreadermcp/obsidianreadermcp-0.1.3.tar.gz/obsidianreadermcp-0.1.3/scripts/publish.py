#!/usr/bin/env python3
"""
发布脚本 - 用于构建和发布包到PyPI
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, check=True):
    """运行命令并打印输出"""
    print(f"运行: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode == 0

def main():
    """主发布流程"""
    # 确保在项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🚀 开始发布流程...")
    
    # 1. 清理旧的构建文件
    print("\n📦 清理旧的构建文件...")
    run_command("rm -rf dist/ build/ *.egg-info/", check=False)
    
    # 2. 运行测试
    print("\n🧪 运行测试...")
    if not run_command("uv run pytest"):
        print("❌ 测试失败，停止发布")
        sys.exit(1)
    
    # 3. 代码格式检查
    print("\n🔍 检查代码格式...")
    if not run_command("uv run black --check src/"):
        print("❌ 代码格式检查失败，请运行 'uv run black src/' 修复")
        sys.exit(1)
    
    # 4. 类型检查
    print("\n🔍 类型检查...")
    if not run_command("uv run mypy src/obsidianreadermcp/", check=False):
        print("⚠️ 类型检查有警告，但继续发布")
    
    # 5. 构建包
    print("\n🔨 构建包...")
    if not run_command("uv build"):
        print("❌ 构建失败")
        sys.exit(1)
    
    # 6. 检查包
    print("\n🔍 检查包...")
    if not run_command("uv run twine check dist/*"):
        print("❌ 包检查失败")
        sys.exit(1)
    
    # 7. 询问是否发布到PyPI
    response = input("\n📤 是否发布到PyPI? (y/N): ")
    if response.lower() == 'y':
        print("\n📤 发布到PyPI...")
        if not run_command("uv run twine upload dist/*"):
            print("❌ 发布失败")
            sys.exit(1)
        print("✅ 发布成功!")
    else:
        print("📦 包已构建但未发布")
        print("要手动发布，请运行: uv run twine upload dist/*")

if __name__ == "__main__":
    main()
