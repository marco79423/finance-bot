class Cache:
    def __init__(self):
        self._data = {}

    def clear(self):
        self._data = {}

    def get(self, key, func, *args, **kargs):
        if key not in self._data:
            self._data[key] = func(*args, **kargs)
        return self._data[key]
