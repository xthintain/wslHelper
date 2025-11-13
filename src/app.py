"""Singleton application class with lifecycle management.

This module implements the main Application singleton that manages the
lifecycle of all components, including screenshot capture, hotkey handling,
and GUI elements.
"""

from typing import Optional
from PyQt5.QtCore import QObject, pyqtSignal

from src.utils.logger import get_logger
from src.utils.config import load_config, Configuration


class Application(QObject):
    """Singleton application class managing the application lifecycle."""

    # Signals
    config_changed = pyqtSignal(Configuration)
    screenshot_taken = pyqtSignal(str)  # WSL path

    _instance: Optional["Application"] = None

    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize application (only once due to singleton)."""
        if self._initialized:
            return

        super().__init__()
        self.logger = get_logger()
        self.config: Optional[Configuration] = None
        self._initialized = True

        # Component references (will be initialized in initialize())
        self.hotkey_manager = None
        self.screenshot_selector = None
        self.tray_icon = None
        self.settings_window = None

    def initialize(self) -> None:
        """Initialize all application components."""
        self.logger.info("Initializing application components")

        # Load configuration
        self.config = load_config()
        self.logger.info(f"Configuration loaded from {self.config.save_directory}")

        # Initialize components
        self._initialize_hotkey_manager()
        self._initialize_screenshot_selector()
        self._initialize_tray_icon()

        self.logger.info("Application initialization complete")

    def _initialize_hotkey_manager(self) -> None:
        """Initialize hotkey manager."""
        from src.core.hotkey import HotkeyManager

        self.hotkey_manager = HotkeyManager()

        # Register screenshot hotkey
        success = self.hotkey_manager.register_hotkey(
            self.config.hotkey, self._on_screenshot_hotkey
        )

        if success:
            self.hotkey_manager.start_listening()
            self.logger.info(f"Hotkey registered: {self.config.hotkey}")
        else:
            self.logger.error(f"Failed to register hotkey: {self.config.hotkey}")

    def _initialize_screenshot_selector(self) -> None:
        """Initialize screenshot selector."""
        from src.gui.selector import ScreenshotSelector

        self.screenshot_selector = ScreenshotSelector(self.config)
        self.screenshot_selector.screenshot_taken.connect(self._on_screenshot_taken)
        self.logger.info("Screenshot selector initialized")

    def _initialize_tray_icon(self) -> None:
        """Initialize system tray icon."""
        from src.gui.tray import SystemTray

        self.tray_icon = SystemTray()
        self.tray_icon.screenshot_requested.connect(self._on_screenshot_hotkey)
        self.tray_icon.settings_requested.connect(self._on_settings_requested)
        self.tray_icon.exit_requested.connect(self.shutdown)
        self.tray_icon.show()
        self.logger.info("System tray icon initialized")

    def _on_settings_requested(self) -> None:
        """Handle settings request from tray icon."""
        self.logger.info("Opening settings window")
        self._show_settings()

    def _show_settings(self) -> None:
        """Show settings window."""
        from src.gui.settings import SettingsWindow

        # Create settings window if not exists
        if self.settings_window is None or not self.settings_window.isVisible():
            self.settings_window = SettingsWindow(self.config)
            self.settings_window.config_saved.connect(self._on_config_saved)
            self.settings_window.show()
        else:
            # Bring existing window to front
            self.settings_window.raise_()
            self.settings_window.activateWindow()

    def _on_config_saved(self, new_config: Configuration) -> None:
        """Handle configuration save event.

        Args:
            new_config: Newly saved configuration
        """
        self.logger.info("Configuration saved, reloading components")

        old_hotkey = self.config.hotkey
        old_save_dir = self.config.save_directory

        # Update config
        self.config = new_config

        # Re-register hotkey if changed
        if old_hotkey != new_config.hotkey:
            self.logger.info(f"Hotkey changed from {old_hotkey} to {new_config.hotkey}")
            self._reregister_hotkey(old_hotkey, new_config.hotkey)

        # Ensure save directory exists if changed
        if old_save_dir != new_config.save_directory:
            self.logger.info(f"Save directory changed to {new_config.save_directory}")
            from src.utils.file_manager import FileManager

            try:
                FileManager.create_directory(new_config.save_directory)
            except Exception as e:
                self.logger.error(f"Failed to create save directory: {e}")

        # Update screenshot selector config
        if self.screenshot_selector:
            self.screenshot_selector.config = new_config

        # Emit config changed signal
        self.config_changed.emit(new_config)

        self.logger.info("Configuration reload complete")

    def _reregister_hotkey(self, old_hotkey: str, new_hotkey: str) -> None:
        """Re-register hotkey.

        Args:
            old_hotkey: Old hotkey combination
            new_hotkey: New hotkey combination
        """
        if self.hotkey_manager:
            # Stop current listener
            self.hotkey_manager.stop_listening()

            # Unregister old hotkey
            self.hotkey_manager.unregister_hotkey(old_hotkey)

            # Register new hotkey
            success = self.hotkey_manager.register_hotkey(
                new_hotkey, self._on_screenshot_hotkey
            )

            if success:
                # Restart listener
                self.hotkey_manager.start_listening()
                self.logger.info(f"Hotkey re-registered: {new_hotkey}")
            else:
                self.logger.error(f"Failed to register new hotkey: {new_hotkey}")
                # Try to restore old hotkey
                self.hotkey_manager.register_hotkey(
                    old_hotkey, self._on_screenshot_hotkey
                )
                self.hotkey_manager.start_listening()

    def _on_screenshot_hotkey(self) -> None:
        """Handle screenshot hotkey press."""
        self.logger.info("Screenshot hotkey pressed")
        if self.screenshot_selector:
            self.screenshot_selector.start_selection()

    def _on_screenshot_taken(self, screenshot) -> None:
        """Handle screenshot taken event."""
        self.logger.info(f"Screenshot taken: {screenshot.wsl_path}")
        self.screenshot_taken.emit(screenshot.wsl_path)

    def reload_config(self) -> None:
        """Reload configuration and notify components."""
        self.logger.info("Reloading configuration")
        self.config = load_config()

        # Validate configuration
        errors = self.config.validate()
        if errors:
            self.logger.error(f"Configuration validation failed: {errors}")
            return

        # Emit signal to notify components
        self.config_changed.emit(self.config)
        self.logger.info("Configuration reloaded successfully")

    def shutdown(self) -> None:
        """Shutdown application and cleanup resources."""
        self.logger.info("Shutting down application")

        # Stop hotkey listener
        if self.hotkey_manager:
            self.hotkey_manager.stop_listening()
            self.logger.debug("Hotkey listener stopped")

        # Hide tray icon
        if self.tray_icon:
            self.tray_icon.hide()
            self.logger.debug("Tray icon hidden")

        self.logger.info("Application shutdown complete")

        # Quit the QApplication
        from PyQt5.QtWidgets import QApplication

        app = QApplication.instance()
        if app:
            app.quit()

    @classmethod
    def instance(cls) -> "Application":
        """Get application instance.

        Returns:
            Application singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
