from dataclasses import dataclass


@dataclass
class VideoDevice:
    """Data class for video devices."""
    name: str
    path: str
    vid: str
    pid: str
    serial_number: str
