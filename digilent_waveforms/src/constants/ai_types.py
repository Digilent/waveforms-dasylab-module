from enum import Enum


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
