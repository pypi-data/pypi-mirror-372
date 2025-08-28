from PySide6.QtWidgets import QFrame


class JZVLine(QFrame):
    """
    A regular vertical line with variable fixed width.

    NOTE: For line to be visible a 'background-color' property must be set.
    """
    def __init__(self, parent, width: int = 2) -> None:
        super().__init__(parent, fixedWidth=width, frameShadow=QFrame.Shadow.Sunken)


class JZHLine(QFrame):
    """
    A regular horizontal line with variable fixed height.

    NOTE: For line to be visible a 'background-color' property must be set.
    """
    def __init__(self, parent, height: int = 2) -> None:
        super().__init__(parent, fixedHeight=height, frameShadow=QFrame.Shadow.Sunken)
