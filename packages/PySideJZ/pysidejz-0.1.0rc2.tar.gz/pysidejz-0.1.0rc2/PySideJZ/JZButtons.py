from PySide6.QtWidgets import QPushButton


class JZFireButton(QPushButton):
    """A button that is used to trigger an action (ON/OFF).

    All checked/unchecked states are handled manually in code.
    User clicks do not toggle the checked state automatically.
    """

    def __init__(self, text_on: str, text_off: str, parent=None):
        super().__init__(text_off, parent)
        self._text_on = text_on
        self._text_off = text_off
        self.setCheckable(True)
        self.setObjectName("JZFireButton")
        self._checked_state = False

    def nextCheckState(self):
        # Prevent automatic toggling
        pass

    def set_on(self):
        self.setChecked(True)
        self._checked_state = True
        self.setText(self._text_on)

    def set_off(self):
        self.setChecked(False)
        self._checked_state = False
        self.setText(self._text_off)
