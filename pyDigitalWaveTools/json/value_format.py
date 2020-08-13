from copy import copy
from typing import List, Tuple

from pyDigitalWaveTools.vcd.value_format import bitToStr, bitVectorToStr, \
    LogValueFormatter
from pyDigitalWaveTools.vcd.writer import VcdVarWritingInfo


class JsonArrayFormatter(LogValueFormatter):
    def __init__(self, dimmensions, elm_formatter):
        self.dimmensions = dimmensions
        self.elm_formatter = elm_formatter

    def bind_var_info(self, varInfo: VcdVarWritingInfo):
        vi = copy(varInfo)
        vi.width = vi.width[-1]
        self.elm_formatter.bind_var_info(vi)

    def format(self, newVal: "Value", updater, t: int, out: List[Tuple]):
        # updater can assign value of whole array, that is why it does not
        # need to have indexes
        indexes = getattr(updater, "indexes", None)
        if indexes:
            indexes = [int(i) for i in updater.indexes]
            for i in indexes:
                newVal = newVal[i]
            self.elm_formatter.format(newVal, updater, t, out) 
            v = out.pop()
            v = (t, (indexes, v[1]))
            out.append(v)
        else:
            for i, v in enumerate(newVal):
                self.elm_formatter.format(v, updater, t, out) 
                v = out.pop()
                v = (t, ([i,], v[1]))
                out.append(v)
                

class JsonEnumFormatter(LogValueFormatter):

    def format(self, newVal: "Value", updater, t: int, out: List[Tuple]):
        if newVal.vld_mask:
            v = newVal.val
        else:
            v = ""
        out.append((t, v))
        

class JsonBitsFormatter(LogValueFormatter):
    
    def bind_var_info(self, varInfo: VcdVarWritingInfo):
        self.width = varInfo.width
        if self.width == 1:
            self.format = self._format_bit
        else:
            self.format = self._format_bits

    def _format_bit(self, newVal: "Value", updater, t: int, out: List[Tuple]):
        out.append((t, bitToStr(newVal.val, newVal.vld_mask)))

    def _format_bits(self, newVal: "Value", updater, t: int, out: List[Tuple]):
        out.append((t, bitVectorToStr(newVal.val, self.width, newVal.vld_mask, 'b', None)))

    def format(self, newVal: "Value", updater, t: int, out: List[Tuple]):
        raise Exception("Should have been replaced in bind_var_info")
