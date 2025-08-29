# -*- coding: utf-8 -*-
from alembic import context
from alembic.autogenerate import renderers
from alembic.operations import MigrateOperation
from alembic.operations import Operations


@Operations.register_operation("grant_permissions")
class GrantPermissionsOp(MigrateOperation):
    def __init__(self, table_name, schema=None):
        self.table_name = table_name
        self.schema = schema

    @classmethod
    def grant_permissions(cls, operations, table_name, **kw):
        op = GrantPermissionsOp(table_name, **kw)
        return operations.invoke(op)

    def reverse(self):
        # only needed to support autogenerate
        return RevokePermissionsOp(self.table_name, schema=self.schema)


@Operations.register_operation("revoke_permissions")
class RevokePermissionsOp(MigrateOperation):
    def __init__(self, table_name, schema=None):
        self.table_name = table_name
        self.schema = schema

    @classmethod
    def revoke_permissions(cls, operations, table_name, **kw):
        op = RevokePermissionsOp(table_name, **kw)
        return operations.invoke(op)

    def reverse(self):
        # only needed to support autogenerate
        return GrantPermissionsOp(self.table_name, schema=self.schema)


@Operations.implementation_for(GrantPermissionsOp)
def grant_permissions(operations, operation):
    """Grants permissions to user on newly created tables"""

    login_info = context.config.attributes["login_info"]

    if login_info["dialect"] == "postgresql":
        user = login_info["user"].split(":")[0]
        admin = login_info["admin"].split(":")[0]

        if operation.schema:
            table_name = operation.schema + "." + operation.table_name
        else:
            table_name = operation.table_name

        grant_user = (
            f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE {table_name} TO {user}"
        )
        grant_admin = f"GRANT ALL ON TABLE {table_name} TO {admin}"

        if operation.schema:
            schema = operation.schema
        else:
            schema = "public"

        grant_user_seq = f"GRANT ALL ON ALL SEQUENCES IN SCHEMA {schema} TO {user}"

        operations.execute(grant_user)
        operations.execute(grant_admin)
        operations.execute(grant_user_seq)


@Operations.implementation_for(RevokePermissionsOp)
def revoke_permissions(table_name, *args, **kwargs):
    """Not needed because downgrading create_table is drop_table"""
    pass


@renderers.dispatch_for(GrantPermissionsOp)
def render_grant_permissions(autogen_context, op):
    rendered = "op.grant_permissions('{table_name}'{schema})".format(
        table_name=op.table_name,
        schema=f", schema='{op.schema}'" if op.schema is not None else "",
    )
    return rendered


@renderers.dispatch_for(RevokePermissionsOp)
def render_revoke_permissions(autogen_context, op):
    pass
