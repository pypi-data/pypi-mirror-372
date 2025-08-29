# -*- coding: utf-8 -*-
"""Rename fkeys

Revision ID: 4559a1933ea0
Revises: 681dd4fd7a35
Create Date: 2022-01-14

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "4559a1933ea0"
down_revision = "681dd4fd7a35"
branch_labels = None
depends_on = None


def upgrade():
    if op.get_context().dialect.name == "sqlite":
        return
    if op.get_context().dialect.name == "postgresql":
        op.execute(
            ";\n".join(
                [
                    "ALTER table outflow_edge rename constraint edge_upstream_task_id_fkey TO outflow_edge_upstream_task_id_fkey",
                    "ALTER table outflow_edge rename constraint edge_downstream_task_id_fkey TO outflow_edge_downstream_task_id_fkey",
                    "ALTER table outflow_run rename constraint run_configuration_id_fkey TO outflow_run_configuration_id_fkey",
                    "ALTER table outflow_runtime_exception rename constraint runtime_exception_task_id_fkey TO outflow_runtime_exception_task_id_fkey",
                    "ALTER table outflow_task rename constraint task TO outflow_task",
                    "ALTER table outflow_task rename constraint task_run_id_fkey TO outflow_task_run_id_fkey",
                    "ALTER table outflow_workflow rename constraint workflow_manager_task_id_fkey TO outflow_workflow_manager_task_id_fkey",
                    "ALTER table outflow_workflow rename constraint workflow_parent_workflow_id_fkey TO outflow_parent_workflow_id_fkey",
                    "ALTER table outflow_workflow rename constraint workflow_run_id_fkey TO outflow_run_id_fkey",
                ]
            )
        )


def downgrade():
    if op.get_context().dialect.name == "sqlite":
        return
    if op.get_context().dialect.name == "postgresql":
        op.execute(
            "ALTER table outflow_edge rename constraint outflow_edge_upstream_task_id_fkey TO edge_upstream_task_id_fkey",
            "ALTER table outflow_edge rename constraint outflow_edge_downstream_task_id_fkey TO edge_downstream_task_id_fkey",
            "ALTER table outflow_run rename constraint outflow_run_configuration_id_fkey TO run_configuration_id_fkey",
            "ALTER table outflow_runtime_exception rename constraint outflow_runtime_exception_task_id_fkey TO runtime_exception_task_id_fkey",
            "ALTER table outflow_task rename constraint outflow_task TO task",
            "ALTER table outflow_task rename constraint outflow_task_run_id_fkey TO task_run_id_fkey",
            "ALTER table outflow_workflow rename constraint outflow_workflow_manager_task_id_fkey TO workflow_manager_task_id_fkey",
            "ALTER table outflow_workflow rename constraint outflow_parent_workflow_id_fkey TO workflow_parent_workflow_id_fkey",
            "ALTER table outflow_workflow rename constraint outflow_run_id_fkey TO workflow_run_id_fkey",
        )
