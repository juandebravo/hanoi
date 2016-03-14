# -*- encoding: utf-8 -*-

import unittest
from pyshould import should, all_of
import re

from hanoi.backend import MemoryBackEnd, RedisBackEnd, RedisHighPerfBackEnd, Feature


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

    def test_field_can_be_none(self):
        f = Feature('foo')
        f.get_item_id('bar') | should.eql('bar')

    def test_get_item_id_casts_to_string(self):
        f = Feature('foo')

        class Foo(object):
            def __str__(self):
                return 'bar'

        f.get_item_id(Foo()) | should.eql('bar')

    def test_get_item_id_calls_the_field_if_callable(self):
        f = Feature('foo', 'bar')

        class Foo(object):
            def bar(self):
                return 'bazz'

        f.get_item_id(Foo()) | should.eql('bazz')

    def test_get_item_id_returns_the_field_if_not_callable(self):
        f = Feature('foo', 'bar')

        class Foo(object):
            @property
            def bar(self):
                return 'bazz'

        f.get_item_id(Foo()) | should.eql('bazz')

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


class MemoryBackEndTestCase(unittest.TestCase):
    def setUp(self):
        self.backend = MemoryBackEnd()

    def test_retrieve_a_variant(self):
        fn = "FOO"
        _variants = ["foo", "bar", "bazz"]
        self.backend.add_functionality(Feature(fn, variants=_variants))
        f = self.backend.get_functionality(fn)
        f.name | should.eql(fn)
        f.percentage | should.eql(100)
        self.backend.variant(fn, 'juan') | should.be_in(f.variants)
        self.backend.variant(fn, 'juan2') | should.be_in(f.variants)

    def test_retrieve_a_variant_is_none_if_disabled(self):
        fn = "FOO"
        _variants = ["foo", "bar", "bazz"]
        self.backend.add_functionality(Feature(fn, percentage=0, variants=_variants))
        f = self.backend.get_functionality(fn)
        f.name | should.eql(fn)
        self.backend.variant(fn, 'juan') | should.be_none()
        self.backend.variant(fn, 'juan2') | should.be_none()


