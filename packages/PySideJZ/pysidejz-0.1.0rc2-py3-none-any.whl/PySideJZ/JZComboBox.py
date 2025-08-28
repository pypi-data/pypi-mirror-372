import sys
import time
from collections.abc import Callable
from enum import IntEnum

import serial.tools.list_ports
from loguru import logger
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QComboBox, QWidget
from serial.tools.list_ports_common import ListPortInfo

from PySideJZ.JZtypes import VideoDevice

if sys.platform == "linux":
    import pyudev

class JZCBF:
    class Property(IntEnum):
        """Port property for filtering serial ports in JZComboBoxSerialPorts."""
        PORT = 0
        PID = 1
        VID = 2
        NAME = 3
        DESCRIPTION = 4
        SERIAL_NUMBER = 5
        SUBSYSTEM = 6
        MANUFACTURER = 7
        PRODUCT = 8
        LOCATION = 9
        INTERFACE = 10
        USB_INTERFACE_PATH = 11
        USB_DEVICE_PATH = 12

    class Action(IntEnum):
        """Actions for filtering serial ports in JZComboBoxSerialPorts."""
        INCLUDE = 0
        EXCLUDE = 1


class JZComboBoxCommonCustomFilter:
    @staticmethod
    def filter_exclude_dev_ttyS(ports: list[ListPortInfo]) -> list[ListPortInfo]:
        """Exclude ports with /dev/ttyS* values."""
        return [port for port in ports if not port.device.startswith('/dev/ttyS')]

    @staticmethod
    def filter_dev_ttyUSB(ports: list[ListPortInfo]) -> list[ListPortInfo]:
        """Filter for /dev/ttyUSB* devices."""
        return [port for port in ports if port.device.startswith('/dev/ttyUSB')]

    @staticmethod
    def filter_dev_ttyACM(ports: list[ListPortInfo]) -> list[ListPortInfo]:
        """Filter for /dev/ttyACM* devices."""
        return [port for port in ports if port.device.startswith('/dev/ttyACM')]

    @staticmethod
    def filter_exclude_none(ports: list[ListPortInfo]) -> list[ListPortInfo]:
        """Exclude ports with None PID/VID values."""
        return [port for port in ports if port.vid is not None and port.pid is not None]


