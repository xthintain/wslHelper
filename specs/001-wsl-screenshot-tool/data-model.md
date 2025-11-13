# Data Model: WSL截图工具

**Feature**: WSL截图工具
**Date**: 2025-11-12
**Purpose**: 定义系统的数据模型和实体关系

## 核心实体

### 1. Screenshot (截图)

表示一次截图操作的结果。

**属性**:
| 字段 | 类型 | 描述 | 验证规则 |
|------|------|------|----------|
| `file_path` | `str` | Windows格式的文件路径 | 必填，符合Windows路径格式 |
| `wsl_path` | `str` | WSL格式的文件路径 | 必填，格式 `/mnt/盘符/...` |
| `filename` | `str` | 文件名（含扩展名） | 必填，格式 `screenshot_YYYYMMDD_HHMMSS.{ext}` |
| `created_at` | `datetime` | 创建时间戳 | 必填，ISO 8601格式 |
| `format` | `str` | 图片格式 | 必填，枚举值: `"jpg"`, `"png"` |
| `file_size` | `int` | 文件大小（字节） | 必填，> 0 |
| `width` | `int` | 图片宽度（像素） | 可选 |
| `height` | `int` | 图片高度（像素） | 可选 |

**Python类定义**:
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

@dataclass
class Screenshot:
    file_path: str
    wsl_path: str
    filename: str
    created_at: datetime
    format: Literal["jpg", "png"]
    file_size: int
    width: int | None = None
    height: int | None = None

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "wsl_path": self.wsl_path,
            "filename": self.filename,
            "created_at": self.created_at.isoformat(),
            "format": self.format,
            "file_size": self.file_size,
            "width": self.width,
            "height": self.height,
        }
```

---

### 2. Configuration (配置)

存储用户的偏好设置。

**属性**:
| 字段 | 类型 | 描述 | 默认值 | 验证规则 |
|------|------|------|--------|----------|
| `hotkey` | `str` | 快捷键组合 | `"ctrl+alt+a"` | 必填，格式如 `"ctrl+alt+a"` |
| `save_directory` | `str` | 截图保存目录（Windows路径） | `"E:\\tmp\\screenshots"` | 必填，绝对路径 |
| `image_format` | `str` | 图片格式 | `"jpg"` | 枚举值: `"jpg"`, `"png"` |
| `image_quality` | `int` | 图片质量（JPG专用） | `90` | 范围: 1-100 |
| `auto_startup` | `bool` | 开机自启动 | `true` | boolean |
| `show_notification` | `bool` | 显示通知 | `true` | boolean |
| `auto_cleanup` | `bool` | 自动清理临时文件 | `false` | boolean |
| `cleanup_days` | `int` | 清理天数阈值 | `7` | > 0，仅当`auto_cleanup=true`时有效 |

**Python类定义**:
```python
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class Configuration:
    hotkey: str = "ctrl+alt+a"
    save_directory: str = "E:\\tmp\\screenshots"
    image_format: Literal["jpg", "png"] = "jpg"
    image_quality: int = 90
    auto_startup: bool = True
    show_notification: bool = True
    auto_cleanup: bool = False
    cleanup_days: int = 7

    def validate(self) -> list[str]:
        """验证配置，返回错误列表"""
        errors = []
        if not self.hotkey:
            errors.append("hotkey不能为空")
        if not self.save_directory:
            errors.append("save_directory不能为空")
        if not (1 <= self.image_quality <= 100):
            errors.append("image_quality必须在1-100之间")
        if self.cleanup_days <= 0:
            errors.append("cleanup_days必须大于0")
        return errors

    def to_dict(self) -> dict:
        return {
            "hotkey": self.hotkey,
            "save_directory": self.save_directory,
            "image_format": self.image_format,
            "image_quality": self.image_quality,
            "auto_startup": self.auto_startup,
            "show_notification": self.show_notification,
            "auto_cleanup": self.auto_cleanup,
            "cleanup_days": self.cleanup_days,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Configuration":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
```

**JSON Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "hotkey": {"type": "string"},
    "save_directory": {"type": "string"},
    "image_format": {"type": "string", "enum": ["jpg", "png"]},
    "image_quality": {"type": "integer", "minimum": 1, "maximum": 100},
    "auto_startup": {"type": "boolean"},
    "show_notification": {"type": "boolean"},
    "auto_cleanup": {"type": "boolean"},
    "cleanup_days": {"type": "integer", "minimum": 1}
  },
  "required": ["hotkey", "save_directory", "image_format"]
}
```

---

### 3. LogEntry (日志条目)

记录系统操作和错误日志。

**属性**:
| 字段 | 类型 | 描述 | 验证规则 |
|------|------|------|----------|
| `timestamp` | `datetime` | 时间戳 | 必填，ISO 8601格式 |
| `level` | `str` | 日志级别 | 枚举: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"` |
| `message` | `str` | 日志消息 | 必填，非空 |
| `module` | `str` | 模块名称 | 可选 |
| `context` | `dict` | 上下文信息（额外数据） | 可选 |

**Python类定义**:
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

@dataclass
class LogEntry:
    timestamp: datetime
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]
    message: str
    module: str | None = None
    context: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "module": self.module,
            "context": self.context,
        }

    def __str__(self) -> str:
        module_str = f"[{self.module}] " if self.module else ""
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} {self.level} {module_str}{self.message}"
```

---

## 数据流

### 截图工作流数据流
```
用户按下快捷键
  ↓
