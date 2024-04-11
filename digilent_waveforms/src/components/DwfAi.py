from ctypes import *  # type: ignore
from digilent_waveforms.src.constants.ai_types import AiAcquisitionMode


class DwfAi:
    dwf = any
    device_handle: c_int

    def __init__(self, dwf: CDLL, device_handle: c_int):
        self.device_handle = device_handle
        self.dwf = dwf

    def set_acquisition_mode(self, mode: AiAcquisitionMode) -> None:
        self.dwf.FDwfAnalogInAcquisitionModeSet(self.device_handle, c_int(mode.value))

    def get_acquisition_mode(self) -> AiAcquisitionMode:
        retval = c_int()
        self.dwf.FDwfAnalogInAcquisitionModeGet(self.device_handle, byref(retval))
        return AiAcquisitionMode(retval.value)
