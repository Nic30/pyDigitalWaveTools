import unittest
import os
from pyDigitalWaveTools.vcd.parser import VcdParser
BASE = os.path.dirname(os.path.realpath(__file__))


class VcdParserUnitTest(unittest.TestCase):
    def test_example0(self):
        fIn = os.path.join(BASE, "example0.vcd")
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

        with open(fIn) as vcd_file:
            vcd = VcdParser()
            vcd.parse(vcd_file)
            data = vcd.scope.toJson()
            self.maxDiff = None
            self.assertDictEqual(reference, data)


if __name__ == "__main__":
    suite = unittest.TestSuite()
    # suite.addTest(VcdParserUnitTest('test_example0'))
    suite.addTest(unittest.makeSuite(VcdParserUnitTest))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
