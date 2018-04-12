import unittest
import os
from pyDigitalWaveTools.vcd.parser import VcdParser
import json
BASE = os.path.dirname(os.path.realpath(__file__))


class VcdParserUnitTest(unittest.TestCase):
    def test_example0(self):
        fIn = os.path.join(BASE, "example0.vcd")
        reference = {"children": {
            "sig0": {"data": [[0, "X"], [1, "0"]], "name": "sig0",
                     "type": {"sigType": "wire", "width": "1"}},
            "sig1": {"data": [[0, "X"], [2, "1"]], "name": "sig1",
                     "type": {"sigType": "wire", "width": "1"}},
            "vect0": {"data": [[0, "bXXXXXXXXXXXXXXXX"], [3, "b0000000000001010"], [4, "b0000000000010100"]],
                      "name": "vect0", "type": {"sigType": "wire", "width": "16"}}}, "name": "unit0"}

        with open(fIn) as vcd_file:
            vcd = VcdParser()
            vcd.parse(vcd_file)
            data = vcd.scope.toJson()
            self.assertEqual(json.dumps(reference, sort_keys=True),
                             json.dumps(data, sort_keys=True))


if __name__ == "__main__":
    suite = unittest.TestSuite()
    # suite.addTest(VcdParserUnitTest('test_example0'))
    suite.addTest(unittest.makeSuite(VcdParserUnitTest))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
