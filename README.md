# pyDigitalWaveTools

[![Build Status](https://travis-ci.org/Nic30/pyDigitalWaveTools.svg?branch=master)](https://travis-ci.org/Nic30/pyDigitalWaveTools)
[![Coverage Status](https://coveralls.io/repos/github/Nic30/pyDigitalWaveTools/badge.svg?branch=master)](https://coveralls.io/github/Nic30/pyDigitalWaveTools?branch=master)
[![PyPI version](https://badge.fury.io/py/pyDigitalWaveTools.svg)](http://badge.fury.io/py/pyDigitalWaveTools) 
[![Documentation Status](https://readthedocs.org/projects/pyDigitalWaveTools/badge/?version=latest)](http://pyDigitalWaveTools.readthedocs.io/en/latest/?badge=latest)
[![Python version](https://img.shields.io/pypi/pyversions/pyDigitalWaveTools.svg)](https://img.shields.io/pypi/pyversions/pyDigitalWaveTools.svg)

python library for operations with VCD and other digital wave files

## Feature list
* parse VCD (std 2009) files to intermediate format
* write VCD files, user specified formaters for user types, predefined formaters for vectors, bits and enum values
* dump intermediate format as simple json



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
