# Quick Start Guide: WSL截图工具

**Feature**: WSL截图工具
**Target Audience**: 开发者
**Purpose**: 快速搭建开发环境并运行项目

## Prerequisites

- Windows 10/11 (x64)
- Python 3.9+
- Git
- WSL (用于测试路径转换)

## Setup Steps

### 1. Clone Repository

```bash
git clone <repository-url>
cd wslScreenShot
git checkout 001-wsl-screenshot-tool
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Run Tests

```bash
pytest tests/ -v --cov=src
```

### 5. Run Application

```bash
python src/main.py
```

## Project Structure

```
src/
├── core/           # 核心功能（screenshot, path_converter, clipboard, hotkey）
├── gui/            # GUI组件（overlay, settings, tray）
├── utils/          # 工具函数（config, logger, notification）
└── system/         # 系统集成（startup, privilege）

tests/
├── unit/           # 单元测试
└── integration/    # 集成测试
```

## Development Workflow

1. **Feature Branch**: 从`001-wsl-screenshot-tool`创建feature分支
2. **Write Tests**: 先编写测试用例（TDD）
3. **Implement**: 实现功能
4. **Format Code**: `black src/ tests/`
5. **Lint**: `flake8 src/ tests/`
6. **Run Tests**: `pytest`
7. **Commit**: 提交代码

## Key Commands

```bash
# 运行程序
python src/main.py

# 运行测试
pytest

# 测试覆盖率
pytest --cov=src --cov-report=html

# 代码格式化
black src/ tests/

# 代码检查
flake8 src/ tests/

# 类型检查
mypy src/

# 打包
pyinstaller --onefile --windowed src/main.py
```

## Next Steps

参考以下文档继续开发：
- [Technical Research](research.md) - 技术选型和最佳实践
- [Data Model](data-model.md) - 数据模型定义
- [Module Contracts](contracts/) - 模块接口契约
- [Project Constitution](../../.specify/memory/constitution.md) - 项目宪章
