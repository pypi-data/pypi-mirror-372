from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from PySideJZ.JZAbvs import JZAbvs
from PySideJZ.JZContainer import JZContainer


class JZTabBar(JZContainer):
    """JZTabBar is similar to QTabBar, difference being that the buttons are stacked vertically.

    QTabBar does not allow doing that without some QPainter trickery, and that messes up the QSS
    stylesheets. Simple implementation is container with buttons inside of it.
    """
    tab_opened = Signal(int)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(
            parent, layout=QVBoxLayout(), size_policy=(JZAbvs.Policy.MAX, JZAbvs.Policy.MAX),
            name="JZTabBar", spacing=0)

        self._buttons: list[QPushButton] = []
        self.setMouseTracking(True)

    def add_button(self, text: str, stretch: int = 0) -> None:
        """
        Add a button to JZTabBar. This will essentially create an entry to a new page to JZTabWidget
        (the button to the page, not the page itself).
        """
        button = QPushButton(parent=self, text=text, checkable=True, objectName="JZTabBarButton")
        if not self._buttons:
            button.setChecked(True)
        button.clicked.connect(lambda: self.check_button_uncheck_others(button))
        self._buttons.append(button)
        self.addWidget(button, stretch=stretch)

    @Slot(QPushButton)
    def check_button_uncheck_others(self, button: QPushButton) -> None:
        """
        For JZTabWidget, one of the tabs will be open, rest will be closed. To indicate that, check
        the button of a tab that will be open and uncheck all the others.
        """
        for i, btn in enumerate(self._buttons):
            if btn == button:
                btn.setChecked(True)
                self.tab_opened.emit(i)
            else:
                btn.setChecked(False)


class JZStackedTab(QStackedWidget):
    """
    JZStackedTab inhereting from QStackedWidget, the only difference being that the widget looks to
    expand as much as possible and has a preset object name for the stylesheet.
    """
    def __init__(self, parent: QWidget) -> None:
        super().__init__(
            parent, objectName="JZStackedTab",
            sizePolicy=(JZAbvs.Policy.MINEX, JZAbvs.Policy.MINEX))


class JZTabWidget(JZContainer):
    """
    JZTabWidget is a simulation of QTabWidget, it contains a JZTabBar and BRLStackedTab. The
    the reason for this is that QTabWidget does not allow to rotate the text inside QTabBar
    without some QPainter trickery, and that messes up the QSS stylesheets
    """
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent, layout=QHBoxLayout(), spacing=0)

        self.stacked_tab = JZStackedTab(self)
        self.tab_bar = JZTabBar(self)
        self.tab_bar.tab_opened.connect(self.stacked_tab.setCurrentIndex)

        self.addWidget(self.tab_bar, alignment=JZAbvs.Align.T | JZAbvs.Align.L)
        self.addWidget(self.stacked_tab, stretch=1)

    def add_tab(self, widget: QWidget, text: str) -> None:
        """
        Add new tab to the tabwidget as in QTabWidget
        """
        self.stacked_tab.addWidget(widget)
        self.tab_bar.add_button(text)
