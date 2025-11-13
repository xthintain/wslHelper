"""Hotkey management module using pynput.

Provides global hotkey registration and monitoring functionality.
"""

from pynput import keyboard
from typing import Callable, Optional, Dict
from threading import Thread
from PyQt5.QtCore import QTimer

from src.utils.logger import get_logger


class HotkeyManager:
    """Manager for global hotkey registration and handling."""

    def __init__(self):
        """Initialize hotkey manager."""
        self.logger = get_logger()
        self._listener: Optional[keyboard.GlobalHotKeys] = None
        self._hotkeys: Dict[str, Callable] = {}
        self._callbacks: Dict[str, Callable] = {}  # Store original callbacks
        self._running = False

    def register_hotkey(self, hotkey: str, callback: Callable) -> bool:
        """Register a global hotkey.

        Args:
            hotkey: Hotkey combination (e.g., "ctrl+alt+a")
            callback: Function to call when hotkey is pressed

        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Convert hotkey format to pynput format
            pynput_hotkey = self._convert_hotkey_format(hotkey)

            # Store the original callback
            self._callbacks[pynput_hotkey] = callback

            # Wrap callback to execute in Qt main thread
            def thread_safe_callback():
                self.logger.debug(f"Hotkey triggered: {hotkey} (in pynput thread)")
                # Use QTimer to invoke callback in main Qt thread
                QTimer.singleShot(0, callback)

            self._hotkeys[pynput_hotkey] = thread_safe_callback
            self.logger.info(f"Hotkey registered: {hotkey}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register hotkey {hotkey}: {e}")
            return False

    def unregister_hotkey(self, hotkey: str) -> bool:
        """Unregister a hotkey.

        Args:
            hotkey: Hotkey combination to unregister

        Returns:
            True if successful, False otherwise
        """
        try:
            pynput_hotkey = self._convert_hotkey_format(hotkey)
            if pynput_hotkey in self._hotkeys:
                del self._hotkeys[pynput_hotkey]
                self.logger.info(f"Hotkey unregistered: {hotkey}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to unregister hotkey {hotkey}: {e}")
            return False

    def start_listening(self) -> None:
        """Start listening for hotkeys in a separate thread."""
        if self._running:
            self.logger.warning("Hotkey listener already running")
            return

        try:
            self._listener = keyboard.GlobalHotKeys(self._hotkeys)
            self._listener.start()
            self._running = True
            self.logger.info("Hotkey listener started")
        except Exception as e:
            self.logger.error(f"Failed to start hotkey listener: {e}")
            raise

    def stop_listening(self) -> None:
        """Stop listening for hotkeys."""
        if self._listener and self._running:
            self._listener.stop()
            self._running = False
            self.logger.info("Hotkey listener stopped")

    def _convert_hotkey_format(self, hotkey: str) -> str:
        """Convert hotkey from config format to pynput format.

        Args:
            hotkey: Hotkey in format "ctrl+alt+a"

        Returns:
            Hotkey in pynput format "<ctrl>+<alt>+a"
        """
        parts = hotkey.split("+")
        converted_parts = []

        for part in parts:
            part = part.strip().lower()
            if part in ["ctrl", "alt", "shift"]:
                converted_parts.append(f"<{part}>")
            else:
                converted_parts.append(part)

        return "+".join(converted_parts)

    def is_running(self) -> bool:
        """Check if listener is running.

        Returns:
            True if running, False otherwise
        """
        return self._running
