"""Application entry point with privilege check and QApplication initialization.

This module serves as the main entry point for the WSL Screenshot Tool,
handling privilege checks, Qt application initialization, and application startup.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

from src.utils.logger import get_logger
from src.system.privilege import check_admin, request_admin
from src.utils.single_instance import SingleInstance


def main():
    """Main application entry point."""
    logger = get_logger()

    # Check for single instance
    single_instance = SingleInstance("WSLScreenshot")
    if single_instance.is_already_running():
        logger.warning("Another instance is already running. Exiting.")
        # Show message to user
        app = QApplication(sys.argv)
        QMessageBox.warning(
            None,
            "WSL Screenshot Tool",
            "程序已经在运行中！\n\n请在系统托盘中查找图标。",
        )
        sys.exit(0)

    logger.info("Single instance check passed")

    # Check for admin privileges
    if not check_admin():
        logger.warning("Application started without administrator privileges")
        # Note: Admin privileges are recommended but not required
        # User will be notified through the UI if needed

    logger.info("Starting WSL Screenshot Tool")

    # Enable high DPI scaling BEFORE creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("WSL Screenshot Tool")
    app.setApplicationVersion("1.0.0")
    app.setQuitOnLastWindowClosed(False)  # Keep running when windows are closed

    logger.info("QApplication created successfully")

    # Import here to avoid circular imports
    from src.app import Application

    try:
        # Create and initialize application
        application = Application()
        application.initialize()

        logger.info("Application initialized successfully")

        # Start event loop
        exit_code = app.exec_()

        # Cleanup single instance lock
        single_instance.cleanup()

        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"Application failed to start: {e}", exc_info=True)
        single_instance.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
