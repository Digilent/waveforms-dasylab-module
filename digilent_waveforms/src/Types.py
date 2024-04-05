# from typing_extensions import TypedDict
from enum import Enum

# DeviceInfo = TypedDict(
#     "DeviceInfo",
#     {
#         "id": int,
#         "name": str,
#         "revision": int,
#         "serial_number": str,
#     },
# )


class DeviceType(Enum):
    ELECTRONICS_EXPLORER = 1
    ANALOG_DISCOVERY = 2
    ANALOG_DISCOVERY_2 = 3
    DIGITAL_DISCOVERY = 4
    ADP3X50 = 6
    ADP5250 = 8
    DPS3340 = 9

    def to_str(self) -> str:
        if self.value == 1:
            return "Electronics Explorer"
        if self.value == 2:
            return "Analog Discovery"
        if self.value == 3:
            return "Analog Discovery 2"
        if self.value == 4:
            return "Analog Discovery 3"
        if self.value == 6:
            return "Analog Discovery Pro 3x50"
        if self.value == 8:
            return "Analog Discovery Pro 5250"
        if self.value == 9:
            return "Analog Discovery Pro 3340"
        else:
            return f"Unknown device type ({self.value})"


class AiAcquisitionMode(Enum):
    Single = 0
    ScanShift = 1
    ScanScreen = 2
    Record = 3
    Overs = 4
    Single1 = 5


class InstrumentState(Enum):
    Ready = 0
    Config = 4
    Prefill = 5
    Armed = 1
    Wait = 7
    Triggered = 3
    Running = 3
    NotDone = 6
    Done = 2
