# -*- coding: utf-8 -*-
from typing import Any


class TargetException(Exception):
    pass


class NoDefault:
    pass


class Target:
    def __init__(self, name, type=Any, default=NoDefault):
        self.name = name
        self.type = type
        self.default = default

    @classmethod
    def output(cls, name, *args, **kwargs):
        """
        Define a new output target for a given class

        :param name: the target name
        :return: the class wrapper
        """
        import warnings

        warnings.warn(
            "@Target.output decorator is deprecated, use return type annotations instead",
            DeprecationWarning,
            stacklevel=2,
        )

        def wrapper(TaskClass):
            TaskClass._outputs.update({name: Target(name=name, *args, **kwargs)})
            return TaskClass

        return wrapper

    @classmethod
    def input(cls, name, *args, **kwargs):
        """
        Define a new input target for a given class

        :param name: the target name
        :return: the class wrapper
        """
        import warnings

        warnings.warn(
            "@Target.input decorator is deprecated, use type annotations instead",
            DeprecationWarning,
            stacklevel=2,
        )

        def wrapper(TaskClass):
            TaskClass._inputs.update({name: Target(name=name, *args, **kwargs)})
            return TaskClass

        return wrapper

    @classmethod
    def parameter(cls, name, *args, **kwargs):
        """
        Define a new input parameter for a given class

        :param name: the target name
        :return: the class wrapper
        """
        import warnings

        warnings.warn(
            "@Target.parameter decorator is deprecated, use type annotations "
            "with custom type outflow.core.types.Parameter instead",
            DeprecationWarning,
            stacklevel=2,
        )

        def wrapper(TaskClass):
            TaskClass._parameters.update({name: Target(name=name, *args, **kwargs)})
            return TaskClass

        return wrapper

    @classmethod
    def parameters(cls, *names):
        """
        Define a list of input parameters for a given class

        :param names: the target names
        :return: the class wrapper
        """
        import warnings

        warnings.warn(
            "@Target.parameters decorator is deprecated, use type annotations "
            "with custom type outflow.core.types.Parameter instead",
            DeprecationWarning,
            stacklevel=2,
        )

        def wrapper(TaskClass):
            for name in names:
                TaskClass._parameters.update({name: Target(name=name)})
            return TaskClass

        return wrapper
