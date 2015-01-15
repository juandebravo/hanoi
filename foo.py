import hanoi


class BackEnd(object):
    def __init__(self):
        self.reg = {}

    def add(self, name, item):
        if not name in self.reg:
            self.reg[name] = []
        self.reg[name].append(item)

    def is_enabled(self, name, item):
        return name in self.reg and item in self.reg[name]

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

foo = Foo("foo")

rollout.register('cdc_on', foo)
rollout.register('is_elegible', foo)


@rollout.check('cdc_on')
@rollout.check('is_elegible', 2)
def my_test(foo, f):
    return "I'm in"

print my_test(foo, Foo("foo"))
print rollout.is_cdc_on(foo)
print rollout.is_cdc_on(Foo("foo1"))
