# WSL Screenshot Tool

**Version**: 1.0.0
**License**: MIT

Windows 平台下的截图工具，专为 WSL（Windows Subsystem for Linux）用户设计。一键截图并自动将 Windows 路径转换为 WSL 路径格式，直接粘贴到 WSL 终端使用。

---

## 🎯 主要功能

### 核心特性
- 🎯 **全局快捷键触发** - 默认 `Ctrl+Alt+S`（可自定义）
- 📸 **鼠标拖拽选择** - 可视化选择截图区域
- 🔄 **自动路径转换** - `E:\tmp\1.jpg` → `/mnt/e/tmp/1.jpg`
- 📋 **自动复制路径** - WSL 路径自动复制到剪贴板
- 💾 **快速保存** - 时间戳命名，自动保存为 JPG/PNG
- 🔔 **桌面通知** - Windows Toast 通知显示结果
- 🖥️ **托盘菜单** - 右键托盘图标快速访问功能

### 高级功能
- ⚙️ **图形化设置** - GUI 配置界面
- 🚀 **开机自启动** - 可选自动启动
- 🎨 **多显示器支持** - 支持多显示器环境
- 📏 **高DPI支持** - 支持 125%-200% 缩放
- 🔒 **单实例运行** - 防止重复启动

---

## 📦 安装

### 方式 1：下载打包版本（推荐）

1. 从 [Releases](../../releases) 下载最新的 `WSLScreenshot.exe`（约 45MB）
2. 双击运行 `WSLScreenshot.exe`
3. 程序会自动最小化到系统托盘（任务栏右下角）
4. 首次运行会在 `%APPDATA%\WSLScreenshot\` 创建配置文件

**特点**：
- ✅ 无需安装 Python
- ✅ 无需安装依赖
- ✅ 绿色便携，单文件运行

### 方式 2：从源码运行（开发者）

**环境要求**：
- Python 3.9+
- Windows 10/11

**安装步骤**：

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/wslScreenShot.git
cd wslScreenShot

# 2. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行程序
python src/main.py
```

---

## 🚀 快速开始

### 第一步：启动程序

**打包版**：双击 `WSLScreenshot.exe`
**源码版**：运行 `python src/main.py`

程序启动后会显示在系统托盘（任务栏右下角），如果看不到图标，点击向上箭头 `^` 展开隐藏的图标。

### 第二步：截图

**方法 1：使用快捷键**（推荐）
1. 按下快捷键 `Ctrl+Alt+S`
2. 屏幕变灰，鼠标变成十字光标 ➕
3. 按住左键拖拽选择区域
4. 释放鼠标完成截图
5. WSL 路径自动复制到剪贴板

**方法 2：使用托盘菜单**
1. 右键点击托盘图标 🖥️
2. 选择"截图 (&C)"
3. 其余步骤同上

**取消截图**：按 `ESC` 键

### 第三步：使用截图

截图完成后，WSL 路径已经在剪贴板中，直接在 WSL 终端粘贴即可：

```bash
# 例如，使用 cat 查看图片
cat /mnt/e/tmp/screenshots/screenshot_20251113_120530.jpg

# 或者用其他命令处理
convert /mnt/e/tmp/screenshots/screenshot_20251113_120530.jpg output.png
```

---

## ⚙️ 配置

### 打开设置

右键点击托盘图标 → 选择"设置 (&S)"

### 可配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| 快捷键 | 全局快捷键组合 | `ctrl+alt+s` |
| 保存目录 | 截图保存路径 | `E:\tmp\screenshots` |
| 图片格式 | JPG 或 PNG | `jpg` |
| 图片质量 | JPG 质量 (1-100) | `90` |
| 开机自启动 | 是否开机自动启动 | `true` |
| 显示通知 | 是否显示桌面通知 | `true` |

### 配置文件位置

- **用户配置**：`%APPDATA%\WSLScreenshot\config.json`
- **日志文件**：`%APPDATA%\WSLScreenshot\logs\app.log`

### 手动编辑配置

