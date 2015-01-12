
class Rollout(object):

    def __init__(self, backend):
        self.backend = backend
        self.funcs = []

    def add_func(self, name, check, percentage=100):
        fn = Function(name, check, percentage)
        self.funcs.append(fn)

    def __getattr__(self, key):
        values = key.split('_', 1)
        return lambda: values[1] in [x.name for x in self.funcs]


class Function(object):

    __slots__ = ['name', 'function', 'percentage']

    def __init__(self, name, function, percentage):
        if not isinstance(name, basestring):
            raise AttributeError("Function name should be a string")

        self.name = name
        self.function = function
        self.percentage = self._validate_percentage(percentage)

    def _validate_percentage(self, percentage):
        try:
            value = int(percentage)
        except ValueError:
            raise AttributeError("Percentage should be a valid number")

        if 0 > value or value > 100:
            raise AttributeError("Percentage should be a number between 0 and 100")
        return value

    def __setattr__(self, name, value):
        if name == 'percentage':
            value = self._validate_percentage(value)
        elif name == 'name' and hasattr(self, name):
            raise RuntimeError("Unable to update the Function name")

        object.__setattr__(self, name, value)

    def __repr__(self):
        return "<{0}> applying {1} to {2}% users".format(
            self.name,
            self.function,
            self.percentage
        )
