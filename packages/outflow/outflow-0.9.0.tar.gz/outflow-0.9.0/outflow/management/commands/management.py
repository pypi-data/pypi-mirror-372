# -*- coding: utf-8 -*-
from datetime import datetime

from rich.console import Console
from rich.table import Table

from outflow.core.commands import RootCommand, Command, argument
from outflow.core.logging import logger
from outflow.core.pipeline import config, context
from outflow.library.tasks.shell_tasks import IPythonTask
from outflow.management.models.run import Run
from outflow.management.models.runtime_exception import RuntimeException

from outflow.management.models.block import Block


@RootCommand.subcommand(invokable=False, db_untracked=True, backend="default")
def Management():
    pass


@Management.subcommand()
def DisplayConfig():
    print(config)


@Management.subcommand(db_untracked=False)
class Shell(Command):
    """
    Run an interactive shell with access to the pipeline context.
    """

    def setup_tasks(self):
        return IPythonTask()


@argument("--no-limit", action="store_true", help="Print all runs")
@argument("--success-only", action="store_true", help="Print only runs that succeeded")
@Management.subcommand()
def ListRuns(no_limit: bool, success_only: bool):
    """
    Print the list of run in the database
    """

    runs_query = (
        context.session.query(Run)
        .filter(Run.start_time != None)  # noqa: E711
        .order_by(Run.start_time.desc())
    )

    if not no_limit:
        runs_query = runs_query.limit(50)

    if success_only:
        runs_query = runs_query.filter(Run.state == "success")

    runs: list = runs_query.all()

    runs.reverse()

    table = Table(title="Pipeline runs in database")

    table.add_column("Run id")
    table.add_column("Command")
    table.add_column("Start time")
    table.add_column("State")

    for run in runs:
        table.add_row(
            str(run.id),
            run.command_name,
            datetime.strftime(run.start_time, "%Y-%m-%d %H:%M:%S"),
            run.state.name,
        )

    console = Console()

    try:
        console.print(table)
    except BrokenPipeError:
        pass


@argument("run_id", help="Id of the run to debug", type=int)
@Management.subcommand()
def Debug(run_id):
    """
    Prints the list of failed task in a run and the exception raised
    """

    task_failed = (
        context.session.query(Block)
        .filter(Block.type == "task")
        .filter(Block.run_id == run_id)
        .filter(Block.state == "failed")
        .all()
    )

    if not task_failed:
        logger.info(f"Run {run_id} does not have any failed task")

    for task in task_failed:
        prev_task = task
        while prev_task.upstream_blocks:
            prev_task = prev_task.upstream_blocks[0]

        input_values = prev_task.input_values

        log_message = f"Task {task.name} failed"
        if input_values:
            log_message += f" with workflow input : {input_values}"

        logger.info(log_message)

        exception = (
            context.session.query(RuntimeException)
            .filter(RuntimeException.block_id == task.id)
            .one()
        )

        logger.info("Reason :")
        logger.error(
            f"\n{exception.traceback}\n{exception.exception_type} {exception.exception_msg}"
        )


# @Management.subcommand()
# class TestSlurm(Command):
#     """
#     Run slurm test suite. Useful to check if your Slurm cluster is properly configured for use with outflow.
#     """
#
#     def setup_tasks(self):
#         from outflow.core.tasks import Task
#         @as_task
#         def ExampleTask() -> {"value": int}:
#             import os
#             return int(os.getenv("SLURM_JOBID"))
#
#
#         from outflow.slurm.map_task import SlurmMapWorkflow
#         with SlurmMapWorkflow() as map:
