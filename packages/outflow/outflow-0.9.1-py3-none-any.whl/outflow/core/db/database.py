# -*- coding: utf-8 -*-
from pathlib import Path

from outflow.core.logging import logger
from outflow.core.pipeline import config, context
from sqlalchemy import create_engine
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.orm import scoped_session, sessionmaker


def get_database_labels():
    return [label for label in config["databases"].keys()]


def connect(func):
    def wrapper(self, *args, **kwargs):
        if context._models is None:
            raise Exception(
                "Databases method/properties can only be called after models have been successfully loaded"
            )
        if not self.is_connected:
            self.init_all_dbs()
        return func(self, *args, **kwargs)

    return wrapper


class Databases:
    def __init__(self):
        self._session = None
        self._admin_session = None
        self._databases = {}
        self.is_connected = False
        self.init_all_dbs()

    def close(self):
        """Close database connections and clear Model metadata"""

        # clear model metadata and reset the context
        for model in context._models:
            model.unregister()
        context._models = None

        self._databases.clear()

        if self._session is not None:
            self._session.close()
            self._session = None

        if self._admin_session is not None:
            self._admin_session.close()
            self._admin_session = None

        self.is_connected = False

    def init_all_dbs(self):
        if self.is_connected:
            return

        for db_label, login_info in config["databases"].items():
            db = Database(login_info, db_label=db_label)
            self._databases[db_label] = db

        self.is_connected = True

    def _get_binds(self, admin=False):
        binds = {}
        for database in self._databases.values():
            binds.update(
                {
                    table: database.admin_engine if admin else database.engine
                    for table in database.get_tables()
                }
            )
        return binds

    @property
    @connect
    def session(self):
        if self._session is None:
            self._session = self._create_session()
        return self._session

    @property
    @connect
    def admin_session(self):
        if self._admin_session is None:
            self._admin_session = self._create_session(admin=True)
        return self._admin_session

    def _create_session(self, admin=False):
        session = scoped_session(sessionmaker(binds=self._get_binds(admin)))
        return session

    @connect
    def __getitem__(self, item):
        return self._databases[item]

    @connect
    def __iter__(self):
        yield iter(self._databases)

    @connect
    def __next__(self):
        return next(self._databases)

    @connect
    def __contains__(self, key):
        return key in self._databases

    @connect
    def keys(self):
        yield from self._databases.keys()

    @connect
    def values(self):
        yield from self._databases.values()


class DatabaseException(Exception):
    pass


class Database:
    """
    A class to manage the connection to the database
    """

    def __init__(self, login_info, db_label):
        self.login_info = login_info
        self.db_label = db_label

        self._engine = None
        self._admin_engine = None
        self.is_connected = False
        self.is_admin_connected = False

        self._reflect()

    def get_tables(self, plugin=None):
        """Returns a list of all tables relevant for a bind."""
        result = []
        from outflow.core.db import Model

        for table in Model.metadata.tables.values():
            bind_key = table.info.get("bind_key")
            table_plugin = table.info.get("plugin")
            if (
                bind_key == self.db_label
                or bind_key is None
                and self.db_label == "default"
            ):
                if plugin is None or plugin is not None and plugin == table_plugin:
                    result.append(table)
        return result

    @property
    def admin_connection(self):
        return self.connect_admin()

    def connect_admin(self):
        """
        Make a connection to the database using SQLAlchemy
        """

        # connected = self.is_available()
        logger.debug("Connecting to database as admin")
        self._reflect()
        return self.admin_engine.connect()

    @property
    def admin_engine(self):
        if self._admin_engine is None:
            admin_url = self._generate_url(admin=True)
            self._admin_engine = create_engine(admin_url)
        return self._admin_engine

    @property
    def engine(self):
        if self._engine is None:
            url = self._generate_url()
            self._engine = create_engine(url)
        return self._engine

    def _generate_url(self, admin=False):
        dialect = self.login_info["dialect"]

        from outflow.core.pipeline import settings

        if dialect == "sqlite":
            path = self.login_info["path"]
            if path != ":memory:":
                is_absolute_path = Path(path).is_absolute()
                if not is_absolute_path:
                    path = Path(settings.ROOT_DIRECTORY) / path

            return f"sqlite:///{path}"

        elif dialect == "postgresql":
            if admin and "admin" not in self.login_info:
                raise DatabaseException(
                    "Admin credentials missing from configuration file"
                )

            return "postgresql://{user}@{address}/{database}".format(
                address=self.login_info["address"],
                user=self.login_info["admin"] if admin else self.login_info["user"],
                database=self.login_info["database"],
            )
        else:
            raise KeyError(
                f"Dialect {dialect} is not recognized, cannot generate sqlalchemy url"
            )

    def _reflect(self):
        try:
            DeferredReflection.prepare(self.engine)
        except NoSuchTableError as e:
            logger.warning(f"The table {e} does not exist")
