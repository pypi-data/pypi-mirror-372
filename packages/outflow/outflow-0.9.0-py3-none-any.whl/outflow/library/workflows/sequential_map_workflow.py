# -*- coding: utf-8 -*-
from outflow.core.pipeline import context
from outflow.library.workflows.base_map_workflow import BaseMapWorkflow
from outflow.management.models.block import Block


class SequentialMapWorkflow(BaseMapWorkflow):
    def run(self, *, block_db: Block, **map_inputs):
        results = list()
        results_from_cache = list()

        self.generated_inputs = list(self.generator(**map_inputs))

        if self.cache:
            results_from_cache = self.filter_cached()

        self.create_graph_in_db(nb_copies=len(self.generated_inputs))
        self.put_input_values_in_db(self.generated_inputs, block_db)
        context.session.commit()

        for index, generated_inputs in enumerate(self.generated_inputs):
            result = self.run_mapped_workflow(index=index, block_db=block_db)

            results.append(result)

        results.extend(results_from_cache)

        return self.reduce(results)
