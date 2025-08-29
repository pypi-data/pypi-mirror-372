#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from alembic import op, context


__all__ = ["create_schema", "execute"]


"""
    These functions are wrappers around alembic execute() and table/schema
    creation and deletion in order to control authorisations on tables/schemas
    and set up a logger
"""


def execute(cmd):
    """Calls logger before executing a SQL command"""
    logger = logging.getLogger("alembic")
    logger.info(cmd)
    op.execute(cmd)


def create_schema(schema_name):
    """Create a schema and grant the corresponding access to users"""

    login_info = context.config.attributes["login_info"]

    admin = login_info["admin"].split(":")[0]
    user = login_info["user"].split(":")[0]

    execute("CREATE SCHEMA IF NOT EXISTS {}".format(schema_name))

    grant_user = "GRANT USAGE ON SCHEMA {0} TO {1}".format(schema_name, user)

    grant_admin = "GRANT ALL ON SCHEMA {0} TO {1}".format(schema_name, admin)

    grant_user_seq = (
        f"GRANT USAGE, SELECT ON ALL SEQUENCES in schema {schema_name} TO {user}"
    )

    execute(grant_user)
    execute(grant_admin)
    execute(grant_user_seq)


def drop_schema(schema_name, cascade=False):
    """Drop a schema"""

    execute(f"DROP SCHEMA {schema_name} {'CASCADE' if cascade else ''}")
