#!/usr/bin/env python3
"""
MCP功能演示脚本 - 展示如何使用ObsidianReaderMCP读取笔记标题
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from obsidianreadermcp.client import ObsidianClient
from obsidianreadermcp.config import get_config
from obsidianreadermcp.models import NoteMetadata

async def demo_create_sample_notes():
    """创建一些示例笔记用于演示"""
    print("📝 创建示例笔记...")
    
    try:
        obsidian_config, _ = get_config()
        
        async with ObsidianClient(obsidian_config) as client:
            # 创建示例笔记
            sample_notes = [
                {
                    "path": "demo/欢迎使用ObsidianReaderMCP.md",
                    "content": """# 欢迎使用ObsidianReaderMCP

这是一个演示笔记，展示ObsidianReaderMCP的功能。

## 功能特性

- 创建、读取、更新、删除笔记
- 搜索笔记内容
- 管理标签
- 批量操作
- 模板系统

## 使用方法

通过MCP协议，您可以在Claude中直接管理Obsidian笔记。

#demo #mcp #obsidian""",
                    "tags": ["demo", "mcp", "obsidian"]
                },
                {
                    "path": "demo/项目管理.md", 
                    "content": """# 项目管理

## 当前项目

### ObsidianReaderMCP
- 状态：已完成
- 版本：v0.1.1
- 功能：MCP服务器，用于管理Obsidian笔记

## 待办事项

- [ ] 完善文档
- [ ] 添加更多示例
- [x] 发布到PyPI

#项目 #管理 #待办""",
                    "tags": ["项目", "管理", "待办"]
                },
                {
                    "path": "demo/学习笔记.md",
                    "content": """# 学习笔记

## Python异步编程

### asyncio基础
- `async def` 定义异步函数
- `await` 等待异步操作
- `asyncio.run()` 运行异步程序

### MCP协议
Model Context Protocol (MCP) 是一个用于AI助手集成的协议。

## 知识管理

使用Obsidian进行知识管理的优势：
1. 双向链接
2. 图谱视图
3. 插件生态
4. Markdown格式

#学习 #python #mcp #知识管理""",
                    "tags": ["学习", "python", "mcp", "知识管理"]
                }
            ]
            
            created_count = 0
            for note_data in sample_notes:
                try:
                    metadata = NoteMetadata(tags=note_data["tags"])
                    await client.create_note(
                        path=note_data["path"],
                        content=note_data["content"],
                        metadata=metadata
                    )
                    created_count += 1
                    print(f"✅ 创建笔记: {note_data['path']}")
                except Exception as e:
                    print(f"⚠️ 创建笔记失败 {note_data['path']}: {e}")
            
            print(f"✅ 成功创建 {created_count} 个示例笔记")
            return True
            
    except Exception as e:
        print(f"❌ 创建示例笔记失败: {e}")
        return False

async def demo_read_all_note_titles():
    """演示读取所有笔记标题"""
    print("\n📚 读取所有笔记标题...")
    
    try:
        obsidian_config, _ = get_config()
        
        async with ObsidianClient(obsidian_config) as client:
            # 获取知识库信息
            vault_info = await client.get_vault_info()
            print(f"📁 知识库: {vault_info.name}")
            print(f"📊 笔记数量: {vault_info.note_count}")
            
            # 获取所有笔记列表
            notes = await client.list_notes()
            print(f"📋 找到 {len(notes)} 个笔记文件")
            
            if not notes:
                print("💡 知识库中没有笔记，建议先创建一些笔记")
                return True
            
            # 读取每个笔记的标题和基本信息
            note_titles = []
            for note_path in notes:
                try:
                    note = await client.get_note(note_path)
                    
                    # 提取标题
                    lines = note.content.split('\n')
                    title = note_path  # 默认使用文件名
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith('# '):
                            title = line[2:].strip()
                            break
                        elif line and not line.startswith('---'):
                            # 如果没有标题，使用第一行内容
                            title = line[:50] + "..." if len(line) > 50 else line
                            break
                    
                    note_titles.append({
                        "path": note_path,
                        "title": title,
                        "size": len(note.content),
                        "tags": note.metadata.tags if note.metadata else []
                    })
                    
                except Exception as e:
                    print(f"⚠️ 无法读取笔记 {note_path}: {e}")
            
            # 显示结果
            print(f"\n📋 笔记标题列表:")
            print("=" * 60)
            for i, note_info in enumerate(note_titles, 1):
                print(f"{i:2d}. 📄 {note_info['title']}")
                print(f"    📁 路径: {note_info['path']}")
                print(f"    📏 大小: {note_info['size']} 字符")
                if note_info['tags']:
                    print(f"    🏷️  标签: {', '.join(note_info['tags'])}")
                print()
            
            return True
            
    except Exception as e:
        print(f"❌ 读取笔记标题失败: {e}")
        return False

async def demo_search_notes():
    """演示搜索笔记功能"""
    print("\n🔍 搜索笔记演示...")
    
    try:
        obsidian_config, _ = get_config()
        
        async with ObsidianClient(obsidian_config) as client:
            # 搜索包含"MCP"的笔记
            search_results = await client.search_notes("MCP", limit=10)
            
            print(f"🔍 搜索 'MCP' 找到 {len(search_results)} 个结果:")
            for i, result in enumerate(search_results, 1):
                print(f"{i}. 📄 {result.note.path}")
                if result.matches:
                    print(f"   📝 匹配内容: {result.matches[0][:100]}...")
                else:
                    print(f"   📝 内容: {result.note.content[:100]}...")
                print()
            
            return True
            
    except Exception as e:
        print(f"❌ 搜索笔记失败: {e}")
        return False

async def main():
    """主演示函数"""
    print("🚀 ObsidianReaderMCP 功能演示")
    print("=" * 50)
    
    # 设置环境变量
    os.environ["OBSIDIAN_HOST"] = "192.168.0.104"
    os.environ["OBSIDIAN_PORT"] = "27123"
    os.environ["OBSIDIAN_API_KEY"] = "1fb6e1d89dacb6eb84a6aa5e1d238faa67b8ddbefeac90b895aeab32e0657b5f"
    
    try:
        # 1. 创建示例笔记（如果需要）
        await demo_create_sample_notes()
        
        # 2. 读取所有笔记标题
        await demo_read_all_note_titles()
        
        # 3. 搜索笔记
        await demo_search_notes()
        
        print("\n🎉 演示完成！")
        print("\n💡 提示：")
        print("- 您可以在Claude Desktop中使用相同的功能")
        print("- 配置MCP服务器后，Claude可以直接管理您的Obsidian笔记")
        print("- 支持创建、读取、更新、删除、搜索等操作")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
