import unittest
import os
from pyDigitalWaveTools.vcd.parser import VcdParser
BASE = os.path.dirname(os.path.realpath(__file__))


class VcdParserTC(unittest.TestCase):
    def test_example0(self):
        reference = {
            "name": "root",
            "type": {"name": "struct"},
            "children": [
                {
                    "name": "unit0",
                    "type": {"name": "struct"},
                    "children": [
                        {
                            "name": "sig0",
                            "type": {"name": "wire", "width": 1},
                            "data": [(0, "X"), (1, "0")],
                        },
                        {
                            "name": "sig1",
                            "type": {"name": "wire", "width": 1},
                            "data": [(0, "X"), (2, "1")],
                        },
                        {
                            "name": "vect0",
                            "type": {"name": "wire", "width": 16},
                            "data": [(0, "bXXXXXXXXXXXXXXXX"), (3, "b0000000000001010"), (4, "b0000000000010100")],
                        },
                    ]
                }
            ]
        }
        vcd = self.parse_file("example0.vcd")
        data = vcd.scope.toJson()
        self.assertDictEqual(reference, data)

    def parse_file(self, rel_name) -> VcdParser:
        fIn = os.path.join(BASE, rel_name)
        with open(fIn) as vcd_file:
            vcd = VcdParser()
            vcd.parse(vcd_file)
            return vcd

    def test_AxiRegTC_test_write(self):
        self.parse_file("AxiRegTC_test_write.vcd")

    def test_verilog2005_sample0(self):
        vcd = self.parse_file("verilog2005-sample0.vcd")
        data = vcd.scope
        self.assertEqual(len(data.children["top"].children), 2)

    def test_verilog2005_sample1(self):
        vcd = self.parse_file("verilog2005-sample0.vcd")
        vcd.scope.toJson()
    
if __name__ == "__main__":
    suite = unittest.TestSuite()
    #suite.addTest(VcdParserTC('test_verilog2005_sample0'))
    suite.addTest(unittest.makeSuite(VcdParserTC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
