# WSL截图工具 - 项目结构

## 目录结构

```
wslScreenShot/
│
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── main.py                   # 程序入口
│   ├── app.py                    # 应用主类
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
│   │   └── admin.py              # 管理员权限检查和请求
│   │
│   └── system/                   # 系统集成模块
│       ├── __init__.py
│       ├── startup.py            # 开机自启动管理
│       └── privilege.py          # 权限管理
│
├── resources/                    # 资源文件目录
│   ├── icons/                    # 图标文件
│   │   ├── app.ico               # 应用图标
│   │   ├── tray.ico              # 托盘图标
│   │   └── tray_disabled.ico    # 托盘图标（禁用状态）
│   │
│   └── ui/                       # UI资源
│       └── settings.ui           # Qt Designer设计的设置界面
│
├── config/                       # 配置文件目录
│   ├── config.json               # 默认配置文件
│   └── config.schema.json        # 配置文件JSON Schema
│
├── tests/                        # 测试目录
│   ├── __init__.py
│   ├── test_screenshot.py        # 截图功能测试
│   ├── test_path_converter.py   # 路径转换测试
│   ├── test_clipboard.py         # 剪贴板测试
│   └── test_config.py            # 配置管理测试
│
├── docs/                         # 文档目录
│   ├── README.md                 # 项目说明
│   ├── INSTALL.md                # 安装指南
│   ├── USER_GUIDE.md             # 用户手册
│   └── DEVELOPMENT.md            # 开发文档
│
├── build/                        # 构建输出目录（Git忽略）
├── dist/                         # 发布目录（Git忽略）
├── logs/                         # 日志目录（Git忽略）
│
├── requirements.txt              # Python依赖列表
├── requirements-dev.txt          # 开发环境依赖
├── setup.py                      # 安装脚本
├── app.manifest                  # Windows应用程序清单（请求管理员权限）
├── .gitignore                    # Git忽略文件
├── .env.example                  # 环境变量示例
├── specify.md                    # 功能规格说明（本文档）
├── cons.md                       # 项目结构说明（当前文档）
└── plan.md                       # 项目计划
```

## 核心模块说明

### 1. src/main.py - 程序入口
- 检查管理员权限，如无则请求提升
- 初始化日志系统
- 加载配置文件
- 启动主应用

### 2. src/app.py - 应用主类
- 单例模式，确保只运行一个实例
- 初始化所有模块
- 管理应用生命周期
- 处理全局事件

### 3. src/core/screenshot.py - 截图核心
```python
class ScreenshotCapture:
    def capture_screen() -> Image
    def capture_region(x, y, width, height) -> Image
    def save_image(image, path) -> bool
```

### 4. src/core/hotkey.py - 快捷键监听
```python
class HotkeyManager:
    def register_hotkey(key_combination, callback)
    def unregister_hotkey(key_combination)
    def start_listening()
    def stop_listening()
```

### 5. src/core/path_converter.py - 路径转换
```python
class PathConverter:
    @staticmethod
    def windows_to_wsl(windows_path: str) -> str
    @staticmethod
    def wsl_to_windows(wsl_path: str) -> str
    @staticmethod
    def validate_path(path: str) -> bool
```

### 6. src/core/clipboard.py - 剪贴板操作
```python
class ClipboardManager:
    @staticmethod
    def set_text(text: str) -> bool
    @staticmethod
    def get_text() -> str
    @staticmethod
    def set_image(image: Image) -> bool
```

### 7. src/gui/overlay.py - 截图遮罩
```python
class ScreenshotOverlay(QWidget):
    def __init__(self, screenshot: Image)
    def paintEvent(event)
    def mousePressEvent(event)
    def mouseMoveEvent(event)
    def mouseReleaseEvent(event)
    signal screenshot_taken(QRect)
```

### 8. src/gui/tray.py - 系统托盘
```python
class SystemTray(QSystemTrayIcon):
    def __init__(self, parent)
    def create_menu()
    def on_settings_clicked()
    def on_exit_clicked()
```

### 9. src/utils/config.py - 配置管理
```python
class ConfigManager:
    def load_config() -> dict
    def save_config(config: dict) -> bool
    def get(key: str, default=None)
    def set(key: str, value)
    def reset_to_default()
```

### 10. src/system/startup.py - 自启动管理
```python
class StartupManager:
    @staticmethod
    def add_to_startup() -> bool
    @staticmethod
    def remove_from_startup() -> bool
    @staticmethod
    def is_in_startup() -> bool
```

## 数据流程

```
用户按下快捷键
    ↓
HotkeyManager捕获 → 触发回调
    ↓
ScreenshotCapture截取全屏
    ↓
ScreenshotOverlay显示遮罩和选区
    ↓
用户选择区域并确认
    ↓
ScreenshotCapture截取选定区域
    ↓
FileManager保存到临时目录
    ↓
PathConverter转换为WSL路径
    ↓
ClipboardManager复制路径到剪贴板
    ↓
NotificationManager显示通知
```

## 配置文件结构

### config.json
```json
{
  "hotkey": "ctrl+alt+a",
  "save_directory": "E:\\tmp\\screenshots",
  "image_format": "jpg",
  "image_quality": 90,
  "auto_startup": true,
  "request_admin": true,
  "show_notification": true,
  "notification_duration": 5,
  "auto_cleanup": false,
  "cleanup_days": 7,
  "multi_monitor": "current",
  "capture_cursor": false
}
```

## 依赖包列表

### requirements.txt
```
PyQt5>=5.15.0
Pillow>=10.0.0
mss>=9.0.0
pywin32>=305
pynput>=1.7.6
```

### requirements-dev.txt
```
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
```

## 编译和打包

### 使用 PyInstaller
```bash
pyinstaller --name="WSL截图工具" \
    --onefile \
    --windowed \
    --icon=resources/icons/app.ico \
    --add-data="resources;resources" \
    --add-data="config;config" \
    --uac-admin \
    src/main.py
```

### 生成安装包
- 使用 Inno Setup 创建Windows安装程序
- 包含自动配置开机自启动选项
- 包含卸载程序

## 版本控制

### Git分支策略
- `main` - 主分支，稳定版本
- `develop` - 开发分支
- `feature/*` - 功能分支
- `bugfix/*` - 修复分支
- `release/*` - 发布分支

### 版本号规则
遵循语义化版本 (Semantic Versioning)：`MAJOR.MINOR.PATCH`
- MAJOR：不兼容的API修改
- MINOR：向后兼容的功能新增
- PATCH：向后兼容的问题修正
