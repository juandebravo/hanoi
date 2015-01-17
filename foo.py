import hanoi
import re


rollout = hanoi.Rollout(hanoi.MemoryBackEnd())

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

    def __repr__(self):
        return self.id

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

rollout.register('cdc_on', "444402")
print rollout.is_cdc_on(Foo("444402"))

rollout.set_current_id("444400")


@rollout.check('cdc_on')
def my_test_ii():
    return "I'm in ii"


print my_test_ii()
print rollout.is_enabled('cdc_on', "44111100")
