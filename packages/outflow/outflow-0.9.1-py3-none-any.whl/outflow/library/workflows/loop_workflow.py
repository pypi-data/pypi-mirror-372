# -*- coding: utf-8 -*-
import traceback

from outflow.core.exceptions import ExitPipeline
from outflow.core.logging import logger
from outflow.core.tasks import BlockRunner
from outflow.core.workflow import Workflow
from outflow.management.models.block import Block


class LoopWorkflow(Workflow):
    def __init__(self, iterations: int = 0, infinite: bool = False, **kwargs):
        super().__init__(**kwargs)

        if iterations and infinite:
            raise RuntimeError(
                "You can only set a number of iterations or infinite=True for LoopTask, not both."
            )

        if not iterations and not infinite:
            raise RuntimeError(
                "You must either set a number of iterations or infinite=True for LoopTask"
            )

        self.nb_iterations = iterations
        self.infinite = infinite

    def run_subworkflow(self, block_db: Block, inputs_copy: dict, index: int = -1):
        # execute workflow
        block_runner = BlockRunner(
            self.block_db_mappings[index],
            parent_block_db=block_db,
            initial_inputs=inputs_copy,
        )
        block_runner.compute(self)

    def run(self, block_db, **inputs: dict):
        inputs_copy = inputs.copy()

        self.setup_external_edges(inputs_copy)

        index = 0

        if self.infinite:
            while True:
                self.create_graph_in_db()
                try:
                    self.run_subworkflow(block_db, inputs_copy, index)
                    index += 1
                except ExitPipeline as exit_pipeline:
                    raise exit_pipeline
                except Exception:
                    logger.warning(
                        f"LoopWorkflow raised an exception. Inputs : {inputs_copy}"
                    )
                    logger.warning(traceback.format_exc())
        else:
            self.create_graph_in_db(self.nb_iterations)

            for index in range(self.nb_iterations):
                self.run_subworkflow(block_db, inputs_copy, index)

    def check_inputs(self, task_inputs, values_from_upstream):
        pass
