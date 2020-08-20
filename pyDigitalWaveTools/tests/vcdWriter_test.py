from datetime import datetime
from io import StringIO
import os
import unittest

from pyDigitalWaveTools.vcd.common import VCD_SIG_TYPE
from pyDigitalWaveTools.vcd.value_format import VcdBitsFormatter
from pyDigitalWaveTools.vcd.writer import VcdWriter

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


if __name__ == "__main__":
    suite = unittest.TestSuite()
    # suite.addTest(VcdWriterTC('test_example0'))
    suite.addTest(unittest.makeSuite(VcdWriterTC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
