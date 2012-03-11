from werkzeug.contrib.cache import BaseCache

import pylibmc as pylibmc_lib

class PyLibMCCacheNotImplementedError(Exception):
    pass


class PyLibMCCache(BaseCache):
    """This just wraps pylibmc in a werkzeug standard cache."""
    def __init__(self, *args, **kwargs):
        try:
            self.prefix = kwargs['prefix']
            del kwargs['prefix']
        except KeyError:
            self.prefix = None
        self.mc = pylibmc_lib.Client(*args, **kwargs)

    def _p(self, key):
        return '%s:%s' % (self.prefix, key)

    def get(self, key):
        return self.mc.get(self._p(key))

    def get_many(self, keys):
        items = self.mc.get_multi([self._p(key) for key in keys])
        return [items[key] for key in keys]

    def get_dict(self, keys):
        _prefixed = [self._p(key) for key in keys]
        rtn = {}
        result = self.mc.get_multi(_prefixed)
        for key in keys:
            rtn[key] = result[self._p(key)]

    def set_many(self, mapping, timeout=None):
        return self.mc.set_multi([self._p(key) for key in mapping], timeout)

    def delete_many(self, keys):
        return self.mc.delete_multi([self._p(key) for key in keys])

    def delete(self, key):
        return self.mc.delete(self._p(key))

    def set(self, key, value, timeout=None):
        return self.mc.set(self._p(key), value, timeout)

    def inc(self, key, delta=None):
        return self.mc.incr(self._p(key), delta)

    def dec(self, key, delta=None):
        return self.mc.decr(self._p(key), delta)


def pylibmc(app, args, kwargs):
    return PyLibMCCache(app.config['CACHE_MEMCACHED_SERVERS'],
            prefix=app.config['CACHE_KEY_PREFIX'],
            binary=app.config['CACHE_MEMCACHED_BINARY'],
            behaviors=app.config['CACHE_MEMCACHED_BEHAVIORS']
    )
