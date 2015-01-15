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


class Foo(object):
    def __init__(self, id):
        self.id = id

foo = Foo("foo")

rollout.register('cdc_on', foo)

@rollout.check('cdc_on')
def my_test(foo):
    print "I'm in"

my_test(foo)
print rollout.is_cdc_on(foo)
print rollout.is_cdc_on(Foo("foo1"))
print rollout.is_cdc_o()
