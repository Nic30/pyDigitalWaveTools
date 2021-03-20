#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from pyDigitalWaveTools.vcd.common import VcdVarScope, VCD_SIG_TYPE, VcdVarInfo
from pyDigitalWaveTools.vcd.value_format import LogValueFormatter


class VarAlreadyRegistered(Exception):
    pass


class VcdVarWritingInfo(VcdVarInfo):
    """
    Container of informations about variable in VCD for VCD file generating
    """

    def __init__(self, vcdId, name, width, sigType, parent,
                 valueFormatter: LogValueFormatter):
        super(VcdVarWritingInfo, self).__init__(
            vcdId, name, width, sigType, parent)
        valueFormatter.bind_var_info(self)
        self.valueFormatter = valueFormatter.format


class VcdVarIdScope(dict):

    def __init__(self):
        super(VcdVarIdScope, self).__init__()
        self._nextId = 0
        self._idChars = [chr(i) for i in range(ord("!"), ord("~") + 1)]
        self._idCharsCnt = len(self._idChars)

    def _idToStr(self, x):
        """
        Convert VCD id in int to string
        """
        if x < 0:
            sign = -1
        elif x == 0:
            return self._idChars[0]
        else:
            sign = 1
        x *= sign
        digits = []
        while x:
            digits.append(self._idChars[x % self._idCharsCnt])
            x //= self._idCharsCnt
        if sign < 0:
            digits.append('-')
        digits.reverse()

        return ''.join(digits)

    def registerVariable(self, sig: object, name: str, parent: VcdVarScope,
                         width: int, sigType: VCD_SIG_TYPE,
                         valueFormatter: LogValueFormatter):
        varId = self._idToStr(self._nextId)
        if sig is not None and sig in self:
            raise VarAlreadyRegistered(f"{sig} is already registered")
        vInf = VcdVarWritingInfo(
            varId, name, width, sigType, parent, valueFormatter)
        self[sig] = vInf
        self._nextId += 1
        return vInf


class VcdVarWritingScope(VcdVarScope):
    """
    Vcd module - container for variables

    :ivar ~.oFile: output file to write vcd to
    :ivar ~.name: name of scope
    :ivar ~.vars: subscopes or signals
    """

    def __init__(self, name, writer, parent=None):
        super(VcdVarWritingScope, self).__init__(name, parent=parent)
        self._writer = writer

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
        self._writer._oFile.write(f"$var {sigType:s} {vInf.width:d} {vInf.vcdId:s} {vInf.name:s} $end\n")

    def varScope(self, name):
        """
        Create sub variable scope with defined name
        """
        ch = self.__class__(name, self._writer, parent=self)
        assert name not in self.children, name
        self.children[name] = ch
        return ch

    def __enter__(self) -> "VcdVarWritingScope":
        self._writeHeader()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._writeFooter()

    def _writeHeader(self):
        self._writer._oFile.write(f"$scope module {self.name:s} $end\n")

    def _writeFooter(self):
        self._writer._oFile.write("$upscope $end\n")


class VcdWriter():

    def __init__(self, oFile=sys.stdout):
        self._oFile = oFile
        self._idScope = VcdVarIdScope()
        self.scopes = []
        self.lastTime = -1

    def date(self, text):
        d = str(text)
        self._oFile.write(f"$date\n   {d:s}\n$end\n")

    def version(self, text):
        self._oFile.write(f"$version   \n{text:s}\n$end\n")

    def timescale(self, picoSeconds):
        self._oFile.write(f"$timescale {picoSeconds:d}ps $end\n")

    def varScope(self, name) -> VcdVarWritingScope:
        """
        Create sub variable scope with defined name
        """
        s = VcdVarWritingScope(name, self, parent=self)
        self.scopes.append(s)
        return s

    def enddefinitions(self):
        self._oFile.write("$enddefinitions $end\n")

    def setTime(self, t):
        lt = self.lastTime
        if lt == t:
            return
        elif lt < t:
            self.lastTime = t
            self._oFile.write(f"#{t:d}\n")
        else:
            raise Exception(f"VcdWriter invalid time update {lt:d} -> {t:d}")

    def logChange(self, time, sig, newVal, valueUpdater):
        self.setTime(time)
        varInfo = self._idScope[sig]
        varInfo.valueFormatter(newVal, valueUpdater, time, self._oFile)


if __name__ == "__main__":
    from datetime import datetime
    from pyDigitalWaveTools.vcd.value_format import VcdBitsFormatter
    from tests.vcdWriter_test import example_dump_values0

    vcd = VcdWriter()
    vcd.date(datetime.now())
    vcd.timescale(1)
    example_dump_values0(vcd, VcdBitsFormatter)

