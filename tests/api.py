# -*- encoding: utf-8 -*-

import unittest
from pyshould import should, all_of

from hanoi.api import Rollout, RolloutException
from hanoi.backend import Feature, MemoryBackEnd, RedisBackEnd


class Foo(object):
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return self.id


class RolloutTestCase(unittest.TestCase):

    FN = 'foo'

    def _get_basic_rollout(self, fn):
        rollout = Rollout(MemoryBackEnd())
        rollout.add_func(fn, 'id')
        return rollout

    def setUp(self):
        self.rollout = self._get_basic_rollout(self.FN)

    def tearDown(self):
        self.rollout = None

    def test_backend_should_not_be_none(self):
        rollout = Rollout(None)
        with should.throw(TypeError):
            rollout.backend

    def test_register_a_functionality(self):
        self.rollout.backend.get_functionalities() | should.have_len(1)

    def test_register_two_functionalities(self):
        self.rollout.add_func('bar', lambda x: x.id, percentage=0)
        self.rollout.backend.get_functionalities() | should.have_len(2)
        self.rollout.backend.get_functionalities() | should.eql([
            self.FN, 'bar'
        ])

    def test_overrides_a_functionality_with_same_name(self):
        self.rollout.add_func(self.FN, lambda x: x.id)
        self.rollout.backend.get_functionalities() | should.have_len(1)

    def test_enable_a_functionality(self):
        self.rollout.enable(self.FN)
        self.rollout.is_enabled(self.FN) | should.be_truthy

    def test_disable_a_functionality(self):
        self.rollout.disable(self.FN)
        self.rollout.is_enabled(self.FN) | should.be_falsy

    def test_toggle_a_functionality(self):
        self.rollout.is_enabled(self.FN) | should.be_truthy
        self.rollout.toggle(self.FN)
        self.rollout.is_enabled(self.FN) | should.be_falsy
        self.rollout.toggle(self.FN)
        self.rollout.is_enabled(self.FN) | should.be_truthy

    def test_set_percentage_to_100(self):
        self.rollout.set_percentage(self.FN, 100)
        self.rollout.is_enabled("foo") | should.be_true

    def test_set_percentage_to_0_func_is_still_enabled(self):
        self.rollout.set_percentage(self.FN, 0)
        self.rollout.is_enabled("foo") | should.be_truthy
        self.rollout.is_enabled("foo", "bar") | should.be_falsy

    def test_set_percentage_to_101(self):
        with should.throw(AttributeError):
            self.rollout.set_percentage(self.FN, 101)

    def test_set_percentage_to_negative(self):
        with should.throw(AttributeError):
            self.rollout.set_percentage(self.FN, -1)

    def test_a_functionality_with_percentage_100_enabled(self):
        self.rollout.enable(self.FN)
        self.rollout.set_percentage(self.FN, 100)
        # Check in 100 different users
        for i in xrange(0, 100):
            self.rollout.is_enabled("foo", str(i)) | should.be_true

    def test_a_functionality_with_percentage_100_disabled(self):
        self.rollout.enable(self.FN)
        self.rollout.set_percentage(self.FN, 0)
        # Check in 100 different users
        for i in xrange(0, 100):
            self.rollout.is_enabled("foo", str(i)) | should.be_falsy

    def test_a_functionality_with_percentage_50_enabled(self):
        self.rollout.enable(self.FN)
        self.rollout.set_percentage(self.FN, 50)
        user = Foo("1")
        self.rollout.is_enabled(self.FN, user) | should.be_truthy
        u = Foo("2")
        self.rollout.is_enabled(self.FN, u) | should.be_falsy

    def test_a_functionality_with_percentage_50_disabled(self):
        self.rollout.disable(self.FN)
        self.rollout.set_percentage(self.FN, 50)
        for x in xrange(1, 100):
            u = Foo(str(x))
            self.rollout.register(self.FN, u)
            self.rollout.is_enabled(self.FN, u) | should.be_falsy

    def test_is_enabled_to_a_register_user(self):
        self.rollout.add_func('bar')
        u = "bazz"
        self.rollout.register(self.FN, u)
        self.rollout.is_enabled(self.FN, u) | should.be_truthy

    def test_is_enabled_to_a_non_register_user(self):
        self.rollout.add_func('bar')
        u = "bazz"
        self.rollout.register(self.FN, u)
        self.rollout.is_enabled(self.FN, u+u) | should.be_falsy

    def test_add_a_user_to_a_disabled_functionality(self):
        self.rollout.disable(self.FN)
        self.rollout.is_enabled(self.FN) | should.be_falsy
        self.rollout.is_enabled(self.FN, 'foo') | should.be_falsy

    def test_set_a_rule_to_a_functionality_user_matches(self):
        import re
        self.rollout.register(self.FN, re.compile("00$"))
        self.rollout.is_enabled(self.FN, '0000000') | should.be_truthy

    def test_set_a_rule_to_a_functionality_user_does_not_match(self):
        import re
        self.rollout.register(self.FN, re.compile("00$"))
        self.rollout.is_enabled(self.FN, "0000010") | should.be_falsy

    def test_set_a_rule_user_does_not_match_but_is_whitelisted(self):
        import re
        self.rollout.register(self.FN, "0000010")
        self.rollout.register(self.FN, re.compile("00$"))
        self.rollout.is_enabled(self.FN, "0000010") | should.be_truthy

    def test_set_a_rule_overrides_previous_rule(self):
        import re
        self.rollout.register(self.FN, re.compile("00$"))
        self.rollout.is_enabled(self.FN, "0000010") | should.be_falsy
        self.rollout.register(self.FN, re.compile("10$"))
        self.rollout.is_enabled(self.FN, "0000010") | should.be_truthy

    def test_decorator_enabled_decorator_when_feature_enabled(self):
        @self.rollout.enabled(self.FN)
        def foo(name):
            return name

        foo('bazz') | should.eql('bazz')

    def test_decorator_enabled_decorator_when_feature_not_exist(self):
        @self.rollout.enabled('bar')
        def foo(name):
            return name

        with should.throw(RolloutException):
            foo('bazz')

    def test_decorator_enabled_decorator_when_feature_disabled(self):
        @self.rollout.enabled(self.FN)
        def foo(name):
            return name

        self.rollout.disable(self.FN)
        with should.throw(RolloutException):
            foo('bazz')

    def test_decorator_check_with_current_id(self):
        @self.rollout.check(self.FN)
        def foo(name):
            return name

        self.rollout.set_current_id('bar')
        self.rollout.register(self.FN, 'bar')
        foo('bazz') | should.eql('bazz')

    def test_decorator_check_with_argument(self):
        @self.rollout.check(self.FN, 1)
        def foo(name):
            return name.id

        self.rollout.set_current_id('foo')
        self.rollout.register(self.FN, 'bar')
        foo(Foo('bar')) | should.eql('bar')


