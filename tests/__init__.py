import unittest

from .api import (
    FeatureTestCase, RolloutTestCase,
    RolloutWithRedisTestCase, RolloutWithRedisHighPerfTestCase
)

from .backend import RedisBackEndTestCase, RedisHighPerfBackEndTestCase, MemoryBackEndTestCase


def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FeatureTestCase))
    suite.addTest(unittest.makeSuite(RolloutTestCase))
    suite.addTest(unittest.makeSuite(RolloutWithRedisTestCase))
    suite.addTest(unittest.makeSuite(RolloutWithRedisHighPerfTestCase))
    suite.addTest(unittest.makeSuite(MemoryBackEndTestCase))
    suite.addTest(unittest.makeSuite(RedisBackEndTestCase))
    suite.addTest(unittest.makeSuite(RedisHighPerfBackEndTestCase))
    return suite
