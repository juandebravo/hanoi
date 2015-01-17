import zlib
try:
    from redis import Redis
except ImportError:
    # Redis not available
    pass


class MemoryBackEnd(object):
    def __init__(self):
        self.funcs = {}
        self.reg = {}
        self.rules = {}

    def get_functionalities(self):
        return self.funcs.keys()

    def add_functionality(self, fn):
        self.funcs[fn.name] = fn

    def get_functionality(self, name):
        return self.funcs[name]

    def _add(self, name, item):
        self.reg[name].append(item)

    def add(self, name, item):
        if not name in self.reg:
            self.reg[name] = []

        if isinstance(item, basestring):
            self._add(name, item)
        elif self.funcs[name].function:
            self._add(name, self.funcs[name].function(item))
        else:
            self._add(name, item)

    def set_rule(self, name, rule):
        self.rules[name] = rule

    def set_percentage(self, name, percentage):
        self.funcs[name].percentage = percentage

    def is_enabled(self, name, item=None):
        func_is_enabled = name in self.funcs and self.funcs[name].enabled
        if item is None:
            # Global funcionality enabled?
            return func_is_enabled

        if not func_is_enabled:
            # Avoid additional lookup as the functionality is globally disabled
            return func_is_enabled

        flag = self.funcs[name].percentage == 100
        flag = flag or (name in self.reg and item in self.reg[name])
        flag = flag or (name in self.rules and self.rules[name].search(str(item)) is not None)
        if not flag and self.funcs[name].percentage > 0:
            flag = zlib.crc32(self.funcs[name].get_item_id(item)) % 100 >= self.funcs[name].percentage
        return flag

    def disable(self, name):
        self.funcs[name].enabled = False

    def enable(self, name, enable_to_all=False):
        self.funcs[name].enabled = True
        if enable_to_all:
            self.funcs[name].percentage = 100

    def toggle(self, name):
        self.funcs[name].enabled = not self.funcs[name].enabled


class RedisBackEnd(object):

    def __init__(self, obj):
        if isinstance(obj, (list, tuple)):
            host, port = obj.pop(0), obj.pop(0)
            db = obj.pop(0) if len(obj) else 0
            self._redis = Redis(host=host, port=port, db=db)
        else:
            self._redis = obj

    # TODO 1: Store the
