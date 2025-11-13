# 快捷键更改说明

## 更改历史

### 第一次更改（2025-11-12）
**原快捷键**: `Ctrl+Alt+A`
**新快捷键**: `Ctrl+Shift+X`
**更改原因**: 系统中其他截图工具（如QQ、微信等）已占用 `Ctrl+Alt+A` 快捷键

### 第二次更改（2025-11-12）
**原快捷键**: `Ctrl+Shift+X`
**新快捷键**: **`Ctrl+Alt+S`**
**更改原因**: **技术限制** - pynput 库在 Windows 上对 Shift 键组合有已知缺陷，无法可靠检测 `Ctrl+Shift+X` 这样的组合键

## 当前快捷键

**`Ctrl+Alt+S`** (S = Screenshot)

## 为什么选择 Ctrl+Alt+S

- ✅ 不与常见软件冲突
- ✅ 容易按（三个键都在键盘左侧）
- ✅ **避免使用 Shift 键**（绕过 pynput 在 Windows 上的技术限制）
- ✅ S 代表 Screenshot，语义清晰

## 其他常见截图工具的快捷键（避免冲突）

| 软件 | 快捷键 |
|------|--------|
| QQ截图 | Ctrl+Alt+A |
| 微信截图 | Alt+A |
| Windows截图 | Win+Shift+S |
| Snipaste | F1 |
| **WSL Screenshot Tool** | **Ctrl+Alt+S** ✅ |

## 如何使用

1. **运行程序**: 双击 `WSLScreenshot.exe`
2. **查看托盘**: 程序启动后会在系统托盘显示图标
3. **截图**: 按 `Ctrl+Alt+S` 快捷键
4. **选择区域**: 鼠标拖拽选择截图区域
5. **完成**: 自动保存并复制WSL路径到剪贴板

## 自定义快捷键

如果您想使用其他快捷键：

1. 右键点击托盘图标
2. 选择"设置"
3. 在"快捷键"输入框中输入您想要的组合键
   - 格式：`ctrl+shift+a`, `ctrl+alt+x`, `shift+f1` 等
4. 点击"保存"

## 已更新的文件

- ✅ `config/config.json` - 默认配置
- ✅ `src/utils/config.py` - 代码默认值
- ✅ `README.md` - 文档说明
- ✅ `dist/WSLScreenshot.exe` - 打包程序

## 验证新快捷键

```bash
# 1. 运行程序
dist/WSLScreenshot.exe

# 2. 按 Ctrl+Alt+S
# 应该出现截图选择界面
```

## 技术说明

### 为什么不能使用 Shift 键组合？

本项目使用 pynput 库来监听全局快捷键。根据 [pynput 官方文档](https://pynput.readthedocs.io/en/latest/limitations.html)，**pynput 在 Windows 平台上对 Shift 键组合有已知限制**：

> "key press events will not be continuously emitted as when holding down a physical key, and certain key sequences, such as shift pressed while pressing arrow keys, do not work as expected."

这意味着在 Windows 上：
- ❌ `Ctrl+Shift+X` - 无法可靠检测
- ❌ `Shift+F1` - 无法可靠检测
- ✅ `Ctrl+Alt+S` - 可以正常工作
- ✅ `Ctrl+Alt+A` - 可以正常工作（但被其他软件占用）
- ✅ `F9`, `F10` - 可以正常工作

### 推荐的替代快捷键

如果 `Ctrl+Alt+S` 不适合您，建议使用以下组合（避免 Shift 键）：

- `Ctrl+Alt+F9` - 功能键组合
- `Ctrl+Alt+X` - 简单字母组合
- `Ctrl+Alt+W` - W = Window/WSL
- `F9` - 单键（如果没有其他软件占用）

**重要**: 避免使用任何涉及 Shift 键的组合！

---

**更新日期**: 2025-11-12
**版本**: 1.0.1
