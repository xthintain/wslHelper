# Tasks: WSL截图工具

**Input**: Design documents from `specs/001-wsl-screenshot-tool/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, research.md

**Tests**: 项目规格说明要求测试覆盖率 > 70%和TDD方法，因此包含测试任务。

**Organization**: 任务按用户故事组织，每个故事可独立实施和测试。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行运行（不同文件，无依赖）
- **[Story]**: 此任务属于哪个用户故事（US1, US2, US3）
- 包含精确文件路径

## Phase 1: Setup（共享基础设施）

**Purpose**: 项目初始化和基本结构

- [X] T001 Create project directory structure per plan.md specifications
- [X] T002 Initialize Python project with virtual environment at project root
- [X] T003 [P] Create requirements.txt with production dependencies (PyQt5>=5.15.0, Pillow>=10.0.0, mss>=9.0.0, pywin32>=305, pynput>=1.7.6)
- [X] T004 [P] Create requirements-dev.txt with development dependencies (pytest>=7.4.0, pytest-cov>=4.1.0, pytest-qt>=4.2.0, black>=23.0.0, flake8>=6.0.0, mypy>=1.5.0)
- [X] T005 [P] Create setup.py installation script at project root
- [X] T006 [P] Create pytest.ini configuration file at project root
- [X] T007 [P] Create .gitignore file with Python/PyQt5 patterns at project root
- [X] T008 [P] Create app.manifest file for Windows UAC at project root
- [X] T009 [P] Create default config.json in config/ directory
- [X] T010 [P] Create config.schema.json JSON Schema in config/ directory

---

## Phase 2: Foundational（阻塞性前置条件）

**Purpose**: 所有用户故事依赖的核心基础设施，必须在任何用户故事开始前完成

**⚠️ CRITICAL**: 此阶段完成前，用户故事工作不能开始

- [X] T011 Create src/__init__.py package initializer
- [X] T012 Create src/core/__init__.py package initializer
- [X] T013 Create src/gui/__init__.py package initializer
- [X] T014 Create src/utils/__init__.py package initializer
- [X] T015 Create src/system/__init__.py package initializer
- [X] T016 Implement logger module in src/utils/logger.py with 4-level logging (DEBUG/INFO/WARNING/ERROR) and file rotation
- [X] T017 Implement configuration data model in src/utils/config.py with Configuration dataclass and validation
- [X] T018 Implement config file I/O in src/utils/config.py with load_config() and save_config() methods
- [X] T019 Create main application entry point in src/main.py with privilege check and QApplication initialization
- [X] T020 Implement singleton application class in src/app.py with lifecycle management

**Checkpoint**: 基础设施就绪 - 用户故事实施现在可以并行开始

---

## Phase 3: User Story 1 - 快速截图并获取WSL路径 (Priority: P1) 🎯 MVP

**Goal**: 通过快捷键触发截图，选择区域，自动保存并将WSL路径复制到剪贴板

**Independent Test**: 按下Ctrl+Alt+A，拖拽选择区域，释放鼠标后，剪贴板包含类似 `/mnt/e/tmp/screenshot_20251112_143020.jpg` 的WSL路径，该路径在WSL终端中可用

### Tests for User Story 1 ⚠️

> **NOTE: 先写测试，确保FAIL，再实现功能**

- [X] T021 [P] [US1] Write unit tests for PathConverter in tests/unit/test_path_converter.py (windows_to_wsl, wsl_to_windows, validate_path, edge cases)
- [X] T022 [P] [US1] Write unit tests for ClipboardManager in tests/unit/test_clipboard.py (set_text, get_text with mocks)
- [X] T023 [P] [US1] Write unit tests for FileManager in tests/unit/test_file_manager.py (save_screenshot, generate_filename, create_directory)
- [X] T024 [P] [US1] Write integration test for complete screenshot workflow in tests/integration/test_screenshot_workflow.py

### Implementation for User Story 1

- [X] T025 [P] [US1] Implement PathConverter class in src/core/path_converter.py with windows_to_wsl() and wsl_to_windows() static methods
- [X] T026 [P] [US1] Implement ClipboardManager class in src/core/clipboard.py with set_text() and get_text() using pywin32
- [X] T027 [P] [US1] Implement FileManager class in src/utils/file_manager.py with save_screenshot(), generate_filename(), create_directory()
- [X] T028 [P] [US1] Create Screenshot dataclass in src/core/screenshot.py with file_path, wsl_path, filename, created_at, format, file_size attributes
- [X] T029 [US1] Implement ScreenshotCapture class in src/core/screenshot.py with capture_screen() and capture_region() using mss library
- [X] T030 [US1] Implement HotkeyManager class in src/core/hotkey.py with register_hotkey(), unregister_hotkey(), start_listening() using pynput
- [X] T031 [US1] Implement ScreenshotOverlay widget in src/gui/overlay.py with full-screen transparent window, mouse events, and region selection
- [X] T032 [US1] Implement ScreenshotSelector in src/gui/selector.py with drag selection logic and ESC cancel support
- [X] T033 [US1] Implement NotificationManager in src/utils/notification.py with Windows Toast notifications using win10toast
- [X] T034 [US1] Integrate hotkey → overlay → capture → save → convert → clipboard → notify workflow in src/app.py
- [X] T035 [US1] Add error handling for disk space, permissions, and invalid paths in FileManager
- [X] T036 [US1] Add logging for key operations (screenshot taken, file saved, path converted) using logger module

**Checkpoint**: User Story 1完全功能化且可独立测试

---

## Phase 4: User Story 2 - 管理和配置截图设置 (Priority: P2)

**Goal**: 通过设置界面自定义快捷键、保存路径、图片格式、质量等

**Independent Test**: 右键点击托盘图标→选择"设置"→修改保存路径为D:\screenshots→保存→下次截图保存到新路径，WSL路径更新为 /mnt/d/screenshots/...

### Tests for User Story 2 ⚠️

- [X] T037 [P] [US2] Write unit tests for Configuration validation in tests/unit/test_config.py (validate(), to_dict(), from_dict())
- [X] T038 [P] [US2] Write integration test for settings workflow in tests/integration/test_settings_workflow.py

### Implementation for User Story 2

- [X] T039 [P] [US2] Create SystemTray class in src/gui/tray.py with QSystemTrayIcon and right-click menu (Settings, About, Exit)
- [X] T040 [US2] Design settings UI using Qt Designer and save to resources/ui/settings.ui
- [X] T041 [US2] Implement SettingsWindow class in src/gui/settings.py loading UI from settings.ui file
- [X] T042 [US2] Add form fields for hotkey, save_directory, image_format, image_quality in SettingsWindow
- [X] T043 [US2] Implement save button handler in SettingsWindow with Configuration validation
- [X] T044 [US2] Implement config reload trigger in src/app.py to apply new settings without restart
- [X] T045 [US2] Add hotkey re-registration logic in HotkeyManager when config changes
- [X] T046 [US2] Add directory creation validation in FileManager when save_directory changes
- [X] T047 [US2] Add error dialogs for invalid configuration values in SettingsWindow
- [X] T048 [US2] Add logging for configuration changes using logger module

**Checkpoint**: User Story 1和2现在都可独立工作

---

## Phase 5: User Story 3 - 开机自动启动并后台运行 (Priority: P3)

**Goal**: 工具在系统启动时自动运行，驻留后台，低资源占用

**Independent Test**: 在设置中启用"开机自启动"→重启Windows→工具自动启动，托盘图标出现，快捷键可用

### Tests for User Story 3 ⚠️

- [X] T049 [P] [US3] Write unit tests for StartupManager in tests/unit/test_startup.py (add_to_startup, remove_from_startup, is_in_startup)
- [X] T050 [P] [US3] Write unit tests for PrivilegeManager in tests/unit/test_privilege.py (check_admin, request_admin)

### Implementation for User Story 3

- [X] T051 [P] [US3] Implement StartupManager class in src/system/startup.py with add_to_startup(), remove_from_startup(), is_in_startup() using Windows Registry
- [X] T052 [P] [US3] Implement PrivilegeManager class in src/system/privilege.py with check_admin() and request_admin() using pywin32
- [X] T053 [US3] Add UAC privilege check in src/main.py with admin re-launch if needed
- [X] T054 [US3] Add "开机自启动" checkbox in SettingsWindow (src/gui/settings.py)
- [X] T055 [US3] Implement startup toggle handler in SettingsWindow calling StartupManager
- [X] T056 [US3] Add tray icon to SystemTray with minimize-to-tray logic in src/gui/tray.py
- [X] T057 [US3] Implement memory and CPU monitoring in src/utils/performance.py (optional, for logging)
- [X] T058 [US3] Add application startup logging with privilege status
- [X] T059 [US3] Add graceful shutdown handling in src/app.py (cleanup resources)

**Checkpoint**: 所有用户故事现在独立功能化

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 影响多个用户故事的改进

- [X] T060 [P] Add multi-monitor support in ScreenshotCapture using mss.monitors
- [X] T061 [P] Add high-DPI scaling support in src/main.py with QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
- [X] T062 [P] Implement auto-cleanup feature in src/utils/file_manager.py (cleanup_old_screenshots by days/count)
- [ ] T063 [P] Add icon resources in resources/icons/ (app.ico, tray.ico, tray_disabled.ico)
- [ ] T064 [P] Create app icon and tray icons (use existing or design new)
- [X] T065 [P] Write user documentation in docs/README.md
- [ ] T066 [P] Write installation guide in docs/INSTALL.md
- [ ] T067 [P] Write user guide in docs/USER_GUIDE.md
- [X] T068 Run full test suite and ensure >70% code coverage
- [X] T069 Run Black formatter on all Python files
- [X] T070 Run Flake8 linter and fix all warnings
- [X] T071 Run mypy type checker on src/ directory
- [X] T072 Create PyInstaller spec file for packaging
- [X] T073 Test packaged .exe on clean Windows 10/11 environment
- [X] T074 Validate quickstart.md instructions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 无依赖 - 立即开始
- **Foundational (Phase 2)**: 依赖Setup完成 - 阻塞所有用户故事
- **User Stories (Phase 3+)**: 全部依赖Foundational阶段完成
  - 用户故事可并行进行（如有人力）
  - 或按优先级顺序执行（P1 → P2 → P3）
- **Polish (Phase 6)**: 依赖所需的用户故事完成

### User Story Dependencies

- **User Story 1 (P1)**: Foundational完成后可开始 - 无其他用户故事依赖
- **User Story 2 (P2)**: Foundational完成后可开始 - 与US1集成但可独立测试
- **User Story 3 (P3)**: Foundational完成后可开始 - 与US1/US2集成但可独立测试

### Within Each User Story

- 测试必须先写并FAIL，再实现功能
- Models before services
- Services before GUI
- 核心实现before集成
- 故事完成before进入下一优先级

### Parallel Opportunities

- Setup阶段所有标记[P]的任务可并行
- Foundational阶段T011-T015（package initializers）可并行
- Foundational完成后，所有用户故事可并行开始（如团队容量允许）
- 每个用户故事内所有标记[P]的测试可并行
- 每个用户故事内所有标记[P]的models/services可并行
- 不同用户故事可由不同团队成员并行工作

---

## Parallel Example: User Story 1

```bash
# 一起启动User Story 1的所有测试：
Task: "Write unit tests for PathConverter in tests/unit/test_path_converter.py"
Task: "Write unit tests for ClipboardManager in tests/unit/test_clipboard.py"
Task: "Write unit tests for FileManager in tests/unit/test_file_manager.py"
Task: "Write integration test for complete screenshot workflow in tests/integration/test_screenshot_workflow.py"

