"""Windows notification module.

Provides functions to show Windows toast notifications.
"""

from win10toast import ToastNotifier
from typing import Optional

from src.utils.logger import get_logger


class NotificationManager:
    """Manager for Windows toast notifications."""

    _toaster: Optional[ToastNotifier] = None
    logger = get_logger()

    @classmethod
    def _get_toaster(cls) -> ToastNotifier:
        """Get or create toast notifier instance.

        Returns:
            ToastNotifier instance
        """
        if cls._toaster is None:
            cls._toaster = ToastNotifier()
        return cls._toaster

    @classmethod
    def show_success(cls, wsl_path: str, duration: int = 5) -> None:
        """Show success notification with WSL path.

        Args:
            wsl_path: WSL path to display
            duration: Notification duration in seconds
        """
        try:
            toaster = cls._get_toaster()
            toaster.show_toast(
                "WSL Screenshot Tool",
                f"Screenshot saved:\n{wsl_path}",
                duration=duration,
                threaded=True,
                icon_path=None,  # Will use default icon
            )
            cls.logger.info(f"Success notification shown: {wsl_path}")
        except Exception as e:
            cls.logger.error(f"Failed to show notification: {e}")

    @classmethod
    def show_error(cls, message: str, duration: int = 5) -> None:
        """Show error notification.

        Args:
            message: Error message to display
            duration: Notification duration in seconds
        """
        try:
            toaster = cls._get_toaster()
            toaster.show_toast(
                "WSL Screenshot Tool - Error",
                message,
                duration=duration,
                threaded=True,
                icon_path=None,
            )
            cls.logger.warning(f"Error notification shown: {message}")
        except Exception as e:
            cls.logger.error(f"Failed to show error notification: {e}")

    @classmethod
    def show_info(cls, title: str, message: str, duration: int = 3) -> None:
        """Show informational notification.

        Args:
            title: Notification title
            message: Notification message
            duration: Notification duration in seconds
        """
        try:
            toaster = cls._get_toaster()
            toaster.show_toast(
                title, message, duration=duration, threaded=True, icon_path=None
            )
            cls.logger.debug(f"Info notification shown: {title} - {message}")
        except Exception as e:
            cls.logger.error(f"Failed to show info notification: {e}")