class RolloutWithRedisTestCase(unittest.TestCase):

    FN = 'foo'

    def _get_basic_rollout(self, fn):
        rollout = Rollout(RedisBackEnd())
        rollout.backend._redis.flushdb()
        rollout.add_func(fn, 'id')
        return rollout

    def setUp(self):
        self.rollout = self._get_basic_rollout(self.FN)

    def tearDown(self):
        self.rollout = None

    def test_backend_should_not_be_none(self):
        rollout = Rollout(None)
        with should.throw(TypeError):
            rollout.backend

    def test_register_a_functionality(self):
        self.rollout.backend.get_functionalities() | should.have_len(1)

    def test_register_two_functionalities(self):
        self.rollout.add_func('bar', 'id', percentage=0)
        self.rollout.backend.get_functionalities() | should.have_len(2)
        all_of([self.FN, 'bar']) | should.be_in(self.rollout.backend.get_functionalities())

    def test_overrides_a_functionality_with_same_name(self):
        self.rollout.add_func(self.FN, 'id')
        self.rollout.backend.get_functionalities() | should.have_len(1)

    def test_enable_a_functionality(self):
        self.rollout.enable(self.FN)
        self.rollout.is_enabled(self.FN) | should.be_truthy

    def test_disable_a_functionality(self):
        self.rollout.disable(self.FN)
        self.rollout.is_enabled(self.FN) | should.be_falsy

    def test_toggle_a_functionality(self):
        self.rollout.is_enabled(self.FN) | should.be_truthy
        self.rollout.toggle(self.FN)
        self.rollout.is_enabled(self.FN) | should.be_falsy
        self.rollout.toggle(self.FN)
        self.rollout.is_enabled(self.FN) | should.be_truthy

    def test_set_percentage_to_100(self):
        self.rollout.set_percentage(self.FN, 100)
        self.rollout.is_enabled("foo") | should.be_true

    def test_set_percentage_to_0_func_is_still_enabled(self):
        self.rollout.set_percentage(self.FN, 0)
        self.rollout.is_enabled("foo") | should.be_truthy
        self.rollout.is_enabled("foo", Foo("bar")) | should.be_falsy

    def test_set_percentage_to_101(self):
        with should.throw(AttributeError):
            self.rollout.set_percentage(self.FN, 101)

    def test_set_percentage_to_negative(self):
        with should.throw(AttributeError):
            self.rollout.set_percentage(self.FN, -1)

    def test_a_functionality_with_percentage_100_enabled(self):
        self.rollout.enable(self.FN)
        self.rollout.set_percentage(self.FN, 100)
        # Check in 100 different users
        for i in xrange(0, 100):
            self.rollout.is_enabled("foo", str(i)) | should.be_true

    def test_a_functionality_with_percentage_100_disabled(self):
        self.rollout.enable(self.FN)
        self.rollout.set_percentage(self.FN, 0)
        # Check in 100 different users
        for i in xrange(0, 100):
            self.rollout.is_enabled("foo", Foo(str(i))) | should.be_falsy

    def test_a_functionality_with_percentage_50_enabled(self):
        self.rollout.enable(self.FN)
        self.rollout.set_percentage(self.FN, 50)
        user = Foo("1")
        self.rollout.register(self.FN, user)
        self.rollout.is_enabled(self.FN, user) | should.be_truthy
        u = Foo("2")
        self.rollout.register(self.FN, u)
        self.rollout.is_enabled(self.FN, u) | should.be_truthy

    def test_a_functionality_with_percentage_50_disabled(self):
        self.rollout.disable(self.FN)
        self.rollout.set_percentage(self.FN, 50)
        for x in xrange(1, 100):
            u = Foo(str(x))
            self.rollout.register(self.FN, u)
            self.rollout.is_enabled(self.FN, u) | should.be_falsy

    def test_is_enabled_to_a_register_user(self):
        self.rollout.add_func('bar')
        u = Foo("bazz")
        self.rollout.register(self.FN, u)
        self.rollout.is_enabled(self.FN, u) | should.be_truthy

    def test_is_enabled_to_a_non_register_user(self):
        self.rollout.add_func('bar')
        u = "bazz"
        self.rollout.register(self.FN, Foo(u))
        self.rollout.is_enabled(self.FN, Foo(u+u)) | should.be_falsy

    def test_add_a_user_to_a_disabled_functionality(self):
        self.rollout.disable(self.FN)
        self.rollout.is_enabled(self.FN) | should.be_falsy
        self.rollout.is_enabled(self.FN, 'foo') | should.be_falsy

    def test_set_a_rule_to_a_functionality_user_matches(self):
        import re
        self.rollout.register(self.FN, re.compile("00$"))
        self.rollout.is_enabled(self.FN, Foo('0000000')) | should.be_truthy

    def test_set_a_rule_to_a_functionality_user_does_not_match(self):
        import re
        self.rollout.register(self.FN, re.compile("00$"))
        self.rollout.is_enabled(self.FN, Foo("0000010")) | should.be_falsy

    def test_set_a_rule_user_does_not_match_but_is_whitelisted(self):
        import re
        self.rollout.register(self.FN, "0000010")
        self.rollout.register(self.FN, re.compile("00$"))
        self.rollout.is_enabled(self.FN, Foo("0000010")) | should.be_truthy

    def test_set_a_rule_overrides_previous_rule(self):
        import re
        self.rollout.register(self.FN, re.compile("00$"))
        self.rollout.is_enabled(self.FN, Foo("0000010")) | should.be_falsy
        self.rollout.register(self.FN, re.compile("10$"))
        self.rollout.is_enabled(self.FN, Foo("0000010")) | should.be_truthy

    def test_decorator_enabled_decorator_when_feature_enabled(self):
        @self.rollout.enabled(self.FN)
        def foo(name):
            return name

        foo('bazz') | should.eql('bazz')

    def test_decorator_enabled_decorator_when_feature_not_exist(self):
        @self.rollout.enabled('bar')
        def foo(name):
            return name

        with should.throw(RolloutException):
            foo('bazz')

    def test_decorator_enabled_decorator_when_feature_disabled(self):
        @self.rollout.enabled(self.FN)
        def foo(name):
            return name

        self.rollout.disable(self.FN)
        with should.throw(RolloutException):
            foo('bazz')

    def test_decorator_check_with_current_id(self):
        @self.rollout.check(self.FN)
        def foo(name):
            return name

        self.rollout.set_current_id(Foo('bar'))
        self.rollout.register(self.FN, Foo('bar'))
        foo('bazz') | should.eql('bazz')

    def test_decorator_check_with_argument(self):
        @self.rollout.check(self.FN, 1)
        def foo(name):
            return name.id

        self.rollout.set_current_id('foo')
        self.rollout.register(self.FN, 'bar')
        foo(Foo('bar')) | should.eql('bar')


class FeatureTestCase(unittest.TestCase):

    def test_is_enabled_by_default(self):
        f = Feature('foo', lambda x: True, '100')
        f.enabled | should.be_truthy

    def test_name_is_valid_as_a_string(self):
        f = Feature('foo', lambda x: True, '100')
        f.name | should.eql('foo')

    def test_name_is_valid_as_unicode(self):
        f = Feature(u'üéê', lambda x: True, '100')
        f.name | should.eql(u'üéê')

    def test_name_cannot_be_None(self):
        with should.throw(AttributeError):
            Feature(None, lambda x: True, '100')

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
