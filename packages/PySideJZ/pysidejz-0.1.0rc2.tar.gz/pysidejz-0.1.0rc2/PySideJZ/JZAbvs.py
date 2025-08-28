"""File contains most commonly used abbreviations so that the code is less lengthy."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy


class JZAbvs:
    class Align:
        C = Qt.AlignmentFlag.AlignCenter
        HC = Qt.AlignmentFlag.AlignHCenter
        VC = Qt.AlignmentFlag.AlignVCenter
        L = Qt.AlignmentFlag.AlignLeft
        R = Qt.AlignmentFlag.AlignRight
        B = Qt.AlignmentFlag.AlignBottom
        T = Qt.AlignmentFlag.AlignTop
        J = Qt.AlignmentFlag.AlignJustify

    class Policy:
        EX = QSizePolicy.Policy.Expanding
        MINEX = QSizePolicy.Policy.MinimumExpanding
        MIN = QSizePolicy.Policy.Minimum
        MAX = QSizePolicy.Policy.Maximum
        PREF = QSizePolicy.Policy.Preferred
        IGN = QSizePolicy.Policy.Ignored
        FIX = QSizePolicy.Policy.Fixed
