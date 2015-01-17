import re

_regex_type = type(re.compile(r''))


class Rollout(object):

    def __init__(self, backend):
        self.backend = backend
        self.funcs = {}
        self._item = None

    def add_func(self, name, check=None, percentage=100):
        fn = Function(name, check, percentage)
        self.funcs[name] = fn

    def is_enabled(self, name):
        return self.funcs[name].enabled

    def register(self, name, item):
        if type(item) == _regex_type:
            self.backend.set_rule(name, item)
        elif isinstance(item, basestring):
            self.backend.add(name, item)
        elif self.funcs[name].function:
            self.backend.add(name, self.funcs[name].function(item))
        else:
            self.backend.add(name, item)

    def set_current_id(self, name):
        """
        Initiate the current user mapped to the request, so there's no need to
        pass as parameter in every check
        """
        self._item = name

    def cleanup_current_id(self):
        self._item = None

    def enabled(self, name):
        def real_decorator(fn):
            def wrapper(*args, **kwargs):
                if self.is_enabled(name):
                    fn(*args, **kwargs)
                else:
                    raise Exception("Function <%s> is not enabled" % name)
            return wrapper
        return real_decorator

    def toggle(self, name):
        self.funcs[name].enabled = not self.funcs[name].enabled

    def disable(self, name):
        self.funcs[name].enabled = False

    def enable(self, name):
        self.funcs[name].enabled = True

    def _is_func_defined(self, name):
        return name in self.funcs

    def _callable(self, fn, func):
        def wrapper(*args, **kwargs):
            _id = func(*args, **kwargs)
            return self.backend.is_enabled(fn, _id)
        return wrapper

    def check(self, func, index=None):
        """ Decorator to check if a functionality is enabled
        for a specific user/item.
        @param func: functionality name to be checked
        @param index: argument to be used as user/item
        """
        def real_decorator(fn):
            def wrapper(*args, **kwargs):
                if self._is_func_defined(func):
                    if index is not None:
                        if self.funcs[func].function:
                            _id = self.funcs[func].function(args[index-1])
                        else:
                            _id = args[index-1]
                    else:
                        _id = self._item
                    if _id is None:
                        raise Exception("Identifier should be set before checking the functionality")
                    if self.backend.is_enabled(func, _id):
                        return fn(*args, **kwargs)
                    else:
                        raise Exception("Function <%s> is not enabled for user <%s> " % (func, _id))
                else:
                    raise Exception("Function <%s> is not defined" % func)
            return wrapper
        return real_decorator

    def __getattr__(self, key):
        prefix, func = key.split('_', 1)
        if prefix == 'is' and self._is_func_defined(func):
            fn = self.funcs[func].function
            if fn is None:
                # Unity lambda. TODO: just avoid wrapping
                fn = lambda x: x
            return self._callable(func, fn)
        else:
            raise ValueError("Function <%s> not defined" % func)


class Function(object):

    __slots__ = ['name', 'function', 'percentage', 'enabled']

    def __init__(self, name, function, percentage):
        if not isinstance(name, basestring):
            raise AttributeError("Function name should be a string")

        self.name = name
        self.function = function
        self.percentage = self._validate_percentage(percentage)
        self.enabled = True

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
