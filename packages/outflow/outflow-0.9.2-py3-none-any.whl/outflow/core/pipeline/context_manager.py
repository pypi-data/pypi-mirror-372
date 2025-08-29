# -*- coding: utf-8 -*-
import functools

from outflow.core.generic.context_manager import ReadWriteContextManager


class PipelineContextManager(ReadWriteContextManager):
    pass


def with_pipeline_context_manager(decorated_func):
    @functools.wraps(decorated_func)
    def inner_func(*args, **kwargs):
        with PipelineContextManager():
            return decorated_func(*args, **kwargs)

    return inner_func