class RedisBackEndTestCase(unittest.TestCase):

    def setUp(self):
        self.backend = RedisBackEnd()
        self.backend._redis.flushdb()

    def test_retrieve_empty_array_when_nofuncionality_added(self):
        self.backend.get_functionalities() | should.be_empty()

    def test_add_a_functionality(self):
        fn = "FOO"
        self.backend.add_functionality(Feature(fn))
        self.backend.get_functionalities() | should.have_len(1)
        f, users = self.backend._get_functionality(fn)
        f.name | should.eql(fn)
        f.percentage | should.eql(100)
        users | should.be_empty().and_array()

    def test_add_a_functionality_with_percentage(self):
        fn = "FOO"
        self.backend.add_functionality(Feature(fn, None, 50))
        self.backend.get_functionalities() | should.have_len(1)
        f, users = self.backend._get_functionality(fn)
        f.name | should.eql(fn)
        f.percentage | should.eql(50)
        users | should.be_empty().and_array()

    def test_add_a_disabled_functionality_with_percentage(self):
        fn = "FOO"
        func = Feature(fn, None, 50)
        func.enabled = False
        self.backend.add_functionality(func)
        self.backend.get_functionalities() | should.have_len(1)
        f, users = self.backend._get_functionality(fn)
        f.name | should.eql(fn)
        f.percentage | should.eql(50)
        f.enabled | should.be_falsy()
        users | should.be_empty().and_array()

    def test_add_an_user(self):
        fn = "FOO"
        self.backend.add_functionality(Feature(fn))
        self.backend.get_functionalities() | should.have_len(1)
        f, users = self.backend._get_functionality(fn)
        users | should.be_empty().and_array()
        self.backend.add(fn, "bar")
        f, users = self.backend._get_functionality(fn)
        users | should.be_array().and_have_len(1)
        self.backend.add(fn, "bazz")
        f, users = self.backend._get_functionality(fn)
        users | should.eql(['bar', 'bazz'])

    def test_add_existing_an_user(self):
        fn = "FOO"
        self.backend.add_functionality(Feature(fn))
        self.backend.get_functionalities() | should.have_len(1)
        f, users = self.backend._get_functionality(fn)
        users | should.be_empty().and_array()
        self.backend.add(fn, "bar")
        self.backend.add(fn, "bar")
        f, users = self.backend._get_functionality(fn)
        users | should.eql(['bar'])

    def test_is_enabled_func_does_not_exist(self):
        fn = "FOO"
        self.backend.is_enabled(fn) | should.be_falsy()

    def test_is_enabled_func_exists(self):
        fn = "FOO"
        self.backend.add_functionality(Feature(fn))
        self.backend.is_enabled(fn) | should.be_truthy()

    def test_is_enabled_func_exists_but_is_disabled(self):
        fn = "FOO"
        func = Feature(fn, None, 50)
        func.enabled = False
        self.backend.add_functionality(func)
        self.backend.is_enabled(fn) | should.be_falsy()

    def test_is_enabled_func_in_an_user_not_added_but_percentage_is_100(self):
        fn = "FOO"
        func = Feature(fn, None, 100)
        self.backend.add_functionality(func)
        self.backend.is_enabled(fn, "bar") | should.be_truthy()

    def test_is_enabled_func_in_an_user_not_added(self):
        fn = "FOO"
        func = Feature(fn, None, 0)
        self.backend.add_functionality(func)
        self.backend.is_enabled(fn, "bar") | should.be_falsy()

    def test_is_enabled_func_in_an_user_added(self):
        fn = "FOO"
        func = Feature(fn, None, 0)
        self.backend.add_functionality(func)
        self.backend.add(fn, "bar")
        self.backend.is_enabled(fn, "bar") | should.be_truthy()

    def test_is_enabled_func_in_an_user_with_an_enabled_rule_that_matches(self):
        fn = "FOO"
        func = Feature(fn, None, 0)
        self.backend.add_functionality(func)
        self.backend.set_rule(fn, re.compile(r"00$"))
        self.backend.is_enabled(fn, "4400") | should.be_truthy()

    def test_is_enabled_func_in_an_user_with_an_enabled_rule_that_doesnt_match(self):
        fn = "FOO"
        func = Feature(fn, None, 0)
        self.backend.add_functionality(func)
        self.backend.set_rule(fn, re.compile(r"00$"))
        self.backend.is_enabled(fn, "44001") | should.be_falsy()

    def test_is_enabled_func_in_an_user_that_matches_the_percentage(self):
        fn = "FOO"
        func = Feature(fn, None, 50)
        self.backend.add_functionality(func)
        self.backend.is_enabled(fn, "0") | should.be_true()

    def test_is_enabled_func_in_an_user_that_does_match_the_percentage(self):
        fn = "FOO"
        func = Feature(fn, None, 50)
        self.backend.add_functionality(func)
        self.backend.is_enabled(fn, "1") | should.be_false()

    def test_disable(self):
        fn = "FOO"
        self.backend.add_functionality(Feature(fn))
        self.backend.disable(fn)
        self.backend.is_enabled(fn) | should.be_falsy()

    def test_enable(self):
        fn = "FOO"
        func = Feature(fn, None, 50)
        func.enabled = False
        self.backend.add_functionality(func)
        self.backend.is_enabled(fn) | should.be_falsy()
        self.backend.enable(fn)
        self.backend.is_enabled(fn) | should.be_truthy()

    def test_toggle(self):
        fn = "FOO"
        self.backend.add_functionality(Feature(fn))
        self.backend.is_enabled(fn) | should.be_truthy()
        self.backend.toggle(fn)
        self.backend.is_enabled(fn) | should.be_falsy()
        self.backend.toggle(fn)
        self.backend.is_enabled(fn) | should.be_truthy()

    def test_retrieve_a_variant(self):
        fn = "FOO"
        _variants = ["foo", "bar", "bazz"]
        self.backend.add_functionality(Feature(fn, variants=_variants))
        f, _ = self.backend._get_functionality(fn)
        f.name | should.eql(fn)
        f.percentage | should.eql(100)
        self.backend.variant(fn, 'juan') | should.be_in(f.variants)
        self.backend.variant(fn, 'juan2') | should.be_in(f.variants)

    def test_retrieve_a_variant_is_none_if_disabled(self):
        fn = "FOO"
        _variants = ["foo", "bar", "bazz"]
        self.backend.add_functionality(Feature(fn, percentage=0, variants=_variants))
        f, _ = self.backend._get_functionality(fn)
        f.name | should.eql(fn)
        self.backend.variant(fn, 'juan') | should.be_none()
        self.backend.variant(fn, 'juan2') | should.be_none()


