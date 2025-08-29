# -*- coding: utf-8 -*-

__all__ = ["TaskException", "ContextArgumentException", "TaskWithKwargsException"]


class TaskException(Exception):
    pass


class ContextArgumentException(TaskException):
    pass


class TaskWithKwargsException(TaskException):
    pass
