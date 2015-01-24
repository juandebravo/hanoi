import re

from .backend import Feature

_regex_type = type(re.compile(r''))


class Rollout(object):

    def __init__(self, backend):
        self._backend = backend
        self._item = None

    @property
    def backend(self):
        if self._backend is None:
            raise TypeError("BackEnd should be a valid BackEnd object")
        return self._backend

    def add_func(self, name, check=None, percentage=0):
        fn = Feature(name, check, percentage)
        self.backend.add_functionality(fn)

    def is_enabled(self, name, item=None):
        return self.backend.is_enabled(name, item)

    def register(self, name, item):
        if type(item) == _regex_type:
            self.backend.set_rule(name, item)
        else:
            self.backend.add(name, item)

    def set_percentage(self, name, percentage):
        self.backend.set_percentage(name, percentage)

    def set_current_id(self, name):
        """
        Map a specifc user to the instance, so there's no need to
        pass as parameter in every check. Don't use this approach if you need
        a thread safe environment.
        """
        self._item = name

    def cleanup_current_id(self):
        self._item = None

    def enabled(self, name):
        """Decorator for global functionalities without checking the specific user"""
        def real_decorator(fn):
            def wrapper(*args, **kwargs):
                if self.is_enabled(name):
                    return fn(*args, **kwargs)
                else:
                    raise RolloutException("Feature <%s> is not enabled" % name)
            return wrapper
        return real_decorator

    def toggle(self, name):
        self.backend.toggle(name)

    def disable(self, name):
        self.backend.disable(name)

    def enable(self, name):
        self.backend.enable(name)

    def _is_func_defined(self, name):
        return name in self.backend.get_functionalities()

    def _callable(self, fn, func):
        def wrapper(*args, **kwargs):
            _id = func(*args, **kwargs)
            return self.backend.is_enabled(fn, _id)
        return wrapper

    def check(self, func, index=None):
        """ Decorator to check if a functionality is enabled
        for a specific user/item.
        @param func: functionality name to be checked
        @param index: argument to be used as user/item. If None, it will seek for the item
        in the current_id value
        """
        def real_decorator(fn):
            def wrapper(*args, **kwargs):
                if self._is_func_defined(func):
                    if index is not None:
                        _fn = self.backend.get_functionality(func)
                        _id = _fn.get_item_id(args[index-1])
                    else:
                        _id = self._item
                    if _id is None:
                        raise Exception("Identifier should be set before checking the functionality")
                    if self.backend.is_enabled(func, _id):
                        return fn(*args, **kwargs)
                    else:
                        raise Exception("Feature <%s> is not enabled for user <%s> " % (func, _id))
                else:
                    raise Exception("Feature <%s> is not defined" % func)
            return wrapper
        return real_decorator

    def __getattr__(self, key):
        prefix, func = key.split('_', 1)
        if prefix == 'is' and self._is_func_defined(func):
            _fn = self.backend.get_functionality(func).function
            if _fn is None:
                # Unity lambda. TODO: just avoid wrapping
                _fn = lambda x: x
            return self._callable(func, _fn)
        else:
            raise ValueError("Feature <%s> not defined" % func)


class RolloutException(Exception):
    pass
