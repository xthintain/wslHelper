"""Clipboard management module using Windows API.

Provides functions to set and get text from Windows clipboard using pywin32.
"""

import win32clipboard
import win32con
from typing import Optional


class ClipboardManager:
    """Manager for Windows clipboard operations."""

    @staticmethod
    def set_text(text: str) -> None:
        """Set text to Windows clipboard.

        Args:
            text: Text to copy to clipboard

        Raises:
            TypeError: If text is not a string
            Exception: If clipboard operation fails
        """
        if not isinstance(text, str):
            raise TypeError("Text must be a string")

        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
        except Exception as e:
            raise Exception(f"Failed to set clipboard text: {e}")
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass  # Ignore errors when closing

    @staticmethod
    def get_text() -> Optional[str]:
        """Get text from Windows clipboard.

        Returns:
            Clipboard text content, or None if clipboard is empty

        Raises:
            Exception: If clipboard operation fails
        """
        try:
            win32clipboard.OpenClipboard()
            try:
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                return text if text else ""
            except TypeError:
                # Clipboard doesn't contain text
                return ""
        except Exception as e:
            raise Exception(f"Failed to get clipboard text: {e}")
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass  # Ignore errors when closing

    @staticmethod
    def clear() -> None:
        """Clear clipboard contents.

        Raises:
            Exception: If clipboard operation fails
        """
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
        except Exception as e:
            raise Exception(f"Failed to clear clipboard: {e}")
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass  # Ignore errors when closing
