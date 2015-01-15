# -*- encoding: utf-8 -*-

import unittest
from pyshould import should

from hanoi.api import Function, Rollout


class RolloutTestCase(unittest.TestCase):

    FN = 'foo'

    def _get_basic_rollout(self, fn):
        rollout = Rollout(None)
        rollout.add_func(fn, lambda x: x.id)
        return rollout

    def test_register_a_functionality(self):
        self._get_basic_rollout(self.FN).funcs | should.have_len(1)

    def test_enable_a_functionality(self):
        rollout = self._get_basic_rollout(self.FN)
        rollout.enable(self.FN)
        rollout.is_enabled(self.FN) | should.be_truthy

    def test_dinable_a_functionality(self):
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


class FunctionTestCase(unittest.TestCase):

    def test_name_is_valid_as_a_string(self):
        f = Function('foo', lambda x: True, '100')
        f.name | should.eql('foo')

    def test_name_is_valid_as_a_unicode(self):
        f = Function(u'üéê', lambda x: True, '100')
        f.name | should.eql(u'üéê')

    def test_name_should_be_a_string(self):
        with should.throw(AttributeError):
            Function(1, lambda x: True, '100')

    def test_name_is_read_only(self):
        f = Function("foo", lambda x: True, 20)

        with should.throw(RuntimeError):
            f.name = "bar"

    def test_percentage_is_casted_to_integer_if_valid_number_as_string(self):
        f = Function('foo', lambda x: True, '100')
        f.percentage | should.eql(100)

    def test_percentage_should_be_a_number(self):
        with should.throw(AttributeError):
            Function('foo', lambda x: True, 'bar')

    def test_percentage_should_be_lower_than_100(self):
        with should.throw(AttributeError):
            Function('foo', lambda x: True, 101)

    def test_percentage_should_be_greater_than_0(self):
        with should.throw(AttributeError):
            Function('foo', lambda x: True, -1)

    def test_cannot_set_invalid_attributes(self):
        f = Function('foo', lambda x: True, 100)

        with should.throw(AttributeError):
            f.bar
