"""Unit tests for StartupManager.

Tests Windows Registry-based auto-startup functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import winreg


class TestStartupManager:
    """Test cases for StartupManager class."""

    @patch("src.system.startup.winreg")
    def test_add_to_startup_success(self, mock_winreg):
        """Test successfully adding application to startup."""
        from src.system.startup import StartupManager

        app_path = "C:\\Program Files\\WSLScreenshot\\app.exe"

        # Mock registry operations
        mock_key = Mock()
        mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
        mock_winreg.HKEY_CURRENT_USER = winreg.HKEY_CURRENT_USER
        mock_winreg.KEY_SET_VALUE = winreg.KEY_SET_VALUE
        mock_winreg.REG_SZ = winreg.REG_SZ

        result = StartupManager.add_to_startup(app_path)

        assert result is True
        mock_winreg.SetValueEx.assert_called_once_with(
            mock_key, "WSLScreenshot", 0, mock_winreg.REG_SZ, app_path
        )

    @patch("src.system.startup.winreg")
    def test_add_to_startup_with_custom_name(self, mock_winreg):
        """Test adding to startup with custom application name."""
        from src.system.startup import StartupManager

        app_path = "C:\\app\\custom.exe"
        app_name = "CustomApp"

        mock_key = Mock()
        mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
        mock_winreg.HKEY_CURRENT_USER = winreg.HKEY_CURRENT_USER
        mock_winreg.KEY_SET_VALUE = winreg.KEY_SET_VALUE
        mock_winreg.REG_SZ = winreg.REG_SZ

        result = StartupManager.add_to_startup(app_path, app_name)

        assert result is True
        mock_winreg.SetValueEx.assert_called_with(
            mock_key, app_name, 0, mock_winreg.REG_SZ, app_path
        )

    @patch("src.system.startup.winreg")
    def test_add_to_startup_registry_error(self, mock_winreg):
        """Test handling of registry error when adding to startup."""
        from src.system.startup import StartupManager

        app_path = "C:\\app.exe"

        # Simulate registry error
        mock_winreg.OpenKey.side_effect = OSError("Registry access denied")

        result = StartupManager.add_to_startup(app_path)

        assert result is False

    @patch("src.system.startup.winreg")
    def test_remove_from_startup_success(self, mock_winreg):
        """Test successfully removing application from startup."""
        from src.system.startup import StartupManager

        mock_key = Mock()
        mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
        mock_winreg.HKEY_CURRENT_USER = winreg.HKEY_CURRENT_USER
        mock_winreg.KEY_SET_VALUE = winreg.KEY_SET_VALUE

        result = StartupManager.remove_from_startup()

        assert result is True
        mock_winreg.DeleteValue.assert_called_once_with(mock_key, "WSLScreenshot")

    @patch("src.system.startup.winreg")
    def test_remove_from_startup_not_exists(self, mock_winreg):
        """Test removing from startup when entry doesn't exist."""
        from src.system.startup import StartupManager

        mock_key = Mock()
        mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
        mock_winreg.DeleteValue.side_effect = FileNotFoundError("Value not found")

        result = StartupManager.remove_from_startup()

        # Should still return True (no entry to remove)
        assert result is True

    @patch("src.system.startup.winreg")
    def test_is_in_startup_true(self, mock_winreg):
        """Test checking if application is in startup (exists)."""
        from src.system.startup import StartupManager

        mock_key = Mock()
        mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
        mock_winreg.QueryValueEx.return_value = ("C:\\app.exe", winreg.REG_SZ)
        mock_winreg.HKEY_CURRENT_USER = winreg.HKEY_CURRENT_USER
        mock_winreg.KEY_READ = winreg.KEY_READ

        result = StartupManager.is_in_startup()

        assert result is True

    @patch("src.system.startup.winreg")
    def test_is_in_startup_false(self, mock_winreg):
        """Test checking if application is in startup (doesn't exist)."""
        from src.system.startup import StartupManager

        mock_key = Mock()
        mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
        mock_winreg.QueryValueEx.side_effect = FileNotFoundError("Value not found")

        result = StartupManager.is_in_startup()

        assert result is False

    @patch("src.system.startup.winreg")
    def test_get_startup_path(self, mock_winreg):
        """Test getting the startup path."""
        from src.system.startup import StartupManager

        expected_path = "C:\\Program Files\\WSLScreenshot\\app.exe"

        mock_key = Mock()
        mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
        mock_winreg.QueryValueEx.return_value = (expected_path, winreg.REG_SZ)
        mock_winreg.HKEY_CURRENT_USER = winreg.HKEY_CURRENT_USER
        mock_winreg.KEY_READ = winreg.KEY_READ

        path = StartupManager.get_startup_path()

        assert path == expected_path

    @patch("src.system.startup.winreg")
    def test_get_startup_path_not_exists(self, mock_winreg):
        """Test getting startup path when not in startup."""
        from src.system.startup import StartupManager

        mock_key = Mock()
        mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
        mock_winreg.QueryValueEx.side_effect = FileNotFoundError("Value not found")

        path = StartupManager.get_startup_path()

        assert path is None
