"""Screenshot capture module using mss library.

Provides functionality to capture full screen or specific regions
with support for multiple monitors.
"""

import mss
import mss.tools
from PIL import Image
from typing import Optional, Tuple
from dataclasses import dataclass

from src.utils.logger import get_logger


# Re-export Screenshot dataclass for convenience
from src.utils.file_manager import Screenshot


class ScreenshotCapture:
    """Screenshot capture using mss library."""

    logger = get_logger()

    @staticmethod
    def capture_screen(monitor_index: int = 1) -> Image.Image:
        """Capture entire screen or specific monitor.

        Args:
            monitor_index: Monitor index (1 = primary monitor, 0 = all monitors)

        Returns:
            PIL Image object

        Raises:
            IndexError: If monitor index is out of range
        """
        try:
            with mss.mss() as sct:
                # Validate monitor index
                if monitor_index < 0 or monitor_index >= len(sct.monitors):
                    raise IndexError(f"Monitor index {monitor_index} out of range")

                # Capture screenshot
                monitor = sct.monitors[monitor_index]
                screenshot = sct.grab(monitor)

                # Convert to PIL Image
                image = Image.frombytes(
                    "RGB", (screenshot.width, screenshot.height), screenshot.rgb
                )

                ScreenshotCapture.logger.debug(
                    f"Screen captured: {screenshot.width}x{screenshot.height} "
                    f"from monitor {monitor_index}"
                )

                return image

        except Exception as e:
            ScreenshotCapture.logger.error(f"Failed to capture screen: {e}")
            raise

    @staticmethod
    def capture_region(left: int, top: int, width: int, height: int) -> Image.Image:
        """Capture specific screen region.

        Args:
            left: Left coordinate
            top: Top coordinate
            width: Region width
            height: Region height

        Returns:
            PIL Image object

        Raises:
            ValueError: If dimensions are invalid
        """
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")

        if left < 0 or top < 0:
            raise ValueError("Left and top coordinates must be non-negative")

        try:
            with mss.mss() as sct:
                # Define region
                region = {"left": left, "top": top, "width": width, "height": height}

                # Capture region
                screenshot = sct.grab(region)

                # Convert to PIL Image
                image = Image.frombytes(
                    "RGB", (screenshot.width, screenshot.height), screenshot.rgb
                )

                ScreenshotCapture.logger.debug(
                    f"Region captured: {width}x{height} at ({left}, {top})"
                )

                return image

        except Exception as e:
            ScreenshotCapture.logger.error(f"Failed to capture region: {e}")
            raise

    @staticmethod
    def get_monitors() -> list[dict]:
        """Get list of available monitors.

        Returns:
            List of monitor dictionaries with position and size info
        """
        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                ScreenshotCapture.logger.debug(f"Found {len(monitors)} monitors")
                return monitors
        except Exception as e:
            ScreenshotCapture.logger.error(f"Failed to get monitors: {e}")
            return []

    @staticmethod
    def get_screen_size(monitor_index: int = 1) -> Tuple[int, int]:
        """Get screen resolution for specific monitor.

        Args:
            monitor_index: Monitor index (1 = primary)

        Returns:
            Tuple of (width, height)

        Raises:
            IndexError: If monitor index is out of range
        """
        try:
            with mss.mss() as sct:
                if monitor_index < 0 or monitor_index >= len(sct.monitors):
                    raise IndexError(f"Monitor index {monitor_index} out of range")

                monitor = sct.monitors[monitor_index]
                return (monitor["width"], monitor["height"])

        except Exception as e:
            ScreenshotCapture.logger.error(f"Failed to get screen size: {e}")
            raise