class JZComboBoxSerialPorts(QComboBox):
    """A combobox that is used for selecting serial ports.

    Specific combobox that is used for selecting serial ports. Includes options to include/exclude
    specific PIDs, VIDs, serial port names and etc. Also implements blocking/non-blocking
    methods."""

    class FilterType:
        """Filter type for combobox"""

    refresh = Signal()
    refresh_filtered = Signal(object)
    refresh_filtered_custom = Signal(Callable)
    refresh_video_devices = Signal()
    refresh_video_devices_custom = Signal(Callable)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent, objectName="JZComboBox", maxVisibleItems=5, editable=False)
        self._refresh_done = True
        self.refresh.connect(self._refresh)
        self.refresh_filtered.connect(self._refresh_filtered)
        self.refresh_filtered_custom.connect(self._refresh_filtered_custom)
        self.refresh_video_devices.connect(self._refresh_video_devices)
        self.refresh_video_devices_custom.connect(self._refresh_video_devices_custom)

    @Slot()
    def _refresh(self) -> None:
        """Refresh the list of serial ports in the combobox, put in all ports unconditionally."""
        self.clear()
        try:
            ports = serial.tools.list_ports.comports()
            for port in ports:
                self.addItem(str(port.device), userData=port)
        except Exception as ex:
            logger.exception(f"Error refreshing serial ports: {ex}")
        self._refresh_done = True

    def refresh_blocking(self) -> None:
        """Refresh the list of serial ports in the combobox, blocking until done."""
        self._refresh_done = False
        self.refresh.emit()
        while not self._refresh_done:
            time.sleep(0.01)

    @Slot(object)
    def _refresh_filtered(
        self,
        conds: list[tuple[JZCBF.Property, JZCBF.Action, list[str]]],
    ) -> None:
        """Refresh the list of serial ports in the combobox, put in only filtered ports (AND logic).

        Each port must match ALL filter conditions to be included.
        example usage:
        _refresh_filered([
                (JZCBF.Property.VID, JZCBF.Action.INCLUDE, ["0x0483"]),
                (JZCBF.Property.PID, JZCBF.Action.INCLUDE, ["0x374b"])
            ])
        would include all ports that have VID 0x0483 and PID 0x374b;

        _refresh_filered([
                (JZCBF.Property.VID, JZCBF.Action.EXCLUDE, ["None"]),
            ])
        would exclude all ports that have VID None

        For property values, only strings are allowed. To check for None, it must be cast to
        a string. All PIDs and VIDs are expected to be in hexadecimal format, e.g. "0x0483".
        """
        self.clear()
        try:
            ports = serial.tools.list_ports.comports()
            filtered_ports = []
            for port in ports:
                if not self._port_matches_conditions(port, conds):
                    continue
                filtered_ports.append(port)
            for port in filtered_ports:
                self.addItem(str(port.device), userData=port)
        except Exception as ex:
            logger.exception(f"Error refreshing serial ports: {ex}")
        self._refresh_done = True

    def refresh_filtered_blocking(
        self,
        conds: list[tuple[JZCBF.Property, JZCBF.Action, list[str]]],
    ) -> None:
        """Refresh the list of serial ports in the combobox, blocking until done."""
        self._refresh_done = False
        self.refresh_filtered.emit(conds)
        while not self._refresh_done:
            time.sleep(0.01)

    def _port_matches_conditions(
            self,
            port: ListPortInfo,
            conds: list[tuple[JZCBF.Property, JZCBF.Action, list[str]]],
        ) -> bool:
        """Helper to check if a port matches all filter conditions."""
        for prop, action, values in conds:
            if not self._validate_args(prop, action, values):
                raise TypeError("Invalid filter arguments")
            port_value = getattr(port, prop.name.lower(), None)
            if self._filter_match(port_value, values, action):
                continue
            return False
        return True

    @staticmethod
    def _validate_args(prop: JZCBF.Property, action: JZCBF.Action, values: list[str]) -> bool:
        """Validate the filter arguments."""
        return (
            isinstance(prop, JZCBF.Property)
            and isinstance(action, JZCBF.Action)
            and isinstance(values, list)
            and all(isinstance(v, str) for v in values)
        )

    @staticmethod
    def _filter_match(port_value: str, values: list[str], action: JZCBF.Action) -> bool:
        """Check if the port value matches the filter conditions."""
        port_value_str = str(port_value) if port_value is not None else "None"
        port_value_hex = (
            f"{port_value:#06x}".lower() if isinstance(port_value, int) else None
        )
        match_found = False
        for v in values:
            v_strip = v.strip()
            v_lower = v_strip.lower()
            if v_lower == "none" and port_value is None:
                match_found = True
                break
            if (
                v_lower.startswith("0x")
                and port_value_hex is not None
                and v_lower == port_value_hex
            ):
                match_found = True
                break
            if (
                not v_lower.startswith("0x")
                and port_value is not None
                and v_strip == port_value_str
            ):
                match_found = True
                break
        if action == JZCBF.Action.INCLUDE:
            return match_found
        if action == JZCBF.Action.EXCLUDE:
            return not match_found
        return False

    @Slot(Callable)
    def _refresh_filtered_custom(self, callback: Callable) -> None:
        """Refresh the combobox and filter ports using a custom callback."""
        self.clear()
        try:
            ports = serial.tools.list_ports.comports()
            filtered_ports = callback(ports)
            for port in filtered_ports:
                self.addItem(str(port.device), userData=port)
        except Exception as ex:
            logger.exception(f"Error refreshing serial ports: {ex}")
        self._refresh_done = True

    def refresh_filtered_custom_blocking(self, callback: Callable) -> None:
        """Refresh the combobox and filter ports using a custom callback, blocking until done."""
        self._refresh_done = False
        self.refresh_filtered_custom.emit(callback)
        while not self._refresh_done:
            time.sleep(0.01)

    @Slot()
    def _refresh_video_devices(self) -> None:
        """Refresh the list of video devices in the combobox."""
        self.clear()
        try:
            if sys.platform == "linux":
                devices = self._get_video_devices_linux()
            else:
                raise NotImplementedError("Video device refresh is only implemented for Linux.")

            for device in devices:
                self.addItem(device.name, userData=device)
        except Exception as ex:
            logger.exception(f"Error refreshing video devices: {ex}")
        self._refresh_done = True

    def refresh_video_devices_blocking(self) -> None:
        """Refresh the list of video devices in the combobox, blocking until done."""
        self._refresh_done = False
        self.refresh_video_devices.emit()
        while not self._refresh_done:
            time.sleep(0.01)

    @Slot(Callable)
    def _refresh_video_devices_custom(self, callback: Callable) -> None:
        """Refresh the combobox with video devices using a custom callback."""
        self.clear()
        try:
            if sys.platform == "linux":
                devices = self._get_video_devices_linux()
            else:
                raise NotImplementedError("Video device refresh is only implemented for Linux.")
            filtered_devices = callback(devices)

            for device in filtered_devices:
                self.addItem(device.name, userData=device)
        except Exception as ex:
            logger.exception(f"Error refreshing video devices: {ex}")
        self._refresh_done = True

    def refresh_video_devices_custom_blocking(self, callback: Callable) -> None:
        """Refresh the combobox with video devices using a custom callback, blocking until done."""
        self._refresh_done = False
        self.refresh_video_devices_custom.emit(callback)
        while not self._refresh_done:
            time.sleep(0.01)

    def _get_video_devices_linux(self) -> list[VideoDevice]:
        """Get a list of video devices on Linux using pyudev."""
        context = pyudev.Context()
        devices = []

        for device in context.list_devices(subsystem='video4linux'):
            device_node = device.device_node
            if not device_node or not device_node.startswith('/dev/video'):
                continue

            capabilities = device.properties.get('ID_V4L_CAPABILITIES', None)
            if ':capture:' in capabilities:
                continue
            serial_number = device.properties.get('ID_SERIAL_SHORT', None)

            parent = device.find_parent('usb', 'usb_device')
            if parent:
                vid = parent.attributes.get('idVendor', None)
                pid = parent.attributes.get('idProduct', None)
            else:
                pid = 'N/A'
                vid = 'N/A'

            devices.append(
                VideoDevice(
                    name=device_node,
                    path=device_node,
                    vid=vid,
                    pid=pid,
                    serial_number=serial_number,
                ),
            )
        return devices

