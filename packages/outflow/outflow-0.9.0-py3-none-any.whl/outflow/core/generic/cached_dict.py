# -*- coding: utf-8 -*-
class CachedDict:
    def __init__(self):
        self._items = dict()

    def _get_dict_value(self, key):
        raise NotImplementedError()

    def __contains__(self, key):
        return key in self._items

    def __iter__(self):
        yield iter(self._items)

    def __next__(self):
        return next(self._items)

    def keys(self):
        yield from self._items.keys()

    def values(self):
        yield from self._items.values()

    def __getitem__(self, key):
        if key not in self._items:
            self._items[key] = self._get_dict_value(key)

        return self._items[key]
