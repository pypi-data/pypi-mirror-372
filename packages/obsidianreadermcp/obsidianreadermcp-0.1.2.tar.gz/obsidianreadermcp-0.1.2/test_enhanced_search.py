#!/usr/bin/env python3
"""
测试增强搜索功能 - 搜索文件夹和文件夹下的笔记
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

async def test_enhanced_search():
    """测试增强搜索功能"""
    print("🔍 测试增强搜索功能")
    print("="*60)
    
    # 设置环境变量
    os.environ["OBSIDIAN_HOST"] = "192.168.0.104"
    os.environ["OBSIDIAN_PORT"] = "27123"
    os.environ["OBSIDIAN_API_KEY"] = "1fb6e1d89dacb6eb84a6aa5e1d238faa67b8ddbefeac90b895aeab32e0657b5f"
    
    try:
        obsidian_config, _ = get_config()
        
        async with ObsidianClient(obsidian_config) as client:
            print("✅ 已连接到Obsidian API")
            
            # 测试1: 普通搜索 vs 增强搜索对比
            print("\n📋 测试1: 搜索'旅游' - 普通搜索 vs 增强搜索")
            print("-" * 50)
            
            # 普通搜索
            print("🔍 普通搜索结果:")
            normal_results = await client.search_notes("旅游", limit=10)
            print(f"找到 {len(normal_results)} 个结果")
            for i, result in enumerate(normal_results, 1):
                print(f"  {i}. 📄 {result.note.path}")
                if result.matches:
                    print(f"     匹配: {result.matches[0][:80]}...")
            
            # 增强搜索
            print("\n🔍 增强搜索结果:")
            enhanced_results = await client.search_notes_enhanced(
                "旅游", 
                limit=10,
                include_folders=True,
                search_in_path=True
            )
            print(f"找到 {len(enhanced_results)} 个结果")
            for i, result in enumerate(enhanced_results, 1):
                result_type = "📄"
                if result.note.path.endswith("/"):
                    result_type = "📁"
                elif any("路径匹配" in match for match in result.matches):
                    result_type = "🔗"
                elif any("文件夹匹配" in match for match in result.matches):
                    result_type = "📁"
                
                print(f"  {i}. {result_type} {result.note.path} (评分: {result.score})")
                for match in result.matches:
                    print(f"     {match[:100]}...")
            
            # 测试2: 搜索文件夹名称
            print(f"\n📋 测试2: 搜索文件夹'计划'")
            print("-" * 50)
            
            folder_results = await client.search_notes_enhanced(
                "计划",
                limit=10,
                include_folders=True,
                search_in_path=True
            )
            print(f"找到 {len(folder_results)} 个结果")
            for i, result in enumerate(folder_results, 1):
                result_type = "📄"
                if result.note.path.endswith("/"):
                    result_type = "📁"
                elif any("文件夹匹配" in match for match in result.matches):
                    result_type = "📁"
                elif any("路径匹配" in match for match in result.matches):
                    result_type = "🔗"
                
                print(f"  {i}. {result_type} {result.note.path}")
                for match in result.matches:
                    print(f"     {match}")
            
            # 测试3: 只搜索内容，不包含文件夹
            print(f"\n📋 测试3: 搜索'江苏' - 仅内容搜索")
            print("-" * 50)
            
            content_only_results = await client.search_notes_enhanced(
                "江苏",
                limit=10,
                include_folders=False,
                search_in_path=False
            )
            print(f"找到 {len(content_only_results)} 个结果")
            for i, result in enumerate(content_only_results, 1):
                print(f"  {i}. 📄 {result.note.path}")
                for match in result.matches:
                    print(f"     {match[:100]}...")
            
            # 测试4: 搜索路径中的关键词
            print(f"\n📋 测试4: 搜索路径中的'demo'")
            print("-" * 50)
            
            path_results = await client.search_notes_enhanced(
                "demo",
                limit=10,
                include_folders=True,
                search_in_path=True
            )
            print(f"找到 {len(path_results)} 个结果")
            for i, result in enumerate(path_results, 1):
                result_type = "📄"
                if any("路径匹配" in match for match in result.matches):
                    result_type = "🔗"
                elif any("文件夹匹配" in match for match in result.matches):
                    result_type = "📁"
                
                print(f"  {i}. {result_type} {result.note.path}")
                for match in result.matches:
                    print(f"     {match}")
            
            # 测试5: 综合搜索测试
            print(f"\n📋 测试5: 综合搜索'学习'")
            print("-" * 50)
            
            comprehensive_results = await client.search_notes_enhanced(
                "学习",
                limit=15,
                include_folders=True,
                search_in_path=True
            )
            print(f"找到 {len(comprehensive_results)} 个结果")
            
            # 按类型分组显示
            content_matches = []
            path_matches = []
            folder_matches = []
            
            for result in comprehensive_results:
                if any("文件夹匹配" in match for match in result.matches):
                    folder_matches.append(result)
                elif any("路径匹配" in match for match in result.matches):
                    path_matches.append(result)
                else:
                    content_matches.append(result)
            
            if folder_matches:
                print("  📁 文件夹匹配:")
                for result in folder_matches:
                    print(f"    - {result.note.path}")
            
            if path_matches:
                print("  🔗 路径匹配:")
                for result in path_matches:
                    print(f"    - {result.note.path}")
            
            if content_matches:
                print("  📄 内容匹配:")
                for result in content_matches:
                    print(f"    - {result.note.path}")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主函数"""
    await test_enhanced_search()
    
    print("\n🎉 增强搜索功能测试完成！")
    print("\n💡 新功能特点:")
    print("- ✅ 搜索笔记内容（原有功能）")
    print("- ✅ 搜索文件路径中的关键词")
    print("- ✅ 搜索文件夹名称")
    print("- ✅ 显示文件夹包含的笔记数量")
    print("- ✅ 按匹配类型分类显示结果")
    print("- ✅ 可配置是否包含文件夹和路径搜索")
    print("\n📋 在Claude Desktop中使用:")
    print("- search_notes: 普通内容搜索")
    print("- search_notes_enhanced: 增强搜索（推荐）")

if __name__ == "__main__":
    asyncio.run(main())
