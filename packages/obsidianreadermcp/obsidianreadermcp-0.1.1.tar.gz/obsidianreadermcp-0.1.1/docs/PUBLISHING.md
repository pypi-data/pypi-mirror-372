# 发布指南

本文档介绍如何将 ObsidianReaderMCP 发布到 PyPI 并配置 uvx 部署。

## 准备工作

### 1. 安装发布工具

```bash
# 安装构建和发布工具
uv add --dev build twine

# 或使用 pip
pip install build twine
```

### 2. 配置 PyPI 凭据

创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers = pypi testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

或使用环境变量：

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here
```

## 发布流程

### 方法一：使用发布脚本（推荐）

```bash
# 运行自动发布脚本
python scripts/publish.py
```

### 方法二：手动发布

#### 1. 更新版本号

在 `pyproject.toml` 中更新版本：

```toml
[project]
version = "0.1.1"  # 更新版本号
```

#### 2. 运行测试

```bash
# 运行所有测试
uv run pytest

# 检查代码格式
uv run black --check src/
uv run isort --check-only src/

# 类型检查
uv run mypy src/obsidianreadermcp/
```

#### 3. 构建包

```bash
# 清理旧的构建文件
rm -rf dist/ build/ *.egg-info/

# 构建包
uv build
```

#### 4. 检查包

```bash
# 检查包的完整性
uv run twine check dist/*
```

#### 5. 测试发布（可选）

```bash
# 发布到测试 PyPI
uv run twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ obsidianreadermcp
```

#### 6. 正式发布

```bash
# 发布到 PyPI
uv run twine upload dist/*
```

## uvx 部署配置

### 1. 确保入口点配置正确

在 `pyproject.toml` 中已配置：

```toml
[project.scripts]
obsidianreadermcp = "obsidianreadermcp.server:main"
```

### 2. 发布后的 uvx 使用方法

用户可以通过以下方式使用：

```bash
# 直接运行（无需安装）
uvx obsidianreadermcp

# 或者安装后运行
uv tool install obsidianreadermcp
obsidianreadermcp
```

### 3. MCP 集成配置

用户可以在 Claude Desktop 配置中添加：

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

## 版本管理

### 语义化版本控制

遵循 [Semantic Versioning](https://semver.org/)：

- `MAJOR.MINOR.PATCH`
- `MAJOR`: 不兼容的 API 更改
- `MINOR`: 向后兼容的功能添加
- `PATCH`: 向后兼容的错误修复

### 发布检查清单

- [ ] 更新版本号
- [ ] 更新 CHANGELOG.md
- [ ] 运行所有测试
- [ ] 检查代码格式
- [ ] 构建包
- [ ] 检查包完整性
- [ ] 测试发布（可选）
- [ ] 正式发布
- [ ] 创建 Git 标签
- [ ] 推送到 GitHub

### Git 标签

```bash
# 创建标签
git tag -a v0.1.0 -m "Release version 0.1.0"

# 推送标签
git push origin v0.1.0
```

## 故障排除

### 常见问题

1. **构建失败**
   - 检查 `pyproject.toml` 配置
   - 确保所有依赖都已安装

2. **上传失败**
   - 检查 PyPI 凭据
   - 确保版本号未被使用

3. **uvx 运行失败**
   - 检查入口点配置
   - 确保依赖正确安装

### 调试命令

```bash
# 检查包内容
tar -tzf dist/obsidianreadermcp-*.tar.gz

# 检查轮子内容
unzip -l dist/obsidianreadermcp-*.whl

# 测试本地安装
pip install dist/obsidianreadermcp-*.whl
```

## 自动化发布

可以使用 GitHub Actions 自动化发布流程。创建 `.github/workflows/publish.yml`：

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install uv
      uses: astral-sh/setup-uv@v1
    - name: Build package
      run: uv build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: uv run twine upload dist/*
```
