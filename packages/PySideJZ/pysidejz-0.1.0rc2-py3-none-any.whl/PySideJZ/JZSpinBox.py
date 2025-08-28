import math

from PySide6.QtWidgets import QSpinBox, QWidget


class JZSpinBoxBytes(QSpinBox):
    """Spinbox containing hexadecimal values representing bytes."""
    def __init__(self, parent: QWidget, minimum: int = 0, maximum: int = 255):
        super().__init__(parent, minimum=minimum, maximum=maximum)

    def calculate_hex_digits_needed(self, maximum: int) -> int:
        """Calculate how many hexadecimal digits are needed to represent the maximum value."""
        if maximum == 0:
            return 1
        if maximum < 0:
            raise ValueError("For this implementation, only positive values of bytes are allowed")
        return math.ceil(math.log(maximum + 1, 16))

    def textFromValue(self, val: int) -> str:
        """Convert the integer value to a hexadecimal string."""
        digits_needed = self.calculate_hex_digits_needed(self.maximum())
        return f"0x{val:0{digits_needed}X}"

    def setMaximum(self, maximum: int) -> None:
        """Set the maximum value and update the spinbox accordingly."""
        super().setMaximum(maximum)
        self.update()


class JZSpinBoxPowerOfTwo(QSpinBox):
    """Spinbox that contains only numbers that are powers of two."""
    def __init__(
        self,
        parent: QWidget,
        minimum: int = 1,
        maximum: int = 8192,
        value: int = 1,
    ) -> None:
        super().__init__(parent)

        self._validate_range(minimum, maximum)
        self._set_range(minimum, maximum)
        self._values = self._generate_powers_of_two()

        self._validate_value(value)
        self._set_value(value)

        self.setSingleStep(1)
        super().setRange(minimum, maximum)
        super().setValue(value)

    def _validate_range(self, minimum: int, maximum: int):
        """Validate that the maximum and minimum values are within the allowed range of QSpinBox."""
        if not (2 ** 0 <= minimum <= 2 ** 32):
            raise ValueError(f"Minimum input ({minimum}) is restricted between 2^0 and 2^32")
        if not (2 ** 0 <= maximum <= 2 ** 32):
            raise ValueError(f"Maximum input ({maximum}) is restricted between 2^0 and 2^32")
        if not self.is_power_of_two(minimum):
            raise ValueError(f"Minimum value passed ({minimum}) is not a power of two")
        if not self.is_power_of_two(maximum):
            raise ValueError(f"Maximum value passed ({maximum}) is not a power of two")
        if minimum > maximum:
            raise ValueError(f"Minimum ({minimum}) cannot be larger than the maximum ({maximum})")

    def _set_range(self, minimum: int, maximum: int) -> None:
        """Set the internal range of the spinbox."""
        self._min = minimum
        self._max = maximum

    def _validate_value(self, value: int) -> None:
        """Validate that the set value is between the minimum and maximum and is a power of two."""
        if not (self._min <= value <= self._max):
            raise ValueError(
                f"Value input ({value}) is restricted between minimum ({self._min}) and maximum"
                f" ({self._max})",
            )
        if not self.is_power_of_two(value):
            raise ValueError(f"Value passed ({value}) is not a power of two")

    def _set_value(self, value: int) -> None:
        """Set the internal value of the spinbox."""
        self._value = value

    def _generate_powers_of_two(self) -> list[int]:
        """Generate a list of powers of two between the minimum and maximum values."""
        values = []
        current = self._min
        while current <= self._max:
            values.append(current)
            current *= 2
        return values

    def is_power_of_two(self, value: int) -> bool:
        """Check if a number is a power of two."""
        return value > 0 and (value & (value - 1)) == 0

    def stepBy(self, steps: int) -> None:
        """Override stepBy to change the value by powers of two."""
        current_value = self.value()
        if current_value not in self._values:
            current_value = self._values[0]
        current_idx = self._values.index(current_value)
        new_idx = current_idx + steps
        new_idx = max(0, min(new_idx, len(self._values) - 1))
        self.setValue(self._values[new_idx])

    def setRange(self, minimum: int, maximum: int) -> None:
        """Set the range of the spinbox and update the values."""
        self._validate_range(minimum, maximum)
        self._set_range(minimum, maximum)
        self._values = self._generate_powers_of_two()
        super().setRange(minimum, maximum)
        self.setValue(self._values[0])

    def setMinimum(self, minimum) -> None:
        """Set the minimum value of the spinbox."""
        self.setRange(minimum, self._max)

    def setMaximum(self, maximum) -> None:
        """Set the maximum value of the spinbox."""
        self.setRange(self._min, maximum)

    def setValue(self, value) -> None:
        """Set the value of the spinbox, validating it first."""
        self._validate_value(value)
        self._set_value(value)
        super().setValue(value)
