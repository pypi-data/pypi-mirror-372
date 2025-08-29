# -*- coding: utf-8 -*-
from outflow.core.tasks import BlockRunner
from outflow.core.types import Skipped


class IOChecker(BlockRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compute(self, workflow):
        from outflow.library.tasks import MergeTask

        # run through each task of the workflow to gather task result references
        for block in workflow.sorted_children():
            if block.id in self.results:
                # avoid reprocessing already visited graph nodes
                continue

                # create a dictionary to store the reference to the block inputs
            task_inputs = {}

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

            block.check_inputs(
                {**task_inputs, **block.bound_kwargs},
                values_from_upstream=values_from_upstream,
            )

            self.results[block.id] = {key: None for key in block.outputs.keys()}