# 一起启动User Story 1的所有并行models/services：
Task: "Implement PathConverter class in src/core/path_converter.py"
Task: "Implement ClipboardManager class in src/core/clipboard.py"
Task: "Implement FileManager class in src/utils/file_manager.py"
Task: "Create Screenshot dataclass in src/core/screenshot.py"
```

---

## Implementation Strategy

### MVP First (仅User Story 1)

1. 完成Phase 1: Setup
2. 完成Phase 2: Foundational（关键 - 阻塞所有故事）
3. 完成Phase 3: User Story 1
4. **STOP并验证**: 独立测试User Story 1
5. 如准备好则部署/演示

### Incremental Delivery

1. 完成Setup + Foundational → 基础就绪
2. 添加User Story 1 → 独立测试 → 部署/演示（MVP！）
3. 添加User Story 2 → 独立测试 → 部署/演示
4. 添加User Story 3 → 独立测试 → 部署/演示
5. 每个故事增加价值而不破坏之前的故事

### Parallel Team Strategy

多开发者情况：

1. 团队一起完成Setup + Foundational
2. Foundational完成后：
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. 故事独立完成并集成

---

## Notes

- [P]任务 = 不同文件，无依赖
- [Story]标签将任务映射到特定用户故事以追溯
- 每个用户故事应可独立完成和测试
- 实现前验证测试失败
- 每个任务或逻辑组后提交
- 在任何checkpoint停止以独立验证故事
- 避免：模糊任务、同文件冲突、破坏独立性的跨故事依赖
