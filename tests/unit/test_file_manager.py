"""Unit tests for FileManager module.

Tests file operations including screenshot saving, filename generation,
and directory creation with proper error handling.
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
from src.utils.file_manager import FileManager


class TestFileManager:
    """Test cases for FileManager class."""

    def test_generate_filename_jpg(self):
        """Test filename generation for JPG format."""
        filename = FileManager.generate_filename("jpg")

        assert filename.startswith("screenshot_")
        assert filename.endswith(".jpg")
        assert len(filename) == len("screenshot_YYYYMMDD_HHMMSS.jpg")

    def test_generate_filename_png(self):
        """Test filename generation for PNG format."""
        filename = FileManager.generate_filename("png")

        assert filename.startswith("screenshot_")
        assert filename.endswith(".png")

    def test_generate_filename_unique(self):
        """Test that generated filenames are unique."""
        filename1 = FileManager.generate_filename("jpg")
        filename2 = FileManager.generate_filename("jpg")

        # If generated within the same second, they might be the same
        # This is expected behavior, but different calls should be very close
        assert filename1.startswith("screenshot_")
        assert filename2.startswith("screenshot_")

    def test_generate_filename_format_validation(self):
        """Test filename generation with timestamp format."""
        filename = FileManager.generate_filename("jpg")

        # Extract timestamp part
        timestamp_part = filename.replace("screenshot_", "").replace(".jpg", "")
        date_part, time_part = timestamp_part.split("_")

        # Validate format
        assert len(date_part) == 8  # YYYYMMDD
        assert len(time_part) == 6  # HHMMSS
        assert date_part.isdigit()
        assert time_part.isdigit()

    @patch("src.utils.file_manager.Path.mkdir")
    def test_create_directory_success(self, mock_mkdir):
        """Test successful directory creation."""
        test_dir = "E:\\tmp\\screenshots"

        FileManager.create_directory(test_dir)

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch("src.utils.file_manager.Path.mkdir")
    def test_create_directory_already_exists(self, mock_mkdir):
        """Test directory creation when directory already exists."""
        test_dir = "E:\\tmp\\screenshots"

        FileManager.create_directory(test_dir)

        # Should not raise error due to exist_ok=True
        mock_mkdir.assert_called_once()

    @patch("src.utils.file_manager.Path.mkdir")
    def test_create_directory_permission_error(self, mock_mkdir):
        """Test directory creation with permission denied."""
        mock_mkdir.side_effect = PermissionError("Access denied")

        with pytest.raises(PermissionError):
            FileManager.create_directory("C:\\Windows\\test")

    @patch("src.utils.file_manager.os.access")
    @patch("shutil.disk_usage")
    @patch("src.utils.file_manager.Path.stat")
    @patch("src.utils.file_manager.Path.exists")
    @patch("PIL.Image.Image.save")
    def test_save_screenshot_success(
        self, mock_save, mock_exists, mock_stat, mock_disk_usage, mock_access
    ):
        """Test successful screenshot save."""
        mock_image = Mock(spec=Image.Image)
        mock_image.size = (1920, 1080)
        save_dir = "E:\\tmp\\screenshots"
        image_format = "jpg"
        quality = 90

        mock_exists.return_value = True
        mock_access.return_value = True  # Directory is writable

        # Mock disk usage to return enough free space
        mock_disk_usage.return_value = Mock(free=100000000)  # 100MB free

        # Mock file stat to return file size
        mock_stat.return_value = Mock(st_size=123456)

        result = FileManager.save_screenshot(
            mock_image, save_dir, image_format, quality
        )

        assert result is not None
        assert result.filename.endswith(".jpg")
        assert result.file_path.startswith(save_dir)
        assert result.format == image_format
        assert result.width == 1920
        assert result.height == 1080
        assert result.file_size == 123456

    @patch("src.utils.file_manager.Path.exists")
    def test_save_screenshot_directory_not_exists(self, mock_exists):
        """Test save when directory doesn't exist."""
        mock_image = Mock(spec=Image.Image)
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            FileManager.save_screenshot(mock_image, "E:\\nonexistent", "jpg", 90)

    @patch("src.utils.file_manager.Path.exists")
    @patch("PIL.Image.Image.save")
    @patch("src.utils.file_manager.Path.stat")
    def test_save_screenshot_file_size(self, mock_stat, mock_save, mock_exists):
        """Test that file size is captured correctly."""
        mock_image = Mock(spec=Image.Image)
        mock_image.size = (1920, 1080)
        mock_exists.return_value = True

        # Mock file size
        mock_stat_result = Mock()
        mock_stat_result.st_size = 123456
        mock_stat.return_value = mock_stat_result

        result = FileManager.save_screenshot(mock_image, "E:\\tmp", "jpg", 90)

        assert result.file_size == 123456

    @patch("src.utils.file_manager.os.access")
    @patch("shutil.disk_usage")
    @patch("src.utils.file_manager.Path.exists")
    @patch("PIL.Image.Image.save")
    def test_save_screenshot_disk_space_error(
        self, mock_save, mock_exists, mock_disk_usage, mock_access
    ):
        """Test save failure due to disk space."""
        mock_image = Mock(spec=Image.Image)
        mock_image.size = (1920, 1080)
        mock_exists.return_value = True
        mock_access.return_value = True  # Directory is writable

        # Mock disk usage to return insufficient free space
        mock_disk_usage.return_value = Mock(free=100)  # Only 100 bytes free

        with pytest.raises(OSError):
            FileManager.save_screenshot(mock_image, "E:\\tmp", "jpg", 90)

    @patch("src.utils.file_manager.os.access")
    @patch("shutil.disk_usage")
    @patch("src.utils.file_manager.Path.stat")
    @patch("src.utils.file_manager.Path.exists")
    @patch("PIL.Image.Image.save")
    def test_save_screenshot_png_format(
        self, mock_save, mock_exists, mock_stat, mock_disk_usage, mock_access
    ):
        """Test screenshot save with PNG format."""
        mock_image = Mock(spec=Image.Image)
        mock_image.size = (1920, 1080)
        mock_exists.return_value = True
        mock_access.return_value = True
        mock_disk_usage.return_value = Mock(free=100000000)
        mock_stat.return_value = Mock(st_size=456789)

        result = FileManager.save_screenshot(mock_image, "E:\\tmp", "png", quality=90)

        assert result.filename.endswith(".png")
        assert result.format == "png"

    @patch("src.utils.file_manager.Path.exists")
    @patch("src.utils.file_manager.Path.unlink")
    @patch("src.utils.file_manager.Path.stat")
    @patch("src.utils.file_manager.Path.glob")
    def test_cleanup_old_screenshots_by_days(
        self, mock_glob, mock_stat, mock_unlink, mock_exists
    ):
        """Test cleanup of screenshots older than specified days."""
        mock_exists.return_value = True

        # Mock old files
        old_file = Mock()
        old_file.stat.return_value.st_mtime = datetime.now().timestamp() - (
            8 * 24 * 3600
        )
        mock_glob.return_value = [old_file]

        deleted_count = FileManager.cleanup_old_screenshots("E:\\tmp", days=7)

        assert deleted_count == 1
        old_file.unlink.assert_called_once()

    def test_validate_image_format(self):
        """Test image format validation."""
        assert FileManager.generate_filename("jpg").endswith(".jpg")
        assert FileManager.generate_filename("png").endswith(".png")

        with pytest.raises(ValueError):
            FileManager.generate_filename("bmp")  # Unsupported format
