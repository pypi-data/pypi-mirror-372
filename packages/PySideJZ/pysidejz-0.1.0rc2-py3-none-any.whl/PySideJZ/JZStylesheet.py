from functools import lru_cache

from loguru import logger
from PySide6.QtCore import QFile, QTextStream, Slot
from PySide6.QtWidgets import QApplication

from PySideJZ.stylesheet import stylesheet  # noqa: F401  # MUST BE IMPORTED TO LOAD STYLESHEET

_is_night_mode = False

def _get_stylesheet_stream(string: str) -> str:
    file = QFile(string)
    file.open(QFile.OpenModeFlag.ReadOnly)
    return QTextStream(file).readAll()


@lru_cache(maxsize=1)
def get_dark_blue_stylesheet():
    return _get_stylesheet_stream(":/dark-blue/stylesheet.qss")


@lru_cache(maxsize=1)
def get_light_blue_stylesheet():
    return _get_stylesheet_stream(":/light-blue/stylesheet.qss")


@Slot()
def night_mode():
    global _is_night_mode  # noqa: PLW0603
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("No QApplication instance found. Create an application first.")
    app.setStyleSheet(get_dark_blue_stylesheet())
    _is_night_mode = True
    logger.info("Night mode activated")


@Slot()
def day_mode():
    global _is_night_mode  # noqa: PLW0603
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("No QApplication instance found. Create an application first.")
    app.setStyleSheet(get_light_blue_stylesheet())
    _is_night_mode = False
    logger.info("Day mode activated")


@Slot()
def toggle_mode():
    day_mode() if _is_night_mode else night_mode()

