# -*- coding: utf-8 -*-
from outflow.core.logging import logger
from outflow.core.tasks import BlockRunner

# from outflow.core.types import Skipped
from outflow.core.workflow import Workflow


class Backend:
    # The backend class is responsible for initializing everything needed for
    # the execution of the top level workflow.
    # For the default backend, this is initializing a block runner and
    # creating the tasks in the database
    # When subclassing this class, override the attribute `name` in __init__
    def __init__(self):
        logger.debug(f"Initialize backend '{self}'")
        self.name = "default"

    def run(self, *, workflow: Workflow, task_returning: list):
        top_level_workflow_db = workflow.create_db_block()

        workflow.create_graph_in_db()

        block_runner = BlockRunner(
            workflow.block_db_mappings[0], parent_block_db=top_level_workflow_db
        )

        block_runner.compute(workflow)

        execution_return = [block_runner.results[task.id] for task in task_returning]

        return execution_return

    def clean(self):
        """This method is always called at the end of the pipeline execution"""
        pass
