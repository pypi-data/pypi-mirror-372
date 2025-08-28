# -*- coding: utf-8 -*-
from outflow.core.tasks import BlockRunner
from outflow.core.tasks.io_checker import IOChecker
from outflow.core.workflow import Workflow


class IterativeWorkflow(Workflow):
    """
    The iterative workflow executes multiple times their task sequence,
    re-injecting one of the outputs as the input of the next execution.
    """

    def __init__(
        self,
        max_iterations,
        break_func,
        initial_value=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.break_func = break_func
        self.max_iterations = max_iterations
        self.initial_value = initial_value

    def run_iterative_workflow(
        self,
        index,
        block_db,
        block_runner_class: type(BlockRunner) = BlockRunner,
        **inputs,
    ) -> dict:
        # execute sub-workflow
        task_manager = block_runner_class(
            self.block_db_mappings[index],
            parent_block_db=block_db,
            initial_inputs=inputs,
        )

        task_manager.compute(self)

        terminating_tasks_results = list()

        # get outputs of last tasks of workflow
        for end_block in self.end_blocks():
            terminating_tasks_results.append(task_manager.results[end_block.id])

        temp_result_dict = {}

        for result in terminating_tasks_results:
            for key, value in result.items():
                temp_result_dict[key] = value

        return temp_result_dict

    def run(self, block_db, **inputs) -> dict:
        inputs_copy = inputs.copy()

        self.setup_external_edges(inputs_copy)

        result = {}

        for index in range(self.max_iterations):
            self.create_graph_in_db()

            result = self.run_iterative_workflow(
                index=index, block_db=block_db, **{**inputs_copy, **result}
            )

            if self.break_func(**result):
                break

        return result

    def check_inputs(self, inputs, values_from_upstream):
        inputs_copy = inputs.copy()

        self.setup_external_edges(inputs_copy)
        self.block_db_mappings = [{}]

        self.run_iterative_workflow(
            index=0, block_db=None, block_runner_class=IOChecker, **inputs_copy
        )
