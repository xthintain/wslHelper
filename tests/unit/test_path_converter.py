"""Unit tests for PathConverter module.

Tests the Windows <-> WSL path conversion functionality including
edge cases for spaces, Chinese characters, and path validation.
"""

import pytest
from src.core.path_converter import PathConverter


class TestPathConverter:
    """Test cases for PathConverter class."""

    def test_windows_to_wsl_basic(self):
        """Test basic Windows to WSL path conversion."""
        assert (
            PathConverter.windows_to_wsl("E:\\tmp\\file.jpg") == "/mnt/e/tmp/file.jpg"
        )
        assert (
            PathConverter.windows_to_wsl("C:\\Users\\test.png")
            == "/mnt/c/Users/test.png"
        )
        assert (
            PathConverter.windows_to_wsl("D:\\screenshots\\image.jpg")
            == "/mnt/d/screenshots/image.jpg"
        )

    def test_windows_to_wsl_with_spaces(self):
        """Test Windows to WSL conversion with spaces in path."""
        assert (
            PathConverter.windows_to_wsl("E:\\my folder\\file.jpg")
            == "/mnt/e/my folder/file.jpg"
        )
        assert (
            PathConverter.windows_to_wsl("C:\\Program Files\\test.png")
            == "/mnt/c/Program Files/test.png"
        )

    def test_windows_to_wsl_with_chinese(self):
        """Test Windows to WSL conversion with Chinese characters."""
        assert (
            PathConverter.windows_to_wsl("E:\\我的文件\\图片.jpg")
            == "/mnt/e/我的文件/图片.jpg"
        )
        assert (
            PathConverter.windows_to_wsl("D:\\桌面\\screenshot.png")
            == "/mnt/d/桌面/screenshot.png"
        )

    def test_windows_to_wsl_different_drives(self):
        """Test conversion for different drive letters."""
        assert PathConverter.windows_to_wsl("A:\\test.jpg") == "/mnt/a/test.jpg"
        assert (
            PathConverter.windows_to_wsl("Z:\\data\\file.png") == "/mnt/z/data/file.png"
        )

    def test_wsl_to_windows_basic(self):
        """Test basic WSL to Windows path conversion."""
        assert (
            PathConverter.wsl_to_windows("/mnt/e/tmp/file.jpg") == "E:\\tmp\\file.jpg"
        )
        assert (
            PathConverter.wsl_to_windows("/mnt/c/Users/test.png")
            == "C:\\Users\\test.png"
        )

    def test_wsl_to_windows_with_spaces(self):
        """Test WSL to Windows conversion with spaces."""
        assert (
            PathConverter.wsl_to_windows("/mnt/e/my folder/file.jpg")
            == "E:\\my folder\\file.jpg"
        )

    def test_wsl_to_windows_with_chinese(self):
        """Test WSL to Windows conversion with Chinese characters."""
        assert (
            PathConverter.wsl_to_windows("/mnt/e/我的文件/图片.jpg")
            == "E:\\我的文件\\图片.jpg"
        )

    def test_validate_path_windows(self):
        """Test path validation for Windows paths."""
        assert PathConverter.validate_path("E:\\tmp\\file.jpg") is True
        assert PathConverter.validate_path("C:\\Users\\test.png") is True
        assert PathConverter.validate_path("Z:\\data\\image.jpg") is True

    def test_validate_path_wsl(self):
        """Test path validation for WSL paths."""
        assert PathConverter.validate_path("/mnt/e/tmp/file.jpg") is True
        assert PathConverter.validate_path("/mnt/c/Users/test.png") is True
        assert PathConverter.validate_path("/mnt/z/data/image.jpg") is True

    def test_validate_path_invalid(self):
        """Test path validation for invalid paths."""
        assert PathConverter.validate_path("/invalid/path") is False
        assert PathConverter.validate_path("relative/path.jpg") is False
        assert PathConverter.validate_path("") is False
        assert (
            PathConverter.validate_path("/mnt/E/test.jpg") is False
        )  # uppercase drive letter

    def test_windows_to_wsl_invalid_path(self):
        """Test conversion with invalid Windows path."""
        with pytest.raises(ValueError):
            PathConverter.windows_to_wsl("/invalid/path")

        with pytest.raises(ValueError):
            PathConverter.windows_to_wsl("relative\\path.jpg")

    def test_wsl_to_windows_invalid_path(self):
        """Test conversion with invalid WSL path."""
        with pytest.raises(ValueError):
            PathConverter.wsl_to_windows("E:\\invalid\\path")

        with pytest.raises(ValueError):
            PathConverter.wsl_to_windows("/invalid/path")

    def test_roundtrip_conversion(self):
        """Test that conversion is reversible."""
        original = "E:\\tmp\\test.jpg"
        wsl_path = PathConverter.windows_to_wsl(original)
        back_to_windows = PathConverter.wsl_to_windows(wsl_path)
        assert back_to_windows == original

    def test_edge_case_single_letter_filename(self):
        """Test edge case with single-letter filename."""
        assert PathConverter.windows_to_wsl("E:\\a.jpg") == "/mnt/e/a.jpg"

    def test_edge_case_long_path(self):
        """Test edge case with long nested path."""
        long_path = "E:\\level1\\level2\\level3\\level4\\file.jpg"
        expected = "/mnt/e/level1/level2/level3/level4/file.jpg"
        assert PathConverter.windows_to_wsl(long_path) == expected
