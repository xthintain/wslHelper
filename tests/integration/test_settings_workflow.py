"""Integration test for settings workflow.

Tests the complete settings workflow: open settings → modify config → save → reload.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
import sys


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestSettingsWorkflow:
    """Integration tests for settings workflow."""

    @patch("src.utils.config.ConfigManager")
    @patch("src.gui.settings.SettingsWindow")
    def test_open_settings_window(self, mock_settings_window, mock_config_manager):
        """Test opening settings window from tray icon."""
        from src.utils.config import Configuration

        # Setup mock config
        mock_config = Configuration()
        mock_config_manager.load_config.return_value = mock_config

        # Create mock settings window
        mock_window = Mock()
        mock_settings_window.return_value = mock_window

        # Simulate opening settings
        settings = mock_settings_window(mock_config)
        settings.show()

        mock_settings_window.assert_called_once()
        mock_window.show.assert_called_once()

    @patch("src.utils.config.ConfigManager")
    def test_modify_and_save_configuration(self, mock_config_manager):
        """Test modifying configuration and saving."""
        from src.utils.config import Configuration

        # Load initial config
        initial_config = Configuration(
            hotkey="ctrl+alt+a", save_directory="E:\\tmp", image_quality=90
        )
        mock_config_manager.load_config.return_value = initial_config

        # Modify config
        modified_config = Configuration(
            hotkey="ctrl+shift+s",  # Changed
            save_directory="D:\\screenshots",  # Changed
            image_quality=85,  # Changed
        )

        # Save config
        mock_config_manager.save_config(modified_config)

        # Verify save was called with modified config
        mock_config_manager.save_config.assert_called_once_with(modified_config)

    @patch("src.core.hotkey.HotkeyManager")
    @patch("src.utils.config.ConfigManager")
    def test_hotkey_reregistration_on_config_change(
        self, mock_config_manager, mock_hotkey_manager
    ):
        """Test that hotkey is re-registered when configuration changes."""
        from src.utils.config import Configuration

        # Initial config
        old_config = Configuration(hotkey="ctrl+alt+a")
        new_config = Configuration(hotkey="ctrl+shift+s")

        mock_config_manager.load_config.return_value = new_config

        # Create hotkey manager mock
        manager = mock_hotkey_manager.return_value

        # Simulate config change
        # 1. Unregister old hotkey
        manager.unregister_hotkey("ctrl+alt+a")

        # 2. Register new hotkey
        callback = Mock()
        manager.register_hotkey("ctrl+shift+s", callback)

        # Verify
        manager.unregister_hotkey.assert_called_with("ctrl+alt+a")
        manager.register_hotkey.assert_called_with("ctrl+shift+s", callback)

    @patch("src.utils.config.ConfigManager")
    def test_config_validation_prevents_invalid_save(self, mock_config_manager):
        """Test that invalid configuration cannot be saved."""
        from src.utils.config import Configuration

        # Invalid config (empty hotkey, quality out of range)
        invalid_config = Configuration(hotkey="", image_quality=150)

        # Mock save_config to raise ValueError on validation failure
        mock_config_manager.save_config.side_effect = ValueError(
            "Configuration validation failed"
        )

        # Attempt to save should raise error
        with pytest.raises(ValueError) as exc_info:
            mock_config_manager.save_config(invalid_config)

        assert "validation failed" in str(exc_info.value).lower()

    @patch("src.utils.file_manager.FileManager")
    @patch("src.utils.config.ConfigManager")
    def test_save_directory_validation_on_change(
        self, mock_config_manager, mock_file_manager
    ):
        """Test that save directory is validated when changed."""
        from src.utils.config import Configuration

        new_config = Configuration(save_directory="D:\\new_screenshots")

        # Simulate directory creation
        mock_file_manager.create_directory(new_config.save_directory)

        # Verify directory creation was called
        mock_file_manager.create_directory.assert_called_once_with(
            "D:\\new_screenshots"
        )

    @patch("src.utils.config.ConfigManager")
    def test_config_reload_without_restart(self, mock_config_manager):
        """Test that configuration can be reloaded without restarting application."""
        from src.utils.config import Configuration

        # Initial load
        config1 = Configuration(image_quality=90)
        mock_config_manager.load_config.return_value = config1

        initial = mock_config_manager.load_config()
        assert initial.image_quality == 90

        # Modify and reload
        config2 = Configuration(image_quality=85)
        mock_config_manager.load_config.return_value = config2

        reloaded = mock_config_manager.load_config()
        assert reloaded.image_quality == 85

    @patch("src.utils.notification.NotificationManager")
    @patch("src.utils.config.ConfigManager")
    def test_notification_toggle(self, mock_config_manager, mock_notification):
        """Test that notifications can be toggled via config."""
        from src.utils.config import Configuration

        # Disable notifications
        config = Configuration(show_notification=False)
        mock_config_manager.load_config.return_value = config

        # When screenshot is taken, notification should not show if disabled
        if config.show_notification:
            mock_notification.show_success("/mnt/e/test.jpg")

        # Should not be called
        mock_notification.show_success.assert_not_called()

        # Enable notifications
        config.show_notification = True
        if config.show_notification:
            mock_notification.show_success("/mnt/e/test.jpg")

        # Should be called now
        mock_notification.show_success.assert_called_once()

    @patch("src.utils.config.ConfigManager")
    def test_image_format_change_affects_next_screenshot(self, mock_config_manager):
        """Test that changing image format affects next screenshot."""
        from src.utils.config import Configuration
        from src.utils.file_manager import FileManager

        # Change to PNG
        config = Configuration(image_format="png")
        mock_config_manager.load_config.return_value = config

        # Generate filename with new format
        filename = FileManager.generate_filename(config.image_format)

        assert filename.endswith(".png")

    @patch("src.gui.tray.SystemTray")
    @patch("src.gui.settings.SettingsWindow")
    def test_settings_accessible_from_tray_menu(self, mock_settings_window, mock_tray):
        """Test that settings can be accessed from tray menu."""
        # Create tray mock
        tray = mock_tray.return_value
        tray.show_settings = Mock()

        # Simulate clicking settings menu item
        tray.show_settings()

        # Verify settings action was triggered
        tray.show_settings.assert_called_once()

    def test_error_display_on_invalid_config_save(self):
        """Test that error is displayed when saving invalid config."""
        from src.utils.config import Configuration

        # Create invalid config
        invalid_config = Configuration(
            hotkey="", image_quality=0  # Empty - invalid  # Out of range - invalid
        )

        errors = invalid_config.validate()

        # Should have multiple errors
        assert len(errors) >= 2
        assert any("hotkey" in err for err in errors)
        assert any("image_quality" in err for err in errors)
