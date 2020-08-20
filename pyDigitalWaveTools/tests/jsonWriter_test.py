import json
import os
import unittest

from pyDigitalWaveTools.json.value_format import JsonBitsFormatter
from pyDigitalWaveTools.json.writer import JsonWriter
from pyDigitalWaveTools.tests.vcdWriter_test import example_dump_values0


BASE = os.path.dirname(os.path.realpath(__file__))


def value_tuples_to_lists(scope: dict):
    """
    We need to convert all tuples to list because the tuple is serialized as list in json
    and after de-serialization the tuple objects will become lists
    """
    data = scope.get("data", None)
    if data is not None:
        data = [list(d) for d in data]
        scope["data"] = data

    children = scope.get("children", None)
    if children is not None:
        for c in children:
            value_tuples_to_lists(c)
    return scope


class JsonWriterTC(unittest.TestCase):

    def test_example0(self):

        res = {}
        w = JsonWriter(res)
        example_dump_values0(w, JsonBitsFormatter)
        
        # with open(os.path.join(BASE, "example0.json"), "w") as f:
        #    json.dump(res, f, indent=2, sort_keys=True)

        res = value_tuples_to_lists(res)
        with open(os.path.join(BASE, "example0.json")) as f:
            ref = json.load(f)
            self.assertDictEqual(ref, res)


if __name__ == "__main__":
    suite = unittest.TestSuite()
    # suite.addTest(JsonWriterTC('test_example0'))
    suite.addTest(unittest.makeSuite(JsonWriterTC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
