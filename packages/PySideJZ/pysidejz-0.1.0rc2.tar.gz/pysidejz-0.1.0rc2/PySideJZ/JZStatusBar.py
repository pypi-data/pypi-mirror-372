from typing import Any

import qtawesome as qta
from loguru import logger
from PySide6.QtCore import Property, QMargins, QTimer, Signal, Slot
from PySide6.QtGui import QBrush, QColor, QPainter, QPaintEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from PySideJZ.JZConsts import JZ_STATUS_DEFAULT_COLOR, JZ_STATUS_DEFAULT_EXPIRE_MS


class JZStatusBar(QWidget):
    """JZStatusBar is a simple status bar for logging output that also doubles as progress bar."""

    _refresh = Signal(int)

    # Set up Q-Properties to be useable with QSS stylesheets

    def get_p(self, p: str) -> Any:
        return getattr(self, p, None)

    def set_p(self, value: Any, p: str) -> None:
        curr_p = getattr(self, p, None)
        if curr_p != value:
            setattr(self, p, value)
            self.update()

    """NOTE: FOR Q-PROPERTIES TO BE APPLIED, QT EVENT LOOP MUST BE RUNNING, MEANING, COLORS
    FOR STATUS BAR WILL BE APPLIED ONLY AFTER INITIALIZATION OF THE APPLICATION."""
    error = Property(QColor, lambda o: o.get_p("_error"), lambda o, c: o.set_p(c, "_error"))
    success = Property(QColor, lambda o: o.get_p("_success"), lambda o, c: o.set_p(c, "_success"))
    warning = Property(QColor, lambda o: o.get_p("_warning"), lambda o, c: o.set_p(c, "_warning"))
    info = Property(QColor, lambda o: o.get_p("_info"), lambda o, c: o.set_p(c, "_info"))
    bg = Property(QColor, lambda o: o.get_p("_bg"), lambda o, c: o.set_p(c, "_bg"))
    border = Property(QColor, lambda o: o.get_p("_border"), lambda o, c: o.set_p(c, "_border"))

    def __init__(self, parent: QWidget, h: int = 32) -> None:
        super().__init__(parent)
        self.setObjectName("JZStatusBar")
        self._h = h
        self._w = self.parent().width()
        self._colored_ratio = 0.0

        self._error = self.error
        self._success = self.success
        self._warning = self.warning
        self._info = self.info
        self._bg = self.bg
        self._border = self.border

        self._status = self._error
        self._message = ""
        self._label = QLabel(self._message, contentsMargins=(QMargins(0, 0, 0, 0)))
        self._label.setStyleSheet("background-color: transparent;")

        icon = qta.icon("mdi6.clipboard-text-outline", scale_factor=1.33)
        self.button = QPushButton(self, icon=icon, objectName="JZIconButton")

        layout = QHBoxLayout(self, contentsMargins=QMargins(4, 2, 4, 0))
        layout.addStretch(1)
        layout.addWidget(self._label)
        layout.addStretch(1)
        self.setLayout(layout)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._clear_status_bar)
        self._refresh.connect(self._refresh_progress_bar)

        self._status_levels = {
            "error": self._error,
            "success": self._success,
            "warning": self._warning,
            "info": self._info,
        }

        _ = logger.add(
            lambda msg: self.on_error(msg), format="{message}", filter=self._error_only)

        _ = logger.add(
            lambda msg: self.on_success(msg), format="{message}", filter=self._success_only)

        _ = logger.add(
            lambda msg: self.on_warning(msg), format="{message}", filter=self._warning_only)

        _ = logger.add(
            lambda msg: self.on_info(msg), format="{message}", filter=self._info_only)

        logger.info("JZStatusBar initialized")

    @Slot(int)
    def _refresh_progress_bar(self, timeout_ms: int) -> None:
        """Refresh the status bar and set a timer to clear it after a timeout."""
        self.update()
        self._hide_timer.setSingleShot(True)
        self._hide_timer.start(timeout_ms)

    @Slot()
    def _clear_status_bar(self) -> None:
        """Clear the status bar."""
        self._status = self._info
        self._message = ""
        self.update()

    @Slot(QPaintEvent)
    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002
        """Paint the bar with the status, message, custom colors and adjust button placement."""
        self._w = self.parent().width()
        self.setFixedHeight(self._h)

        painter = QPainter(self, renderHint=QPainter.RenderHint.Antialiasing)

        # handle the case where stylesheet is not set and we need some color
        info_color = self.info if self.info is not None else QColor(JZ_STATUS_DEFAULT_COLOR)
        color = QBrush(info_color) if self._status is None else QBrush(QColor(self._status))
        bg_color = QBrush(self.bg if self.bg is not None else QColor(JZ_STATUS_DEFAULT_COLOR))
        border_color = QBrush(
            self.border if self.border is not None else QColor(JZ_STATUS_DEFAULT_COLOR))

        # handle case where we have progress bar: we will use success status and fill only part of
        # the progress bar that is equivalent to the percentage of the progress, fill remaining
        # part with blank color. Colore ratio 1.0 will be used for the messages of various level.
        colored_width = self.width() * self._colored_ratio
        blank_width = self.width() - colored_width

        # use the painter to fill the box
        painter.fillRect(0, 0, colored_width, self._h, color)  # fill the colored part
        painter.fillRect(colored_width, 0, blank_width, self._h, bg_color)  # fill the blank part
        painter.fillRect(0, 0, self._w, 2, border_color)  # hardcode top border to 2px width

        # if message is more than one line, we will display only the last line
        if "\n" in self._message:
            self._message = self._message.splitlines()[-1]

        # set the text to the status bar that was passed by logger
        self._label.setText(self._message.strip())

        # Calculate button geometry
        button_width = self.button.sizeHint().width()
        button_height = self.button.sizeHint().height()
        x = self.width() - button_width - 1
        y = ((self.height() - button_height) // 2) + 1
        self.button.setGeometry(x, y, button_width, button_height)

    """Slots for the sinks to connect to in order to update the bar with messages/progress."""
    @Slot(float, str)
    def _update_progress_bar(self, ratio: float, extra_message: str = "") -> None:
        self._status = self._success
        self._colored_ratio = ratio
        self._message = f"{extra_message}: {round(int(ratio * 100))} %"
        self._refresh.emit(JZ_STATUS_DEFAULT_EXPIRE_MS)

    def _update_status(self, level: str, message: str) -> None:
        self._status = level
        self._message = message if message else ""
        self._colored_ratio = 1.0
        self._refresh.emit(JZ_STATUS_DEFAULT_EXPIRE_MS)

    @Slot(str)
    def on_error(self, message: str) -> None:
        self._update_status(self._error, message)

    @Slot(str)
    def on_success(self, message: str) -> None:
        self._update_status(self._success, message)

    @Slot(str)
    def on_warning(self, message: str) -> None:
        self._update_status(self._warning, message)

    @Slot(str)
    def on_info(self, message: str) -> None:
        self._update_status(self._info, message)

    def _error_only(self, record: dict) -> bool:
        return record["level"].name == "ERROR"

    def _warning_only(self, record: dict) -> bool:
        return record["level"].name == "WARNING"

    def _info_only(self, record: dict) -> bool:
        return record["level"].name == "INFO"

    def _success_only(self, record: dict) -> bool:
        return record["level"].name == "SUCCESS"

    def _debug_only(self, record: dict) -> bool:
        return record["level"].name == "DEBUG"





