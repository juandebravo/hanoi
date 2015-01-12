import unittest

from .api import FunctionTestCase


def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FunctionTestCase))
    return suite
