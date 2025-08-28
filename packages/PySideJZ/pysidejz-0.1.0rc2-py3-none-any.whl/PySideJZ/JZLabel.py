from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QLabel, QWidget

from PySideJZ.JZAbvs import JZAbvs


class JZLabel(QLabel):
    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(text=text, parent=parent)
        self.setSizePolicy(JZAbvs.Policy.MAX, JZAbvs.Policy.MINEX)
        self.setWordWrap(True)


class JZStatusLabel(QLabel):
    """A label that is used for status display, such as 'Connected', 'Disconnected', etc.

    Has connected signals that change stylesheet of the label (takes it from QSS file).
    Therefore, QSS file must be loaded when using this class, otherwise the colorings
    will not work.

    It is possible to provide a default status text for each of the states, if state will
    not be used, pass empty string as the default status text.
    """

    class Status:
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"
        CONNECTING = "Connecting"
        NEUTRAL = "Neutral"
        INFO = "Info"

    connected = Signal()
    disconnected = Signal()
    connecting = Signal()
    neutral = Signal()
    info = Signal()

    def __init__(
        self,
        parent: QWidget,
        init_status: str = Status.NEUTRAL,
        status_texts: tuple[str, str, str, str, str] = (
            "Connected",
            "Disconnected",
            "Connecting",
            "Disconnected",
            "Disconnected",
        ),
    ) -> None:
        super().__init__(parent=parent)
        self.setObjectName("JZStatusLabel")
        self.setSizePolicy(JZAbvs.Policy.MINEX, JZAbvs.Policy.MINEX)
        self.setWordWrap(True)
        self.status = init_status

        if len(status_texts) != 5 or (not isinstance(status_texts, tuple)):  # noqa: PLR2004
            raise ValueError("status_texts must be a tuple of 5 strings")
        if not all(isinstance(text, str) for text in status_texts):
            raise TypeError("All status_texts tuple elements must be strings")
        self._status_texts = status_texts

        self.connected.connect(self._on_connected)
        self.disconnected.connect(self._on_disconnected)
        self.connecting.connect(self._on_connecting)
        self.neutral.connect(self._on_neutral)
        self.info.connect(self._on_info)

        match init_status:
            case self.Status.CONNECTED: self.connected.emit()  # noqa: E701
            case self.Status.DISCONNECTED: self.disconnected.emit()  # noqa: E701
            case self.Status.CONNECTING: self.connecting.emit()  # noqa: E701
            case self.Status.NEUTRAL: self.neutral.emit()  # noqa: E701
            case self.Status.INFO: self.info.emit()  # noqa: E701
            case _: raise ValueError(f"Unknown status for JZStatusLabel: {init_status}")  # noqa: E701

    @Slot()
    def _on_connected(self) -> None:
        self.setProperty("onLabelStatus", "On")
        self.style().polish(self)
        self.setText(self._status_texts[0])
        self.status = self.Status.CONNECTED

    @Slot()
    def _on_disconnected(self) -> None:
        self.setProperty("onLabelStatus", "Off")
        self.style().polish(self)
        self.setText(self._status_texts[1])
        self.status = self.Status.DISCONNECTED

    @Slot()
    def _on_connecting(self) -> None:
        self.setProperty("onLabelStatus", "Ongoing")
        self.style().polish(self)
        self.setText(self._status_texts[2])
        self.status = self.Status.CONNECTING

    @Slot()
    def _on_neutral(self) -> None:
        self.setProperty("onLabelStatus", "Neutral")
        self.style().polish(self)
        self.setText(self._status_texts[3])
        self.status = self.Status.NEUTRAL

    @Slot()
    def _on_info(self) -> None:
        self.setProperty("onLabelStatus", "Info")
        self.style().polish(self)
        self.setText(self._status_texts[4])
        self.status = self.Status.INFO


class JZMeasLabel(QLabel):
    """The label that is used to display measurements and highlight in a specific way.

    When making measurements, we want to highlight label in a specific way, e.g. measurement
    failed, or not, we want it usually centered and bolded."""

    class Status:
        PASS = "Pass"
        FAIL = "Fail"
        HOLD = "Hold"
        NEUTRAL = "Neutral"

    passed = Signal()
    failed = Signal()
    hold = Signal()
    neutral = Signal()
    reset = Signal()
    update_measurement = Signal(float)
    update_ongoing = Signal(float)

    def __init__(
        self,
        parent: QWidget,
        minimum_value: float,
        maximum_value: float,
        suffix: str | None = None,
        decimal_precision: int = 3,
        default_value: float = 0.0,
    ) -> None:
        super().__init__(parent=parent)
        self.setObjectName("JZMeasLabel")
        self.setSizePolicy(JZAbvs.Policy.MINEX, JZAbvs.Policy.MINEX)
        self.setWordWrap(False)
        self.status = JZMeasLabel.Status.NEUTRAL
        self._suffix = suffix
        self._decimal_precision = decimal_precision
        self._min = minimum_value
        self._max = maximum_value
        self._default_value = default_value

        self.passed.connect(self._on_passed)
        self.failed.connect(self._on_failed)
        self.hold.connect(self._on_hold)
        self.neutral.connect(self._on_neutral)
        self.update_measurement.connect(self._on_update_measurement)
        self.update_ongoing.connect(self._on_update_ongoing)
        self.reset.connect(self._on_reset)
        self.reset.emit()

    @Slot()
    def _on_passed(self) -> None:
        self.setProperty("onLabelStatus", "On")
        self.style().polish(self)
        self.status = JZMeasLabel.Status.PASS

    @Slot()
    def _on_failed(self) -> None:
        self.setProperty("onLabelStatus", "Off")
        self.style().polish(self)
        self.status = JZMeasLabel.Status.FAIL

    @Slot()
    def _on_hold(self) -> None:
        self.setProperty("onLabelStatus", "Ongoing")
        self.style().polish(self)
        self.status = JZMeasLabel.Status.HOLD

    @Slot()
    def _on_neutral(self) -> None:
        self.setProperty("onLabelStatus", "Neutral")
        self.style().polish(self)
        self.status = JZMeasLabel.Status.NEUTRAL

    @Slot(float)
    def _on_update_measurement(self, measurement: float) -> None:
        """Update the measurement text in the label."""
        self.setText(
            f"{measurement:.{self._decimal_precision}f} {self._suffix if self._suffix else ''}")
        if self._min <= measurement <= self._max:
            self._on_passed()
        else:
            self._on_failed()

    @Slot()
    def _on_update_ongoing(self, measurement: float) -> None:
        """Update the measurement text in the label while the measurement is ongoing."""
        self.setText(
            f"{measurement:.{self._decimal_precision}f} {self._suffix if self._suffix else ''}")
        if self._min <= measurement <= self._max:
            self._on_passed()
        else:
            self._on_hold()

    @Slot()
    def _on_reset(self) -> None:
        """Reset the label to neutral state."""
        suffix = f" {self._suffix}" if self._suffix else ""
        self.setText(f"{self._default_value:.{self._decimal_precision}f}{suffix}")
        self._on_neutral()
        self.status = JZMeasLabel.Status.NEUTRAL
