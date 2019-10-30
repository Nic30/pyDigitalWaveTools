#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import Callable
from pyDigitalWaveTools.vcd.common import VcdVarScope, VCD_SIG_TYPE, VcdVarInfo


class VarAlreadyRegistered(Exception):
    pass


class VcdVarWritingInfo(VcdVarInfo):
    """
    Container of informations about variable in VCD for VCD file generating
    """

    def __init__(self, vcdId, name, width, sigType, parent,
                 valueFormatter: Callable[["value"], str]):
        super(VcdVarWritingInfo, self).__init__(
            vcdId, name, width, sigType, parent)
        self.data = []
        self.valueFormatter = valueFormatter


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
                         valueFormatter: Callable[["Value"], str]):
        varId = self._idToStr(self._nextId)
        if sig is not None and sig in self:
            raise VarAlreadyRegistered("%r is already registered" % (sig))
        vInf = VcdVarWritingInfo(
            varId, name, width, sigType, parent, valueFormatter)
        self[sig] = vInf
        self._nextId += 1
        return vInf


class VcdVarWritingScope(VcdVarScope):
    """
    Vcd module - container for variables

    :ivar oFile: output file to write vcd to
    :ivar name: name of scope
    :ivar vars: subscopes or signals
    """

    def __init__(self, name, writer, parent=None):
        super(VcdVarWritingScope, self).__init__(name, parent=parent)
        self._writer = writer

    def addVar(self, sig: object, name: str, sigType: VCD_SIG_TYPE, width: int,
               valueFormatter: Callable[["Value"], str]):
        """
        Add variable to scope

        :ivar sig: user specified object to keep track of VcdVarInfo in change() 
        :ivar sigType: vcd type name
        :ivar valueFormatter: value which converts new value in change() to vcd string
        """
        vInf = self._writer._idScope.registerVariable(sig, name, self, width,
                                                      sigType, valueFormatter)
        self.children[vInf.name] = vInf
        self._writer._oFile.write("$var %s %d %s %s $end\n" % (
            sigType, vInf.width, vInf.vcdId, vInf.name))

    def varScope(self, name):
        """
        Create sub variable scope with defined name
        """
        ch = VcdVarWritingScope(name, self._writer, parent=self)
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
        self._writer._oFile.write("$scope module %s $end\n" % self.name)

    def _writeFooter(self):
        self._writer._oFile.write("$upscope $end\n")


class VcdWriter():

    def __init__(self, oFile=sys.stdout):
        self._oFile = oFile
        self._idScope = VcdVarIdScope()
        self.lastTime = -1
        self.defaultTop = None

    def date(self, text):
        self._oFile.write("$date\n   %s\n$end\n" % text)

    def version(self, text):
        self._oFile.write("$version   \n%s\n$end\n" % text)

    def timescale(self, picoSeconds):
        self._oFile.write("$timescale %dps $end\n" % picoSeconds)

    def varScope(self, name) -> VcdVarWritingScope:
        """
        Create sub variable scope with defined name
        """
        return VcdVarWritingScope(name, self, parent=self)

    def enddefinitions(self):
        self._oFile.write("$enddefinitions $end\n")

    def setTime(self, t):
        lt = self.lastTime
        if lt == t:
            return
        elif lt < t:
            self.lastTime = t
            self._oFile.write("#%d\n" % (t))
        else:
            raise Exception("VcdWriter invalid time update %d -> %d" % (
                            lt, t))

    def logChange(self, time, sig, newVal):
        self.setTime(time)
        varInfo = self._idScope[sig]
        v = varInfo.valueFormatter(sig, newVal, varInfo)
        self._oFile.write(v)


def bitVectorToStr(sig, val, width, vld_mask):
    buff = []
    for i in range(width - 1, -1, -1):
        mask = (1 << i)
        b = val & mask

        if vld_mask & mask:
            s = "1" if b else "0"
        else:
            s = "X"
        buff.append(s)

    return ''.join(buff)


def vcdEnumFormatter(sig, newVal: "Value", varInfo: VcdVarWritingInfo):
    if newVal.vld_mask:
        val = newVal.val
    else:
        val = "XXXX"

    return "s%s %s\n" % (val, varInfo.vcdId)


def vcdBitsFormatter(sig, newVal: "Value", varInfo: VcdVarWritingInfo):
    v = bitVectorToStr(sig, newVal.val, varInfo.width, newVal.vld_mask)

    if varInfo.width == 1:
        frmt = "%s%s\n"
    else:
        frmt = "b%s %s\n"

    return frmt % (v, varInfo.vcdId)


if __name__ == "__main__":
    from datetime import datetime

    class MaskedValue():

        def __init__(self, val, vld_mask):
            self.val = val
            self.vld_mask = vld_mask

    vcd = VcdWriter()
    vcd.date(datetime.now())
    vcd.timescale(1)
    sig0 = "sig0"
    vect0 = "vect0"
    sig1 = "sig1"

    with vcd.varScope("unit0") as m:
        m.addVar(sig0, sig0, VCD_SIG_TYPE.WIRE, 1, vcdBitsFormatter)
        m.addVar(sig1, sig1, VCD_SIG_TYPE.WIRE, 1, vcdBitsFormatter)
        m.addVar(vect0, vect0, VCD_SIG_TYPE.WIRE, 16, vcdBitsFormatter)
    vcd.enddefinitions()

    for s in [sig0, sig1, vect0]:
        vcd.logChange(0, s, MaskedValue(0, 0))

    vcd.logChange(1, sig0, MaskedValue(0, 1))
    vcd.logChange(2, sig1, MaskedValue(1, 1))

    vcd.logChange(3, vect0, MaskedValue(10, (1 << 16) - 1))
    vcd.logChange(4, vect0, MaskedValue(20, (1 << 16) - 1))
