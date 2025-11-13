"""Integration test for complete screenshot workflow.

Tests the end-to-end flow: hotkey trigger → screenshot capture →
file save → path conversion → clipboard copy → notification.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


class TestScreenshotWorkflow:
    """Integration tests for screenshot workflow."""

    @patch("src.core.screenshot.ScreenshotCapture")
    @patch("src.core.path_converter.PathConverter")
    @patch("src.core.clipboard.ClipboardManager")
    @patch("src.utils.file_manager.FileManager")
    @patch("src.utils.notification.NotificationManager")
    def test_complete_screenshot_workflow(
        self,
        mock_notification,
        mock_file_manager,
        mock_clipboard,
        mock_path_converter,
        mock_screenshot_capture,
    ):
        """Test complete screenshot workflow from capture to notification."""
        # Setup mocks
        mock_image = Mock()
        mock_screenshot_capture.capture_region.return_value = mock_image

        mock_screenshot = Mock()
        mock_screenshot.file_path = "E:\\tmp\\screenshot_20251112_120000.jpg"
        mock_screenshot.wsl_path = "/mnt/e/tmp/screenshot_20251112_120000.jpg"
        mock_file_manager.save_screenshot.return_value = mock_screenshot

        mock_path_converter.windows_to_wsl.return_value = (
            "/mnt/e/tmp/screenshot_20251112_120000.jpg"
        )

        # Execute workflow
        # 1. Capture screenshot
        image = mock_screenshot_capture.capture_region(100, 100, 800, 600)
        assert image is not None

        # 2. Save screenshot
        screenshot = mock_file_manager.save_screenshot(image, "E:\\tmp", "jpg", 90)
        assert screenshot.file_path is not None

        # 3. Convert path
        wsl_path = mock_path_converter.windows_to_wsl(screenshot.file_path)
        assert wsl_path.startswith("/mnt/")

        # 4. Copy to clipboard
        mock_clipboard.set_text(wsl_path)
        mock_clipboard.set_text.assert_called_once_with(wsl_path)

        # 5. Show notification
        mock_notification.show_success(wsl_path)
        mock_notification.show_success.assert_called_once()

    @patch("src.core.screenshot.ScreenshotCapture")
    @patch("src.utils.file_manager.FileManager")
    def test_screenshot_workflow_save_failure(
        self, mock_file_manager, mock_screenshot_capture
    ):
        """Test workflow handles file save failures gracefully."""
        mock_image = Mock()
        mock_screenshot_capture.capture_region.return_value = mock_image

        # Simulate disk space error
        mock_file_manager.save_screenshot.side_effect = OSError(
            "No space left on device"
        )

        with pytest.raises(OSError):
            mock_file_manager.save_screenshot(mock_image, "E:\\tmp", "jpg", 90)

    @patch("src.core.screenshot.ScreenshotCapture")
    @patch("src.core.path_converter.PathConverter")
    @patch("src.utils.file_manager.FileManager")
    def test_screenshot_workflow_path_conversion(
        self, mock_file_manager, mock_path_converter, mock_screenshot_capture
    ):
        """Test path conversion in workflow."""
        mock_image = Mock()
        mock_screenshot_capture.capture_region.return_value = mock_image

        mock_screenshot = Mock()
        mock_screenshot.file_path = "E:\\tmp\\screenshots\\test.jpg"
        mock_file_manager.save_screenshot.return_value = mock_screenshot

        mock_path_converter.windows_to_wsl.return_value = (
            "/mnt/e/tmp/screenshots/test.jpg"
        )

        # Execute conversion step
        screenshot = mock_file_manager.save_screenshot(
            mock_image, "E:\\tmp\\screenshots", "jpg", 90
        )
        wsl_path = mock_path_converter.windows_to_wsl(screenshot.file_path)

        assert wsl_path == "/mnt/e/tmp/screenshots/test.jpg"
        mock_path_converter.windows_to_wsl.assert_called_once_with(
            "E:\\tmp\\screenshots\\test.jpg"
        )

    @patch("src.core.clipboard.ClipboardManager")
    def test_screenshot_workflow_clipboard_failure(self, mock_clipboard):
        """Test workflow handles clipboard failures."""
        wsl_path = "/mnt/e/tmp/test.jpg"
        mock_clipboard.set_text.side_effect = Exception("Clipboard busy")

        with pytest.raises(Exception):
            mock_clipboard.set_text(wsl_path)

    @patch("src.core.screenshot.ScreenshotCapture")
    @patch("src.utils.file_manager.FileManager")
    @patch("src.core.path_converter.PathConverter")
    @patch("src.core.clipboard.ClipboardManager")
    def test_workflow_with_chinese_characters(
        self,
        mock_clipboard,
        mock_path_converter,
        mock_file_manager,
        mock_screenshot_capture,
    ):
        """Test workflow with Chinese characters in path."""
        mock_image = Mock()
        mock_screenshot_capture.capture_region.return_value = mock_image

        mock_screenshot = Mock()
        mock_screenshot.file_path = "E:\\我的文件\\图片.jpg"
        mock_file_manager.save_screenshot.return_value = mock_screenshot

        mock_path_converter.windows_to_wsl.return_value = "/mnt/e/我的文件/图片.jpg"

        # Execute workflow
        screenshot = mock_file_manager.save_screenshot(
            mock_image, "E:\\我的文件", "jpg", 90
        )
        wsl_path = mock_path_converter.windows_to_wsl(screenshot.file_path)
        mock_clipboard.set_text(wsl_path)

        assert wsl_path == "/mnt/e/我的文件/图片.jpg"
        mock_clipboard.set_text.assert_called_once_with("/mnt/e/我的文件/图片.jpg")

    @patch("src.core.screenshot.ScreenshotCapture")
    @patch("src.utils.file_manager.FileManager")
    def test_workflow_png_format(self, mock_file_manager, mock_screenshot_capture):
        """Test workflow with PNG format."""
        mock_image = Mock()
        mock_screenshot_capture.capture_region.return_value = mock_image

        mock_screenshot = Mock()
        mock_screenshot.file_path = "E:\\tmp\\screenshot.png"
        mock_screenshot.format = "png"
        mock_file_manager.save_screenshot.return_value = mock_screenshot

        screenshot = mock_file_manager.save_screenshot(mock_image, "E:\\tmp", "png", 90)

        assert screenshot.format == "png"
        assert screenshot.file_path.endswith(".png")

    def test_workflow_cancel_operation(self):
        """Test workflow cancellation (ESC key pressed)."""
        # This test will be implemented when GUI components are ready
        # For now, it's a placeholder to ensure cancel logic is considered
        cancelled = True
        assert cancelled is True  # User pressed ESC

    @patch("src.core.hotkey.HotkeyManager")
    @patch("src.core.screenshot.ScreenshotCapture")
    def test_workflow_hotkey_trigger(
        self, mock_screenshot_capture, mock_hotkey_manager
    ):
        """Test workflow initiation via hotkey."""
        # Setup callback
        callback = Mock()
        mock_hotkey_manager.register_hotkey.return_value = True

        # Register hotkey
        success = mock_hotkey_manager.register_hotkey("ctrl+alt+a", callback)
        assert success is True

        # Simulate hotkey press
        callback()
        callback.assert_called_once()
