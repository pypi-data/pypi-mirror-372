import datetime
from collections.abc import Callable

import qtawesome as qta
from loguru import logger
from PySide6.QtCore import QMargins, QTimer, Slot
from PySide6.QtGui import QIcon, QKeySequence, QPaintEvent, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from PySideJZ.JZContainer import JZContainer
from PySideJZ.JZStylesheet import day_mode, night_mode


class JZToolBar(JZContainer):
    """Simple toolbar to go on top of the main window. (HARDCODED FOR TOP POSITION)"""

    def __init__(
        self,
        parent: QWidget,
        home_callback: Callable | None = None,
        settings_callback: Callable | None = None,
        info_callback: Callable | None = None,
        help_callback: Callable | None = None,
    ) -> None:

        super().__init__(parent, name="JZToolBar", layout=QHBoxLayout(), spacing=0)
        self._custom_button_insert_location = 0

        """If a callback is attached to HOME BUTTON press, it means we will use the button and we
        need it, otherwise, we will not create the button. Same logic applies to the rest."""
        if home_callback:
            self._generate_button_functionality(
                icon=qta.icon("mdi6.home", scale_factor=1.33),
                item_name="Home",
                callback=home_callback,
                shortcut="F9")

        if settings_callback:
            self._generate_button_functionality(
                icon=qta.icon("mdi6.hammer-wrench", scale_factor=1.33),
                item_name="Settings",
                callback=settings_callback,
                shortcut="F10")

        if info_callback:
            self._generate_button_functionality(
                icon=qta.icon("mdi6.information-variant", scale_factor=1.5),
                item_name="Info",
                callback=info_callback,
                shortcut="F12")

        if help_callback:
            self._generate_button_functionality(
                icon=qta.icon("mdi6.help", scale_factor=1.1),
                item_name="Help",
                callback=help_callback,
                shortcut="F1")

        self._setup_fullscreen()
        self._setup_night_mode()
        self._setup_clock()

        # widgets need to be added in the specific order
        self.addWidget(self._button_fullscreen)
        self.addWidget(self._button_night_mode)
        self.addStretch(1)
        self.addWidget(self._current_time_label)
        self.addWidget(self._button_minimize)
        self.addWidget(self._button_close)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Override paint event to center the clock label in the toolbar."""
        toolbar_width = self.width()
        toolbar_height = self.height()
        label_width = self._current_time_label.width()
        label_height = self._current_time_label.height()
        x = (toolbar_width - label_width) // 2
        y = (toolbar_height - label_height) // 2
        self._current_time_label.setGeometry(x, y, label_width, label_height)
        super().paintEvent(event)

    def add_custom_button(
        self,
        icon: QIcon,
        item_name: str,
        callback: Callable,
        shortcut: str | None = None,
        ) -> None:
        """Allows user to add custom button to the toolbar."""
        self._generate_button_functionality(
            icon=icon,
            item_name=item_name,
            callback=callback,
            shortcut=shortcut,
            custom=True,
        )

    def _generate_button_functionality(
        self,
        icon: QIcon,
        item_name: str,
        callback: Callable,
        shortcut: str | None = None,
        custom: bool = False,
    ) -> None:
        """Generate functionality for the button given the information, icon, callback and etc."""

        attr_icon = f"_icon_{item_name.lower()}"
        attr_button = f"_button_{item_name.lower()}"
        tooltip = f"{item_name.capitalize()}"
        if shortcut:
            tooltip += f" ({shortcut})"

        setattr(self, attr_icon, icon)
        button = QPushButton(self, icon=icon)
        button.clicked.connect(callback)
        button.setToolTip(tooltip)
        setattr(self, attr_button, button)

        if shortcut:
            shortcut = QShortcut(QKeySequence(shortcut), self.parent())
            shortcut.activated.connect(callback)

        if custom:
            self.insertWidget(self._custom_button_insert_location, button)
        else:
            self.addWidget(button)
        self._custom_button_insert_location += 1

    def _setup_fullscreen(self) -> None:
        """Setup the fullscreen button and its functionality."""

        # enabling/disabling fullscreen requires separate and more complex logic
        # create the button for fullscreen toggle
        self._icon_fullscreen = qta.icon("mdi6.fullscreen", scale_factor=1.66)
        self._icon_exit_fullscreen = qta.icon("mdi6.fullscreen-exit", scale_factor=1.66)
        self._button_fullscreen = QPushButton(self, "E", icon=self._icon_fullscreen)
        self._button_fullscreen.clicked.connect(self._toggle_fullscreen)

        # if not in fullscreen, native controls are shown, else use our own close/minimize
        self._icon_close = qta.icon("mdi6.window-close", scale_factor=1.33)
        self._icon_minimize = qta.icon("mdi6.window-minimize", scale_factor=1.33)
        self._button_minimize = QPushButton(self, icon=self._icon_minimize)
        self._button_close = QPushButton(self, icon=self._icon_close)
        self._button_close.clicked.connect(self.window().close)
        self._button_minimize.clicked.connect(self.window().showMinimized)
        self._show_controls(False)

        shortcut = QShortcut(QKeySequence("F11"), self.parent())
        shortcut.activated.connect(self._toggle_fullscreen)
        self._button_fullscreen.setToolTip("Toggle Fullscreen (F11)")

    def _setup_clock(self) -> None:
        """Setup the clock label and timer to update it every second."""
        self._current_time = self._get_current_time()
        self._time_timer = QTimer(self)
        self._time_timer.timeout.connect(self._update_time)
        self._time_timer.start(1000)
        self._current_time_label = QLabel(
            parent=self, contentsMargins=(QMargins(0, 0, 0, 0)), objectName="JZCurrentTimeLabel")
        self._current_time_label.setText(self._current_time)

    def _setup_night_mode(self) -> None:
        """Setup the night mode toggle functionality."""
        day_mode()
        self._is_night_mode = False
        self._icon_night = qta.icon("mdi6.weather-night", scale_factor=1.33)
        self._icon_day = qta.icon("mdi6.weather-sunny", scale_factor=1.33)
        self._button_night_mode = QPushButton(self, icon=self._icon_night)
        self._button_night_mode.clicked.connect(self._toggle_night_mode)

        shortcut = QShortcut(QKeySequence("Ctrl+N"), self.parent())
        shortcut.activated.connect(self._toggle_night_mode)
        self._button_night_mode.setToolTip("Toggle Night Mode (Ctrl+N)")

    @Slot()
    def _update_time(self) -> None:
        """Update the current time label."""
        new_time = self._get_current_time()
        if new_time != self._current_time:
            self._current_time = new_time
            self._current_time_label.setText(self._current_time)
            self.update()

    def _get_current_time(self) -> str:
        """Get the current time in a formatted string."""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @Slot()
    def enter_fullscreen(self) -> None:
        """Enter fullscreen mode and show custom minimize/close buttons."""
        self.window().showFullScreen()
        self._button_fullscreen.setIcon(self._icon_exit_fullscreen)
        self._show_controls(True)
        logger.info("Entered fullscreen mode")

    @Slot()
    def exit_fullscreen(self) -> None:
        """Exit fullscreen mode and restore the native minimize/close buttons."""
        self.window().showNormal()
        self._button_fullscreen.setIcon(self._icon_fullscreen)
        self._show_controls(False)
        logger.info("Exited fullscreen mode")

    @Slot()
    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        self.exit_fullscreen() if self.window().isFullScreen() else self.enter_fullscreen()

    @Slot(bool)
    def _show_controls(self, show: bool) -> None:
        """Show or hide custom minimize/close buttons."""
        self._button_close.setVisible(show)
        self._button_minimize.setVisible(show)

    @Slot()
    def _toggle_night_mode(self) -> None:
        """Toggle night mode."""
        self.exit_night_mode() if self.is_night_mode() else self.enter_night_mode()

    @Slot()
    def enter_night_mode(self) -> None:
        """Enter night mode."""
        night_mode()
        self._button_night_mode.setIcon(self._icon_day)
        self._is_night_mode = True

    @Slot()
    def exit_night_mode(self) -> None:
        """Exit night mode."""
        day_mode()
        self._button_night_mode.setIcon(self._icon_night)
        self._is_night_mode = False

    def is_night_mode(self) -> bool:
        """Check if the application is in night mode."""
        return self._is_night_mode
