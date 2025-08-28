#!/usr/bin/env python3
"""
测试MCP服务器功能的脚本
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from obsidianreadermcp.server import ObsidianMCPServer
from obsidianreadermcp.config import get_config

async def test_server_initialization():
    """测试服务器初始化"""
    print("🧪 测试服务器初始化...")
    
    try:
        # 设置测试环境变量
        os.environ["OBSIDIAN_HOST"] = "192.168.0.104"
        os.environ["OBSIDIAN_PORT"] = "27123"
        os.environ["OBSIDIAN_API_KEY"] = "1fb6e1d89dacb6eb84a6aa5e1d238faa67b8ddbefeac90b895aeab32e0657b5f"
        
        # 创建服务器实例
        server = ObsidianMCPServer()
        print("✅ 服务器实例创建成功")
        
        # 测试配置加载
        obsidian_config, mcp_config = get_config()
        print(f"✅ 配置加载成功:")
        print(f"   - Obsidian Host: {obsidian_config.host}")
        print(f"   - Obsidian Port: {obsidian_config.port}")
        print(f"   - MCP Server Name: {mcp_config.server_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 服务器初始化失败: {e}")
        return False

def test_cli_entry_point():
    """测试CLI入口点"""
    print("\n🧪 测试CLI入口点...")
    
    try:
        from obsidianreadermcp.server import cli_main
        print("✅ CLI入口点导入成功")
        return True
    except Exception as e:
        print(f"❌ CLI入口点测试失败: {e}")
        return False

async def test_read_all_note_titles():
    """测试读取所有笔记标题"""
    print("\n📚 测试读取所有笔记标题...")

    try:
        from obsidianreadermcp.client import ObsidianClient
        from obsidianreadermcp.config import get_config

        # 获取配置
        obsidian_config, _ = get_config()

        # 创建客户端并连接
        async with ObsidianClient(obsidian_config) as client:
            print("✅ 已连接到Obsidian API")

            # 获取所有笔记列表
            notes = await client.list_notes()
            print(f"✅ 找到 {len(notes)} 个笔记")

            # 读取每个笔记的标题
            note_titles = []
            for i, note_path in enumerate(notes[:10]):  # 限制前10个笔记以避免输出过多
                try:
                    note = await client.get_note(note_path)
                    # 提取标题（通常是第一行的# 标题）
                    lines = note.content.split('\n')
                    title = note_path  # 默认使用文件名

                    for line in lines:
                        line = line.strip()
                        if line.startswith('# '):
                            title = line[2:].strip()
                            break
                        elif line and not line.startswith('---'):  # 跳过frontmatter
                            title = line[:50] + "..." if len(line) > 50 else line
                            break

                    note_titles.append({
                        "path": note_path,
                        "title": title,
                        "size": len(note.content)
                    })

                except Exception as e:
                    print(f"⚠️ 无法读取笔记 {note_path}: {e}")

            # 显示结果
            print(f"\n📋 笔记标题列表（前{len(note_titles)}个）:")
            for i, note_info in enumerate(note_titles, 1):
                print(f"  {i:2d}. {note_info['title']}")
                print(f"      路径: {note_info['path']}")
                print(f"      大小: {note_info['size']} 字符")
                print()

            return True

    except Exception as e:
        print(f"❌ 读取笔记标题失败: {e}")
        return False

def test_claude_desktop_config():
    """生成Claude Desktop配置"""
    print("\n📋 生成Claude Desktop配置...")

    config = {
        "mcpServers": {
            "obsidian": {
                "command": "uvx",
                "args": ["obsidianreadermcp"],
                "env": {
                    "OBSIDIAN_HOST": "192.168.0.104",
                    "OBSIDIAN_PORT": "27123",
                    "OBSIDIAN_API_KEY": "1fb6e1d89dacb6eb84a6aa5e1d238faa67b8ddbefeac90b895aeab32e0657b5f"
                }
            }
        }
    }

    print("✅ Claude Desktop配置:")
    print(json.dumps(config, indent=2, ensure_ascii=False))
    return True

async def main():
    """主测试函数"""
    print("🚀 开始测试ObsidianReaderMCP...")

    results = []

    # 测试服务器初始化
    results.append(await test_server_initialization())

    # 测试CLI入口点
    results.append(test_cli_entry_point())

    # 测试读取所有笔记标题
    results.append(await test_read_all_note_titles())

    # 生成配置
    results.append(test_claude_desktop_config())

    # 总结结果
    print(f"\n📊 测试结果:")
    print(f"   - 通过: {sum(results)}/{len(results)}")
    print(f"   - 失败: {len(results) - sum(results)}/{len(results)}")

    if all(results):
        print("\n🎉 所有测试通过！MCP服务器已准备就绪。")
        print("\n📝 使用说明:")
        print("1. 确保Obsidian正在运行，并启用了obsidian-local-rest-api插件")
        print("2. 将上面的配置添加到Claude Desktop配置文件中")
        print("3. 重启Claude Desktop")
        print("4. 现在可以在Claude中使用Obsidian功能了！")
    else:
        print("\n❌ 部分测试失败，请检查配置。")

    return all(results)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
