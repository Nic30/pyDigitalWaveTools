# pyDigitalWaveTools

[![Build Status](https://travis-ci.org/Nic30/pyDigitalWaveTools.svg?branch=master)](https://travis-ci.org/Nic30/pyDigitalWaveTools)
[![Coverage Status](https://coveralls.io/repos/github/Nic30/pyDigitalWaveTools/badge.svg?branch=master)](https://coveralls.io/github/Nic30/pyDigitalWaveTools?branch=master)
[![PyPI version](https://badge.fury.io/py/pyDigitalWaveTools.svg)](http://badge.fury.io/py/pyDigitalWaveTools) 
[![Documentation Status](https://readthedocs.org/projects/pyDigitalWaveTools/badge/?version=latest)](http://pyDigitalWaveTools.readthedocs.io/en/latest/?badge=latest)
[![Python version](https://img.shields.io/pypi/pyversions/pyDigitalWaveTools.svg)](https://img.shields.io/pypi/pyversions/pyDigitalWaveTools.svg)

python library for operations with VCD and other digital wave files

## Feature list
* parse VCD (std 2009) files to intermediate format
* write VCD files, user specified formatters for user types, predefined formatters for vectors, bits and enum values
* dump intermediate format as simple json

## Hello pyDigitalWaveTools

Here is a simple example how to use the VCD parser:

```python
#!/usr/bin/env python3
import json
import sys
from pyDigitalWaveTools.vcd.parser import VcdParser

if len(sys.argv) > 1:
    fname = sys.argv[1]
else:
    print('Give me a vcd file to parse')
    sys.exit(-1)

with open(fname) as vcd_file:
    vcd = VcdParser()
    vcd.parse(vcd_file)
    data = vcd.scope.toJson()
    print(json.dumps(data, indent=4, sort_keys=True))
```


## Output json format
```
scope
{ "name": "<scope name>"
  "children" : {"<children name>" : child}
}

child can be scope or signal record

signal record 
{ "name": "<signal name>"
  "type": {"sigType": "<vcd signal type>",
           "width": <bit width of signal (integer)>},
  "data": [<data records>],
}

data record format
[<time (number)>, <value (string, format dependent on datatype)>]
```


## Related open source

* [verilog-vcd-parser](https://github.com/ben-marshall/verilog-vcd-parser) - Python, A parser for Value Change Dump (VCD) files as specified in the IEEE System Verilog 1800-2012 standard.
* [pyvcd](https://github.com/SanDisk-Open-Source/pyvcd) - Python, vcd writer, GTKWave config writer