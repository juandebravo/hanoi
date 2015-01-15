import unittest

from .api import FunctionTestCase, RolloutTestCase


def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FunctionTestCase))
    suite.addTest(unittest.makeSuite(RolloutTestCase))
    return suite
