# -*- encoding: utf-8 -*-

import unittest
from nose.plugins.skip import SkipTest
from pyshould import should

from hanoi.api import Feature, Rollout
from hanoi.backend import MemoryBackEnd


class Foo(object):
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return self.id


class RolloutTestCase(unittest.TestCase):

    FN = 'foo'

    def _get_basic_rollout(self, fn):
        rollout = Rollout(MemoryBackEnd())
        rollout.add_func(fn, lambda x: x.id)
        return rollout

    def test_register_a_functionality(self):
        self._get_basic_rollout(self.FN).backend.get_functionalities() | should.have_len(1)

    def test_enable_a_functionality(self):
        rollout = self._get_basic_rollout(self.FN)
        rollout.enable(self.FN)
        rollout.is_enabled(self.FN) | should.be_truthy

    def test_disable_a_functionality(self):
        rollout = self._get_basic_rollout(self.FN)
        rollout.disable(self.FN)
        rollout.is_enabled(self.FN) | should.be_falsy

    def test_toggle_a_functionality(self):
        rollout = self._get_basic_rollout(self.FN)
        rollout.is_enabled(self.FN) | should.be_truthy
        rollout.toggle(self.FN)
        rollout.is_enabled(self.FN) | should.be_falsy
        rollout.toggle(self.FN)
        rollout.is_enabled(self.FN) | should.be_truthy

    def test_set_percentage_to_100(self):
        ro = self._get_basic_rollout(self.FN)
        ro.set_percentage(self.FN, 100)
        ro.is_enabled("foo") | should.be_true

    def test_set_percentage_to_0_func_is_still_enabled(self):
        ro = self._get_basic_rollout(self.FN)
        ro.set_percentage(self.FN, 0)
        ro.is_enabled("foo") | should.be_truthy
        ro.is_enabled("foo", "bar") | should.be_falsy

    def test_set_percentage_to_101(self):
        with should.throw(AttributeError):
            self._get_basic_rollout(self.FN).set_percentage(self.FN, 101)

    def test_set_percentage_to_negative(self):
        with should.throw(AttributeError):
            self._get_basic_rollout(self.FN).set_percentage(self.FN, -1)

    def test_a_functionality_with_percentage_100_enabled(self):
        ro = self._get_basic_rollout(self.FN)
        ro.enable(self.FN)
        ro.set_percentage(self.FN, 100)
        # Check in 100 different users
        for i in xrange(0, 100):
            ro.is_enabled("foo", str(i)) | should.be_true

    def test_a_functionality_with_percentage_100_disabled(self):
        ro = self._get_basic_rollout(self.FN)
        ro.enable(self.FN)
        ro.set_percentage(self.FN, 0)
        # Check in 100 different users
        for i in xrange(0, 100):
            ro.is_enabled("foo", str(i)) | should.be_falsy

    def test_a_functionality_with_percentage_50_enabled(self):
        ro = self._get_basic_rollout(self.FN)
        ro.enable(self.FN)
        ro.set_percentage(self.FN, 50)
        user = Foo("1")
        ro.register(self.FN, user)
        ro.is_enabled(self.FN, user) | should.be_truthy
        u = Foo("2")
        ro.register(self.FN, u)
        ro.is_enabled(self.FN, u) | should.be_falsy

    def test_a_functionality_with_percentage_50_disabled(self):
        ro = self._get_basic_rollout(self.FN)
        ro.disable(self.FN)
        ro.set_percentage(self.FN, 50)
        for x in xrange(1, 100):
            u = Foo(str(x))
            ro.register(self.FN, u)
            ro.is_enabled(self.FN, u) | should.be_falsy

    def test_is_enabled_to_a_register_user(self):
        ro = self._get_basic_rollout(self.FN)
        ro.add_func('bar')
        u = "bazz"
        ro.register(self.FN, u)
        ro.is_enabled(self.FN, u) | should.be_truthy

    def test_is_enabled_to_a_non_register_user(self):
        ro = self._get_basic_rollout(self.FN)
        ro.add_func('bar')
        u = "bazz"
        ro.register(self.FN, u)
        ro.is_enabled(self.FN, u+u) | should.be_falsy

    def test_add_a_user_to_a_disabled_functionality(self):
        ro = self._get_basic_rollout(self.FN)
        ro.disable(self.FN)
        ro.is_enabled(self.FN) | should.be_falsy
        ro.is_enabled(self.FN, 'foo') | should.be_falsy

    def test_set_a_rule_to_a_functionality_user_matches(self):
        ro = self._get_basic_rollout(self.FN)
        import re
        ro.register(self.FN, re.compile("00$"))
        ro.is_enabled(self.FN, '0000000') | should.be_truthy

    def test_set_a_rule_to_a_functionality_user_does_not_match(self):
        ro = self._get_basic_rollout(self.FN)
        import re
        ro.register(self.FN, re.compile("00$"))
        ro.is_enabled(self.FN, "0000010") | should.be_falsy

    def test_set_a_rule_user_does_not_match_but_is_whitelisted(self):
        ro = self._get_basic_rollout(self.FN)
        import re
        ro.register(self.FN, "0000010")
        ro.register(self.FN, re.compile("00$"))
        ro.is_enabled(self.FN, "0000010") | should.be_truthy

    def test_set_a_rule_overrides_previous_rule(self):
        ro = self._get_basic_rollout(self.FN)
        import re
        ro.register(self.FN, re.compile("00$"))
        ro.is_enabled(self.FN, "0000010") | should.be_falsy
        ro.register(self.FN, re.compile("10$"))
        ro.is_enabled(self.FN, "0000010") | should.be_truthy

    def test_decorator_enabled(self):
        raise SkipTest("to be done")

    def test_decorator_check(self):
        raise SkipTest("to be done")


class FeatureTestCase(unittest.TestCase):

    def test_name_is_valid_as_a_string(self):
        f = Feature('foo', lambda x: True, '100')
        f.name | should.eql('foo')

    def test_name_is_valid_as_a_unicode(self):
        f = Feature(u'üéê', lambda x: True, '100')
        f.name | should.eql(u'üéê')

    def test_name_should_be_a_string(self):
        with should.throw(AttributeError):
            Feature(1, lambda x: True, '100')

    def test_name_is_read_only(self):
        f = Feature("foo", lambda x: True, 20)

        with should.throw(RuntimeError):
            f.name = "bar"

    def test_percentage_is_casted_to_integer_if_valid_number_as_string(self):
        f = Feature('foo', lambda x: True, '100')
        f.percentage | should.eql(100)

    def test_percentage_should_be_a_number(self):
        with should.throw(AttributeError):
            Feature('foo', lambda x: True, 'bar')

    def test_percentage_should_be_lower_than_100(self):
        with should.throw(AttributeError):
            Feature('foo', lambda x: True, 101)

    def test_percentage_should_be_greater_than_0(self):
        with should.throw(AttributeError):
            Feature('foo', lambda x: True, -1)

    def test_cannot_set_invalid_attributes(self):
        f = Feature('foo', lambda x: True, 100)

        with should.throw(AttributeError):
            f.bar
