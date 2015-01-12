# -*- encoding: utf-8 -*-

import unittest
from pyshould import should

from hanoi.api import Function


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
