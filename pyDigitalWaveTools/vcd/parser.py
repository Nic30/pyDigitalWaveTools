#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
:note: inspired by https://github.com/GordonMcGregor/vcd_parser/blob/master/vcd/parser.py

A basic self contained VCD parser object

Walks through the definitions constructing the appropriate signal references.
Caches XMR paths if and when the signal value changes in the dump for future reference.
Needs some hooks for callbacks on signal changes and methods to allow sampling of a signal with an appropriate clock reference

Refer to IEEE SystemVerilog standard 1800-2009 for VCD details Section 21.7 Value Change Dump (VCD) files
'''

from collections import defaultdict
from io import StringIO
from itertools import dropwhile

from pyDigitalWaveTools.vcd.common import VcdVarScope, VcdVarInfo


class VcdSyntaxError(Exception):
    pass

class VcdDuplicatedVariableError(Exception):
    """
    This is when multiple definition to one variable happens. 
    E.g.
    $scope module testbench $end
    $var reg 3 ! x [2:0] $end
    $upscope $end
    $scope module testbench $end
    $var wire 8 " x [7:0] $end
    $upscope $end
    """
    pass

class VcdVarParsingInfo(VcdVarInfo):
    """
    Container of informations about variable in VCD for parsing of VCD file
    """

    def __init__(self, vcdId, name, width, sigType, parent):
        super(VcdVarParsingInfo, self).__init__(
            vcdId, name, width, sigType, parent)
        self.data = []

    def toJson(self):
        return {"name": self.name,
                "type": {"width": self.width,
                         "name": self.sigType},
                "data": self.data}


class VcdParser(object):
    '''
    A parser object for VCD files.
    Reads definitions and walks through the value changes
    https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=954909&tag=1

    :ivar ~.keyword_dispatch: dictionary {keyword: parse function}
    :ivar ~.scope: actual VcdSignalInfo
    :ivar ~.now: actual time (int)
    :ivar ~.idcode2series: dictionary {idcode: series} where series are list of tuples (time, value)
    :ivar ~.signals: dict {topName: VcdSignalInfo instance}
    '''
    VECTOR_VALUE_CHANGE_PREFIX = {
        "b", "B", "r", "R"
    }
    SCOPE_TYPES = {
        "begin", "fork", "function", "module", "task"
    }
    def __init__(self):
        keyword_functions = {
            # declaration_keyword ::=
            "$comment":        self.drop_while_end,
            "$date":           self.save_declaration,
            "$enddefinitions": self.vcd_enddefinitions,
            "$scope":          self.vcd_scope,
            "$timescale":      self.save_declaration,
            "$upscope":        self.vcd_upscope,
            "$var":            self.vcd_var,
            "$version":        self.save_declaration,
            # simulation_keyword ::=
            "$dumpall":        self.vcd_dumpall,
            "$dumpoff":        self.vcd_dumpoff,
            "$dumpon":         self.vcd_dumpon,
            "$dumpvars":       self.vcd_dumpvars,
            "$end":            self.vcd_end,
        }

        self.keyword_dispatch = defaultdict(
            lambda: self.parse_error, keyword_functions)

        # A root scope is used to deal with situations like
        # ------
        # $scope module testbench $end
        # $var reg 3 ! x [2:0] $end
        # $upscope $end
        # $scope module testbench $end
        # $var wire 8 " y [7:0] $end
        # $upscope $end
        # $enddefinitions $end
        # ------
        self.scope = VcdVarScope("root", None)
        self.now = 0
        self.idcode2series = {}
        self.end_of_definitions = False

    def value_change(self, vcdId, value):
        '''append change from VCD file signal data series'''
        self.idcode2series[vcdId].append((self.now, value))

    def parse_str(self, vcd_string: str):
        """
        Same as :func:`~.parse` just for string 
        """
        buff = StringIO(vcd_string)
        return self.parse(buff)

    def parse(self, file_handle):
        '''
        Tokenize and parse the VCD file

        :ivar ~.file_handle: opened file with vcd string
        '''
        # open the VCD file and create a token generator
        lineIterator = iter(enumerate(file_handle))
        tokeniser = ((lineNo, word)
                     for lineNo, line in lineIterator
                     for word in line.split() if word)
        #def tokeniser_wrap():
        #    for t in _tokeniser:
        #        print(t)
        #        yield t
        #tokeniser = tokeniser_wrap()

        while True:
            token = next(tokeniser)
            # parse VCD until the end of definitions
            self.keyword_dispatch[token[1]](tokeniser, token[1])
            if self.end_of_definitions:
                break

        while True:
            try:
                lineNo, token = next(tokeniser)
            except StopIteration:
                break

            # parse changes
            c = token[0]
            if c == '$':
                fn = self.keyword_dispatch[token.strip()]
                fn(tokeniser, token)
            elif c == '#':
                # [TODO] may be a float
                self.now = int(token[1:])
            else:
                self.vcd_value_change(lineNo, token, tokeniser)

    def vcd_value_change(self, lineNo, token, tokenizer):
        token = token.strip()
        if not token:
            return

        if token[0] in self.VECTOR_VALUE_CHANGE_PREFIX:
            # vectors and strings
            value = token
            _, vcdId = next(tokenizer)
        elif token[0] == "s":
            # string value
            value = token[1:]
            _, vcdId = next(tokenizer)
        else:
            # 1 bit value
            value = token[0]
            vcdId = token[1:]

        self.value_change(vcdId, value)

    def parse_error(self, tokeniser, keyword):
        raise VcdSyntaxError("Don't understand keyword: ", keyword)

    def drop_while_end(self, tokeniser, keyword):
        next(dropwhile(lambda x: x[1] != "$end", tokeniser))

    def read_while_end(self, tokeniser):
        for _, word in tokeniser:
            if word == "$end":
                return
            else:
                yield word

    def save_declaration(self, tokeniser, keyword):
        self.__setattr__(keyword.lstrip('$'),
                         " ".join(self.read_while_end(tokeniser)))

    def vcd_enddefinitions(self, tokeniser, keyword):
        self.end_of_definitions = True
        self.drop_while_end(tokeniser, keyword)

    def vcd_scope(self, tokeniser, keyword):
        scopeType = next(tokeniser)
        scopeTypeName = scopeType[1]
        assert scopeTypeName in self.SCOPE_TYPES, scopeType
        scopeName = next(tokeniser)
        assert next(tokeniser)[1] == "$end"
        s = self.scope
        name = scopeName[1]
        self.scope = VcdVarScope(name, s)
        if isinstance(s, VcdVarScope):
            # TODO: handling for cases when both module and var of the same name
            # exists in one scope
            assert name not in s.children, (s, name)
            s.children[name] = self.scope

    def vcd_upscope(self, tokeniser, keyword):
        self.scope = self.scope.parent
        assert next(tokeniser)[1] == "$end"

    def vcd_var(self, tokeniser, keyword):
        data = tuple(self.read_while_end(tokeniser))
        # ignore range on identifier ( TODO  Fix this )
        (var_type, size, vcdId, reference) = data[:4]
        parent = self.scope
        size = int(size)
        info = VcdVarParsingInfo(vcdId, reference, size, var_type, parent)
        assert vcdId not in self.idcode2series
        assert reference not in parent.children
        parent.children[reference] = info
        self.idcode2series[vcdId] = info.data

    def _vcd_value_change_list(self, tokeniser):
        while True:
            try:
                lineNo, token = next(tokeniser)
            except StopIteration:
                break
            if token and token[0] == "$":
                if token.startswith("$end"):
                    return
                else:
                    raise VcdSyntaxError(
                        "Line %d: Expected $end: %s " % (lineNo, token))
            else:
                self.vcd_value_change(lineNo, token, tokeniser)

    def vcd_dumpall(self, tokeniser, keyword):
        """
        specifies current values of all variables dumped

        vcd_simulation_dumpall ::= $dumpall { value_changes } $end

        .. code-block:: verilog

            $dumpall   1*@  x*#   0*$   bx   (k $end
        """
        self._vcd_value_change_list(tokeniser)

    def vcd_dumpoff(self, tokeniser, keyword):
        """
        all variables dumped with X values

        vcd_simulation_dumpoff ::= $dumpoff { value_changes } $end

        .. code-block:: verilog

            $dumpoff  x*@  x*#   x*$   bx   (k $end
        """
        self._vcd_value_change_list(tokeniser)

    def vcd_dumpon(self, tokeniser, keyword):
        """
        resumption of dumping and lists current values of all variables dumped.

        vcd_simulation_dumpon ::= $dumpon { value_changes } $end

        .. code-block:: verilog

            $dumpon   x*@  0*#   x*$   b1   (k $end
        """
        self._vcd_value_change_list(tokeniser)

    def vcd_dumpvars(self, tokeniser, keyword):
        """
        lists initial values of all variables dumped

        vcd_simulation_dumpvars ::= $dumpvars { value_changes } $end

        .. code-block:: verilog

            $dumpvars   x*@   z*$   b0   (k $end
        """
        self._vcd_value_change_list(tokeniser)

    def vcd_end(self, tokeniser, keyword):
        if not self.end_of_definitions:
            raise VcdSyntaxError("missing end of declaration section")


if __name__ == '__main__':
    import json
    import sys
    argc = len(sys.argv)
    if argc == 1:
        fIn = "../tests/AxiRegTC_test_write.vcd"
    elif argc == 2:
        fIn = sys.argv[1]
    elif argc == 3:
        fIn = sys.argv[1]
        fOut = sys.argv[2]
    else:
        raise ValueError(sys.argv)

    with open(fIn) as vcd_file:
        vcd = VcdParser()
        vcd.parse(vcd_file)
        data = vcd.scope.toJson()

        if argc == 3:
            with open(fOut, 'w') as jsonFile:
                jsonFile.write(data)
        else:
            print(json.dumps(data))
