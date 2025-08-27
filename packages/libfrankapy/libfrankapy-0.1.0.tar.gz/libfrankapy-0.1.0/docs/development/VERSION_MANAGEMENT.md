# Version Management Guide

本文档说明了 libfrankapy 项目的版本管理和发布流程。

## 版本同步机制

为了确保 git tag 和项目文件中的版本号保持同步，我们实现了以下自动化机制：

### 自动同步（推荐）

GitHub Actions 工作流会在发布时自动同步版本号：

1. 当推送 `v*.*.*` 格式的标签时，GitHub Actions 会自动触发
2. 工作流会从 git tag 中提取版本号
3. 自动更新 `pyproject.toml` 和 `libfrankapy/__init__.py` 中的版本号
4. 构建并发布到 PyPI
5. 创建 GitHub Release

### 手动同步（可选）

如果需要在本地预先同步版本号，可以使用提供的工具脚本：

```bash
# 更新版本号到 1.0.0
python scripts/update_version.py 1.0.0

# 预览更改（不实际修改文件）
python scripts/update_version.py 1.0.0 --dry-run
```

## 发布流程

### 标准发布流程

1. **准备发布**
   ```bash
   # 确保代码已提交
   git status
   
   # 可选：本地更新版本号
   python scripts/update_version.py 1.0.0
   git add .
   git commit -m "chore: bump version to 1.0.0"
   ```

2. **创建并推送标签**
   ```bash
   # 创建标签
   git tag v1.0.0
   
   # 推送标签（触发自动发布）
   git push origin v1.0.0
   ```

3. **自动化流程**
   - GitHub Actions 自动构建包
   - 运行测试验证
   - 发布到 PyPI
   - 创建 GitHub Release
   - 更新文档

### 版本号格式

遵循 [语义化版本控制](https://semver.org/lang/zh-CN/) 规范：

- `MAJOR.MINOR.PATCH` (例如: `1.0.0`)
- `MAJOR.MINOR.PATCH-PRERELEASE` (例如: `1.0.0-alpha.1`)

### 版本号规则

- **MAJOR**: 不兼容的 API 修改
- **MINOR**: 向下兼容的功能性新增
- **PATCH**: 向下兼容的问题修正
- **PRERELEASE**: 预发布版本标识

## 文件同步说明

以下文件会自动同步版本号：

1. **`pyproject.toml`**
   ```toml
   [project]
   version = "1.0.0"
   ```

2. **`libfrankapy/__init__.py`**
   ```python
   __version__ = "1.0.0"
   ```

## 故障排除

### 版本不匹配问题

如果发现版本号不同步：

1. **检查当前版本**
   ```bash
   # 检查 git tag
   git describe --tags --abbrev=0
   
   # 检查 pyproject.toml
   grep "^version = " pyproject.toml
   
   # 检查 __init__.py
   grep "__version__ = " libfrankapy/__init__.py
   ```

2. **手动同步**
   ```bash
   # 使用工具脚本同步
   python scripts/update_version.py <正确的版本号>
   ```

3. **重新发布**
   ```bash
   # 提交更改
   git add .
   git commit -m "fix: sync version numbers"
   
   # 删除旧标签（如果需要）
   git tag -d v1.0.0
   git push origin :refs/tags/v1.0.0
   
   # 创建新标签
   git tag v1.0.0
   git push origin v1.0.0
   ```

### GitHub Actions 失败

如果自动发布失败：

1. 检查 [GitHub Actions 页面](https://github.com/libfrankapy/libfrankapy/actions)
2. 查看失败的步骤和错误信息
3. 修复问题后重新推送标签

## 最佳实践

1. **发布前测试**
   ```bash
   # 运行完整测试套件
   pytest tests/ -v
   
   # 检查代码质量
   pre-commit run --all-files
   ```

2. **版本号规划**
   - 提前规划版本号
   - 遵循语义化版本控制
   - 在 CHANGELOG.md 中记录变更

3. **发布验证**
   - 发布后验证 PyPI 页面
   - 测试安装新版本
   - 检查 GitHub Release 页面

## 相关链接

- [语义化版本控制](https://semver.org/lang/zh-CN/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [PyPI 发布指南](https://packaging.python.org/en/latest/tutorials/packaging-projects/)