import os
import platform
from collections.abc import Callable
from enum import Enum
from pathlib import Path

import qtawesome as qta
from loguru import logger
from PySide6.QtCore import QMargins, Qt, Signal, Slot
from PySide6.QtGui import QColor, QKeySequence, QMouseEvent, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from PySideJZ.JZContainer import JZContainer, JZDraggableFrame, JZDragPosition
from PySideJZ.JZStatusBar import JZStatusBar


class JZLogLevel(str, Enum):
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"

class JZLoggerWidget(QListWidget):
    """
    JZLoggerWidget is a custom widget that contains the logs that are passed by loguru logger,
    displaying them in a QListWidget.
    """
    _log_error = Signal(str)
    _log_success = Signal(str)
    _log_warning = Signal(str)
    _log_info = Signal(str)
    _log_debug = Signal(str)

    def __init__(
        self,
        parent: QWidget,
        default_log_directory: str | None = None,
        max_items: int = 999,
        debug: bool = False,
    ):
        super().__init__(parent, mouseTracking=True)
        self.setContentsMargins(0, 0, 0, 0)
        self._debug = debug
        self._max_items = max_items
        self.setObjectName("JZLoggerWidget")

        self._log_error.connect(self._on_error)
        self._log_success.connect(self._on_success)
        self._log_warning.connect(self._on_warning)
        self._log_info.connect(self._on_info)
        self._log_debug.connect(self._on_debug)

        # callback for the aforementioned log levels if something else needs to be done
        self._cb_error = []
        self._cb_success = []
        self._cb_warning = []
        self._cb_info = []
        self._cb_debug = []

        # message formats to be used
        self._fmt = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<7} | -> {message}"
        self._fmt_msg_only = "{message}"
        self._fmt_all = (
            "[{time:YYYY-MM-DD HH:mm:ss.SSS}][{level}]"
            "[line {line}: {name}.{function}] --> {message}"
        )

        # declare sinks for all of the logger types
        _ = logger.add(
            lambda item: self._log_error.emit(item), format=self._fmt, filter=self._error_only,
            backtrace=True)

        _ = logger.add(
            lambda msg: self._log_success.emit(msg), format=self._fmt, filter=self._success_only)

        _ = logger.add(
            lambda msg: self._log_warning.emit(msg), format=self._fmt, filter=self._warning_only)

        _ = logger.add(
            lambda msg: self._log_info.emit(msg), format=self._fmt, filter=self._info_only)

        _ = logger.add(
            lambda msg: self._log_debug.emit(msg), format=self._fmt, filter=self._debug_only)

        # enable scrollbars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self._log_levels = {
            JZLogLevel.ERROR: (self._log_error, QColor("red"), self._cb_error),
            JZLogLevel.SUCCESS: (self._log_success, QColor("green"), self._cb_success),
            JZLogLevel.WARNING: (self._log_warning, QColor("orange"), self._cb_warning),
            JZLogLevel.INFO: (self._log_info, None, self._cb_info),
            JZLogLevel.DEBUG: (self._log_debug, None, self._cb_debug),
        }

        if default_log_directory:
            _ = self.init_logger_file_sink(default_log_directory)
        logger.info("JZLoggerWidget initialized")

    def _create_logger_all_sink(self, directory: str) -> bool:
        """Create a sink for all log levels."""
        timestamp = "{time:YYYY_MM_DD____HH_mm_ss}"
        filename = f"{platform.node()}__{timestamp}.log"
        full_log_path = str(Path(directory) / filename)

        timestamp = "{time:YYYY_MM_DD____HH_mm_ss}"
        filename = f"{platform.node()}__{timestamp}.log"
        full_log_path = str(Path(directory) / filename)

        old_sink = getattr(self, "logger_sink_all", None)
        try:
            new_sink = logger.add(
                full_log_path, format=self._fmt_all, rotation="10 MB", retention="10 days",
                opener=self._log_file_opener)
        except PermissionError:
            logger.error(
                f"The app does not have permission to write log to the directory: {directory}")
            return False
        except FileNotFoundError:
            logger.error(
                f"The directory {directory} does not exist, cannot create log file sink.")
            return False
        else:
            if old_sink is not None:
                logger.remove(old_sink)
            self.logger_sink_all = new_sink
            logger.info("Logger file sink successfully created")
            return True

    def init_logger_file_sink(self, directory: str) -> bool:
        """Reinitialize the logger with a new directory."""
        return self._create_logger_all_sink(directory)

    def enable_debug(self, enable: bool):
        self._debug = enable
    def _log_file_opener(self, file: str, flags: int) -> int:
        return os.open(file, flags, 0o777)

    def sub_callback(self, level: str, cb: Callable[[str], None]):
        """
        Calling this allows to attach a callback to the logger for a specific log level.
        """
        match (level):
            case JZLogLevel.ERROR:
                self._cb_error.append(cb)
            case JZLogLevel.SUCCESS:
                self._cb_success.append(cb)
            case JZLogLevel.WARNING:
                self._cb_warning.append(cb)
            case JZLogLevel.INFO:
                self._cb_info.append(cb)
            case JZLogLevel.DEBUG:
                self._cb_debug.append(cb)
            case _:
                raise Exception(f"Unknown log level: {level}")

    def unsub_callback(self, level: str, cb: Callable[[str], None]):
        """
        Unsubscribing from a callback for a specific log level.
        """
        match (level):
            case JZLogLevel.ERROR:
                self._cb_error.remove(cb)
            case JZLogLevel.SUCCESS:
                self._cb_success.remove(cb)
            case JZLogLevel.WARNING:
                self._cb_warning.remove(cb)
            case JZLogLevel.INFO:
                self._cb_info.remove(cb)
            case JZLogLevel.DEBUG:
                self._cb_debug.remove(cb)
            case _:
                raise Exception(f"Unknown log level: {level}")

    def add_item(self, item: QListWidgetItem):
        """
        Add a log message to the list widget. Having more than self._max_items will remove the
        oldest item.
        """
        if self.count() >= self._max_items:
            self.takeItem(0)
        self.addItem(item)

    def _handle_log(self, level: JZLogLevel, message: str):
        signal, color, callbacks = self._log_levels[level]
        if level == JZLogLevel.DEBUG and not self._debug:
            return

        item = QListWidgetItem(message.strip())
        if color:
            item.setBackground(color)
        self.add_item(item)
        self.scrollToBottom()

        for cb in callbacks:
            cb(message)

    @Slot(str)
    def _on_error(self, message: str):
        self._handle_log(JZLogLevel.ERROR, message)

    @Slot(str)
    def _on_success(self, message: str):
        self._handle_log(JZLogLevel.SUCCESS, message)

    @Slot(str)
    def _on_warning(self, message: str):
        self._handle_log(JZLogLevel.WARNING, message)

    @Slot(str)
    def _on_info(self, message: str):
        self._handle_log(JZLogLevel.INFO, message)

    @Slot(str)
    def _on_debug(self, message: str):
        self._handle_log(JZLogLevel.DEBUG, message)

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

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        return super().mouseMoveEvent(event)

