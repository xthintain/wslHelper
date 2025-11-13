"""File management module for screenshot operations.

Handles screenshot saving, filename generation, directory creation,
and automatic cleanup of old screenshots.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal, Optional
from dataclasses import dataclass
from PIL import Image

from src.utils.logger import get_logger


@dataclass
class Screenshot:
    """Screenshot data model."""

    file_path: str
    wsl_path: str
    filename: str
    created_at: datetime
    format: Literal["jpg", "png"]
    file_size: int
    width: Optional[int] = None
    height: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
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


class FileManager:
    """File manager for screenshot operations."""

    logger = get_logger()

    @staticmethod
    def generate_filename(image_format: Literal["jpg", "png"]) -> str:
        """Generate unique timestamp-based filename.

        Args:
            image_format: Image format ("jpg" or "png")

        Returns:
            Generated filename (e.g., "screenshot_20251112_143020.jpg")

        Raises:
            ValueError: If image format is not supported
        """
        if image_format not in ["jpg", "png"]:
            raise ValueError(f"Unsupported image format: {image_format}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"screenshot_{timestamp}.{image_format}"

    @staticmethod
    def create_directory(directory: str) -> None:
        """Create directory if it doesn't exist.

        Args:
            directory: Directory path to create

        Raises:
            PermissionError: If permission denied
            OSError: If directory creation fails
        """
        path = Path(directory)
        try:
            path.mkdir(parents=True, exist_ok=True)
            FileManager.logger.debug(f"Directory created/verified: {directory}")
        except PermissionError as e:
            FileManager.logger.error(
                f"Permission denied creating directory: {directory}"
            )
            raise
        except OSError as e:
            FileManager.logger.error(f"Failed to create directory: {e}")
            raise

    @staticmethod
    def save_screenshot(
        image: Image.Image,
        save_directory: str,
        image_format: Literal["jpg", "png"],
        quality: int = 90,
    ) -> Screenshot:
        """Save screenshot image to file.

        Args:
            image: PIL Image object to save
            save_directory: Directory to save screenshot
            image_format: Image format ("jpg" or "png")
            quality: JPEG quality (1-100, only applies to JPG)

        Returns:
            Screenshot object with file information

        Raises:
            FileNotFoundError: If save directory doesn't exist
            OSError: If disk space insufficient or other IO error
            PermissionError: If write permission denied
        """
        # Verify directory exists
        dir_path = Path(save_directory)
        if not dir_path.exists():
            error_msg = f"Save directory does not exist: {save_directory}"
            FileManager.logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Check write permissions
        if not os.access(save_directory, os.W_OK):
            error_msg = f"Write permission denied for directory: {save_directory}"
            FileManager.logger.error(error_msg)
            raise PermissionError(error_msg)

        # Generate filename
        filename = FileManager.generate_filename(image_format)
        file_path = dir_path / filename

        try:
            # Check available disk space (rough estimate: uncompressed size * 0.3 for JPEG)
            width, height = image.size
            estimated_size = width * height * 3  # RGB bytes
            if image_format == "jpg":
                estimated_size = int(estimated_size * 0.3)  # JPEG compression estimate

            # Check disk space
            import shutil

            stat = shutil.disk_usage(save_directory)
            if stat.free < estimated_size:
                error_msg = f"Insufficient disk space. Available: {stat.free} bytes, Required: ~{estimated_size} bytes"
                FileManager.logger.error(error_msg)
                raise OSError(error_msg)

            # Save image
            if image_format == "jpg":
                image.save(file_path, format="JPEG", quality=quality)
                FileManager.logger.info(
                    f"Screenshot saved as JPEG (quality={quality}): {file_path}"
                )
            else:  # png
                image.save(file_path, format="PNG")
                FileManager.logger.info(f"Screenshot saved as PNG: {file_path}")

            # Get file info
            file_stat = file_path.stat()
            width, height = image.size

            FileManager.logger.info(
                f"File size: {file_stat.st_size} bytes ({file_stat.st_size / 1024:.2f} KB)"
            )

            # Import here to avoid circular dependency
            from src.core.path_converter import PathConverter

            wsl_path = PathConverter.windows_to_wsl(str(file_path))
            FileManager.logger.info(f"WSL path: {wsl_path}")

            # Create Screenshot object
            screenshot = Screenshot(
                file_path=str(file_path),
                wsl_path=wsl_path,
                filename=filename,
                created_at=datetime.now(),
                format=image_format,
                file_size=file_stat.st_size,
                width=width,
                height=height,
            )

            FileManager.logger.info(f"Screenshot successfully saved: {filename}")
            return screenshot

        except PermissionError as e:
            error_msg = f"Permission denied while saving screenshot: {e}"
            FileManager.logger.error(error_msg)
            raise
        except OSError as e:
            error_msg = f"Failed to save screenshot (disk space/IO error): {e}"
            FileManager.logger.error(error_msg)
            raise
        except Exception as e:
            error_msg = f"Unexpected error saving screenshot: {e}"
            FileManager.logger.error(error_msg, exc_info=True)
            raise

    @staticmethod
    def cleanup_old_screenshots(directory: str, days: int) -> int:
        """Delete screenshots older than specified days.

        Args:
            directory: Directory containing screenshots
            days: Delete files older than this many days

        Returns:
            Number of files deleted

        Raises:
            ValueError: If days <= 0
        """
        if days <= 0:
            raise ValueError("Days must be greater than 0")

        dir_path = Path(directory)
        if not dir_path.exists():
            FileManager.logger.warning(f"Directory does not exist: {directory}")
            return 0

        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0

        try:
            # Find all screenshot files
            for file_path in dir_path.glob("screenshot_*.jpg"):
                file_stat = file_path.stat()
                file_mtime = datetime.fromtimestamp(file_stat.st_mtime)

                if file_mtime < cutoff_date:
                    file_path.unlink()
                    deleted_count += 1
                    FileManager.logger.debug(f"Deleted old screenshot: {file_path}")

            # Also check PNG files
            for file_path in dir_path.glob("screenshot_*.png"):
                file_stat = file_path.stat()
                file_mtime = datetime.fromtimestamp(file_stat.st_mtime)

                if file_mtime < cutoff_date:
                    file_path.unlink()
                    deleted_count += 1
                    FileManager.logger.debug(f"Deleted old screenshot: {file_path}")

            FileManager.logger.info(f"Cleanup complete: {deleted_count} files deleted")
            return deleted_count

        except Exception as e:
            FileManager.logger.error(f"Cleanup failed: {e}")
            return deleted_count
