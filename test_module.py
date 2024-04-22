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
        self.foo()

    def foo(self):
        print("foo")

    def Create(self):
        pass

    def Delete(self):
        pass

    def DlgInit(self, dlg):
        pass

    def DlgOk(self, dlg):
        pass

    def DlgCancel(self, dlg):
        pass

    def DlgEvent(self, dlg, label, value):
        pass

    def Save(self):
        pass

    def Load(self):
        pass

    def Start(self):
        pass

    def Stop(self):
        pass

    def SetupFifo(self, channel):
        return True

    def ProcessValue(self, v, c):
        return True
