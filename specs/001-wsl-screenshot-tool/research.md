# Technical Research: WSL截图工具

**Feature**: WSL截图工具
**Date**: 2025-11-12
**Purpose**: 研究Python桌面应用开发的关键技术选型和最佳实践

## 研究主题

本文档记录以下关键技术决策的研究结果：
1. 截图库选择（mss vs其他）
2. GUI框架选择（PyQt5 vs alternatives）
3. 全局快捷键监听方案
4. 高DPI显示器支持策略
5. Windows系统集成最佳实践
6. 路径转换实现方案

---

## 1. 截图库选择

### Decision: mss (Multiple Screen Shots)

### Rationale:
- **性能优异**: mss是纯Python实现的跨平台截图库，专为高性能设计
- **多显示器支持**: 原生支持多显示器环境，可独立截取单个显示器或所有显示器
- **跨平台**: 支持Windows、Linux、macOS，符合宪章的跨平台兼容性原则
- **活跃维护**: 项目活跃，定期更新，兼容Python 3.9+
- **简单API**: API简洁，易于集成，减少学习成本

### Alternatives Considered:
- **Pillow.ImageGrab**:
  - ❌ 性能较慢，不适合高频截图
  - ❌ 多显示器支持有限
  - ✅ 但已是项目依赖，可用于图像处理

- **pyautogui**:
  - ❌ 功能过于庞大，包含自动化操作（不需要）
  - ❌ 性能不如mss
  - ❌ 依赖项较多

### Implementation Notes:
```python
import mss

# 单显示器截图
with mss.mss() as sct:
    monitor = sct.monitors[1]  # 1 = 主显示器
    screenshot = sct.grab(monitor)

# 自定义区域截图
with mss.mss() as sct:
    region = {"top": 100, "left": 100, "width": 800, "height": 600}
    screenshot = sct.grab(region)
```

---

## 2. GUI框架选择

### Decision: PyQt5

### Rationale:
- **功能完整**: 提供完整的GUI组件库，包括系统托盘、通知、高DPI支持
- **跨平台**: 支持Windows、Linux、macOS
- **成熟稳定**: 基于Qt5，工业级GUI框架，稳定性高
- **丰富文档**: 文档和社区资源丰富，问题易解决
- **性能优秀**: 原生GUI性能，满足 < 200ms响应时间要求

### Alternatives Considered:
- **Tkinter**:
  - ❌ 系统托盘支持差
  - ❌ 高DPI支持不够完善
  - ❌ 外观陈旧，用户体验不佳
  - ✅ 标准库自带，无需安装

- **PySide6**:
  - ✅ Qt6的官方Python绑定，LGPL许可
  - ❌ 生态较PyQt5略少
  - ⚠️ 可作为备选方案

### Implementation Notes:
- 使用Qt Designer设计设置界面UI
- QSystemTrayIcon实现托盘图标
- QWidget实现全屏遮罩（无边框、透明背景）
- 高DPI支持：`QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)`

---

## 3. 全局快捷键监听

### Decision: pynput

### Rationale:
- **全局监听**: 支持全局快捷键监听（后台运行时也能捕获）
- **跨平台**: Windows、Linux、macOS均支持
- **组合键支持**: 支持Ctrl+Alt+A等组合键
- **轻量级**: 依赖少，性能开销小
- **易用性**: API简洁，易于集成

### Alternatives Considered:
- **keyboard**:
  - ❌ Windows上需要管理员权限监听（pynput也需要但更灵活）
  - ⚠️ 文档相对较少

- **pyHook (Windows-only)**:
  - ❌ 仅支持Windows，违反跨平台兼容性原则
  - ❌ 维护较少

### Implementation Notes:
```python
from pynput import keyboard

def on_activate():
    print('截图快捷键触发')

# 监听 Ctrl+Alt+A
with keyboard.GlobalHotKeys({
    '<ctrl>+<alt>+a': on_activate
}) as h:
    h.join()
```

**注意事项**:
- 全局热键监听需要在独立线程运行，避免阻塞主GUI线程
- 快捷键冲突检测可通过尝试注册+捕获异常实现

---

## 4. 高DPI显示器支持

### Decision: Qt的高DPI自动缩放 + 手动坐标转换

