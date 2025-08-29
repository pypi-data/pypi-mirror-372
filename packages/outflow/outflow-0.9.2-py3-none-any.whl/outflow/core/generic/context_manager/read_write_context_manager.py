# -*- coding: utf-8 -*-
from contextvars import ContextVar

__all__ = []


class ReadWriteContextManagerReentryError(Exception):
    """Context re-entry exception"""

    pass


class ReadWriteContextManager:
    def __init__(self):
        self._token = None
        self._parent_context = None

    @classmethod
    def _ensure_context_var(cls):
        if not hasattr(cls, "_CONTEXT_VAR"):
            cls._CONTEXT_VAR = ContextVar(cls.__name__ + "_context_var", default=None)

    def __new__(cls, *args, **kwargs):
        cls._ensure_context_var()
        return super().__new__(cls, *args, **kwargs)

    def __enter__(self):
        if self._token is not None:
            raise ReadWriteContextManagerReentryError(
                f"The same manager cannot be re-entered until exiting; token: {self._token}"
            )
        self._parent_context = self.get_context()

        if self._parent_context is None:
            # the context has no parent
            self._context = {}
            self._token = self._CONTEXT_VAR.set(self._context)
        else:
            # pass the parent context
            self._context = self._parent_context

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context, resetting parent_context and context to None"""
        if self._token:
            self._CONTEXT_VAR.reset(self._token)
        self._parent_context = None
        self._context = None
        self._token = None

    @property
    def context(self):
        return self._context

    @property
    def parent_context(self):
        return self._parent_context

    @classmethod
    def get_context(cls):
        """Get context from flex_context ContextVar; always current state"""
        cls._ensure_context_var()
        context = cls._CONTEXT_VAR.get()
        return context
