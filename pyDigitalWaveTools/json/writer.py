#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyDigitalWaveTools.vcd.common import VcdVarScope, VCD_SIG_TYPE
from pyDigitalWaveTools.vcd.parser import VcdVarParsingInfo
from pyDigitalWaveTools.vcd.value_format import LogValueFormatter
from pyDigitalWaveTools.vcd.writer import VarAlreadyRegistered, VcdVarWritingScope, VcdWriter


class VarIdScopeJson(dict):

    def registerVariable(self, sig: object, name: str, parent: VcdVarScope,
                         width: int, sigType: VCD_SIG_TYPE,
                         valueFormatter: LogValueFormatter):
        if sig is not None and sig in self:
            raise VarAlreadyRegistered("%r is already registered" % (sig))
        vInf = VcdVarParsingInfo(
            None, name, width, sigType, parent)
        valueFormatter.bind_var_info(vInf)
        vInf.valueFormatter = valueFormatter.format
        self[sig] = vInf

        return vInf


class VarWritingScopeJson(VcdVarWritingScope):
    """
    Logical container of signals
    """

    def addVar(self, sig: object, name: str, sigType: VCD_SIG_TYPE, width: int,
               valueFormatter: LogValueFormatter):
        """
        Add variable to scope

        :ivar ~.sig: user specified object to keep track of VcdVarInfo in change() 
        :ivar ~.sigType: vcd type name
        :ivar ~.valueFormatter: value which converts new value in change() to vcd string
        """
        vInf = self._writer._idScope.registerVariable(sig, name, self, width,
                                                      sigType, valueFormatter)
        self.children[vInf.name] = vInf

    def __enter__(self) -> "VcdVarWritingScope":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class JsonWriter(VcdWriter):

    def __init__(self, output: dict):
        self._output = output
        self._idScope = VarIdScopeJson()
        self.lastTime = -1
        self._top_var_scope = None

    def date(self, text):
        pass

    def version(self, text):
        pass

    def timescale(self, picoSeconds):
        pass

    def varScope(self, name) -> VcdVarWritingScope:
        """
        Create sub variable scope with defined name
        """
        vs = VarWritingScopeJson(name, self, parent=self)
        if self._top_var_scope is not None:
            raise AssertionError("Only one top scope currently supported")
        self._top_var_scope = vs
        return vs

    def enddefinitions(self):
        self._output.update(self._top_var_scope.toJson())

    def setTime(self, t):
        lt = self.lastTime
        if lt == t:
            return
        elif lt < t:
            self.lastTime = t
        else:
            raise Exception("VcdWriter invalid time update %d -> %d" % (
                            lt, t))

    def logChange(self, time, sig, newVal, valueUpdater):
        self.setTime(time)
        varInfo = self._idScope[sig]
        varInfo.valueFormatter(newVal, valueUpdater, self.lastTime, varInfo.data)



if __name__ == "__main__":
    from pyDigitalWaveTools.json.value_format import JsonBitsFormatter
    from pyDigitalWaveTools.tests.vcdWriter_test import example_dump_values0

    res = {}
    vcd = JsonWriter(res)
    example_dump_values0(vcd, JsonBitsFormatter)

    print(res)
