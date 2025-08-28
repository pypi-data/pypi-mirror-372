#!/usr/bin/env python3
"""
测试ObsidianReaderMCP的所有基础CRUD功能
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from obsidianreadermcp.client import ObsidianClient
from obsidianreadermcp.config import get_config
from obsidianreadermcp.models import NoteMetadata

class CRUDTester:
    def __init__(self):
        self.test_results = []
        self.test_notes = []
        
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        
    async def setup_client(self):
        """设置客户端连接"""
        print("🔧 设置客户端连接...")
        try:
            # 设置环境变量
            os.environ["OBSIDIAN_HOST"] = "192.168.0.104"
            os.environ["OBSIDIAN_PORT"] = "27123"
            os.environ["OBSIDIAN_API_KEY"] = "1fb6e1d89dacb6eb84a6aa5e1d238faa67b8ddbefeac90b895aeab32e0657b5f"
            
            obsidian_config, _ = get_config()
            self.client = ObsidianClient(obsidian_config)
            await self.client.connect()
            
            self.log_result("客户端连接", True, "成功连接到Obsidian API")
            return True
        except Exception as e:
            self.log_result("客户端连接", False, f"连接失败: {e}")
            return False
    
    async def test_create_operations(self):
        """测试创建操作 (Create)"""
        print("\n📝 测试创建操作...")
        
        # 测试1: 创建简单笔记
        try:
            note_path = "test/简单笔记.md"
            content = "# 简单笔记\n\n这是一个测试笔记。"
            
            note = await self.client.create_note(path=note_path, content=content)
            self.test_notes.append(note_path)
            self.log_result("创建简单笔记", True, f"路径: {note.path}")
        except Exception as e:
            self.log_result("创建简单笔记", False, str(e))
        
        # 测试2: 创建带元数据的笔记
        try:
            note_path = "test/带元数据笔记.md"
            content = """# 带元数据的笔记

这是一个包含元数据的测试笔记。

## 内容
- 标签测试
- 前置元数据测试
- 创建时间记录

## 总结
测试成功！"""
            
            metadata = NoteMetadata(
                tags=["测试", "元数据", "CRUD"],
                frontmatter={
                    "title": "带元数据的笔记",
                    "author": "CRUD测试器",
                    "created": datetime.now().isoformat(),
                    "category": "测试"
                }
            )
            
            note = await self.client.create_note(
                path=note_path, 
                content=content, 
                metadata=metadata
            )
            self.test_notes.append(note_path)
            self.log_result("创建带元数据笔记", True, f"标签: {metadata.tags}")
        except Exception as e:
            self.log_result("创建带元数据笔记", False, str(e))
        
        # 测试3: 创建嵌套目录笔记
        try:
            note_path = "test/子目录/嵌套笔记.md"
            content = "# 嵌套目录笔记\n\n测试在子目录中创建笔记。"
            
            note = await self.client.create_note(path=note_path, content=content)
            self.test_notes.append(note_path)
            self.log_result("创建嵌套目录笔记", True, f"目录: {note_path}")
        except Exception as e:
            self.log_result("创建嵌套目录笔记", False, str(e))
    
    async def test_read_operations(self):
        """测试读取操作 (Read)"""
        print("\n📖 测试读取操作...")
        
        # 测试1: 读取单个笔记
        if self.test_notes:
            try:
                note_path = self.test_notes[0]
                note = await self.client.get_note(note_path)
                self.log_result("读取单个笔记", True, f"内容长度: {len(note.content)} 字符")
            except Exception as e:
                self.log_result("读取单个笔记", False, str(e))
        
        # 测试2: 列出所有笔记
        try:
            notes = await self.client.list_notes()
            self.log_result("列出所有笔记", True, f"找到 {len(notes)} 个笔记")
        except Exception as e:
            self.log_result("列出所有笔记", False, str(e))
        
        # 测试3: 列出特定文件夹的笔记
        try:
            notes = await self.client.list_notes(folder="test")
            self.log_result("列出文件夹笔记", True, f"test文件夹中有 {len(notes)} 个笔记")
        except Exception as e:
            self.log_result("列出文件夹笔记", False, str(e))
        
        # 测试4: 搜索笔记
        try:
            results = await self.client.search_notes("测试", limit=10)
            self.log_result("搜索笔记", True, f"找到 {len(results)} 个匹配结果")
        except Exception as e:
            self.log_result("搜索笔记", False, str(e))
        
        # 测试5: 获取知识库信息
        try:
            vault_info = await self.client.get_vault_info()
            self.log_result("获取知识库信息", True, f"知识库: {vault_info.name}")
        except Exception as e:
            self.log_result("获取知识库信息", False, str(e))
        
        # 测试6: 获取标签列表
        try:
            tags = await self.client.get_tags()
            self.log_result("获取标签列表", True, f"找到 {len(tags)} 个标签")
        except Exception as e:
            self.log_result("获取标签列表", False, str(e))
    
    async def test_update_operations(self):
        """测试更新操作 (Update)"""
        print("\n✏️ 测试更新操作...")
        
        if not self.test_notes:
            self.log_result("更新操作", False, "没有可更新的笔记")
            return
        
        # 测试1: 更新笔记内容
        try:
            note_path = self.test_notes[0]
            new_content = """# 更新后的简单笔记

