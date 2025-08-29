# -*- coding: utf-8 -*-
import datetime
import socket
import traceback
from typing import Optional

from outflow.core.block import Block
from outflow.core.types import Skipped
from outflow.core.workflow import Workflow

from outflow.management.models.block import Block as BlockModel


class BlockRunner:
    """
    Manage block calls and store the results
    """

    def __init__(
        self,
        block_db_mapping: dict,
        *,
        parent_block_db: BlockModel,
        initial_inputs: Optional[dict] = None,
    ):
        self.parent_block_db = parent_block_db
        self.block_db_mapping = block_db_mapping

        self.results = {}

        # initial_inputs is used to pass the targets values from one workflow execution to another
        if initial_inputs:
            self.initial_inputs = initial_inputs
        else:
            self.initial_inputs = {}

    def compute(self, workflow: Workflow):
        from outflow.library.tasks import MergeTask

        # run through each task of the workflow to gather task result references
        for block in workflow.sorted_children():
            if block.id in self.results:
                # avoid reprocessing already visited graph nodes
                continue

                # create a dictionary to store the reference to the block inputs
            task_inputs = {}

            # if this is the first executable (no parents) look for inputs in self.initial_inputs
            task_inputs.update(
                {
                    key: self.initial_inputs[key]
                    for key in block.inputs.keys()
                    if key in self.initial_inputs
                }
            )
            if isinstance(block, MergeTask):
                task_inputs.update(
                    {
                        upstream_block.name
                        + "_"
                        + key: self.results[upstream_block.id][key]
                        for upstream_block in block.upstream_blocks
                        for key in upstream_block.outputs.keys()
                        if not isinstance(self.results[upstream_block.id], Skipped)
                    }
                )

            values_from_upstream = {
                key: self.results[upstream_block.id][key]
                for upstream_block in block.upstream_blocks
                for key in upstream_block.outputs.keys()
                if not isinstance(self.results[upstream_block.id], Skipped)
            }

            task_inputs.update(
                {
                    key: values_from_upstream[key]
                    for key in block.inputs.keys()
                    if key in values_from_upstream
                }
            )

            task_return_value = self.run(block, task_inputs)
            task_return_value = self.post_process(block, task_return_value)

            self.results[block.id] = task_return_value

    def run(self, block: Block, task_inputs: dict):
        """Run a block and manage its state in database"""

        db_block = self.block_db_mapping[block]

        if db_block is None:
            # fix for MapWorkflows ran with db_untracked
            # because NullObjects deserialize into None
            from outflow.core.generic.null_object import NullObject

            db_block = NullObject()

        db_block.parent = self.parent_block_db

        if block.skip_if_upstream_skip and any(
            upstream.skip for upstream in block.upstream_blocks
        ):
            block.skip = True

        if block.skip:
            db_block.skip()
            return Skipped()

        db_block.start()
        db_block.hostname = socket.gethostname()

        task_kwargs = {**task_inputs, **block.bound_kwargs}

        try:
            # call the block
            return_value = block(**task_kwargs, block_db=db_block)
        except Exception as e:
            db_block.fail()

            from outflow.management.models.runtime_exception import RuntimeException
            from outflow.core.pipeline import context

            if not context.dry_run and not context.db_untracked:
                RuntimeException.create(
                    block=db_block,
                    exception_type=e.__class__.__name__,
                    exception_msg=traceback.format_exc().splitlines()[-1],
                    traceback=traceback.format_exc(),
                    time=datetime.datetime.now(),
                )

            raise e

        db_block.success()

        return return_value

    def post_process(self, block, task_return_value):
        post_processed = task_return_value

        return post_processed
