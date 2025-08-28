# ObsidianReaderMCP

[![GitHub](https://img.shields.io/badge/GitHub-QianJue--CN%2FObsidianReaderMCP-blue?logo=github)](https://github.com/QianJue-CN/ObsidianReaderMCP)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

[English](README.md) | 中文

一个全面的 Python MCP（模型上下文协议）服务器，用于通过 obsidian-local-rest-api 插件管理 Obsidian 知识库。

## 功能特性

### 核心 CRUD 操作
- **创建**：创建带有内容、元数据和标签的新笔记
- **读取**：通过路径检索笔记内容和元数据
- **更新**：修改现有笔记（内容、元数据、标签）
- **删除**：从知识库中删除笔记

### 扩展功能
- **批量操作**：一次创建、更新或删除多个笔记
- **模板系统**：创建和使用带变量的笔记模板
- **链接分析**：分析笔记之间的关系
- **搜索和过滤**：按内容、标签、日期范围、字数进行高级搜索
- **知识库统计**：生成全面的知识库分析
- **备份管理**：创建和管理知识库备份

### MCP 服务器集成
- 完整的 MCP 协议支持，用于 AI 助手集成
- 异步/等待支持，实现高性能
- 全面的错误处理和日志记录
- 速率限制和连接管理

## 安装

### 前置要求
1. 安装并配置了 **obsidian-local-rest-api** 插件的 **Obsidian**
2. **Python 3.10+**

### 方法一：使用 uvx（推荐）

使用 ObsidianReaderMCP 最简单的方法是通过 `uvx`，无需安装即可运行：

```bash
# 直接运行，无需安装
uvx obsidianreadermcp

# 或安装为工具
uv tool install obsidianreadermcp
obsidianreadermcp
```

### 方法二：使用 pip

```bash
# 从 PyPI 安装
pip install obsidianreadermcp

# 运行服务器
obsidianreadermcp
```

### 方法三：从源码安装

```bash
# 克隆仓库
git clone https://github.com/QianJue-CN/ObsidianReaderMCP.git
cd ObsidianReaderMCP

# 安装依赖
uv sync

# 或使用 pip
pip install -e .
```

## 配置

### 环境变量

在项目根目录创建 `.env` 文件（从 `.env.example` 复制）：

```env
# Obsidian API 配置
OBSIDIAN_HOST=localhost
OBSIDIAN_PORT=27123
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_USE_HTTPS=false
OBSIDIAN_TIMEOUT=30
OBSIDIAN_MAX_RETRIES=3
OBSIDIAN_RATE_LIMIT=10

# MCP 服务器配置
LOG_LEVEL=INFO
ENABLE_DEBUG=false
```

### Obsidian 设置

1. 从社区插件安装 **obsidian-local-rest-api** 插件
2. 在 Obsidian 设置中启用插件
3. 配置插件：
   - 设置 API 端口（默认：27123）
   - 生成 API 密钥
   - 如需要，启用 CORS
4. 启动本地 REST API 服务器

## 使用方法

### 作为 Python 库

```python
import asyncio
from obsidianreadermcp import ObsidianClient
from obsidianreadermcp.config import ObsidianConfig
from obsidianreadermcp.models import NoteMetadata

async def main():
    # 创建配置
    config = ObsidianConfig()  # 使用环境变量

    # 创建并连接客户端
    async with ObsidianClient(config) as client:
        # 创建笔记
        metadata = NoteMetadata(
            tags=["示例", "演示"],
            frontmatter={"title": "我的笔记", "author": "我"}
        )

        note = await client.create_note(
            path="my_note.md",
            content="# 我的笔记\n\n这是我的笔记内容。",
            metadata=metadata
        )

        # 读取笔记
        retrieved_note = await client.get_note("my_note.md")
        print(f"笔记内容: {retrieved_note.content}")

        # 更新笔记
        await client.update_note(
            path="my_note.md",
            content="# 更新的笔记\n\n这个内容已经被更新了。"
        )

        # 搜索笔记
        results = await client.search_notes("更新")
        print(f"找到 {len(results)} 个匹配的笔记")

        # 删除笔记
        await client.delete_note("my_note.md")

asyncio.run(main())
```

### 作为 MCP 服务器

```bash
# 方法一：使用 uvx（推荐）
uvx obsidianreadermcp

# 方法二：使用已安装的包
obsidianreadermcp

# 方法三：使用 Python 模块
python -m obsidianreadermcp.server

# 方法四：编程方式运行
python -c "
import asyncio
from obsidianreadermcp.server import main
asyncio.run(main())
"
```

### Claude Desktop 集成

在 Claude Desktop 配置文件中添加：

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uvx",
      "args": ["obsidianreadermcp"],
      "env": {
        "OBSIDIAN_HOST": "localhost",
        "OBSIDIAN_PORT": "27123",
        "OBSIDIAN_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

或者如果您已全局安装：

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "obsidianreadermcp",
      "env": {
        "OBSIDIAN_HOST": "localhost",
        "OBSIDIAN_PORT": "27123",
        "OBSIDIAN_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 扩展功能示例

```python
from obsidianreadermcp.extensions import ObsidianExtensions

async with ObsidianClient(config) as client:
    extensions = ObsidianExtensions(client)

    # 创建模板
    template = extensions.create_template(
        name="daily_note",
        content="# {{date}}\n\n## 任务\n- {{task}}\n\n## 笔记\n{{notes}}",
        description="日记模板"
    )

    # 从模板创建笔记
    note = await extensions.create_note_from_template(
        template_name="daily_note",
        path="daily/2024-01-15.md",
        variables={
            "date": "2024-01-15",
            "task": "审查项目状态",
            "notes": "所有系统运行正常"
        }
    )

    # 批量操作
    batch_notes = [
        {"path": "note1.md", "content": "内容 1", "tags": ["批量"]},
        {"path": "note2.md", "content": "内容 2", "tags": ["批量"]},
    ]
    result = await extensions.batch_create_notes(batch_notes)

    # 分析知识库
    stats = await extensions.generate_vault_stats()
    print(f"知识库有 {stats.total_notes} 个笔记，共 {stats.total_words} 个单词")

    # 查找孤立笔记
    orphaned = await extensions.find_orphaned_notes()
    print(f"找到 {len(orphaned)} 个孤立笔记")
```

## MCP 工具

作为 MCP 服务器运行时，提供以下工具：

### 核心操作
- `create_note`：创建带有内容和元数据的新笔记
- `get_note`：通过路径检索笔记
- `update_note`：更新现有笔记
- `delete_note`：删除笔记
- `list_notes`：列出知识库或文件夹中的所有笔记
- `search_notes`：按内容搜索笔记

### 知识库管理
- `get_vault_info`：获取知识库信息和统计
- `get_tags`：列出知识库中使用的所有标签
- `get_notes_by_tag`：查找具有特定标签的笔记

## API 参考

### ObsidianClient

与 Obsidian 交互的主要客户端类。

#### 方法

- `async create_note(path: str, content: str = "", metadata: Optional[NoteMetadata] = None) -> Note`
- `async get_note(path: str) -> Note`
- `async update_note(path: str, content: Optional[str] = None, metadata: Optional[NoteMetadata] = None) -> Note`
- `async delete_note(path: str) -> bool`
- `async list_notes(folder: str = "") -> List[str]`
- `async search_notes(query: str, limit: int = 50, context_length: int = 100) -> List[SearchResult]`
- `async get_vault_info() -> VaultInfo`
- `async get_tags() -> List[str]`
- `async get_notes_by_tag(tag: str) -> List[Note]`

### ObsidianExtensions

高级知识库管理的扩展功能。

#### 方法

- `async batch_create_notes(notes_data: List[Dict], continue_on_error: bool = True) -> Dict`
- `async batch_update_notes(updates: List[Dict], continue_on_error: bool = True) -> Dict`
- `async batch_delete_notes(paths: List[str], continue_on_error: bool = True) -> Dict`
- `create_template(name: str, content: str, variables: Optional[List[str]] = None, description: Optional[str] = None) -> Template`
- `async create_note_from_template(template_name: str, path: str, variables: Optional[Dict[str, str]] = None, metadata: Optional[NoteMetadata] = None) -> Note`
- `async create_backup(backup_path: str, include_attachments: bool = True) -> BackupInfo`
- `async analyze_links() -> List[LinkInfo]`
- `async find_orphaned_notes() -> List[str]`
- `async find_broken_links() -> List[LinkInfo]`
- `async generate_vault_stats() -> VaultStats`
- `async search_by_date_range(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, date_field: str = "created") -> List[Note]`
- `async search_by_word_count(min_words: Optional[int] = None, max_words: Optional[int] = None) -> List[Note]`

## 测试

运行测试套件：

```bash
# 使用 uv
uv run pytest

# 使用 pip
pytest

# 带覆盖率
pytest --cov=obsidianreadermcp --cov-report=html
```

## 示例

查看 `examples/` 目录获取更详细的使用示例：

- `basic_usage.py`：演示核心 CRUD 操作
- `advanced_features.py`：展示扩展功能
- `mcp_integration.py`：MCP 服务器集成示例

## 贡献

我们欢迎贡献！请查看我们的[贡献指南](CONTRIBUTING.md)了解详情。

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 进行更改
4. 为新功能添加测试
5. 运行测试套件 (`uv run pytest`)
6. 提交更改 (`git commit -m 'Add some amazing feature'`)
7. 推送到分支 (`git push origin feature/amazing-feature`)
8. 打开 Pull Request

## 问题和支持

- 🐛 **错误报告**：[GitHub Issues](https://github.com/QianJue-CN/ObsidianReaderMCP/issues)
- 💡 **功能请求**：[GitHub Issues](https://github.com/QianJue-CN/ObsidianReaderMCP/issues)
- 📖 **文档**：[API 文档](docs/API.md)

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 致谢

- [obsidian-local-rest-api](https://github.com/coddingtonbear/obsidian-local-rest-api) - 使这一切成为可能的 Obsidian 插件
- [MCP (模型上下文协议)](https://modelcontextprotocol.io/) - AI 助手集成协议
- [Obsidian](https://obsidian.md/) - 知识管理应用程序

## Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=QianJue-CN/ObsidianReaderMCP&type=Date)](https://star-history.com/#QianJue-CN/ObsidianReaderMCP&Date)
