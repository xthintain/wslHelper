# 手动测试指南

由于快捷键 `Ctrl+Alt+S` 无法触发，我创建了两个测试脚本来帮助诊断问题。

## 测试1: 快捷键检测测试（命令行）

**文件**: `test_hotkey_detection.py`

**功能**: 测试 pynput 是否能检测到 `Ctrl+Alt+S` 和 `Ctrl+Alt+A` 快捷键

**运行方法**:
```bash
# 在项目根目录下运行
.venv\Scripts\python.exe test_hotkey_detection.py
```

**操作步骤**:
1. 运行脚本后，会显示 "Listener started"
2. 按下 `Ctrl+Alt+S` 或 `Ctrl+Alt+A`
3. 如果检测到，会显示 "SUCCESS! Detected: Ctrl+Alt+S"
4. 如果60秒内未检测到，会显示 "Test FAILED"

**预期结果**:
- 如果显示 "SUCCESS"，说明 pynput 可以工作，问题在主程序的其他地方
- 如果显示 "FAILED"，说明 pynput 在你的系统上无法检测这些快捷键

---

## 测试2: 手动截图测试（GUI）

**文件**: `test_manual_screenshot.py`

**功能**: 提供一个带按钮的窗口，点击按钮即可触发截图（无需快捷键）

**运行方法**:
```bash
# 在项目根目录下运行
.venv\Scripts\python.exe test_manual_screenshot.py
```

**操作步骤**:
1. 运行脚本后，会弹出一个窗口
2. 点击 "📷 点击触发截图" 按钮
3. 用鼠标拖拽选择截图区域
4. 释放鼠标后，截图会自动保存
5. 命令行会显示截图的路径信息

**预期结果**:
- 截图功能正常工作
- 能看到 Windows 路径和 WSL 路径
- WSL 路径会被复制到剪贴板

---

## 推荐的测试顺序

### 第一步: 测试快捷键检测
```bash
.venv\Scripts\python.exe test_hotkey_detection.py
```
- 按 `Ctrl+Alt+S` 测试
- 如果失败，尝试按 `Ctrl+Alt+A` 测试
- 如果两个都失败，说明 pynput 在你的系统上有问题

### 第二步: 测试截图功能
```bash
.venv\Scripts\python.exe test_manual_screenshot.py
```
- 点击按钮触发截图
- 验证截图功能是否正常

---

## 可能的问题和解决方案

### 问题1: 快捷键检测失败

**可能原因**:
1. pynput 在 Windows 11 上有兼容性问题
2. 系统安全软件拦截了键盘监听
3. 其他程序占用了这些快捷键

**解决方案**:
1. **尝试其他快捷键**:
   - 修改 `config/config.json` 中的 `hotkey` 为:
     - `"ctrl+alt+f9"` (功能键组合)
     - `"f9"` (单功能键)
     - `"ctrl+alt+x"` (其他字母)

2. **使用替代方案**:
   - 改用 `keyboard` 库替代 `pynput`
   - 改用 Windows API (`win32api`) 注册热键

3. **以管理员权限运行**:
   ```bash
   # 右键点击 cmd，选择"以管理员身份运行"，然后运行程序
   ```

### 问题2: 截图功能正常，但快捷键无效

**说明**: 如果手动测试中截图功能正常，说明程序本身没问题，只是快捷键监听有问题。

**临时解决方案**: 可以修改程序，添加托盘菜单中的"截图"选项，通过点击菜单触发截图。

---

## 下一步行动

请运行测试并告诉我结果：

1. ✅ 测试1成功 / ❌ 测试1失败
2. ✅ 测试2成功 / ❌ 测试2失败

根据测试结果，我会提供针对性的解决方案。

---

**注意**: 运行测试时，请确保没有其他 WSLScreenshot 程序在运行。可以用以下命令检查：
```bash
tasklist | findstr WSLScreenshot
```

如果有进程在运行，先结束它们：
```bash
taskkill /F /IM WSLScreenshot.exe
```
