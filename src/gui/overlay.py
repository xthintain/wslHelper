"""Screenshot overlay widget for region selection.

Provides a full-screen transparent overlay for screenshot region selection.
"""

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QCursor
from typing import Optional

from src.utils.logger import get_logger


class ScreenshotOverlay(QWidget):
    """Full-screen transparent overlay for screenshot selection."""

    # Signal emitted when region is selected (left, top, width, height)
    region_selected = pyqtSignal(int, int, int, int)
    # Signal emitted when selection is cancelled
    selection_cancelled = pyqtSignal()

    def __init__(self):
        """Initialize screenshot overlay."""
        super().__init__()
        self.logger = get_logger()

        # Selection state
        self._start_point: Optional[QPoint] = None
        self._current_point: Optional[QPoint] = None
        self._is_selecting = False

        # Setup window
        self._setup_window()

    def _setup_window(self) -> None:
        """Setup full-screen transparent window."""
        # Use simplest possible window configuration
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )

        # Set translucent background
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Get screen geometry and set
        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        self.setGeometry(geometry)

        # Enable mouse tracking
        self.setMouseTracking(True)

        # Set focus policy
        self.setFocusPolicy(Qt.StrongFocus)

        # Set cursor
        self.setCursor(Qt.CrossCursor)

    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        self.logger.debug("Screenshot overlay shown")

    def mousePressEvent(self, event):
        """Handle mouse press - start selection."""
        self.logger.debug(f"Mouse press event: button={event.button()}, pos={event.pos()}")
        if event.button() == Qt.LeftButton:
            self._start_point = event.pos()
            self._current_point = event.pos()
            self._is_selecting = True
            self.update()
            self.logger.info(f"Selection started at {self._start_point}")

    def mouseMoveEvent(self, event):
        """Handle mouse move - update selection."""
        if self._is_selecting:
            self._current_point = event.pos()
            self.update()
            # Don't log every move, too verbose
            # self.logger.debug(f"Mouse move: {self._current_point}")

    def mouseReleaseEvent(self, event):
        """Handle mouse release - finish selection."""
        self.logger.debug(f"Mouse release event: button={event.button()}")
        if event.button() == Qt.LeftButton and self._is_selecting:
            self._is_selecting = False

            if self._start_point and self._current_point:
                # Calculate region
                left = min(self._start_point.x(), self._current_point.x())
                top = min(self._start_point.y(), self._current_point.y())
                width = abs(self._current_point.x() - self._start_point.x())
                height = abs(self._current_point.y() - self._start_point.y())

                # Emit signal
                if width > 0 and height > 0:
                    self.region_selected.emit(left, top, width, height)
                    self.logger.info(
                        f"Region selected: ({left}, {top}, {width}, {height})"
                    )
                else:
                    self.selection_cancelled.emit()

                self.close()

    def keyPressEvent(self, event):
        """Handle key press - ESC to cancel."""
        if event.key() == Qt.Key_Escape:
            self.logger.info("Screenshot cancelled by user (ESC)")
            self.selection_cancelled.emit()
            self.close()

    def paintEvent(self, event):
        """Paint semi-transparent overlay and selection rectangle."""
        painter = QPainter(self)

        # Draw semi-transparent background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        # Draw selection rectangle if selecting
        if self._is_selecting and self._start_point and self._current_point:
            # Calculate selection rectangle
            left = min(self._start_point.x(), self._current_point.x())
            top = min(self._start_point.y(), self._current_point.y())
            width = abs(self._current_point.x() - self._start_point.x())
            height = abs(self._current_point.y() - self._start_point.y())

            selection_rect = QRect(left, top, width, height)

            # Clear selection area (make it visible)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(selection_rect, Qt.transparent)

            # Draw border
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            pen = QPen(QColor(0, 120, 215), 2)  # Blue border
            painter.setPen(pen)
            painter.drawRect(selection_rect)

    def show_overlay(self) -> None:
        """Show the overlay in full screen."""
        # Show window
        self.show()
        self.showFullScreen()

        # Bring to front and activate
        self.raise_()
        self.activateWindow()
        self.setFocus()

        self.logger.debug("Overlay shown and activated")

    def closeEvent(self, event):
        """Handle close event."""
        super().closeEvent(event)
        self.logger.debug("Overlay closed")