这是更新后的内容。

## 更新信息
- 更新时间: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
- 更新内容: 添加了更多信息
- 测试状态: 进行中

## 新增章节
这是新增的章节内容。"""
            
            updated_note = await self.client.update_note(path=note_path, content=new_content)
            self.log_result("更新笔记内容", True, f"新内容长度: {len(updated_note.content)} 字符")
        except Exception as e:
            self.log_result("更新笔记内容", False, str(e))
        
        # 测试2: 更新笔记元数据
        if len(self.test_notes) > 1:
            try:
                note_path = self.test_notes[1]
                new_metadata = NoteMetadata(
                    tags=["测试", "元数据", "CRUD", "已更新"],
                    frontmatter={
                        "title": "更新后的带元数据笔记",
                        "author": "CRUD测试器",
                        "updated": datetime.now().isoformat(),
                        "category": "测试",
                        "status": "已更新"
                    }
                )
                
                updated_note = await self.client.update_note(
                    path=note_path, 
                    metadata=new_metadata
                )
                self.log_result("更新笔记元数据", True, f"新标签: {new_metadata.tags}")
            except Exception as e:
                self.log_result("更新笔记元数据", False, str(e))
        
        # 测试3: 同时更新内容和元数据
        if len(self.test_notes) > 2:
            try:
                note_path = self.test_notes[2]
                new_content = """# 完全更新的嵌套笔记

这个笔记的内容和元数据都被更新了。

## 更新详情
- 内容: 完全重写
- 元数据: 新增标签和前置数据
- 位置: 子目录中

## 测试结果
更新功能正常工作！"""
                
                new_metadata = NoteMetadata(
                    tags=["嵌套", "更新", "完整测试"],
                    frontmatter={
                        "title": "完全更新的嵌套笔记",
                        "updated": datetime.now().isoformat()
                    }
                )
                
                updated_note = await self.client.update_note(
                    path=note_path,
                    content=new_content,
                    metadata=new_metadata
                )
                self.log_result("同时更新内容和元数据", True, "内容和元数据都已更新")
            except Exception as e:
                self.log_result("同时更新内容和元数据", False, str(e))
    
    async def test_delete_operations(self):
        """测试删除操作 (Delete)"""
        print("\n🗑️ 测试删除操作...")
        
        # 删除所有测试笔记
        for note_path in self.test_notes:
            try:
                success = await self.client.delete_note(note_path)
                if success:
                    self.log_result(f"删除笔记 {note_path}", True, "删除成功")
                else:
                    self.log_result(f"删除笔记 {note_path}", False, "删除失败")
            except Exception as e:
                self.log_result(f"删除笔记 {note_path}", False, str(e))
        
        # 验证删除结果
        try:
            # 尝试读取已删除的笔记
            if self.test_notes:
                try:
                    await self.client.get_note(self.test_notes[0])
                    self.log_result("验证删除结果", False, "笔记仍然存在")
                except:
                    self.log_result("验证删除结果", True, "笔记已成功删除")
        except Exception as e:
            self.log_result("验证删除结果", False, str(e))
    
    async def cleanup(self):
        """清理资源"""
        if hasattr(self, 'client'):
            await self.client.disconnect()
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("📊 CRUD操作测试总结")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n🎉 CRUD功能测试完成！")

async def main():
    """主测试函数"""
    print("🚀 开始CRUD操作全面测试")
    print("="*50)
    
    tester = CRUDTester()
    
    try:
        # 设置客户端
        if not await tester.setup_client():
            return
        
        # 执行所有测试
        await tester.test_create_operations()
        await tester.test_read_operations()
        await tester.test_update_operations()
        await tester.test_delete_operations()
        
    except Exception as e:
        print(f"❌ 测试过程中出现严重错误: {e}")
    finally:
        await tester.cleanup()
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
