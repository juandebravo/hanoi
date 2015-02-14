import unittest

from .api import FeatureTestCase, RolloutTestCase, RolloutWithRedisTestCase
from .backend import RedisBackEndTestCase, RedisHighPerfBackEndTestCase


def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FeatureTestCase))
    suite.addTest(unittest.makeSuite(RolloutTestCase))
    suite.addTest(unittest.makeSuite(RolloutWithRedisTestCase))
    suite.addTest(unittest.makeSuite(RedisBackEndTestCase))
    suite.addTest(unittest.makeSuite(RedisHighPerfBackEndTestCase))
    return suite
