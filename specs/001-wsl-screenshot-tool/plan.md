# Implementation Plan: WSL截图工具

**Branch**: `001-wsl-screenshot-tool` | **Date**: 2025-11-12 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-wsl-screenshot-tool/spec.md`

## Summary

开发一个Windows平台下的截图工具，专为WSL用户设计。核心功能是通过全局快捷键触发截图，用户选择区域后自动保存截图文件，并将Windows路径转换为WSL路径格式（/mnt/盘符/...）复制到剪贴板。工具常驻系统托盘，提供配置界面和开机自启动功能，支持多显示器和高DPI环境。

技术方案采用Python桌面应用架构，使用PyQt5实现GUI，mss库实现高性能截图，pywin32调用Windows API实现系统集成功能。架构采用模块化设计，核心功能模块（截图、路径转换、剪贴板、快捷键）相互独立，便于测试和维护。

## Technical Context

**Language/Version**: Python 3.9+
**Primary Dependencies**: PyQt5 (GUI), Pillow (图像处理), mss (截图), pywin32 (Windows API), pynput (全局快捷键监听)
**Storage**: 本地文件系统（截图文件、配置JSON、日志文件），Windows注册表（开机自启动）
**Testing**: pytest (单元测试和集成测试), pytest-cov (覆盖率检查)
**Target Platform**: Windows 10/11 (x64)
**Project Type**: Single desktop application
**Performance Goals**: 快捷键响应 < 200ms, 截图处理 < 500ms (1080p), 启动时间 < 3秒
**Constraints**: 内存占用 < 50MB, CPU空闲占用 < 1%, 支持多显示器和高DPI（125%-200%缩放）
**Scale/Scope**: 单用户桌面工具，约3000-5000行Python代码，10个核心模块，20个功能需求

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. 模块化优先 - ✅ PASS
- 设计采用模块化架构，核心功能模块（`src/core/`）相互独立
- 每个模块有清晰接口定义（screenshot.py, path_converter.py, clipboard.py, hotkey.py）
- 模块之间通过公共接口通信，不直接访问内部实现
- 所有核心模块可独立进行单元测试

### II. 用户体验至上 - ✅ PASS
- 性能目标明确：快捷键响应 < 200ms, 截图处理 < 500ms
- 界面设计直观：快捷键触发→拖拽选择→自动完成，核心流程无需点击
- 错误提示友好：规格要求95%错误有清晰用户友好提示
- 通知完整：显示WSL路径而非简单"成功"消息

### III. 测试驱动开发 - ✅ PASS
- 计划要求测试覆盖率 > 70%
- 核心模块（路径转换、剪贴板、配置）必须有完整单元测试
- 关键路径（截图→保存→转换→复制）有集成测试
- 覆盖正常场景和边界条件（特殊字符路径、权限不足等）

### IV. 性能与资源效率 - ✅ PASS
- 明确资源限制：内存 < 50MB, CPU < 1%（空闲）
- 启动时间 < 3秒
- 日志文件轮转，避免无限增长
- 可选临时文件清理功能

### V. 安全与隐私 - ✅ PASS
- 管理员权限请求有明确说明（UAC提示）
- 不收集、上传或分享用户截图
- 配置和日志仅本地存储
- 规避常见安全漏洞（路径遍历、命令注入）

### VI. 跨平台兼容性 - ✅ PASS
- 平台相关代码隔离在 `src/system/` 模块
- 核心逻辑（路径转换、配置）平台无关
- 使用pathlib处理文件路径（跨平台方式）
- 依赖库选择考虑跨平台支持（PyQt5、Pillow、mss）

### VII. 简洁性原则 (YAGNI) - ✅ PASS
- 功能范围明确，仅实现规格要求的功能
- 不引入不必要的抽象层
- 配置项最少必要（8个配置项，符合需求）
- 优先使用成熟第三方库（PyQt5、mss等）而非重复造轮子

**Constitution Check Result**: ✅ ALL GATES PASSED - 可以继续 Phase 0 研究

## Project Structure

### Documentation (this feature)

```text
specs/001-wsl-screenshot-tool/
├── spec.md              # 功能规格说明
├── plan.md              # 实施计划（本文件）
├── research.md          # Phase 0 技术研究输出
├── data-model.md        # Phase 1 数据模型
├── quickstart.md        # Phase 1 快速开始指南
├── contracts/           # Phase 1 模块契约
│   ├── screenshot_module.md
│   ├── path_converter_module.md
│   ├── clipboard_module.md
│   ├── hotkey_module.md
│   └── config_module.md
└── checklists/
    └── requirements.md  # 规格质量检查清单
