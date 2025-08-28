# -*- coding: utf-8 -*-
from functools import partial
from multiprocessing import Pool, cpu_count

from outflow.core.pipeline import context
from outflow.library.workflows.base_map_workflow import BaseMapWorkflow
import cloudpickle
from outflow.core.pipeline.pipeline import set_pipeline_state, get_pipeline_states
from outflow.core.pipeline.context_manager import PipelineContextManager


class ParallelMapWorkflow(BaseMapWorkflow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(self.parent_workflow, BaseMapWorkflow):
            raise NotImplementedError(
                "Nested MapWorkflows are not supported with parallel backend"
            )

    @staticmethod
    def _run_workflow(index, serialized_pipeline_states, serialized_map_info):
        # restore the pipeline states
        # note: we need to recreate a context manager before restoring the states
        # when using a fresh python interpreter process (spawn)
        # see https://gitlab.com/outflow-project/outflow/-/issues/56
        with PipelineContextManager():
            set_pipeline_state(**cloudpickle.loads(serialized_pipeline_states))
            self = cloudpickle.loads(serialized_map_info)
            return self.run_mapped_workflow(index=index, block_db=self.block_db)

    def run(self, block_db, **map_inputs):
        self.generated_inputs = list(self.generator(**map_inputs))
        results_from_cache = list()

        if self.cache:
            results_from_cache = self.filter_cached()

        self.create_graph_in_db(nb_copies=len(self.generated_inputs))
        self.put_input_values_in_db(self.generated_inputs, block_db)
        context.session.commit()

        self.block_db = block_db

        serialized_map_info = cloudpickle.dumps(self)

        run = partial(
            self._run_workflow,
            serialized_pipeline_states=cloudpickle.dumps(get_pipeline_states()),
            serialized_map_info=serialized_map_info,
        )

        indices = range(len(self.generated_inputs))

        with Pool(cpu_count()) as pool:
            results = pool.map(run, indices)

        results.extend(results_from_cache)

        return self.reduce(results)
