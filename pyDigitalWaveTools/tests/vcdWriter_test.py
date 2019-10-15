import os
import unittest
from datetime import datetime
from pyDigitalWaveTools.vcd.common import VCD_SIG_TYPE
from pyDigitalWaveTools.vcd.writer import VcdWriter, vcdBitsFormatter


BASE = os.path.dirname(os.path.realpath(__file__))

try:
    # python3
    from io import StringIO
except ImportError:
    # python2
    from StringIO import StringIO


class VcdWriterUnitTest(unittest.TestCase):
    def test_example0(self):

        class MaskedValue():
            def __init__(self, val, vld_mask):
                self.val = val
                self.vld_mask = vld_mask
        out = StringIO()
        vcd = VcdWriter(out)
        d = datetime.strptime("2018-04-12 18:04:03.652880",
                              "%Y-%m-%d %H:%M:%S.%f")
        vcd.date(d)
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

        with open(os.path.join(BASE, "example0.vcd")) as f:
            ref = f.read()
            out = out.getvalue()
            self.assertEqual(ref, out)


if __name__ == "__main__":
    suite = unittest.TestSuite()
    # suite.addTest(VcdParserUnitTest('test_example0'))
    suite.addTest(unittest.makeSuite(VcdWriterUnitTest))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