```json
{
  "hotkey": "ctrl+alt+s",
  "save_directory": "E:\\tmp\\screenshots",
  "image_format": "jpg",
  "image_quality": 90,
  "auto_startup": true,
  "show_notification": true,
  "auto_cleanup": false,
  "cleanup_days": 7
}
```

---

## ❓ 常见问题

### Q1: 快捷键不工作？

**原因**：pynput 库在 Windows 上对某些快捷键组合支持有限。

**解决方案**：
1. 使用托盘菜单触发截图（右键图标 → 截图）
2. 或者在设置中更改快捷键，**避免使用包含 Shift 的组合**

**推荐的快捷键**：
- ✅ `Ctrl+Alt+S`（默认）
- ✅ `Ctrl+Alt+X`
- ✅ `Ctrl+Alt+F9`
- ✅ `F9`（单键）
- ❌ `Ctrl+Shift+X`（不推荐，可能不工作）

### Q2: 托盘图标找不到？

1. 点击任务栏右下角的向上箭头 `^`
2. 查找电脑图标 🖥️
3. 鼠标悬停会显示"WSL Screenshot Tool"

### Q3: 如何退出程序？

右键点击托盘图标 → 选择"退出 (&X)"

### Q4: 程序启动多次？

程序内置单实例检查，如果尝试启动第二个实例会提示"程序已经在运行中"。

如果仍然有问题：
```bash
# 结束所有实例
taskkill /F /IM WSLScreenshot.exe
```

### Q5: 截图保存在哪里？

默认保存在 `E:\tmp\screenshots\`，可以在设置中修改。

截图文件名格式：`screenshot_YYYYMMDD_HHMMSS.jpg`

---

## 🛠️ 技术栈

- **GUI**: PyQt5
- **截图**: mss (高性能屏幕捕获)
- **快捷键**: pynput (全局热键监听)
- **图像处理**: Pillow
- **Windows API**: pywin32 (剪贴板、注册表)
- **通知**: win10toast
- **打包**: PyInstaller

---

## 📝 开发

### 项目结构

```
wslScreenShot/
├── src/
│   ├── core/              # 核心功能
│   │   ├── clipboard.py       # 剪贴板操作
│   │   ├── hotkey.py          # 全局快捷键
│   │   ├── path_converter.py  # 路径转换
│   │   └── screenshot.py      # 截图捕获
│   ├── gui/               # GUI 组件
│   │   ├── overlay.py         # 截图遮罩
│   │   ├── selector.py        # 选择器
│   │   ├── settings.py        # 设置界面
│   │   └── tray.py           # 系统托盘
│   ├── utils/             # 工具模块
│   │   ├── config.py          # 配置管理
│   │   ├── file_manager.py    # 文件管理
│   │   ├── logger.py          # 日志系统
│   │   └── notification.py    # 通知
│   ├── system/            # 系统集成
│   │   ├── privilege.py       # 权限检查
│   │   └── startup.py         # 自启动
│   ├── main.py           # 入口点
│   └── app.py            # 应用单例
├── tests/
│   ├── unit/             # 单元测试
│   └── integration/      # 集成测试
├── config/               # 默认配置
├── dist/                 # 打包输出
└── requirements.txt      # 依赖列表
```

### 运行测试

```bash
# 激活虚拟环境
.venv\Scripts\activate

# 运行所有测试
pytest

# 运行特定测试
pytest tests/unit/test_path_converter.py

# 查看覆盖率
pytest --cov=src tests/
```

### 代码质量

```bash
# 代码格式化
black src/

# 代码检查
flake8 src/
ruff check src/
```

### 打包

```bash
# 使用 PyInstaller 打包
pyinstaller wslscreenshot.spec --clean --noconfirm

# 输出文件
dist/WSLScreenshot.exe
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI 框架
- [mss](https://github.com/BoboTiG/python-mss) - 截图库
- [pynput](https://github.com/moses-palmer/pynput) - 键盘监听
- [Pillow](https://python-pillow.org/) - 图像处理

---

## 📧 联系方式

- **问题反馈**: [GitHub Issues](../../issues)
- **功能建议**: [GitHub Discussions](../../discussions)

---

**⭐ 如果这个工具对你有帮助，请给个 Star！**
