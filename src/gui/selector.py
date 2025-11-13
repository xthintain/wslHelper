"""Screenshot selector with drag selection logic.

Coordinates the screenshot capture workflow with the overlay.
"""

from PyQt5.QtCore import QObject, pyqtSignal
from typing import Optional

from src.gui.overlay import ScreenshotOverlay
from src.core.screenshot import ScreenshotCapture
from src.core.clipboard import ClipboardManager
from src.utils.file_manager import FileManager, Screenshot
from src.utils.notification import NotificationManager
from src.utils.config import Configuration
from src.utils.logger import get_logger


class ScreenshotSelector(QObject):
    """Coordinator for screenshot selection workflow."""

    # Signal emitted when screenshot is taken successfully
    screenshot_taken = pyqtSignal(Screenshot)

    def __init__(self, config: Configuration):
        """Initialize screenshot selector.

        Args:
            config: Application configuration
        """
        super().__init__()
        self.config = config
        self.logger = get_logger()
        self._overlay: Optional[ScreenshotOverlay] = None

    def start_selection(self) -> None:
        """Start screenshot selection process."""
        self.logger.info("Starting screenshot selection")

        # Create and show overlay
        self._overlay = ScreenshotOverlay()
        self._overlay.region_selected.connect(self._on_region_selected)
        self._overlay.selection_cancelled.connect(self._on_selection_cancelled)
        self._overlay.show_overlay()

    def _on_region_selected(self, left: int, top: int, width: int, height: int) -> None:
        """Handle region selection.

        Args:
            left: Left coordinate
            top: Top coordinate
            width: Region width
            height: Region height
        """
        self.logger.info(f"Region selected: ({left}, {top}, {width}, {height})")

        try:
            # Capture region
            image = ScreenshotCapture.capture_region(left, top, width, height)

            # Ensure save directory exists
            FileManager.create_directory(self.config.save_directory)

            # Save screenshot
            screenshot = FileManager.save_screenshot(
                image,
                self.config.save_directory,
                self.config.image_format,
                self.config.image_quality,
            )

            # Copy WSL path to clipboard
            ClipboardManager.set_text(screenshot.wsl_path)
            self.logger.info(f"WSL path copied to clipboard: {screenshot.wsl_path}")

            # Show notification
            if self.config.show_notification:
                NotificationManager.show_success(screenshot.wsl_path)

            # Emit signal
            self.screenshot_taken.emit(screenshot)

        except Exception as e:
            self.logger.error(f"Screenshot workflow failed: {e}", exc_info=True)
            NotificationManager.show_error(f"Screenshot failed: {str(e)}")

    def _on_selection_cancelled(self) -> None:
        """Handle selection cancellation."""
        self.logger.info("Screenshot selection cancelled")