class JZLoggerTab(JZDraggableFrame):
    """
    LoggerTab is a widget that will be overlaid on top of everything when the log window is opened.
    It will contain a layout with following:

    1. The logger widget iself (QTableWidget)
    2. A button to close the logger window
    3. The label that is draggable to expand/shrink the height of the tab

    NOTE: THE PARENT ITSELF MUST CALL THE .resize() METHOD TO RESIZE THE WIDGET TO FIT THE PARENT
    """
    def __init__(
        self,
        parent: QWidget,
        position: JZDragPosition,
        log_directory: str | None,
        status_bar: JZStatusBar | None = None,
    ):
        super().__init__(parent, position)
        self.setObjectName("ColorInBackground")
        """
        Create a new layout and set the new layout as the layout of this widget. The widget will be
        overlaid on top of the application and will be draggable to expand/shrink.
        """
        self._layout = QVBoxLayout(spacing=0, contentsMargins=QMargins(0, 0, 0, 0))
        self.setLayout(self._layout)
        self._logger_widget = JZLoggerWidget(self, log_directory)

        # top bar with text and close button
        self._label = QLabel("Log", mouseTracking=True)
        self._label.setContentsMargins(QMargins(0, 0, 0, 0))

        # button for closing the logger tab
        icon = qta.icon("mdi6.window-close", scale_factor=1.33)
        self._button_close = QPushButton(self, icon=icon, objectName="JZIconButton")
        self._button_close.clicked.connect(self.hide)
        self.hide()

        # if we have a status bar, we will connect it to the logger widget
        if status_bar:
            status_bar.button.clicked.connect(self.show)

        # container for button + label
        self._top_container = JZContainer(
            self, layout=QHBoxLayout(), spacing=0, name="JZLoggerTabTop")
        self._top_container.setContentsMargins(0, 0, 0, 0)
        self._top_container.addMultiple([self._label, 1, self._button_close])
        self._top_container.setMouseTracking(True)

        # shortcut for closing/opening the logger tab with CTRL+L
        shortcut = QShortcut(QKeySequence("CTRL+L"), parent)
        shortcut.activated.connect(self.toggle)

        self._layout.addWidget(self._top_container)
        self._layout.addWidget(self._logger_widget)

        logger.info("JZLoggerTab initialized")

    @Slot()
    def toggle(self):
        self.setVisible(not self.isVisible())

    def init_logger_file_sink(self, directory: str) -> bool:
        """Reinitialize the logger with a new directory."""
        return self._logger_widget.init_logger_file_sink(directory)
