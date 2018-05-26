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
from itertools import dropwhile
from pyDigitalWaveTools.vcd.common import VcdVarScope, VcdVarInfo


class VcdSyntaxError(Exception):
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
                         "sigType": self.sigType},
                "data": self.data}


class VcdParser(object):
    '''
    A parser object for VCD files.
    Reads definitions and walks through the value changes

    :ivar keyword_dispatch: dictionary {keyword: parse function}
    :ivar scope: actual VcdSignalInfo
    :ivar now: actual time (int)
    :ivar idcode2series: dictionary {idcode: series} where series are list of tuples (time, value)
    :ivar signals: dict {topName: VcdSignalInfo instance}
    '''

    def __init__(self):

        keyword_functions = {
            # declaration_keyword ::=
            "$comment":        self.drop_declaration,
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
            self.parse_error, keyword_functions)

        self.scope = None
        self.now = 0
        self.idcode2series = {}
        self.end_of_definitions = False

    def value_change(self, vcdId, value):
        '''append change from VCD file signal data series'''
        self.idcode2series[vcdId].append((self.now, value))

    def parse(self, file_handle):
        '''
        Tokenize and parse the VCD file

        :ivar file_handle: opened file with vcd string
        '''
        # open the VCD file and create a token generator
        lineIterator = iter(enumerate(file_handle))
        tokeniser = ((lineNo, word) for lineNo, line in lineIterator
                     for word in line.split() if word)

        while True:
            token = next(tokeniser)
            # parse VCD until the end of definitions
            self.keyword_dispatch[token[1]](tokeniser, token[1])
            if self.end_of_definitions:
                break

        while True:
            try:
                lineNo, token = next(lineIterator)
            except StopIteration:
                break

            # parse changes
            c = token[0]
            if c == '$':
                # skip $dump* tokens and $end tokens in sim section
                continue
            elif c == '#':
                # [TODO] may be a float
                self.now = int(token[1:])
            else:
                sp = token.split()
                sp_len = len(sp)
                if sp_len == 1:
                    # 1 bit value
                    value = c
                    vcdId = token[1:]
                elif sp_len == 2:
                    # vectors and strings
                    value, vcdId = sp
                else:
                    raise VcdSyntaxError(
                        "Line %d: Don't understand: %s " % (lineNo, token))

                self.value_change(vcdId.strip(), value.strip())

    def parse_error(self, tokeniser, keyword):
        raise VcdSyntaxError("Don't understand keyword: ", keyword)

    def drop_declaration(self, tokeniser, keyword):
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
        self.drop_declaration(tokeniser, keyword)

    def vcd_scope(self, tokeniser, keyword):
        scopeType = next(tokeniser)
        assert scopeType[1] == "module", scopeType
        scopeName = next(tokeniser)
        assert next(tokeniser)[1] == "$end"
        self.scope = VcdVarScope(scopeName[1], self.scope)

    def vcd_upscope(self, tokeniser, keyword):
        p = self.scope.parent
        if p is not None:
            self.scope = p
        assert next(tokeniser)[1] == "$end"

    def vcd_var(self, tokeniser, keyword):
        data = tuple(self.read_while_end(tokeniser))
        # ignore range on identifier ( TODO  Fix this )
        (var_type, size, vcdId, reference) = data[:4]
        parent = self.scope
        info = VcdVarParsingInfo(vcdId, reference, size, var_type, parent)
        assert vcdId not in self.idcode2series
        assert reference not in parent.children
        parent.children[reference] = info
        self.idcode2series[vcdId] = info.data

    def vcd_dumpall(self, tokeniser, keyword):
        pass

    def vcd_dumpoff(self, tokeniser, keyword):
        pass

    def vcd_dumpon(self, tokeniser, keyword):
        pass

    def vcd_dumpvars(self, tokeniser, keyword):
        pass

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