```

### Source Code (repository root)

采用 **Option 1: Single project** 结构，因为这是单体桌面应用：

```text
wslScreenShot/
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── main.py                   # 程序入口
│   ├── app.py                    # 应用主类（单例模式）
│   │
│   ├── core/                     # 核心功能模块
│   │   ├── __init__.py
│   │   ├── screenshot.py         # 截图核心功能
│   │   ├── hotkey.py             # 全局快捷键监听
│   │   ├── path_converter.py    # Windows路径转WSL路径
│   │   └── clipboard.py          # 剪贴板操作
│   │
│   ├── gui/                      # 图形界面模块
│   │   ├── __init__.py
│   │   ├── overlay.py            # 截图时的全屏遮罩
│   │   ├── selector.py           # 区域选择器
│   │   ├── settings.py           # 设置界面
│   │   └── tray.py               # 系统托盘图标
│   │
│   ├── utils/                    # 工具函数模块
│   │   ├── __init__.py
│   │   ├── config.py             # 配置文件读写
│   │   ├── logger.py             # 日志管理
│   │   ├── notification.py       # Windows通知
│   │   ├── file_manager.py       # 文件管理（保存、清理）
│   │   └── admin.py              # 管理员权限检查
│   │
│   └── system/                   # 系统集成模块（平台相关）
│       ├── __init__.py
│       ├── startup.py            # 开机自启动管理
│       └── privilege.py          # 权限管理
│
├── tests/                        # 测试目录
│   ├── __init__.py
│   ├── unit/                     # 单元测试
│   │   ├── test_path_converter.py
│   │   ├── test_clipboard.py
│   │   ├── test_config.py
│   │   └── test_file_manager.py
│   ├── integration/              # 集成测试
│   │   ├── test_screenshot_workflow.py
│   │   └── test_settings_workflow.py
│   └── fixtures/                 # 测试夹具
│       └── test_config.json
│
├── resources/                    # 资源文件目录
│   ├── icons/
│   │   ├── app.ico
│   │   ├── tray.ico
│   │   └── tray_disabled.ico
│   └── ui/
│       └── settings.ui           # Qt Designer设计的设置界面
│
├── config/                       # 默认配置文件
│   ├── config.json
│   └── config.schema.json
│
├── docs/                         # 用户文档
│   ├── README.md
│   ├── INSTALL.md
│   └── USER_GUIDE.md
│
├── requirements.txt              # 生产依赖
├── requirements-dev.txt          # 开发依赖
├── setup.py                      # 安装脚本
├── app.manifest                  # Windows应用清单（UAC）
├── pytest.ini                    # pytest配置
├── .gitignore
├── specify.md                    # 原始项目规格
├── cons.md                       # 项目结构文档
└── plan.md                       # 项目开发计划
```

**Structure Decision**: 选择单体项目结构（Option 1），因为：
1. 这是桌面应用，无前后端分离需求
2. Python桌面应用标准结构（src/ + tests/）
3. 模块化设计通过目录结构体现（core/, gui/, utils/, system/）
4. 便于打包为单个可执行文件（PyInstaller）

## Complexity Tracking

> 本项目无宪章违规，此部分为空

无需填写，所有宪章检查项均通过。
