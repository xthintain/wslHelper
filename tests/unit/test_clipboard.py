"""Unit tests for ClipboardManager module.

Tests clipboard operations for setting and getting text with mocking
of Windows clipboard API.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.clipboard import ClipboardManager


class TestClipboardManager:
    """Test cases for ClipboardManager class."""

    @patch("src.core.clipboard.win32con")
    @patch("src.core.clipboard.win32clipboard")
    def test_set_text_success(self, mock_clipboard, mock_con):
        """Test successful text copy to clipboard."""
        test_text = "/mnt/e/tmp/screenshot.jpg"
        mock_con.CF_UNICODETEXT = 13

        ClipboardManager.set_text(test_text)

        # Verify clipboard operations were called in correct order
        mock_clipboard.OpenClipboard.assert_called_once()
        mock_clipboard.EmptyClipboard.assert_called_once()
        mock_clipboard.SetClipboardText.assert_called_once_with(test_text, 13)
        mock_clipboard.CloseClipboard.assert_called_once()

    @patch("src.core.clipboard.win32con")
    @patch("src.core.clipboard.win32clipboard")
    def test_set_text_with_chinese_characters(self, mock_clipboard, mock_con):
        """Test clipboard with Chinese characters."""
        test_text = "/mnt/e/我的文件/图片.jpg"
        mock_con.CF_UNICODETEXT = 13

        ClipboardManager.set_text(test_text)

        mock_clipboard.SetClipboardText.assert_called_once_with(test_text, 13)

    @patch("src.core.clipboard.win32con")
    @patch("src.core.clipboard.win32clipboard")
    def test_set_text_with_spaces(self, mock_clipboard, mock_con):
        """Test clipboard with paths containing spaces."""
        test_text = "/mnt/e/my folder/screenshot.jpg"
        mock_con.CF_UNICODETEXT = 13

        ClipboardManager.set_text(test_text)

        mock_clipboard.SetClipboardText.assert_called_once_with(test_text, 13)

    @patch("src.core.clipboard.win32con")
    @patch("src.core.clipboard.win32clipboard")
    def test_set_text_empty_string(self, mock_clipboard, mock_con):
        """Test setting empty string to clipboard."""
        mock_con.CF_UNICODETEXT = 13

        ClipboardManager.set_text("")

        mock_clipboard.SetClipboardText.assert_called_once_with("", 13)

    @patch("src.core.clipboard.win32clipboard")
    def test_set_text_clipboard_error(self, mock_clipboard):
        """Test error handling when clipboard operation fails."""
        mock_clipboard.OpenClipboard.side_effect = Exception("Clipboard access denied")

        with pytest.raises(Exception):
            ClipboardManager.set_text("/mnt/e/test.jpg")

        # Clipboard should still be closed even on error
        mock_clipboard.CloseClipboard.assert_called()

    @patch("src.core.clipboard.win32con")
    @patch("src.core.clipboard.win32clipboard")
    def test_get_text_success(self, mock_clipboard, mock_con):
        """Test successful text retrieval from clipboard."""
        expected_text = "/mnt/e/tmp/screenshot.jpg"
        mock_con.CF_UNICODETEXT = 13
        mock_clipboard.GetClipboardData.return_value = expected_text

        result = ClipboardManager.get_text()

        assert result == expected_text
        mock_clipboard.OpenClipboard.assert_called_once()
        mock_clipboard.GetClipboardData.assert_called_once_with(13)
        mock_clipboard.CloseClipboard.assert_called_once()

    @patch("src.core.clipboard.win32con")
    @patch("src.core.clipboard.win32clipboard")
    def test_get_text_empty_clipboard(self, mock_clipboard, mock_con):
        """Test retrieval when clipboard is empty."""
        mock_con.CF_UNICODETEXT = 13
        mock_clipboard.GetClipboardData.return_value = ""

        result = ClipboardManager.get_text()

        assert result == ""

    @patch("src.core.clipboard.win32con")
    @patch("src.core.clipboard.win32clipboard")
    def test_get_text_clipboard_error(self, mock_clipboard, mock_con):
        """Test error handling when getting clipboard data fails."""
        mock_con.CF_UNICODETEXT = 13
        mock_clipboard.OpenClipboard.side_effect = Exception("Clipboard busy")

        with pytest.raises(Exception):
            ClipboardManager.get_text()

        mock_clipboard.CloseClipboard.assert_called()

    @patch("src.core.clipboard.win32con")
    @patch("src.core.clipboard.win32clipboard")
    def test_clipboard_closes_on_exception(self, mock_clipboard, mock_con):
        """Test that clipboard is always closed even if exception occurs."""
        mock_con.CF_UNICODETEXT = 13
        mock_clipboard.SetClipboardText.side_effect = Exception("Set failed")

        with pytest.raises(Exception):
            ClipboardManager.set_text("test")

        # Verify CloseClipboard was called despite exception
        mock_clipboard.CloseClipboard.assert_called()

    def test_set_text_type_validation(self):
        """Test that set_text validates input type."""
        # This assumes ClipboardManager validates input type
        # If not implemented, this test will need to be updated
        with pytest.raises((TypeError, AttributeError)):
            ClipboardManager.set_text(None)

        with pytest.raises((TypeError, AttributeError)):
            ClipboardManager.set_text(123)
