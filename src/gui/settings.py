"""Settings window for application configuration.

Provides GUI for modifying application settings including hotkey,
save directory, image format, and other options.
"""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QLabel,
)
from PyQt5.QtCore import pyqtSignal, Qt
from typing import Optional

from src.utils.config import Configuration, ConfigManager
from src.utils.logger import get_logger


class SettingsWindow(QDialog):
    """Settings dialog window."""

    # Signal emitted when configuration is saved
    config_saved = pyqtSignal(Configuration)

    def __init__(self, config: Configuration, parent=None):
        """Initialize settings window.

        Args:
            config: Current configuration
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = get_logger()
        self.config = (
            config.copy()
            if hasattr(config, "copy")
            else Configuration.from_dict(config.to_dict())
        )

        self._setup_ui()
        self._load_config_to_ui()

        self.logger.debug("Settings window initialized")

    def _setup_ui(self) -> None:
        """Setup user interface."""
        self.setWindowTitle("设置 - WSL Screenshot Tool")
        self.setModal(True)
        self.setMinimumWidth(500)

        # Main layout
        main_layout = QVBoxLayout()

        # Create form groups
        main_layout.addWidget(self._create_screenshot_group())
        main_layout.addWidget(self._create_behavior_group())
        main_layout.addWidget(self._create_cleanup_group())

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self._on_save_clicked)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _create_screenshot_group(self) -> QGroupBox:
        """Create screenshot settings group.

        Returns:
            QGroupBox with screenshot settings
        """
        group = QGroupBox("截图设置")
        layout = QFormLayout()

        # Hotkey
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setPlaceholderText("例如: ctrl+alt+a")
        layout.addRow("快捷键:", self.hotkey_edit)

        # Save directory
        dir_layout = QHBoxLayout()
        self.save_dir_edit = QLineEdit()
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self._on_browse_directory)
        dir_layout.addWidget(self.save_dir_edit)
        dir_layout.addWidget(browse_button)
        layout.addRow("保存目录:", dir_layout)

        # Image format
        self.format_combo = QComboBox()
        self.format_combo.addItems(["jpg", "png"])
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        layout.addRow("图片格式:", self.format_combo)

        # Image quality (only for JPG)
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setSuffix("%")
        layout.addRow("图片质量:", self.quality_spin)

        group.setLayout(layout)
        return group

    def _create_behavior_group(self) -> QGroupBox:
        """Create behavior settings group.

        Returns:
            QGroupBox with behavior settings
        """
        group = QGroupBox("行为设置")
        layout = QVBoxLayout()

        # Auto startup
        self.auto_startup_check = QCheckBox("开机自动启动")
        self.auto_startup_check.stateChanged.connect(self._on_auto_startup_changed)
        layout.addWidget(self.auto_startup_check)

        # Show notification
        self.show_notification_check = QCheckBox("显示截图成功通知")
        layout.addWidget(self.show_notification_check)

        group.setLayout(layout)
        return group

    def _on_auto_startup_changed(self, state: int) -> None:
        """Handle auto startup checkbox change.

        Args:
            state: Checkbox state
        """
        # Update config immediately to reflect in UI
        self.config.auto_startup = state == Qt.Checked

    def _create_cleanup_group(self) -> QGroupBox:
        """Create cleanup settings group.

        Returns:
            QGroupBox with cleanup settings
        """
        group = QGroupBox("自动清理")
        layout = QFormLayout()

        # Auto cleanup
        self.auto_cleanup_check = QCheckBox("启用自动清理")
        self.auto_cleanup_check.stateChanged.connect(self._on_cleanup_toggled)
        layout.addRow(self.auto_cleanup_check)

        # Cleanup days
        self.cleanup_days_spin = QSpinBox()
        self.cleanup_days_spin.setRange(1, 365)
        self.cleanup_days_spin.setSuffix(" 天")
        layout.addRow("清理超过:", self.cleanup_days_spin)

        group.setLayout(layout)
        return group

    def _load_config_to_ui(self) -> None:
        """Load configuration values into UI fields."""
        self.hotkey_edit.setText(self.config.hotkey)
        self.save_dir_edit.setText(self.config.save_directory)
        self.format_combo.setCurrentText(self.config.image_format)
        self.quality_spin.setValue(self.config.image_quality)
        self.auto_startup_check.setChecked(self.config.auto_startup)
        self.show_notification_check.setChecked(self.config.show_notification)
        self.auto_cleanup_check.setChecked(self.config.auto_cleanup)
        self.cleanup_days_spin.setValue(self.config.cleanup_days)

        # Update quality field visibility
        self._on_format_changed(self.config.image_format)
        self._on_cleanup_toggled(
            Qt.Checked if self.config.auto_cleanup else Qt.Unchecked
        )

    def _on_format_changed(self, format: str) -> None:
        """Handle image format change.

        Args:
            format: Selected image format
        """
        # Quality only applies to JPG
        self.quality_spin.setEnabled(format == "jpg")

    def _on_cleanup_toggled(self, state: int) -> None:
        """Handle auto cleanup checkbox toggle.

        Args:
            state: Checkbox state
        """
        self.cleanup_days_spin.setEnabled(state == Qt.Checked)

    def _on_browse_directory(self) -> None:
        """Handle browse directory button click."""
        directory = QFileDialog.getExistingDirectory(
            self, "选择截图保存目录", self.save_dir_edit.text()
        )

        if directory:
            self.save_dir_edit.setText(directory)
            self.logger.debug(f"Directory selected: {directory}")

    def _on_save_clicked(self) -> None:
        """Handle save button click."""
        # Get values from UI
        self.config.hotkey = self.hotkey_edit.text().strip()
        self.config.save_directory = self.save_dir_edit.text().strip()
        self.config.image_format = self.format_combo.currentText()
        self.config.image_quality = self.quality_spin.value()
        self.config.auto_startup = self.auto_startup_check.isChecked()
        self.config.show_notification = self.show_notification_check.isChecked()
        self.config.auto_cleanup = self.auto_cleanup_check.isChecked()
        self.config.cleanup_days = self.cleanup_days_spin.value()

        # Validate configuration
        errors = self.config.validate()
        if errors:
            # Show validation errors
            error_message = "配置验证失败:\n\n" + "\n".join(
                f"• {err}" for err in errors
            )
            QMessageBox.warning(self, "配置错误", error_message)
            self.logger.warning(f"Configuration validation failed: {errors}")
            return

        try:
            # Save configuration
            ConfigManager.save_config(self.config)
            self.logger.info("Configuration saved successfully")

            # Handle auto-startup setting
            self._update_startup_setting(self.config.auto_startup)

            # Emit signal
            self.config_saved.emit(self.config)

            # Show success message
            QMessageBox.information(self, "保存成功", "配置已保存。新设置将立即生效。")

            # Close dialog
            self.accept()

        except Exception as e:
            # Show error
            QMessageBox.critical(self, "保存失败", f"保存配置时发生错误:\n\n{str(e)}")
            self.logger.error(f"Failed to save configuration: {e}", exc_info=True)

    def _update_startup_setting(self, enable: bool) -> None:
        """Update Windows startup setting.

        Args:
            enable: True to enable auto-startup, False to disable
        """
        from src.system.startup import StartupManager
        import sys

        try:
            if enable:
                # Get application path
                if getattr(sys, "frozen", False):
                    # Running as compiled executable
                    app_path = sys.executable
                else:
                    # Running as script - use python + script path
                    app_path = f'"{sys.executable}" "{sys.argv[0]}"'

                success = StartupManager.add_to_startup(app_path)
                if success:
                    self.logger.info("Auto-startup enabled")
                else:
                    self.logger.warning("Failed to enable auto-startup")
            else:
                success = StartupManager.remove_from_startup()
                if success:
                    self.logger.info("Auto-startup disabled")
                else:
                    self.logger.warning("Failed to disable auto-startup")

        except Exception as e:
            self.logger.error(f"Failed to update startup setting: {e}", exc_info=True)