### Rationale:
- Qt 5.6+提供自动高DPI缩放支持
- 结合手动坐标转换确保像素级精度
- 满足规格要求：200%缩放下误差 < 2像素

### Implementation Strategy:

#### 4.1 启用Qt高DPI支持
```python
# 在QApplication创建前设置
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# 启用高DPI缩放
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

app = QApplication(sys.argv)
```

#### 4.2 坐标转换
```python
from PyQt5.QtGui import QScreen

# 获取设备像素比
screen = QApplication.primaryScreen()
device_pixel_ratio = screen.devicePixelRatio()

# 逻辑坐标 → 物理坐标
physical_x = logical_x * device_pixel_ratio
physical_y = logical_y * device_pixel_ratio

# 物理坐标 → 逻辑坐标
logical_x = physical_x / device_pixel_ratio
logical_y = physical_y / device_pixel_ratio
```

#### 4.3 多显示器DPI处理
- 每个显示器的DPI可能不同
- 使用`QScreen.devicePixelRatio()`获取特定显示器DPI
- 鼠标坐标所在显示器：`QApplication.screenAt(QPoint(x, y))`

---

## 5. Windows系统集成

### 5.1 开机自启动

**Decision**: Windows注册表方式（主）+ 启动文件夹（备选）

#### 注册表方式
```python
import winreg

def add_to_startup(app_path):
    key = winreg.HKEY_CURRENT_USER
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
        winreg.SetValueEx(reg_key, "WSLScreenshot", 0, winreg.REG_SZ, app_path)
```

**优点**:
- 可靠性高，Windows标准方法
- 可通过注册表编辑器手动管理
- 支持命令行参数

**缺点**:
- 需要注册表访问权限

#### 启动文件夹方式（备选）
```python
import os
import shutil

startup_folder = os.path.join(
    os.getenv('APPDATA'),
    r'Microsoft\Windows\Start Menu\Programs\Startup'
)
shortcut_path = os.path.join(startup_folder, 'WSLScreenshot.lnk')
# 使用pywin32创建快捷方式
```

### 5.2 管理员权限请求

**Decision**: app.manifest文件

创建`app.manifest`:
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
</assembly>
```

PyInstaller打包时引用：
```python
# spec文件中
exe = EXE(
    # ...
    manifest='app.manifest',
    # ...
)
```

**注意**: 根据用户反馈，可能改为可选管理员权限（通过设置控制）

### 5.3 Windows Toast通知

**Decision**: 使用win10toast库（如需跨版本兼容）或pywin32

```python
from win10toast import ToastNotifier

toaster = ToastNotifier()
toaster.show_toast(
    "WSL截图工具",
    "截图已保存: /mnt/e/tmp/screenshot_20251112.jpg",
    duration=5,
    threaded=True
)
```

---

## 6. 路径转换实现

### Decision: 正则表达式 + pathlib组合

### Implementation Strategy:

```python
from pathlib import Path, PureWindowsPath
import re

class PathConverter:
    @staticmethod
    def windows_to_wsl(windows_path: str) -> str:
        """
        将Windows路径转换为WSL路径
        E:\\tmp\\file.jpg -> /mnt/e/tmp/file.jpg
        """
        # 规范化路径
        path_obj = PureWindowsPath(windows_path)

        # 提取盘符
        drive = path_obj.drive.rstrip(':').lower()

        # 提取路径部分（去除盘符）
        path_parts = path_obj.as_posix().split('/')[1:]  # 跳过盘符

        # 构建WSL路径
        wsl_path = f"/mnt/{drive}/" + '/'.join(path_parts)

        return wsl_path

    @staticmethod
    def wsl_to_windows(wsl_path: str) -> str:
        """
        将WSL路径转换为Windows路径
        /mnt/e/tmp/file.jpg -> E:\\tmp\\file.jpg
        """
        # 匹配 /mnt/盘符/路径
        match = re.match(r'^/mnt/([a-z])/(.*)$', wsl_path)
        if not match:
            raise ValueError(f"Invalid WSL path: {wsl_path}")

        drive, path = match.groups()
        windows_path = f"{drive.upper()}:\\{path.replace('/', '\\')}"

        return windows_path

    @staticmethod
    def validate_path(path: str) -> bool:
        """验证路径格式是否合法"""
        # Windows路径
        if re.match(r'^[A-Za-z]:\\', path):
            return True
        # WSL路径
        if re.match(r'^/mnt/[a-z]/', path):
            return True
        return False
