# pyDigitalWaveTools
python library for operations with VCD and other digital wave files

## Feature list
* parse VCD (std 2009) files to intermediate format
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