class RedisHighPerfBackEndTestCase(unittest.TestCase):

    def setUp(self):
        self.backend = RedisHighPerfBackEnd()
        self.backend._redis.flushdb()

    def test_get_functionalities_not_implemented(self):
        with should.throw(NotImplementedError):
            self.backend.get_functionalities()

    def test_add_a_functionality(self):
        fn = "FOO"
        self.backend.add_functionality(Feature(fn))
        f = self.backend._get_functionality(fn)
        f.name | should.eql(fn)
        f.percentage | should.eql(100)

    def test_add_a_functionality_with_percentage(self):
        fn = "FOO"
        self.backend.add_functionality(Feature(fn, None, 50))
        f = self.backend._get_functionality(fn)
        f.name | should.eql(fn)
        f.percentage | should.eql(50)

    def test_add_a_functionality_with_one_user(self):
        fn = "FOO"
        self.backend.add_functionality(Feature(fn, None, 0), ["bar"])
        self.backend.is_enabled(fn, "bar") | should.be_true()

    def test_add_a_functionality_with_a_hundred_users(self):
        fn = "FOO"
        users = ["bar" + str(i) for i in range(100)]

        self.backend.add_functionality(Feature(fn, None, 0), users)

        for u in users:
            self.backend.is_enabled(fn, u) | should.be_true()

        self.backend.is_enabled(fn, "bar100") | should.be_false()

    def test_add_a_disabled_functionality_with_percentage(self):
        fn = "FOO"
        func = Feature(fn, None, 50)
        func.enabled = False
        self.backend.add_functionality(func)
        f = self.backend._get_functionality(fn)
        f.name | should.eql(fn)
        f.percentage | should.eql(50)
        f.enabled | should.be_falsy()
        self.backend._redis.smembers("rollout:users:FOO") | should.be_empty()

    def test_add_a_functionality_with_variants(self):
        fn = "FOO"
        _variants = ["foo", "bar", "bazz"]
        self.backend.add_functionality(Feature(fn, variants=_variants))
        f = self.backend._get_functionality(fn)
        f.name | should.eql(fn)
        f.percentage | should.eql(100)
        all_of(["foo", "bar", "bazz"]) | should.be_in(f.variants)

    def test_add_an_user(self):
        fn = "FOO"
        self.backend.add_functionality(Feature(fn, percentage=0))
        self.backend.add(fn, "bar")
        self.backend.is_enabled("FOO", "bar") | should.be_truthy
        self.backend.is_enabled("FOO", "bazz") | should.be_falsy
        self.backend.add(fn, "bazz")
        self.backend.is_enabled("FOO", "bazz") | should.be_truthy

    def test_add_an_existing_user(self):
        fn = "FOO"
        self.backend.add_functionality(Feature(fn))
        self.backend.add(fn, "bar")
        self.backend.add(fn, "bar")
        self.backend.is_enabled("FOO", "bar") | should.be_truthy

    def test_is_enabled_func_does_not_exist(self):
        fn = "FOO"
        self.backend.is_enabled(fn) | should.be_falsy()

    def test_is_enabled_func_exists(self):
        fn = "FOO"
        self.backend.add_functionality(Feature(fn))
        self.backend.is_enabled(fn) | should.be_truthy()

    def test_is_enabled_func_exists_but_is_disabled(self):
        fn = "FOO"
        func = Feature(fn, None, 50)
        func.enabled = False
        self.backend.add_functionality(func)
        self.backend.is_enabled(fn) | should.be_falsy()

    def test_is_enabled_func_in_an_user_not_added_but_percentage_is_100(self):
        fn = "FOO"
        func = Feature(fn, None, 100)
        self.backend.add_functionality(func)
        self.backend.is_enabled(fn, "bar") | should.be_truthy()

    def test_is_enabled_func_in_an_user_not_added(self):
        fn = "FOO"
        func = Feature(fn, None, 0)
        self.backend.add_functionality(func)
        self.backend.is_enabled(fn, "bar") | should.be_falsy()

    def test_is_enabled_func_in_an_user_added(self):
        fn = "FOO"
        func = Feature(fn, None, 0)
        self.backend.add_functionality(func)
        self.backend.add(fn, "bar")
        self.backend.is_enabled(fn, "bar") | should.be_truthy()

    def test_is_enabled_func_in_an_user_with_an_enabled_rule_that_matches(self):
        fn = "FOO"
        func = Feature(fn, None, 0)
        self.backend.add_functionality(func)
        self.backend.set_rule(fn, re.compile(r"00$"))
        self.backend.is_enabled(fn, "4400") | should.be_truthy()

    def test_is_enabled_func_in_an_user_with_an_enabled_rule_that_doesnt_match(self):
        fn = "FOO"
        func = Feature(fn, None, 0)
        self.backend.add_functionality(func)
        self.backend.set_rule(fn, re.compile(r"00$"))
        self.backend.is_enabled(fn, "44001") | should.be_falsy()

    def test_is_enabled_func_in_an_user_that_matches_the_percentage(self):
        fn = "FOO"
        func = Feature(fn, None, 50)
        self.backend.add_functionality(func)
        self.backend.is_enabled(fn, "0") | should.be_true()

    def test_is_enabled_func_in_an_user_that_does_match_the_percentage(self):
        fn = "FOO"
        func = Feature(fn, None, 50)
        self.backend.add_functionality(func)
        self.backend.is_enabled(fn, "1") | should.be_false()

    def test_disable(self):
        fn = "FOO"
        self.backend.add_functionality(Feature(fn))
        self.backend.disable(fn)
        self.backend.is_enabled(fn) | should.be_falsy()

    def test_enable(self):
        fn = "FOO"
        func = Feature(fn, None, 50)
        func.enabled = False
        self.backend.add_functionality(func)
        self.backend.is_enabled(fn) | should.be_falsy()
        self.backend.enable(fn)
        self.backend.is_enabled(fn) | should.be_truthy()

    def test_toggle(self):
        fn = "FOO"
        self.backend.add_functionality(Feature(fn))
        self.backend.is_enabled(fn) | should.be_truthy()
        self.backend.toggle(fn)
        self.backend.is_enabled(fn) | should.be_falsy()
        self.backend.toggle(fn)
        self.backend.is_enabled(fn) | should.be_truthy()

    def test_retrieve_a_variant(self):
        fn = "FOO"
        _variants = ["foo", "bar", "bazz"]
        self.backend.add_functionality(Feature(fn, variants=_variants))
        f = self.backend._get_functionality(fn)
        f.name | should.eql(fn)
        f.percentage | should.eql(100)
        self.backend.variant(fn, 'juan') | should.be_in(f.variants)
        self.backend.variant(fn, 'juan2') | should.be_in(f.variants)

    def test_retrieve_a_variant_is_none_if_disabled(self):
        fn = "FOO"
        _variants = ["foo", "bar", "bazz"]
        self.backend.add_functionality(Feature(fn, percentage=0, variants=_variants))
        f = self.backend._get_functionality(fn)
        f.name | should.eql(fn)
        self.backend.variant(fn, 'juan') | should.be_none()
        self.backend.variant(fn, 'juan2') | should.be_none()