```

**测试用例**:
- `E:\tmp\1.jpg` → `/mnt/e/tmp/1.jpg`
- `C:\Users\用户\Desktop\test.png` → `/mnt/c/Users/用户/Desktop/test.png`
- `D:\Program Files\app.jpg` → `/mnt/d/Program Files/app.jpg`

**边界情况处理**:
- 空格：保留（WSL支持带空格路径）
- 中文字符：保留（WSL支持UTF-8）
- 特殊字符：需转义（如`?`, `*`等在WSL中有特殊含义）

---

## 7. 性能优化策略

### 7.1 快捷键响应（< 200ms）
- 使用独立线程监听快捷键
- 快捷键回调通过Qt信号槽触发GUI操作（线程安全）
- 遮罩窗口提前创建并隐藏，触发时直接显示

### 7.2 截图处理（< 500ms）
- mss截图本身已高效（~10ms）
- 路径转换为纯字符串操作（~1ms）
- 剪贴板操作使用pywin32异步API
- 文件保存使用线程池避免阻塞

### 7.3 内存优化（< 50MB）
- 截图后立即释放Image对象
- 避免缓存大量历史截图
- 使用Qt的资源管理机制

---

## 8. 测试策略

### 8.1 单元测试
- **路径转换**: 测试各种路径格式（正常、边界、异常）
- **配置管理**: 测试加载、保存、验证、默认值
- **剪贴板**: Mock Windows API测试
- **文件管理**: 测试保存、清理、目录创建

### 8.2 集成测试
- **截图工作流**: 快捷键→截图→保存→转换→剪贴板
- **设置工作流**: 修改配置→保存→立即生效

### 8.3 测试工具
- **pytest**: 测试运行器
- **pytest-cov**: 覆盖率检查（目标 > 70%）
- **pytest-mock**: Mock外部依赖（Windows API）
- **pytest-qt**: Qt应用测试支持

---

## 9. 打包和发布

### Decision: PyInstaller

```bash
pyinstaller --name="WSL截图工具" \
    --onefile \
    --windowed \
    --icon=resources/icons/app.ico \
    --add-data="resources;resources" \
    --add-data="config;config" \
    --manifest=app.manifest \
    src/main.py
```

**打包策略**:
- `--onefile`: 单文件可执行程序
- `--windowed`: 无控制台窗口
- `--icon`: 自定义图标
- `--manifest`: 嵌入UAC清单
- 包含资源文件和默认配置

**发布方式**:
1. GitHub Releases发布.exe文件
2. 可选：使用Inno Setup创建安装程序

---

## 10. 依赖版本确定

### Production Dependencies (requirements.txt)
```
PyQt5>=5.15.0,<6.0.0
Pillow>=10.0.0,<11.0.0
mss>=9.0.0,<10.0.0
pywin32>=305,<400
pynput>=1.7.6,<2.0.0
win10toast>=0.9,<1.0  # Windows通知
```

### Development Dependencies (requirements-dev.txt)
```
pytest>=7.4.0,<8.0.0
pytest-cov>=4.1.0,<5.0.0
pytest-qt>=4.2.0,<5.0.0
pytest-mock>=3.12.0,<4.0.0
black>=23.0.0,<24.0.0
flake8>=6.0.0,<7.0.0
mypy>=1.5.0,<2.0.0
PyInstaller>=5.13.0,<6.0.0
```

**版本策略**:
- 固定主版本号，允许次版本和补丁版本更新
- 确保依赖库活跃维护且兼容Python 3.9+

---

## 研究结论

所有技术决策已明确，无悬而未决的问题。技术栈选择符合项目宪章的所有原则：
- ✅ 模块化：各技术组件职责清晰
- ✅ 用户体验：性能指标可达成
- ✅ 测试支持：完善的测试工具链
- ✅ 跨平台：所有依赖支持跨平台
- ✅ 简洁性：使用成熟库，避免重复造轮子
- ✅ 安全隐私：本地化处理，无网络传输

可以继续Phase 1设计阶段。
