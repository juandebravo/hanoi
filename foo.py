import hanoi
import re


class BackEnd(object):
    def __init__(self):
        self.reg = {}
        self.rules = {}

    def add(self, name, item):
        if not name in self.reg:
            self.reg[name] = []
        self.reg[name].append(item)

    def set_rule(self, name, rule):
        self.rules[name] = rule

    def is_enabled(self, name, item):
        flag = name in self.reg and item in self.reg[name]
        flag = flag or (name in self.rules and self.rules[name].search(item) is not None)
        return flag

rollout = hanoi.Rollout(BackEnd())

rollout.add_func(
    'cdc_on',
    lambda x: x.id
)

rollout.add_func(
    'is_elegible',
    lambda x: x.id
)


class Foo(object):
    def __init__(self, id):
        self.id = id

foo = Foo("444400")

rollout.register('cdc_on', re.compile(r"00$"))
rollout.register('is_elegible', foo)


@rollout.check('cdc_on', 1)
@rollout.check('is_elegible', 2)
def my_test(foo, f):
    return "I'm in"

print my_test(foo, Foo("444400"))
print rollout.is_cdc_on(foo)
print rollout.is_cdc_on(Foo("foo1"))

rollout.set_current_id("444400")


@rollout.check('cdc_on')
def my_test_ii():
    return "I'm in ii"


print my_test_ii()
