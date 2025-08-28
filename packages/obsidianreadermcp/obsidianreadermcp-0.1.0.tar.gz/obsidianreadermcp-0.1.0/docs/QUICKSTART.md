# 快速开始指南

本指南将帮助您快速设置和使用 ObsidianReaderMCP。

## 安装

### 方法一：通过 uvx（推荐）

```bash
# 直接运行，无需安装
uvx obsidianreadermcp

# 或者安装为工具
uv tool install obsidianreadermcp
obsidianreadermcp
```

### 方法二：通过 pip

```bash
pip install obsidianreadermcp
```

### 方法三：从源码安装

```bash
git clone https://github.com/QianJue-CN/ObsidianReaderMCP.git
cd ObsidianReaderMCP
uv sync
```

## 配置 Obsidian

### 1. 安装插件

1. 打开 Obsidian
2. 进入设置 → 社区插件
3. 搜索并安装 "Local REST API"
4. 启用插件

### 2. 配置插件

1. 在插件设置中：
   - 设置端口（默认：27123）
   - 生成 API 密钥
   - 启用 CORS（如果需要）
2. 启动 REST API 服务器

### 3. 环境配置

创建 `.env` 文件：

```env
OBSIDIAN_HOST=localhost
OBSIDIAN_PORT=27123
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_USE_HTTPS=false
```

## 基本使用

### 作为 Python 库

```python
import asyncio
from obsidianreadermcp import ObsidianClient
from obsidianreadermcp.config import ObsidianConfig

async def main():
    config = ObsidianConfig()
    
    async with ObsidianClient(config) as client:
        # 创建笔记
        note = await client.create_note(
            path="test.md",
            content="# 测试笔记\n\n这是一个测试。"
        )
        print(f"创建笔记: {note.path}")
        
        # 读取笔记
        note = await client.get_note("test.md")
        print(f"笔记内容: {note.content}")

asyncio.run(main())
```

### 作为 MCP 服务器

```bash
# 启动 MCP 服务器
obsidianreadermcp

# 或使用 Python 模块
python -m obsidianreadermcp.server
```

## Claude Desktop 集成

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
        "OBSIDIAN_API_KEY": "your-api-key"
      }
    }
  }
}
```

## 常用功能

### 搜索笔记

```python
results = await client.search_notes("关键词")
for result in results:
    print(f"找到: {result.path}")
```

### 批量操作

```python
from obsidianreadermcp.extensions import ObsidianExtensions

extensions = ObsidianExtensions(client)

# 批量创建笔记
notes_data = [
    {"path": "note1.md", "content": "内容1"},
    {"path": "note2.md", "content": "内容2"},
]
result = await extensions.batch_create_notes(notes_data)
```

### 模板使用

```python
# 创建模板
template = extensions.create_template(
    name="daily",
    content="# {{date}}\n\n## 任务\n{{tasks}}"
)

# 使用模板创建笔记
note = await extensions.create_note_from_template(
    template_name="daily",
    path="daily/2024-01-15.md",
    variables={"date": "2024-01-15", "tasks": "完成项目"}
)
```

## 故障排除

### 连接问题

1. 确保 Obsidian 正在运行
2. 确保 Local REST API 插件已启用
3. 检查端口和 API 密钥配置
4. 检查防火墙设置

### 常见错误

- **ConnectionError**: 检查 Obsidian 是否运行，端口是否正确
- **AuthenticationError**: 检查 API 密钥是否正确
- **NotFoundError**: 检查笔记路径是否存在

### 调试模式

```bash
# 启用调试日志
export LOG_LEVEL=DEBUG
obsidianreadermcp
```

## 下一步

- 查看 [API 文档](API.md)
- 浏览 [示例代码](../examples/)
- 阅读 [完整文档](../README.md)
- 参与 [项目贡献](../CONTRIBUTING.md)

## 获取帮助

- 🐛 [报告问题](https://github.com/QianJue-CN/ObsidianReaderMCP/issues)
- 💡 [功能请求](https://github.com/QianJue-CN/ObsidianReaderMCP/issues)
- 📖 [文档](https://github.com/QianJue-CN/ObsidianReaderMCP)
