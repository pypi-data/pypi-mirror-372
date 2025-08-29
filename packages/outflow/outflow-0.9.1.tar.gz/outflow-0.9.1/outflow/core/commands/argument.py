# -*- coding: utf-8 -*-
import inspect


def argument(*args, **kwargs):
    def decorator(func_or_command_subclass):
        if inspect.isclass(func_or_command_subclass):
            instance = func_or_command_subclass()
            instance.add_argument(*args, **kwargs)
        else:
            if not hasattr(func_or_command_subclass, "__cli_params__"):
                func_or_command_subclass.__cli_params__ = []
            func_or_command_subclass.__cli_params__.append((args, kwargs))
        return func_or_command_subclass

    return decorator
