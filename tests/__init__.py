import unittest

from .api import FeatureTestCase, RolloutTestCase


def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FeatureTestCase))
    suite.addTest(unittest.makeSuite(RolloutTestCase))
    return suite
