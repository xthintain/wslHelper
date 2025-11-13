"""Windows Registry-based startup management.

Provides functionality to add/remove application from Windows startup
using the Registry Run key.
"""

import winreg
from typing import Optional

from src.utils.logger import get_logger


class StartupManager:
    """Manager for Windows startup registry entries."""

    _registry_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    _app_name = "WSLScreenshot"
    logger = get_logger()

    @classmethod
    def add_to_startup(cls, app_path: str, app_name: Optional[str] = None) -> bool:
        """Add application to Windows startup.

        Args:
            app_path: Full path to application executable
            app_name: Name of registry entry (default: "WSLScreenshot")

        Returns:
            True if successful, False otherwise
        """
        if app_name is None:
            app_name = cls._app_name

        try:
            # Open registry key
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, cls._registry_path, 0, winreg.KEY_SET_VALUE
            ) as key:
                # Set value
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)

            cls.logger.info(f"Added to startup: {app_name} = {app_path}")
            return True

        except OSError as e:
            cls.logger.error(f"Failed to add to startup: {e}")
            return False

    @classmethod
    def remove_from_startup(cls, app_name: Optional[str] = None) -> bool:
        """Remove application from Windows startup.

        Args:
            app_name: Name of registry entry (default: "WSLScreenshot")

        Returns:
            True if successful, False otherwise
        """
        if app_name is None:
            app_name = cls._app_name

        try:
            # Open registry key
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, cls._registry_path, 0, winreg.KEY_SET_VALUE
            ) as key:
                # Delete value
                try:
                    winreg.DeleteValue(key, app_name)
                    cls.logger.info(f"Removed from startup: {app_name}")
                except FileNotFoundError:
                    # Entry doesn't exist - that's fine
                    cls.logger.debug(f"Startup entry not found: {app_name}")

            return True

        except OSError as e:
            cls.logger.error(f"Failed to remove from startup: {e}")
            return False

    @classmethod
    def is_in_startup(cls, app_name: Optional[str] = None) -> bool:
        """Check if application is in Windows startup.

        Args:
            app_name: Name of registry entry (default: "WSLScreenshot")

        Returns:
            True if in startup, False otherwise
        """
        if app_name is None:
            app_name = cls._app_name

        try:
            # Open registry key (read-only)
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, cls._registry_path, 0, winreg.KEY_READ
            ) as key:
                # Query value
                winreg.QueryValueEx(key, app_name)
                return True

        except FileNotFoundError:
            return False
        except OSError as e:
            cls.logger.error(f"Failed to check startup status: {e}")
            return False

    @classmethod
    def get_startup_path(cls, app_name: Optional[str] = None) -> Optional[str]:
        """Get the startup path for the application.

        Args:
            app_name: Name of registry entry (default: "WSLScreenshot")

        Returns:
            Path to application executable, or None if not in startup
        """
        if app_name is None:
            app_name = cls._app_name

        try:
            # Open registry key (read-only)
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, cls._registry_path, 0, winreg.KEY_READ
            ) as key:
                # Query value
                value, _ = winreg.QueryValueEx(key, app_name)
                return value

        except FileNotFoundError:
            return None
        except OSError as e:
            cls.logger.error(f"Failed to get startup path: {e}")
            return None
