#!/usr/bin/env python3
"""
调试搜索功能 - 检查为什么"旅游计划"文件夹中的笔记没有显示
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

async def debug_search_and_list():
    """调试搜索和列表功能"""
    print("🔍 调试搜索和列表功能")
    print("="*50)
    
    # 设置环境变量
    os.environ["OBSIDIAN_HOST"] = "192.168.0.104"
    os.environ["OBSIDIAN_PORT"] = "27123"
    os.environ["OBSIDIAN_API_KEY"] = "1fb6e1d89dacb6eb84a6aa5e1d238faa67b8ddbefeac90b895aeab32e0657b5f"
    
    try:
        obsidian_config, _ = get_config()
        
        async with ObsidianClient(obsidian_config) as client:
            print("✅ 已连接到Obsidian API")
            
            # 1. 获取知识库信息
            print("\n📁 知识库信息:")
            vault_info = await client.get_vault_info()
            print(f"  - 名称: {vault_info.name}")
            print(f"  - 路径: {vault_info.path}")
            print(f"  - 笔记数量: {vault_info.note_count}")
            
            # 2. 列出所有笔记（不限制文件夹）
            print("\n📋 列出所有笔记:")
            all_notes = await client.list_notes()
            print(f"  - 总数: {len(all_notes)}")
            
            if all_notes:
                print("  - 笔记列表:")
                for i, note_path in enumerate(all_notes, 1):
                    print(f"    {i:2d}. {note_path}")
            else:
                print("  - ⚠️ 没有找到任何笔记")
            
            # 3. 列出特定文件夹的笔记
            print("\n📂 列出'旅游计划'文件夹的笔记:")
            travel_notes = await client.list_notes(folder="旅游计划")
            print(f"  - 数量: {len(travel_notes)}")
            
            if travel_notes:
                print("  - 笔记列表:")
                for i, note_path in enumerate(travel_notes, 1):
                    print(f"    {i:2d}. {note_path}")
            else:
                print("  - ⚠️ '旅游计划'文件夹中没有找到笔记")
            
            # 4. 尝试不同的文件夹名称
            print("\n🔍 尝试不同的文件夹路径:")
            folder_variations = [
                "旅游计划",
                "旅游计划/",
                "/旅游计划",
                "/旅游计划/",
                "旅游计划\\",
                "\\旅游计划",
                "\\旅游计划\\",
            ]
            
            for folder in folder_variations:
                try:
                    notes = await client.list_notes(folder=folder)
                    print(f"  - '{folder}': {len(notes)} 个笔记")
                except Exception as e:
                    print(f"  - '{folder}': 错误 - {e}")
            
            # 5. 搜索包含"旅游"的笔记
            print("\n🔍 搜索包含'旅游'的笔记:")
            search_results = await client.search_notes("旅游", limit=20)
            print(f"  - 找到: {len(search_results)} 个结果")
            
            if search_results:
                for i, result in enumerate(search_results, 1):
                    print(f"    {i:2d}. 📄 {result.note.path}")
                    if result.matches:
                        print(f"        匹配: {result.matches[0][:100]}...")
                    else:
                        print(f"        内容: {result.note.content[:100]}...")
            
            # 6. 搜索包含"计划"的笔记
            print("\n🔍 搜索包含'计划'的笔记:")
            search_results = await client.search_notes("计划", limit=20)
            print(f"  - 找到: {len(search_results)} 个结果")
            
            if search_results:
                for i, result in enumerate(search_results, 1):
                    print(f"    {i:2d}. 📄 {result.note.path}")
                    if result.matches:
                        print(f"        匹配: {result.matches[0][:100]}...")
                    else:
                        print(f"        内容: {result.note.content[:100]}...")
            
            # 7. 尝试读取具体的笔记路径
            print("\n📖 尝试读取可能的笔记路径:")
            possible_paths = [
                "旅游计划.md",
                "旅游计划/旅游计划.md",
                "旅游计划/README.md",
                "旅游计划/index.md",
                "旅游计划/计划.md",
                "旅游计划/行程.md",
                "旅游计划/目的地.md",
            ]
            
            for path in possible_paths:
                try:
                    note = await client.get_note(path)
                    print(f"  ✅ 找到: {path}")
                    print(f"      内容长度: {len(note.content)} 字符")
                    print(f"      内容预览: {note.content[:100]}...")
                    if note.metadata and note.metadata.tags:
                        print(f"      标签: {note.metadata.tags}")
                except Exception as e:
                    print(f"  ❌ 未找到: {path} - {e}")
            
            # 8. 获取所有标签
            print("\n🏷️ 获取所有标签:")
            tags = await client.get_tags()
            print(f"  - 标签数量: {len(tags)}")
            if tags:
                print("  - 标签列表:")
                for i, tag in enumerate(tags, 1):
                    print(f"    {i:2d}. {tag}")
            
            # 9. 根据标签搜索笔记
            if tags:
                print("\n🔍 根据标签搜索笔记:")
                for tag in tags[:5]:  # 只测试前5个标签
                    try:
                        tagged_notes = await client.get_notes_by_tag(tag)
                        print(f"  - 标签'{tag}': {len(tagged_notes)} 个笔记")
                        for note in tagged_notes[:3]:  # 只显示前3个
                            print(f"    - {note.path}")
                    except Exception as e:
                        print(f"  - 标签'{tag}': 错误 - {e}")
            
    except Exception as e:
        print(f"❌ 调试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主函数"""
    await debug_search_and_list()
    
    print("\n💡 调试建议:")
    print("1. 检查Obsidian中'旅游计划'文件夹是否真的存在")
    print("2. 确认文件夹中是否有.md文件")
    print("3. 检查文件夹名称是否有特殊字符或空格")
    print("4. 确认obsidian-local-rest-api插件是否正确索引了所有文件")
    print("5. 尝试在Obsidian中刷新或重启插件")

if __name__ == "__main__":
    asyncio.run(main())
