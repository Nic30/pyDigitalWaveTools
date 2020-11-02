from io import StringIO
from typing import Optional


def bitVectorToStr(val: int, width: int, vld_mask: int, prefix: Optional[str], suffix: Optional[str]):
    buff = []
    if prefix is not None:
        buff.append(prefix)

    for i in range(width - 1, -1, -1):
        mask = (1 << i)
        b = val & mask

        if vld_mask & mask:
            s = "1" if b else "0"
        else:
            s = "X"
        buff.append(s)

    if suffix is not None:
        buff.append(suffix)

    return ''.join(buff)


def bitToStr(val: int, vld_mask: int):
    if vld_mask:
        return "1" if val else "0"
    else:
        return "X"

class LogValueFormatter():
    def bind_var_info(self, varInfo: "VcdVarWritingInfo"):
        pass

    def format(self, newVal: "Value", updater, t: int, out: StringIO):
        pass

class VcdEnumFormatter(LogValueFormatter):

    def bind_var_info(self, varInfo: "VcdVarWritingInfo"):
        self.vcdId = varInfo.vcdId

    def format(self, newVal: "Value", updater, t: int, out: StringIO):
        if newVal.vld_mask:
            val = newVal.val
        else:
            val = "UNDEF"
    
        out.write("s%s %s\n" % (val, self.vcdId))


class VcdBitsFormatter(LogValueFormatter):
    
    def bind_var_info(self, varInfo: "VcdVarWritingInfo"):
        self.width = varInfo.width
        self.vcdId = varInfo.vcdId
        if self.width == 1:
            self.format = self._format_bit
            self.suffix = "%s\n" % self.vcdId
        else:
            self.format = self._format_bits
            self.suffix = " %s\n" % self.vcdId

    def _format_bit(self, newVal: "Value", updater, t: int, out: StringIO):
        v = bitToStr(newVal.val, newVal.vld_mask)
        out.write(v + self.suffix)

    def _format_bits(self, newVal: "Value", updater, t: int, out: StringIO):
        out.write(bitVectorToStr(newVal.val, self.width, newVal.vld_mask, "b", self.suffix))

    def format(self, newVal: "Value", updater):
        raise Exception("Should have been replaced in bind_var_info")

