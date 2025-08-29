# -*- coding: utf-8 -*-
"""Add table RunnableBlock, remove task and workflow

Revision ID: 6739ea807c29
Revises: 4559a1933ea0
Create Date: 2022-01-14 13:08:23.100943

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

# revision identifiers, used by Alembic.
revision = "6739ea807c29"
down_revision = "4559a1933ea0"
branch_labels = None
depends_on = None


def upgrade():
    if op.get_context().dialect.name == "sqlite":
        op.create_table(
            "outflow_configuration",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("config", sa.JSON(), nullable=False),
            sa.Column("settings", sa.JSON(), nullable=False),
            sa.Column("hash", sa.String(length=64), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("hash"),
        )
        op.grant_permissions("outflow_configuration")
        op.create_table(
            "outflow_run",
            sa.Column("uuid", sa.String(length=36), nullable=False),
            sa.Column("start_time", sa.DateTime(), nullable=True),
            sa.Column("end_time", sa.DateTime(), nullable=True),
            sa.Column(
                "state",
                sa.Enum(
                    "pending",
                    "running",
                    "failed",
                    "success",
                    "skipped",
                    name="stateenum",
                ),
                nullable=False,
            ),
            sa.Column("hostname", sa.String(length=256), nullable=True),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("configuration_id", sa.Integer(), nullable=False),
            sa.Column("command_name", sa.String(), nullable=True),
            sa.ForeignKeyConstraint(
                ["configuration_id"],
                ["outflow_configuration.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("uuid"),
        )
        op.grant_permissions("outflow_run")
        op.create_table(
            "outflow_block",
            sa.Column("uuid", sa.String(length=36), nullable=False),
            sa.Column("start_time", sa.DateTime(), nullable=True),
            sa.Column("end_time", sa.DateTime(), nullable=True),
            sa.Column(
                "state",
                sa.Enum(
                    "pending",
                    "running",
                    "failed",
                    "success",
                    "skipped",
                    name="stateenum",
                ),
                nullable=False,
            ),
            sa.Column("hostname", sa.String(length=256), nullable=True),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column(
                "type",
                sa.Enum("task", "workflow", name="blocktypeenum"),
                nullable=False,
            ),
            sa.Column("plugin", sa.String(length=256), nullable=True),
            sa.Column("name", sa.String(length=256), nullable=False),
            sa.Column("run_id", sa.Integer(), nullable=False),
            sa.Column("input_targets", sa.JSON(), server_default="{}", nullable=False),
            sa.Column("output_targets", sa.JSON(), server_default="{}", nullable=False),
            sa.Column("input_values", sa.JSON(), server_default="{}", nullable=True),
            sa.Column("parent_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(
                ["parent_id"],
                ["outflow_block.id"],
            ),
            sa.ForeignKeyConstraint(
                ["run_id"],
                ["outflow_run.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("uuid"),
        )
        op.grant_permissions("outflow_block")
        op.create_table(
            "outflow_edge",
            sa.Column("upstream_block_id", sa.Integer(), nullable=False),
            sa.Column("downstream_block_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(
                ["downstream_block_id"],
                ["outflow_block.id"],
            ),
            sa.ForeignKeyConstraint(
                ["upstream_block_id"],
                ["outflow_block.id"],
            ),
            sa.PrimaryKeyConstraint("upstream_block_id", "downstream_block_id"),
        )
        op.grant_permissions("outflow_edge")
        op.create_table(
            "outflow_runtime_exception",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("block_id", sa.Integer(), nullable=True),
            sa.Column("exception_type", sa.String(length=64), nullable=False),
            sa.Column("exception_msg", sa.Text(), nullable=False),
            sa.Column("traceback", sa.Text(), nullable=False),
            sa.Column("time", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(
                ["block_id"],
                ["outflow_block.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.grant_permissions("outflow_runtime_exception")
        return
    # ### commands auto generated by Alembic - please adjust! ###

    blocktypeenum = pg.ENUM("task", "workflow", name="blocktypeenum")
    blocktypeenum.create(op.get_bind())
    op.rename_table("outflow_task", "outflow_block")
    op.add_column(
        "outflow_block", sa.Column("type", blocktypeenum)
    )  # , nullable=False))

    op.execute("UPDATE outflow_block SET type='task';")
    op.alter_column("outflow_block", "type", nullable=False)
    op.add_column("outflow_block", sa.Column("parent_id", sa.Integer(), nullable=True))
    # op.drop_constraint("task", "outflow_block", type_="foreignkey")
    op.execute(
        "alter table outflow_block rename constraint outflow_task_run_id_fkey to outflow_block_run_id_fkey"
    )
    op.execute(
        "alter table outflow_block add constraint outflow_block_parent_id_fkey foreign key(parent_id) references outflow_block(id)"
    )

    op.execute(
        "alter table outflow_edge rename constraint outflow_edge_upstream_task_id_fkey to outflow_edge_upstream_block_id_fkey;"
    )
    op.execute(
        "alter table outflow_edge rename constraint outflow_edge_downstream_task_id_fkey to outflow_edge_downstream_block_id_fkey;"
    )
    op.execute("alter table outflow_block drop constraint outflow_task;")

    op.alter_column(
        "outflow_edge", "upstream_task_id", new_column_name="upstream_block_id"
    )
    op.alter_column(
        "outflow_edge", "downstream_task_id", new_column_name="downstream_block_id"
    )

    op.alter_column("outflow_runtime_exception", "task_id", new_column_name="block_id")
    op.execute(
        "alter table outflow_block rename constraint outflow_task_pkey to outflow_block_pkey;"
    )

    op.execute(
        "alter table outflow_block rename constraint outflow_task_uuid_key to outflow_block_uuid_key;"
    )
    op.execute(
        "alter table outflow_runtime_exception rename constraint outflow_runtime_exception_task_id_fkey to outflow_edge_downstream_block_id_fkey;"
    )
    op.drop_table("outflow_workflow")
    # ### end Alembic commands ###
    op.execute("ALTER SEQUENCE  outflow_task_id_seq RENAME TO outflow_block_id_seq")
    op.drop_column("outflow_block", "workflow_id")


def downgrade():
    if op.get_context().dialect.name == "sqlite":
        return

    return  # TODO finish downgrade migration

    # ### commands auto generated by Alembic - please adjust! ###

    # original downgrade migration, keep what is necessary

    # op.add_column(
    #     "outflow_runtime_exception",
    #     sa.Column("task_id", sa.INTEGER(), autoincrement=False, nullable=True),
    # )
    # op.drop_constraint(None, "outflow_runtime_exception", type_="foreignkey")
    # op.create_foreign_key(
    #     "runtime_exception_task_id_fkey",
    #     "outflow_runtime_exception",
    #     "outflow_task",
    #     ["task_id"],
    #     ["id"],
    # )
    # op.drop_column("outflow_runtime_exception", "block_id")
    # op.add_column(
    #     "outflow_edge",
    #     sa.Column(
    #         "downstream_task_id", sa.INTEGER(), autoincrement=False, nullable=False
    #     ),
    # )
    # op.add_column(
    #     "outflow_edge",
    #     sa.Column(
    #         "upstream_task_id", sa.INTEGER(), autoincrement=False, nullable=False
    #     ),
    # )
    # op.drop_constraint(None, "outflow_edge", type_="foreignkey")
    # op.drop_constraint(None, "outflow_edge", type_="foreignkey")
    # op.create_foreign_key(
    #     "edge_downstream_task_id_fkey",
    #     "outflow_edge",
    #     "outflow_task",
    #     ["downstream_task_id"],
    #     ["id"],
    # )
    # op.create_foreign_key(
    #     "edge_upstream_task_id_fkey",
    #     "outflow_edge",
    #     "outflow_task",
    #     ["upstream_task_id"],
    #     ["id"],
    # )
    # op.drop_column("outflow_edge", "downstream_block_id")
    # op.drop_column("outflow_edge", "upstream_block_id")
    # op.drop_table("outflow_block")
    # ### end Alembic commands ###

    # wip manual operations
    op.execute("drop type blocktypeenum")

    op.rename_table("outflow_block", "outflow_task")
    op.drop_column("outflow_task", "type")

    op.drop_column("outflow_task", "parent_id")

    op.execute(
        "alter table outflow_task rename constraint outflow_block_run_id_fkey to outflow_task_run_id_fkey"
    )
    op.execute("alter table outflow_task drop constraint outflow_block_parent_id_fkey")
