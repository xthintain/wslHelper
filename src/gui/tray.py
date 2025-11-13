"""System tray icon with context menu.

Provides system tray icon with right-click menu for Settings, About, and Exit.
"""

from PyQt5.QtWidgets import (
    QSystemTrayIcon,
    QMenu,
    QAction,
    QMessageBox,
    QApplication,
    QStyle,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal
from typing import Optional

from src.utils.logger import get_logger


class SystemTray(QObject):
    """System tray icon manager."""

    # Signals
    screenshot_requested = pyqtSignal()  # New signal for manual screenshot
    settings_requested = pyqtSignal()
    exit_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize system tray.

        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        self.logger = get_logger()

        self._tray_icon: Optional[QSystemTrayIcon] = None
        self._menu: Optional[QMenu] = None

        self._setup_tray()

    def _setup_tray(self) -> None:
        """Setup system tray icon and menu."""
        # Create tray icon
        self._tray_icon = QSystemTrayIcon(self)

        # Set icon - use system default camera/application icon
        # Try to use a system icon as fallback
        app = QApplication.instance()
        if app:
            style = app.style()
            # Use SP_ComputerIcon as a visible default icon
            icon = style.standardIcon(QStyle.SP_ComputerIcon)
            self._tray_icon.setIcon(icon)
            self.logger.info("Using system default icon for tray")
        else:
            # Fallback: try to create a simple pixmap icon
            from PyQt5.QtGui import QPixmap, QPainter, QColor
            from PyQt5.QtCore import QSize

            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(0, 120, 215))  # Blue color
            painter = QPainter(pixmap)
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(pixmap.rect(), 0x0084, "S")  # Draw "S" for Screenshot
            painter.end()

            icon = QIcon(pixmap)
            self._tray_icon.setIcon(icon)
            self.logger.info("Using custom pixmap icon for tray")

        # Set tooltip
        self._tray_icon.setToolTip("WSL Screenshot Tool")

        # Create context menu
        self._create_menu()

        # Connect signals
        self._tray_icon.activated.connect(self._on_tray_activated)

        self.logger.debug("System tray initialized")

    def _create_menu(self) -> None:
        """Create tray icon context menu."""
        self._menu = QMenu()

        # Screenshot action (NEW - manual trigger)
        screenshot_action = QAction("截图 (&C)", self)
        screenshot_action.triggered.connect(self._on_screenshot_clicked)
        self._menu.addAction(screenshot_action)

        # Separator
        self._menu.addSeparator()

        # Settings action
        settings_action = QAction("设置 (&S)", self)
        settings_action.triggered.connect(self._on_settings_clicked)
        self._menu.addAction(settings_action)

        # Separator
        self._menu.addSeparator()

        # About action
        about_action = QAction("关于 (&A)", self)
        about_action.triggered.connect(self._on_about_clicked)
        self._menu.addAction(about_action)

        # Separator
        self._menu.addSeparator()

        # Exit action
        exit_action = QAction("退出 (&X)", self)
        exit_action.triggered.connect(self._on_exit_clicked)
        self._menu.addAction(exit_action)

        # Set menu to tray icon
        self._tray_icon.setContextMenu(self._menu)

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle tray icon activation.

        Args:
            reason: Activation reason
        """
        if reason == QSystemTrayIcon.DoubleClick:
            # Double-click shows settings
            self.logger.debug("Tray icon double-clicked")
            self.settings_requested.emit()

    def _on_screenshot_clicked(self) -> None:
        """Handle screenshot menu item click."""
        self.logger.info("Screenshot requested from tray menu")
        self.screenshot_requested.emit()

    def _on_settings_clicked(self) -> None:
        """Handle settings menu item click."""
        self.logger.info("Settings requested from tray menu")
        self.settings_requested.emit()

    def _on_about_clicked(self) -> None:
        """Handle about menu item click."""
        self.logger.info("About dialog requested")

        # Show about dialog
        QMessageBox.about(
            None,
            "关于 WSL Screenshot Tool",
            "<h3>WSL Screenshot Tool</h3>"
            "<p>版本: 1.0.0</p>"
            "<p>Windows平台下的截图工具，专为WSL用户设计</p>"
            "<p>功能:</p>"
            "<ul>"
            "<li>全局快捷键触发截图</li>"
            "<li>自动转换Windows路径为WSL路径</li>"
            "<li>自动复制路径到剪贴板</li>"
            "</ul>"
            "<p>技术栈: Python + PyQt5 + mss + pynput</p>"
            "<p><a href='https://github.com/your-repo'>GitHub</a></p>",
        )

    def _on_exit_clicked(self) -> None:
        """Handle exit menu item click."""
        self.logger.info("Exit requested from tray menu")

        # Confirm exit
        reply = QMessageBox.question(
            None,
            "确认退出",
            "确定要退出WSL Screenshot Tool吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.exit_requested.emit()

    def show(self) -> None:
        """Show tray icon."""
        if self._tray_icon:
            self._tray_icon.show()
            self.logger.info("System tray icon shown")

    def hide(self) -> None:
        """Hide tray icon."""
        if self._tray_icon:
            self._tray_icon.hide()
            self.logger.info("System tray icon hidden")

    def show_message(
        self,
        title: str,
        message: str,
        icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.Information,
        duration: int = 3000,
    ) -> None:
        """Show tray message balloon.

        Args:
            title: Message title
            message: Message content
            icon: Message icon type
            duration: Display duration in milliseconds
        """
        if self._tray_icon and self._tray_icon.isVisible():
            self._tray_icon.showMessage(title, message, icon, duration)
            self.logger.debug(f"Tray message shown: {title}")

    def is_visible(self) -> bool:
        """Check if tray icon is visible.

        Returns:
            True if visible, False otherwise
        """
        return self._tray_icon.isVisible() if self._tray_icon else False
