from pyDigitalWaveTools.vcd.value_format import bitToStr, bitVectorToStr,\
    LogValueFormatter
from pyDigitalWaveTools.vcd.writer import VcdVarWritingInfo


class JsonArrayFormatter(LogValueFormatter):
    def __init__(self, dimmensions, elm_formatter):
        self.dimmensions = dimmensions
        self.elm_formatter = elm_formatter

    def bind_var_info(self, varInfo: VcdVarWritingInfo):
        self.elm_formatter.bind_var_info(varInfo)

    def format(self, newVal: "Value", updater):
        indexes = [int(i) for i in updater.indexes]
        for i in indexes:
            newVal = newVal[i]
        v = self.elm_formatter.format(newVal, updater) 
        return (indexes, v)

class JsonEnumFormatter(LogValueFormatter):

    def format(self, newVal: "Value", updater):
        if newVal.vld_mask:
            return newVal.val
        else:
            return ""


class JsonBitsFormatter(LogValueFormatter):
    
    def bind_var_info(self, varInfo: VcdVarWritingInfo):
        self.width = varInfo.width
        if self.width == 1:
            self.format = self._format_bit
        else:
            self.format = self._format_bits

    def _format_bit(self, newVal: "Value", updater):
        return bitToStr(newVal.val, newVal.vld_mask)

    def _format_bits(self, newVal: "Value", updater):
        return bitVectorToStr(newVal.val, self.width, newVal.vld_mask, 'b', None)

    def format(self, newVal: "Value", updater):
        raise Exception("Should have been replaced in bind_var_info")
