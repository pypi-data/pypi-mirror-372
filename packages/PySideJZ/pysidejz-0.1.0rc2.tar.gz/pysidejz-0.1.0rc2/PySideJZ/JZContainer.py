from functools import wraps
from typing import Any

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from PySideJZ.JZAbvs import JZAbvs


class JZContainer(QFrame):
    """JZContainer is a regular container that can be used to hold widgets.

    Subclassed from QFrame for QSS styling purposes.
    """
    def __init__(
        self,
        parent: Any,
        layout: QHBoxLayout | QVBoxLayout | QGridLayout,
        name: str | None = "Container",
        size_policy: tuple[JZAbvs.Policy, JZAbvs.Policy] = (JZAbvs.Policy.PREF, JZAbvs.Policy.PREF),
        margin: int | None = None,
        margins: tuple[int, int, int, int] = (0, 0, 0, 0),
        spacing: int = 6,
        hspacing: int | None = None,
        vspacing: int | None = None,
    ) -> None:

        super().__init__(parent, mouseTracking=True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._enable_resizing = True

        if not isinstance(layout, (QHBoxLayout | QVBoxLayout | QGridLayout)):
            raise TypeError("layout must be QHBoxLayout, QVBoxLayout or QGridLayout")
        self._layout = layout
        self.setLayout(self._layout)

        self.setSizePolicy(size_policy[0], size_policy[1])
        if margin is not None:
            self._layout.setContentsMargins(margin, margin, margin, margin)
        elif margins is not None:
            self._layout.setContentsMargins(*margins)

        if hspacing is None:
            hspacing = spacing
        if vspacing is None:
            vspacing = spacing

        match layout:
            case QGridLayout():
                self._layout.setHorizontalSpacing(hspacing)
                self._layout.setVerticalSpacing(vspacing)
            case QVBoxLayout() | QHBoxLayout():
                self._layout.setSpacing(spacing)
            case _:
                raise TypeError("layout is expected to be one of Qt layouts")

        if name:
            self.setObjectName(name)

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
    layout = widget.layout()
    layout.addItem(item)

    we can do widget.addItem()
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

    def addItem(self, *args, **kwargs) -> None:
        self._layout.addItem(*args, **kwargs)

    def addWidget(self, *args, **kwargs) -> None:
        self._layout.addWidget(*args, **kwargs)

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

class JZDragPosition:
    """An enumerator that indicates either position or direction of the draggable window
    selectable part."""
    TOP = 0
    BOTTOM = 1
    LEFT = 2
    RIGHT = 3
    VERTICAL = 4
    HORIZONTAL = 5

    @staticmethod
    def stylesheet_property_name(val: "JZDragPosition") -> str:
        """Returns the name of the stylesheet property for the given JZDragPosition value."""
        match val:
            case JZDragPosition.TOP:
                return "onEdgeTop"
            case JZDragPosition.BOTTOM:
                return "onEdgeBottom"
            case JZDragPosition.LEFT:
                return "onEdgeLeft"
            case JZDragPosition.RIGHT:
                return "onEdgeRight"
            case _:
                raise Exception(f"Invalid JZDragPosition value: {val}")

    @staticmethod
    def position_to_direction(val: "JZDragPosition") -> "JZDragPosition":
        """
        Converts a JZDragPosition value to its corresponding direction.
        """
        match val:
            case JZDragPosition.TOP:
                return JZDragPosition.VERTICAL
            case JZDragPosition.BOTTOM:
                return JZDragPosition.VERTICAL
            case JZDragPosition.LEFT:
                return JZDragPosition.HORIZONTAL
            case JZDragPosition.RIGHT:
                return JZDragPosition.HORIZONTAL
            case _:
                raise Exception(f"Invalid JZDragPosition value: {val}")


class JZDraggableFrame(QFrame):
    """Container is expanded/shrunk by dragging the edge of the window.

    NOTE: IMPLEMENTED ONLY FOR MOVEMENT IN VERTICAL DIRECTION SO FAR.

    The frame that is used to expand/shrink the window. It does it by registering the mouse
    events and then calling the resize method. Howering over the edge of the window will active
    onEdge stylesheet property and highlight the edge. The edge is the part of the window that is
    draggable.

    NOTE: For the edge to change the color upon the hover, the following stylesheet properties
    must be implemented:

        - onEdgeTop
        - onEdgeBottom
        - onEdgeLeft
        - onEdgeRight
    """

    def __init__(self, parent: QWidget, position: JZDragPosition) -> None:
        super().__init__(parent=parent, mouseTracking=True)
        self._resizing = False
        self._edge_detection_value = 5
        self._position = position
        self._stylesheet_property = JZDragPosition.stylesheet_property_name(position)
        self._direction = JZDragPosition.position_to_direction(position)
        self._basic_cursor = Qt.CursorShape.ArrowCursor

        self._max_ratio = 0.8
        self._min_ratio = 0.00
        self._default_ratio = 0.6
        self._ratio = self._default_ratio

        # if dragging in the horizontal direction, then get_position() should return the x
        # coordinate of the mouse, otherwise it should return the y coordinate
        match self._direction:
            case JZDragPosition.HORIZONTAL:
                self._get_position = lambda e: e.pos().x()
                self._get_position_in_main_window = \
                    lambda e: self.window().mapFromGlobal(e.globalPos()).x()
                self._expand_cursor = Qt.CursorShape.SplitHCursor
            case JZDragPosition.VERTICAL:
                self._get_position = lambda e: e.pos().y()
                self._get_position_in_main_window = \
                    lambda e: self.window().mapFromGlobal(e.globalPos()).y()
                self._expand_cursor = Qt.CursorShape.SplitVCursor
            case _:
                raise Exception(f"Invalid JZDragPosition value: {self._direction}")

        self.on_edge_apply_style(False)
        self._recalculate_geometry()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Do logic when mouse is on the edge of the draggable container.

        If mouse was pressed on the label, check the locaton of the press.
        If mouse was pressed on the edge, then enable resizing, depending on how mouse is dragged
        The resizing will be enabled until the mouseReleaseEvent is called.
        Moving the cursor will now resize the parent window until the mouse button is released.
        """
        if self.on_edge(event):
            self._resizing = True
            self.on_edge_apply_style(True)
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """On mouse release, disable resizing, moving cursor will not resize the parent anymore."""
        if self._resizing:
            self._resizing = False
            self.on_edge_apply_style(False)
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event) -> None:
        """Do logic when mouse is moved on the edge of the draggable container.

        If mouse is moved on the widget:
        1. Check if mouse near the edge, if so, change the cursor shape
        2. If the mouse is being clicked and dragged, in a desired direction, expand/shrink the
        parent window
        """
        if self.on_edge(event) or self._resizing:
            self.on_edge_apply_style(True)
        else:
            self.on_edge_apply_style(False)

        if self._resizing:
            self.expand(self._get_position_in_main_window(event))

        return super().mouseMoveEvent(event)

    def leaveEvent(self, event: QMouseEvent) -> None:
        """If mouse leaves the widget, reset the stylesheet."""
        if not self._resizing:
            self.on_edge_apply_style(False)
        return super().leaveEvent(event)

    def on_edge(self, event: QMouseEvent) -> bool:
        """Check if the mouse is on the edge so that the stylesheet could be applied."""
        local_position = self._get_position(event)
        match self._position:
            case JZDragPosition.TOP:
                return local_position <= self._edge_detection_value
            case JZDragPosition.LEFT:
                return local_position <= self._edge_detection_value
            case JZDragPosition.BOTTOM:
                h = self.height()
                edge_u = h
                edge_l = h - self._edge_detection_value
                return edge_l <= local_position <= edge_u
            case JZDragPosition.RIGHT:
                w = self.width()
                edge_u = w
                edge_l = w - self._edge_detection_value
                return edge_l <= local_position <= edge_u

    def on_edge_apply_style(self, on_edge: bool) -> None:
        """Apply specific styles for the case when mouse button hovers over the edge.

        This includes the QSS stylesheet property itself and the cursor shape.
        """
        self.setCursor(self._expand_cursor if on_edge else self._basic_cursor)
        self.setProperty(self._stylesheet_property, 1 if on_edge else 0)
        self.style().polish(self)

    def expand(self, y: int) -> None:
        """Expand/shrink the window depending on the y of the mouse movement event."""
        self._ratio = y / self.parent().height()
        self._ratio = min(max(self._ratio, self._min_ratio), self._max_ratio)
        self._recalculate_geometry()

    def resize(self) -> None:
        """Resize the widget."""
        self._recalculate_geometry()

    def _recalculate_geometry(self) -> None:
        """Recalculates geometry according to the ratio and parent size.

        Ratio may be changed only by dragging the bar up or down.
        """
        self._x = 0
        self._w = self.parent().width()
        self._y = int(self.parent().height() * self._ratio)
        self._h = self.parent().height() - self._y
        self.setGeometry(self._x, self._y, self._w, self._h)

    @Slot()
    def toggle(self) -> None:
        """Toggle the visibility of the widget."""
        self.setVisible(not self.isVisible())

    @Slot()
    def open(self) -> None:
        """Show the widget, set the default ratio and recalculate geometry."""
        self._ratio = self._default_ratio
        self._recalculate_geometry()
        self.show()

    @Slot()
    def close(self) -> None:
        """Hide the widget."""
        self.hide()








