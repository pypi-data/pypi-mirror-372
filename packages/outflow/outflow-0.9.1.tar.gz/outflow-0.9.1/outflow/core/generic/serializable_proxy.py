# -*- coding: utf-8 -*-
from .lazy_object_proxy import LazyObjectProxy


def recreate_lazy_object(factory):
    return SerializableProxy(factory=factory)


class SerializableProxy(LazyObjectProxy):
    def __getstate__(self):
        return {}

    def __setstate__(self, state):
        pass

    def getstate(self):
        return self.__wrapped__.__getstate__()

    def setstate(self, state):
        self.__wrapped__.__setstate__(state)

    def __reduce_ex__(self, protocol):
        return recreate_lazy_object, (self.__factory__,)
