# -*- coding: utf-8 -*-
from contextlib import suppress
from contextvars import ContextVar


class ContextManagerMeta(type):
    """
    A metaclass to create ContextManager classes with dedicated ContextVar
    """

    def __init__(cls, name, bases, nmspc):
        super().__init__(name, bases, nmspc)
        cls._CONTEXT_VAR = ContextVar(name + "_context_var", default={})


class ContextManagerReentryError(Exception):
    pass


class ContextManager(metaclass=ContextManagerMeta):
    """
    A context manager based on the python context variables.

    Each context declared with the context manager shares a single class-bind cls._CONTEXT_VAR dictionary
    stored within a python `ContextVar`.

    A copy of the current self._CONTEXT_VAR can be retrieved via get_context().

    Each ContextManager instance is initialized with a `delta` dictionary
    applied upon the parent context, if any.

    Upon context exit, the self._CONTEXT_VAR is reset to the parent context. In
    addition, the `context` and `parent_context` fields are reset to None.

    Multiple ContextManager instances may be applied by nesting `with`
    statements. A single ContextManager instance may be re-entered multiple
    times, but only after exiting after each use.

    Usage:
    >>> MyManager(ContextManager): pass
    >>> print(MyManager.get_context())
    {}
    >>> with MyManager(color='blue', number=42, obj=object()) as manager_a:
            print(MyManager.get_context())
            assert manager_a.context == MyManager.get_context()
            assert manager_a.parent_context == {}
            with MyManager(color='yellow', obj=object()) as manager_b:
                print(MyManager.get_context())
                assert manager_b.context == MyManager.get_context()
                assert manager_b.parent_context == manager_a.context
            print(MyManager.get_context())
            assert manager_b.context is None and manager_b.parent_context is None
    {'color': 'blue', 'number': 42, 'obj': <object object at 0x107b4ca60>}
    {'color': 'yellow', 'number': 42, 'obj': <object object at 0x107b4caa0>}
    {'color': 'blue', 'number': 42, 'obj': <object object at 0x107b4ca60>}
    >>> print(MyManager.get_context())
    {}
    """

    @classmethod
    def get_context(cls):
        """Get context from flex_context ContextVar; always current state"""
        context = cls._CONTEXT_VAR.get()
        return context.copy()

    @property
    def delta(self):
        """Delta context vars; dict to apply to parent context upon entry"""
        return self._delta.copy()

    @property
    def parent_context(self):
        """Parent context dict upon entry; None outside context"""
        return None if self._parent_context is None else self._parent_context.copy()

    @property
    def context(self):
        """Context (new) dict upon entry; None outside context"""
        return None if self._context is None else self._context.copy()

    def __enter__(self):
        """Enter context, applying delta to parent context to form a new context"""
        if self._token is not None:
            raise ContextManagerReentryError(
                f"The same context cannot be re-entered until exiting; token: {self._token}"
            )
        self._parent_context = self.get_context()
        self._context = {**self._parent_context, **self._delta}
        self._token = self._CONTEXT_VAR.set(self._context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context, resetting parent_context and context to None"""
        self._CONTEXT_VAR.reset(self._token)
        self._parent_context = None
        self._context = None
        self._token = None

    def __getattr__(self, name):
        """Get delta vars and within context, context vars"""

        # Use suppress to ignore KeyError exceptions.
        with suppress(KeyError):
            return self._delta[name]
        try:
            return self._context[name]
        except TypeError as e:
            raise AttributeError(
                f"'{self!r}' context vars are only available within context"
            ) from e
        except KeyError as e:
            raise AttributeError(f"'{name}' not found in '{self!r}' context") from e

    def __setattr__(self, name, value):
        """Setattr is disabled for context vars; contexts are immutable"""
        if name in self.__dict__:
            return super().__setattr__(name, value)
        raise AttributeError(f"'{self!r}' vars are immutable")

    def __delattr__(self, name):
        """Delattr is disabled for context vars; contexts are immutable"""
        if name in self.__dict__:
            return super().__delattr__(name)
        raise AttributeError(f"'{self!r}' vars cannot be deleted")

    def __contains__(self, item):
        """Contains item in delta vars or, within context, context vars"""
        try:
            return item in self._delta or item in self._context
        except TypeError:
            return False

    def __repr__(self):
        arguments = [f"{k}={v!r}" for k, v in self._delta.items()]
        return f"{self.__class__.__name__}({', '.join(arguments)})"

    def __init__(self, **delta):
        """Initialize instance with `delta` dict of context var names/values"""
        self._initialize_attributes(
            _delta=delta, _parent_context=None, _context=None, _token=None
        )

    def _initialize_attributes(self, **attributes):
        """Initialize attributes on instance given dict of attribute names/values"""
        for attribute, value in attributes.items():
            super().__setattr__(attribute, value)
