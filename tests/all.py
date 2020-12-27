#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from unittest import TestLoader, TextTestRunner, TestSuite
from tests.jsonWriter_test import JsonWriterTC
from tests.vcdParser_test import VcdParserTC
from tests.vcdWriter_test import VcdWriterTC



def testSuiteFromTCs(*tcs):
    loader = TestLoader()
    loadedTcs = [loader.loadTestsFromTestCase(tc) for tc in tcs]
    suite = TestSuite(loadedTcs)
    return suite


suite = testSuiteFromTCs(
    JsonWriterTC,
    VcdParserTC,
    VcdWriterTC,
)


if __name__ == '__main__':
    runner = TextTestRunner(verbosity=2)

    try:
        from concurrencytest import ConcurrentTestSuite, fork_for_tests
        useParallerlTest = True
    except ImportError:
        # concurrencytest is not installed, use regular test runner
        useParallerlTest = False

    if useParallerlTest:
        # Run same tests across 4 processes
        concurrent_suite = ConcurrentTestSuite(suite, fork_for_tests())
        runner.run(concurrent_suite)
    else:
        sys.exit(not runner.run(suite).wasSuccessful())
