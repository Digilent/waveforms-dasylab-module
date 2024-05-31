# DASYLab Imports
import Ly  # type: ignore
import lys  # type: ignore

import debugpy
from time import sleep
import debugpy

debugpy.listen(5678, in_process_debug_adapter=True)


class info(object):
    def __init__(self):
        print("info()")


class pvar(object):
    def __init__(self):
        print("info()")


class pscript(lys.mclass):
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

    def DlgOk(self, dlg):
        print("DlgOk()")

    def DlgCancel(self, dlg):
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
