# -*- coding: utf-8 -*-
def skip_if_untracked(func):
    def wrapper(*args, **kwargs):
        from outflow.core.pipeline import context

        if context.db_untracked:
            return
        else:
            return func(*args, **kwargs)

    return wrapper
