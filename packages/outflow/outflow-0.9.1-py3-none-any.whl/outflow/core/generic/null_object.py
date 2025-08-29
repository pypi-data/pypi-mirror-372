# -*- coding: utf-8 -*-
class NullObject:
    """Null objects always and reliably "do nothing." """

    # TODO probably replace with magic mock

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self

    def __repr__(self):
        return f"NullObject():{id(self)}"

    def __bool__(self):
        return False

    def __getattr__(self, name):
        return self

    def __setattr__(self, name, value):
        return self

    def __delattr__(self, name):
        return self

    def __getitem__(self, item):
        return self

    def __iter__(self):
        for n in []:
            yield n
