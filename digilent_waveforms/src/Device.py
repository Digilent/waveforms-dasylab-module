from ctypes import *  # type: ignore
import sys


class Device:
    def __init__(self, device_handle: c_int):

        if sys.platform.startswith("win"):
            self.dwf = cdll.dwf
        elif sys.platform.startswith("darwin"):
            self.dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
        else:
            self.dwf = cdll.LoadLibrary("libdwf.so")

        self.dwf = cdll.dwf
        self.device_handle = device_handle
