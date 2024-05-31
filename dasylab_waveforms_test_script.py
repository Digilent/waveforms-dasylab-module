import sys
from ctypes import *  # type: ignore
from multiprocessing import Process


if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")


if __name__ == "__main__":
    print("Running without DASYLab")

    class dummyBaseClass:
        def __init__(self):
            pass

    pscriptBaseClass = dummyBaseClass


else:
    # DASYLab Imports
    import Ly  # type: ignore
    import lys  # type: ignore
    import debugpy

    pscriptBaseClass = lys.mclass

    debugpy.listen(5678, in_process_debug_adapter=True)


device_index = 1


class info(object):
    def __init__(self):
        print("info()")


class pvar(object):
    def __init__(self):
        print("info()")


class pscript(pscriptBaseClass):
    def __init__(self, magic):
        self.info = info()
        self.pvar = pvar()

    def ProcessData(self):
        print("ProcessData()")

    def Create(self):
        print("Create()")

    def Delete(self):
        print("Delete()")

    def DlgInit(self, dlg):
        print("DlgInit()")

        try:
            retval = c_int()
            dwf.FDwfEnum(0, byref(retval))

            device_handle = c_int()
            dwf.FDwfDeviceOpen(c_int(device_index), byref(device_handle))

            if device_handle.value == c_int(0).value:
                szerr = create_string_buffer(512)
                dwf.FDwfGetLastErrorMsg(szerr)
                print(str(szerr.value))
                print("failed to open device")
        except Exception as e:
            print(e)

        print("DlgInit() Complete")

    def DlgOk(self, dlg):
        dwf.FDwfDeviceCloseAll()
        print("DlgOk()")

    def DlgCancel(self, dlg):
        dwf.FDwfDeviceCloseAll()
        print("DlgCancel()")

    def DlgEvent(self, dlg, label, value):
        print("DlgEvent()")

    def Save(self):
        print("Save()")

    def Load(self):
        print("Load()")

    def Start(self):
        print("Start()")

    def Stop(self):
        print("Stop()")

    def SetupFifo(self, channel):
        print("SetupFifo()")
        return True

    def ProcessValue(self, v, c):
        print("ProcessValue()")
        return True


if __name__ == "__main__":

    ps = pscript(None)
    ps.DlgInit(None)
    ps.DlgOk(None)
