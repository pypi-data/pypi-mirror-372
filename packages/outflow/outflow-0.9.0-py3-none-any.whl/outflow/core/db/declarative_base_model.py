# -*- coding: utf-8 -*-
import re

import sqlalchemy as sa
from outflow.core.db.handlers import create, get_or_create, one
from outflow.core.db.skip_if_untracked import skip_if_untracked
from outflow.core.pipeline import context
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base, declared_attr
from sqlalchemy.sql.schema import _get_table_key


def should_set_tablename(cls):
    """Determine whether ``__tablename__`` should be automatically generated
    for a model.
    * If no class in the MRO sets a name, one should be generated.
    * If a declared attr is found, it should be used instead.
    * If a name is found, it should be used if the class is a mixin, otherwise
      one should be generated.
    * Abstract models should not have one generated.
    Later, :meth:`._BoundDeclarativeMeta.__table_cls__` will determine if the
    model looks like single or joined-table inheritance. If no primary key is
    found, the name will be unset.
    """
    if cls.__dict__.get("__abstract__", False) or not any(
        isinstance(b, DeclarativeMeta) for b in cls.__mro__[1:]
    ):
        return False

    for base in cls.__mro__:
        if "__tablename__" not in base.__dict__:
            continue

        if isinstance(base.__dict__["__tablename__"], declared_attr):
            return False

        return not (
            base is cls
            or base.__dict__.get("__abstract__", False)
            or not isinstance(base, DeclarativeMeta)
        )

    return True


def camel_to_snake_case(name):
    name = re.sub(r"((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))", r"_\1", name)
    return name.lower().lstrip("_")


class NameMetaMixin(type):
    def __init__(cls, name, bases, d):
        if should_set_tablename(cls):
            cls.__tablename__ = camel_to_snake_case(cls.__name__)

        super().__init__(name, bases, d)

        # __table_cls__ has run at this point
        # if no table was created, use the parent table
        if (
            "__tablename__" not in cls.__dict__
            and "__table__" in cls.__dict__
            and cls.__dict__["__table__"] is None
        ):
            del cls.__table__

    def __table_cls__(cls, *args, **kwargs):
        """This is called by SQLAlchemy during mapper setup. It determines the
        final table object that the model will use.
        If no primary key is found, that indicates single-table inheritance,
        so no table will be created and ``__tablename__`` will be unset.
        """
        # check if a table with this name already exists
        # allows reflected tables to be applied to model by name
        key = _get_table_key(args[0], kwargs.get("schema"))

        if key in cls.metadata.tables:
            return sa.Table(*args, **kwargs)

        # if a primary key or constraint is found, create a table for
        # joined-table inheritance
        for arg in args:
            if (isinstance(arg, sa.Column) and arg.primary_key) or isinstance(
                arg, sa.PrimaryKeyConstraint
            ):
                return sa.Table(*args, **kwargs)

        # if no base classes define a table, return one
        # ensures the correct error shows up when missing a primary key
        for base in cls.__mro__[1:-1]:
            if "__table__" in base.__dict__:
                break
        else:
            return sa.Table(*args, **kwargs)

        # single-table inheritance, use the parent tablename
        if "__tablename__" in cls.__dict__:
            del cls.__tablename__


class BindMetaMixin(type):
    _module = None

    def __init__(cls, name, bases, d):
        bind_key = d.pop("__bind_key__", None) or getattr(cls, "__bind_key__", None)

        if cls._module is not None:
            module = cls._module
        else:
            module = d.get("__module__", None)

        super().__init__(name, bases, d)

        if bind_key is not None and getattr(cls, "__table__", None) is not None:
            cls.__table__.info["bind_key"] = bind_key

        if module is not None and getattr(cls, "__table__", None) is not None:
            split_module = module.split(".")
            try:
                cls.__table__.info["plugin"] = ".".join(
                    [split_module[0], split_module[1]]
                )
            except IndexError:
                cls.__table__.info["plugin"] = ""


class DefaultMeta(NameMetaMixin, BindMetaMixin, DeclarativeMeta):
    pass


class BaseModel:
    """Base class for SQLAlchemy declarative base model.
    To define models, subclass :attr:`db.Model <SQLAlchemy.Model>`, not this
    class. To customize ``db.Model``, subclass this and pass it as
    ``model_class`` to :class:`SQLAlchemy`.
    """

    # store the table metadata to reload the model if needed
    _sa_table_metadata = None

    #: Query class used by :attr:`query`. Defaults to
    # :class:`SQLAlchemy.Query`, which defaults to :class:`BaseQuery`.
    query_class = None

    #: Convenience property to query the database for instances of this model
    # using the current session. Equivalent to ``db.session.query(Model)``
    # unless :attr:`query_class` has been changed.
    query = None

    def __repr__(self):
        identity = inspect(self).identity

        if identity is None:
            pk = f"(transient {id(self)})"
        else:
            pk = ", ".join(str(value) for value in identity)

        return f"<{type(self).__name__} {pk}>"

    @classmethod
    @skip_if_untracked
    def one(cls, **kwargs):
        return one(context.session, cls, **kwargs)

    @classmethod
    def create(cls, **kwargs):
        return create(context.session, cls, **kwargs)

    @classmethod
    def get_or_create(cls, create_method="", create_method_kwargs=None, **kwargs):
        return get_or_create(
            context.session,
            cls,
            create_method=create_method,
            create_method_kwargs=create_method_kwargs,
            **kwargs,
        )

    @classmethod
    def register(cls):
        """Use table metadata stored in the model to (re-)populate the shared SQLAlchemy metadata attribute"""
        if not cls.is_registered() and cls.is_registrable():
            return cls.metadata.tables._insert_item(
                cls.__tablename__, cls._sa_table_metadata
            )

    @classmethod
    def unregister(cls):
        """Clear the shared SQLAlchemy metadata attribute and store a backup of the table metadata in the model for future usage"""

        cls._sa_table_metadata = dict.pop(cls.metadata.tables, cls.__tablename__, None)

        return cls._sa_table_metadata

    @classmethod
    def is_registered(cls):
        return cls.__tablename__ in cls.metadata.tables

    @classmethod
    def is_registrable(cls):
        return cls._sa_table_metadata is not None


def make_declarative_base(model, metadata=None):
    """Creates the declarative base that all models will inherit from.
    :param model: base model class (or a tuple of base classes) to pass
        to :func:`~sqlalchemy.ext.declarative.declarative_base`. Or a class
        returned from ``declarative_base``, in which case a new base class
        is not created.
    :param metadata: :class:`~sqlalchemy.MetaData` instance to use, or
        none to use SQLAlchemy's default.
    .. versionchanged 2.3.0::
        ``model`` can be an existing declarative base in order to support
        complex customization such as changing the metaclass.
    """
    if not isinstance(model, DeclarativeMeta):
        model = declarative_base(
            cls=model, name="Model", metadata=metadata, metaclass=DefaultMeta
        )

    # if user passed in a declarative base and a metaclass for some reason,
    # make sure the base uses the metaclass
    if metadata is not None and model.metadata is not metadata:
        model.metadata = metadata

    return model
