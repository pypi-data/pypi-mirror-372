# -*- coding: utf-8 -*-
import copy
import random
import string

import pytest
from outflow.core.pipeline import config, context
from pytest_postgresql import factories

from .database_command_test_case import DatabaseCommandTestCase


def generate_create_user_query(user, password):
    return [
        "DO $$",
        "BEGIN",
        f"CREATE USER \"{user}\" PASSWORD '{password}' NOSUPERUSER CREATEDB NOCREATEROLE INHERIT;",
        "EXCEPTION WHEN DUPLICATE_OBJECT THEN",
        f"RAISE NOTICE 'not creating role {user} -- it already exists';",
        "END",
        "$$;",
    ]


db_name = "test_db_" + "".join(
    random.choices(string.ascii_uppercase + string.digits, k=5)
)

postgresql_fixture = factories.postgresql("postgresql_nooproc", dbname=db_name)


class PostgresCommandTestCase(DatabaseCommandTestCase):
    databases_config = {
        "default": {
            "dialect": "postgresql",
            "admin": "pipeadmin:adminpwd",
            "user": "pipeuser:userpwd",
        }
    }

    @pytest.fixture(autouse=True)
    def setup_database(self, setup_within_pipeline_context, input_postgresql_fixture=postgresql_fixture):
        self.postgresql = input_postgresql_fixture
        config["databases"] = copy.deepcopy(self.databases_config)

        # get db info
        config["databases"]["default"][
            "address"
        ] = f"{self.postgresql.info.host}:{self.postgresql.info.port}"
        config["databases"]["default"]["database"] = self.postgresql.info.dbname

        # change create users if needed and change table owner
        cur = self.postgresql.cursor()
        for user, password in [
            self.databases_config["default"]["admin"].split(":"),
            self.databases_config["default"]["user"].split(":"),
        ]:
            cur.execute("\n".join(generate_create_user_query(user, password)))

        cur.execute(
            f'ALTER DATABASE "{self.postgresql.info.dbname}" OWNER TO "pipeadmin";'
        )
        self.postgresql.commit()
        cur.close()

        context.force_dry_run = False
