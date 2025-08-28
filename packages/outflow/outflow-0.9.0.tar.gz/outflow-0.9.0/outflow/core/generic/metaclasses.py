# -*- coding: utf-8 -*-
class Singleton(type):
    """
    A metaclass to create singletons, i.e classes that can have at most only
    one instance created at a given time.
    """

    def __call__(cls, *args, **kwargs):
        """
        Check that an instance is already stored before creating a new one.
        """

        if hasattr(cls, "instance"):
            return cls.instance

        cls.instance = super(Singleton, cls).__call__(*args, **kwargs)

        return cls.instance

    def reset(cls):
        del cls.instance
        cls.instance = None
