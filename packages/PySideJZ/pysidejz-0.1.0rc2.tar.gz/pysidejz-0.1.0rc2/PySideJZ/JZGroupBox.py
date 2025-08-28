from functools import wraps
from typing import Any

from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from PySideJZ.JZAbvs import JZAbvs


class JZGroupBox(QGroupBox):
    """JZGroupBox is a boilerplate QGroupBox that has most commonly settings used for me."""
    def __init__(
        self,
        parent: QWidget,
        layout: QVBoxLayout | QHBoxLayout | QGridLayout,
        title: str = "",
        name: str | None = "GroupBoxSmall",
        size_policy: tuple[JZAbvs.Policy, JZAbvs.Policy] = (JZAbvs.Policy.PREF, JZAbvs.Policy.PREF),
        margin: int | None = None,
        margins: tuple[int, int, int, int] | None = None,
        spacing: int = 6,
        hspacing: int | None = None,
        vspacing: int | None = None,
    ) -> None:

        super().__init__(parent=parent)

        if not isinstance(layout, (QHBoxLayout | QVBoxLayout | QGridLayout)):
            raise TypeError("layout must be QHBoxLayout, QVBoxLayout or QGridLayout")

        self._layout = layout
        self.setLayout(self._layout)
        self.setSizePolicy(size_policy[0], size_policy[1])
        self.setTitle(title)
        if name:
            self.setObjectName(name)

        if hspacing is None:
            hspacing = spacing
        if vspacing is None:
            vspacing = spacing

        if margin is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        elif margins is not None:
            self.setContentsMargins(*margins)

        match layout:
            case QGridLayout():
                self._layout.setHorizontalSpacing(hspacing)
                self._layout.setVerticalSpacing(vspacing)
            case QVBoxLayout() | QHBoxLayout():
                self._layout.setSpacing(spacing)
            case _:
                raise TypeError("layout is expected to be one of Qt layouts")

    def check_if_grid_layout(method) -> Any:
        """Decorator to check if layout is QGridLayout before executing the method."""
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if not isinstance(self._layout, QGridLayout):
                raise TypeError(f"{method.__name__}: layout must be QGridLayout")
            return method(self, *args, **kwargs)
        return wrapper

    def check_if_linear_layout(method) -> Any:
        """Decorator to check if layout is QVBoxLayout/QHBoxLayout before executing the method."""
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if not isinstance(self._layout, QVBoxLayout | QHBoxLayout):
                raise TypeError(f"{method.__name__}: layout must be QVBoxLayout or QHBoxLayout")
            return method(self, *args, **kwargs)
        return wrapper

    """Override methods to set layour properties, add items and etc.

    This is done to avoid using self._layout directly, so that the code is more readable

    e.g. instead of:
    layout = groupbox.layout()
    layout.addItem(item)

    we can do groupbox.addItem()
    """
    def setSpacing(self, *args, **kwargs) -> None:
        self._layout.setSpacing(*args, **kwargs)

    @check_if_grid_layout
    def setVerticalSpacing(self, *args, **kwargs) -> None:
        self._layout.setVerticalSpacing(*args, **kwargs)

    @check_if_grid_layout
    def setHorizontalSpacing(self, *args, **kwargs) -> None:
        self._layout.setHorizontalSpacing(*args, **kwargs)

    @check_if_linear_layout
    def addSpaceItem(self, *args, **kwargs) -> None:
        self._layout.addSpacerItem(*args, **kwargs)

    @check_if_linear_layout
    def addSpacing(self, *args, **kwargs) -> None:
        self._layout.addSpacing(*args, **kwargs)

    @check_if_linear_layout
    def addStretch(self, *args, **kwargs) -> None:
        self._layout.addStretch(*args, **kwargs)

    @check_if_linear_layout
    def setStretch(self, *args, **kwargs) -> None:
        self._layout.setStretch(*args, **kwargs)

    @check_if_grid_layout
    def setRowStretch(self, *args, **kwargs) -> None:
        self._layout.setRowStretch(*args, **kwargs)

    @check_if_grid_layout
    def setColumnStretch(self, *args, **kwargs) -> None:
        self._layout.setColumnStretch(*args, **kwargs)

    @check_if_linear_layout
    def insertWidget(self, *args, **kwargs) -> None:
        self._layout.insertWidget(*args, **kwargs)

    def addWidget(self, *args, **kwargs) -> None:
        self._layout.addWidget(*args, **kwargs)

    def addItem(self, *args, **kwargs) -> None:
        self._layout.addItem(*args, **kwargs)

    def addLayout(self, *args, **kwargs) -> None:
        self._layout.addLayout(*args, **kwargs)

    def addMultiple(
        self,
        items: list[Any],
        row: int | None = None,
        column: int | None = None,
    ) -> None:
        """
        Add multiple widgets in one call instead of having to call addWidget multiple times.

        Args:
            widgets (list[QWidget]): List of widgets to add.

            row (int | None, optional): If layout is QGridLayout, then row and column are required.
            If layout is QVBoxLayout or QHBoxLayout, then row and column are ignored. Default to
            None.

            column (int | None, optional): If layout is QGridLayout, then row and column are
            required. If layout is QVBoxLayout or QHBoxLayout, then row and column are ignored.
            Default to None.
        """
        if isinstance(self._layout, QGridLayout):
            for i, widget in enumerate(items):
                if isinstance(widget, str):
                    self._layout.addWidget(QLabel(widget), row, column + i)
                elif isinstance(widget, QSpacerItem):
                    self._layout.addItem(widget, row, column + i)
                elif isinstance(widget, QWidget):
                    self._layout.addWidget(widget, row, column + i)
                else:
                    raise TypeError(f"Expected QWidget or variation, but got {type(widget)}")
        else:
            for widget in items:
                if isinstance(widget, str):
                    self._layout.addWidget(QLabel(widget))
                elif isinstance(widget, int):
                    self._layout.addStretch(widget)
                elif isinstance(widget, QSpacerItem):
                    self._layout.addItem(widget)
                elif isinstance(widget, QWidget):
                    self._layout.addWidget(widget)
                else:
                    raise TypeError(f"Expected QWidget or variation, but got {type(widget)}")
