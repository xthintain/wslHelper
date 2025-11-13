# Module Contract: Path Converter

**Module**: `src/core/path_converter.py`
**Purpose**: Windows路径与WSL路径的双向转换
**Dependencies**: `pathlib`, `re`

## Public Interface

### Class: PathConverter

静态方法类，提供路径转换功能。

#### Method: `windows_to_wsl(windows_path: str) -> str`

**Purpose**: 将Windows格式路径转换为WSL格式

**Parameters**:
- `windows_path` (str): Windows路径，如 `E:\tmp\file.jpg`

**Returns**:
- `str`: WSL路径，如 `/mnt/e/tmp/file.jpg`

**Raises**:
- `ValueError`: 如果输入路径格式无效

**Examples**:
```python
PathConverter.windows_to_wsl("E:\\tmp\\screenshot.jpg")
# Returns: "/mnt/e/tmp/screenshot.jpg"

PathConverter.windows_to_wsl("C:\\Users\\用户\\文件.png")
# Returns: "/mnt/c/Users/用户/文件.png"
```

#### Method: `wsl_to_windows(wsl_path: str) -> str`

**Purpose**: 将WSL格式路径转换为Windows格式

**Parameters**:
- `wsl_path` (str): WSL路径，如 `/mnt/e/tmp/file.jpg`

**Returns**:
- `str`: Windows路径，如 `E:\tmp\file.jpg`

**Raises**:
- `ValueError`: 如果输入路径格式无效

#### Method: `validate_path(path: str) -> bool`

**Purpose**: 验证路径格式是否合法（Windows或WSL）

**Parameters**:
- `path` (str): 待验证的路径

**Returns**:
- `bool`: True表示合法，False表示非法

## Contract Tests

```python
def test_windows_to_wsl_basic():
    assert PathConverter.windows_to_wsl("E:\\tmp\\file.jpg") == "/mnt/e/tmp/file.jpg"

def test_windows_to_wsl_with_spaces():
    assert PathConverter.windows_to_wsl("E:\\my folder\\file.jpg") == "/mnt/e/my folder/file.jpg"

def test_windows_to_wsl_with_chinese():
    assert PathConverter.windows_to_wsl("E:\\我的文件\\图片.jpg") == "/mnt/e/我的文件/图片.jpg"

def test_wsl_to_windows_basic():
    assert PathConverter.wsl_to_windows("/mnt/e/tmp/file.jpg") == "E:\\tmp\\file.jpg"

def test_invalid_path_raises_error():
    with pytest.raises(ValueError):
        PathConverter.windows_to_wsl("/invalid/path")
```
