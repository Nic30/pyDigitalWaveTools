from datetime import datetime
from io import StringIO
import os
import unittest

from pyDigitalWaveTools.vcd.common import VCD_SIG_TYPE, VcdVarScope
from pyDigitalWaveTools.vcd.value_format import VcdBitsFormatter,\
    LogValueFormatter
from pyDigitalWaveTools.vcd.writer import VcdWriter, VcdVarWritingScope
from pyDigitalWaveTools.vcd.parser import VcdParser, VcdVarParsingInfo
from typing import Union, Dict, Tuple, List

BASE = os.path.dirname(os.path.realpath(__file__))


class MaskedValue():

    def __init__(self, val, vld_mask):
        self.val = val
        self.vld_mask = vld_mask



def example_dump_values0(vcd, bitsFromatter=VcdBitsFormatter):
    sig0 = "sig0"
    vect0 = "vect0"
    sig1 = "sig1"

    with vcd.varScope("unit0") as m:
        m.addVar(sig0, sig0, VCD_SIG_TYPE.WIRE, 1, bitsFromatter())
        m.addVar(sig1, sig1, VCD_SIG_TYPE.WIRE, 1, bitsFromatter())
        m.addVar(vect0, vect0, VCD_SIG_TYPE.WIRE, 16, bitsFromatter())
    vcd.enddefinitions()

    for s in [sig0, sig1, vect0]:
        vcd.logChange(0, s, MaskedValue(0, 0), None)

    vcd.logChange(1, sig0, MaskedValue(0, 1), None)
    vcd.logChange(2, sig1, MaskedValue(1, 1), None)

    vcd.logChange(3, vect0, MaskedValue(10, (1 << 16) - 1), None)
    vcd.logChange(4, vect0, MaskedValue(20, (1 << 16) - 1), None)


class AsIsFormatter(LogValueFormatter):
    """
    Return value as is withou any formating or conversion
    """
    
    def bind_var_info(self, varInfo: "VcdVarWritingInfo"):
        self.vcdId = varInfo.vcdId
        
        if varInfo.sigType == VCD_SIG_TYPE.WIRE and varInfo.width == 1:
            self.format = self.format_bit
        elif varInfo.sigType == VCD_SIG_TYPE.WIRE:
            self.format = self.format_bits
        elif varInfo.sigType == VCD_SIG_TYPE.ENUM or varInfo.sigType == VCD_SIG_TYPE.REAL:
            self.format = self.format_enum
        else:
            raise NotImplementedError(varInfo.sigType)

    def format_bit(self, newVal: str, updater, t, of):
        of.write(newVal)
        of.write(self.vcdId)
        of.write("\n")

    def format_bits(self, newVal: str, updater, t, of):
        of.write(newVal)
        of.write(" ")
        of.write(self.vcdId)
        of.write("\n")

    def format_enum(self, newVal: str, updater, t, of):
        of.write("s")
        of.write(newVal)
        of.write(" ")
        of.write(self.vcdId)
        of.write("\n")

    def format(self, newVal: str, updater, t, of):
        raise NotImplementedError()


def copy_signals_from_parser_recursion(parser_scope: Union[VcdVarScope, VcdVarParsingInfo], writer_scope: VcdVarWritingScope):
    if isinstance(parser_scope, VcdVarScope):
        with writer_scope.varScope(parser_scope.name) as m:
            for _, child in sorted(parser_scope.children.items(), key=lambda x: x[0]):
                copy_signals_from_parser_recursion(child, m)
    else:
        writer_scope.addVar(parser_scope, parser_scope.name, parser_scope.sigType, parser_scope.width, AsIsFormatter())


def copy_signals_from_parser(vcd_in: VcdParser, vcd_out: VcdWriter):
    root = list(vcd_in.scope.children.values())[0]
    copy_signals_from_parser_recursion(root, vcd_out)
    vcd_out.enddefinitions()

def aggregate_signal_updates_by_time(parser_scope: VcdVarScope, res: Dict[int, List[Tuple[VcdVarParsingInfo, str]]]):
    if isinstance(parser_scope, VcdVarScope):
        for _, child in sorted(parser_scope.children.items(), key=lambda x: x[0]):
            aggregate_signal_updates_by_time(child, res)
    else:
        for (t, val) in parser_scope.data:
            try:
                time_quantum = res[t]
            except KeyError:
                time_quantum = res[t] = []
            time_quantum.append((parser_scope, val))


class VcdWriterTC(unittest.TestCase):

    def test_example0(self):

        out = StringIO()
        vcd = VcdWriter(out)
        d = datetime.strptime("2018-04-12 18:04:03.652880",
                              "%Y-%m-%d %H:%M:%S.%f")
        vcd.date(d)
        vcd.timescale(1)
        example_dump_values0(vcd)

        with open(os.path.join(BASE, "example0.vcd")) as f:
            ref = f.read()
            out = out.getvalue()
            self.assertEqual(ref, out)
    
    def test_rewrite_AxiRegTC_test_write(self):
        fIn = os.path.join(BASE, "AxiRegTC_test_write.vcd")
        with open(fIn) as vcd_file:
            vcd_in = VcdParser()
            vcd_in.parse(vcd_file)

        out = StringIO()
        vcd_out = VcdWriter(out)
        d = datetime.strptime("2018-03-21 20:20:48.479224",
                              "%Y-%m-%d %H:%M:%S.%f")
        vcd_out.date(d)
        vcd_out.timescale(1)
        
        copy_signals_from_parser(vcd_in, vcd_out)

        # for value writing we need to have it time order because
        # we can not move back in time in VCD        
        all_updates = {}
        aggregate_signal_updates_by_time(vcd_in.scope, all_updates)
        for t, updates in sorted(all_updates.items()):
            for sig, val in updates:
                vcd_out.logChange(t, sig, val, None)
        
        new_vcd_str = out.getvalue()

        # parse it again to check if format is correct
        vcd_in = VcdParser()
        vcd_in.parse_str(new_vcd_str)


if __name__ == "__main__":
    suite = unittest.TestSuite()
    # suite.addTest(VcdWriterTC('test_example0'))
    suite.addTest(unittest.makeSuite(VcdWriterTC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