HotkeyManager 触发回调
  ↓
ScreenshotCapture 截取屏幕 → 生成 Image 对象
  ↓
FileManager 保存图片 → 生成 Screenshot 实体
  ↓
PathConverter 转换路径 → 更新 Screenshot.wsl_path
  ↓
ClipboardManager 复制 wsl_path 到剪贴板
  ↓
NotificationManager 显示通知（包含 wsl_path）
  ↓
LogEntry 记录操作（INFO级别）
```

### 配置变更数据流
```
用户打开设置界面
  ↓
加载当前 Configuration → 显示在UI
  ↓
用户修改配置项
  ↓
ConfigManager 验证配置 → Configuration.validate()
  ↓
如果有错误 → 显示错误提示，阻止保存
  ↓
如果无错误 → ConfigManager.save_config()
  ↓
写入 config.json（Configuration.to_dict()）
  ↓
触发配置重载事件 → 各模块响应更新
  ↓
LogEntry 记录配置更改（INFO级别）
```

---

## 持久化策略

### 1. 配置文件 (config.json)
- **位置**: `%APPDATA%\WSLScreenshot\config.json`
- **格式**: JSON
- **更新时机**: 用户修改设置时立即保存
- **备份**: 保存前备份为 `config.json.bak`

### 2. 日志文件 (app.log)
- **位置**: `%APPDATA%\WSLScreenshot\logs\app.log`
- **格式**: 纯文本，每行一条日志
- **轮转策略**:
  - 单个文件最大10MB
  - 保留最近5个日志文件
  - 命名格式: `app.log`, `app.log.1`, ..., `app.log.5`

### 3. 截图文件
- **位置**: 用户配置的 `save_directory`（默认 `E:\tmp\screenshots\`）
- **命名**: `screenshot_YYYYMMDD_HHMMSS.{ext}`
- **清理策略**:
  - 如果 `auto_cleanup=true`，自动删除超过 `cleanup_days` 天的文件
  - 清理操作在程序启动时和每日定时执行

---

## 约束和验证规则

### Configuration验证
1. `hotkey`: 非空，符合 `pynput` 快捷键格式
2. `save_directory`: 绝对路径，目录可访问（自动创建如不存在）
3. `image_quality`: 1-100整数
4. `cleanup_days`: 正整数

### Screenshot验证
1. `file_path`: 文件实际存在于文件系统
2. `wsl_path`: 格式 `/mnt/[a-z]/.*`
3. `filename`: 匹配时间戳格式
4. `file_size`: 大于0

### LogEntry验证
1. `level`: 必须是四种级别之一
2. `message`: 非空字符串

---

## 状态转换

### Screenshot生命周期
```
[创建] → [已保存] → [已复制到剪贴板] → [已通知]
                 ↓
              [已清理]（如启用auto_cleanup）
```

### Configuration状态
```
[加载] → [验证中] → [有效]   → [已保存] → [已应用]
                 ↓
              [无效] → [显示错误]
```

---

## 扩展性考虑

### 未来可能添加的实体

#### ScreenshotHistory (截图历史)
- 记录所有截图操作历史
- 支持搜索和过滤
- 提供历史管理界面

#### UserPreset (用户预设)
- 保存多套配置预设
- 快速切换不同工作场景

#### HotkeyConflict (快捷键冲突)
- 检测并记录快捷键冲突
- 提供冲突解决建议

这些扩展在v1.0中不实现，符合YAGNI原则。
