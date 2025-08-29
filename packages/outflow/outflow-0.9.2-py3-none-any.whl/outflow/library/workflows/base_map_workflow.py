# -*- coding: utf-8 -*-
import json
import traceback
from typing import List, Optional

import simple_slurm

from outflow.core.exceptions import IOCheckerError
from outflow.core.tasks.io_checker import IOChecker
from outflow.core.logging import logger
from outflow.core.target import Target
from outflow.core.tasks import BlockRunner
from outflow.core.types import IterateOn
from outflow.core.workflow import Workflow


class SigTerm(Exception):
    pass


class BaseMapWorkflow(Workflow):
    def __init__(
        self,
        *,
        no_outputs: bool = False,
        output_name: str = "map_output",
        raise_exceptions: bool = False,
        flatten_output: bool = True,
        map_on: Optional[dict] = None,
        **kwargs,
    ):
        """

        Args:
            no_outputs: if true, map workflow will return None, if false,
                returns a dictionary with one key being `output_name`, and
                value is a list of list of dict. (list of results of the list
                of the end blocks of each mapped workflow)
            output_name: name of the key of the return dictionary
            raise_exceptions: if false, catch and log exceptions but continue
                execution. If true, raise any exception.
            flatten_output: if true, will flatten the output of the map
                workflow, from a list of list of dict, to a single dict,
                with keys being the merged outputs of each end blocks,
                and value the list of the returned values
            map_on: dictionary that indicate which input of the map workflow
                should be split and mapped on. Optional if workflow has only
                one input, and first block of the workflow has only one input.
                Otherwise if more than one input, inputs are unmapped by default.
            **kwargs:
        """

        self.map_on = map_on
        self.input_mapping = {}

        # filter out eventual sbatch directives from kwargs
        sbatch_directive_name = [
            sublist[0] for sublist in simple_slurm.core.read_simple_txt("arguments.txt")
        ]
        for directive in sbatch_directive_name:
            if directive in kwargs:
                del kwargs[directive]

        super().__init__(**kwargs)
        self.raise_exceptions = raise_exceptions
        self.no_outputs = no_outputs
        self.output_name = output_name
        self.flatten_output = flatten_output
        self.generated_inputs: List[dict] = None
        self.results_from_cache = []

    def filter_cached(self):
        no_cache_indices = []
        results_from_cache = []

        for input_value in self.generated_inputs:
            self.inputs_value = input_value
            if self.cache.exists():
                try:
                    results_from_cache.append(
                        self.cache.read()
                    )  # try except here and skip if cannot read
                    no_cache_indices.append(False)
                except Exception:
                    logger.warning("Could not read artifact file")
                    no_cache_indices.append(True)
            else:
                no_cache_indices.append(True)

        from itertools import compress

        self.generated_inputs = list(compress(self.generated_inputs, no_cache_indices))

        # return the list of inputs with existing cache
        return results_from_cache

    def add_upstream(self, upstream_block: "Block"):
        super().add_upstream(upstream_block)
        self.setup_targets()

    def add_downstream(self, downstream_block: "Block"):
        super().add_downstream(downstream_block)
        self.setup_targets()

    def setup_input_mapping(self):
        """
        Called by setup_targets to populate input_mapping attribute, needed for
        generator and check_inputs methods
        """
        self.input_mapping = {}

        if self.map_on:
            self.input_mapping = self.map_on

            for upstream_output_name, input_name in self.map_on.items():
                del self.inputs[input_name]
                self.inputs.update({upstream_output_name: Target(upstream_output_name)})

        else:
            # deprecated IterateOn type
            for _, target in self.inputs.items():
                try:
                    if target.type.__name__.startswith(IterateOn.prefix):
                        sequence_name = target.type.__name__[len(IterateOn.prefix) :]
                        self.input_mapping.update({sequence_name: target.name})
                except AttributeError:
                    continue
            # end deprecated section

            if (
                len(self.inputs) == 1
                and len(self.upstream_blocks) == 1
                and len(self.upstream_blocks[0].outputs) == 1
            ) and not self.input_mapping:
                # only one upstream task with one output, and only one input, automatically iterate on the only target
                upstream_output_target = list(self.upstream_blocks[0].outputs.values())[
                    0
                ]
                input_name = list(self.inputs.keys())[0]
                self.input_mapping = {upstream_output_target.name: input_name}
                del self.inputs[input_name]
                self.inputs.update(
                    {upstream_output_target.name: upstream_output_target}
                )

    def setup_targets(self):
        """
        This method sets up the targets of a Map Workflow.
        The automatic map_on needs to know the upstream_blocks of the MapWorkflow,
        this means it must be called after add_upstream and add_downstream.
        So it needs to clear self.inputs but keep the inputs set by external edges.
        """

        # clear self.inputs but only for non external edges
        for input_name in self.inputs.copy().keys():
            for external_edge_upstream_block in self.external_edges.keys():
                if input_name not in external_edge_upstream_block.outputs.keys():
                    del self.inputs[input_name]

        self.outputs = {}

        for task in self.start_blocks():
            for target in task.inputs.values():
                try:
                    if target.type.__name__.startswith(IterateOn.prefix):
                        key = target.type.__name__[len(IterateOn.prefix) :]
                    else:
                        key = target.name
                except AttributeError:
                    key = target.name
                    pass
                self.inputs.update({key: target})

        if not self.outputs and not self.no_outputs:
            if self.flatten_output:
                self.outputs = {
                    output.name: output
                    for block in self.end_blocks()
                    for output in block.outputs.values()
                }
            else:
                self.outputs = {self.output_name: Target(self.output_name, type=List)}

        self.setup_input_mapping()

    def run(self, **map_inputs):
        raise NotImplementedError()

    def generator(self, **map_inputs):
        """
        default generator function
        :param map_inputs:
        :return:
        """

        inputs = map_inputs.copy()

        # sequence_input_names = []
        input_names = []
        sequences = []

        if not self.input_mapping:
            raise AttributeError(
                f"MapWorkflow {self.name} has multiple inputs. You must specify "
                "on which target to map with the map_on attribute of MapWorkflow"
            )

        # get IterateOn inputs
        for sequence_input_name, iterable_target in self.input_mapping.items():
            input_names.append(iterable_target)
            sequences.append(map_inputs[sequence_input_name])

            del inputs[sequence_input_name]

        for input_values in zip(*sequences):
            vals = {input_names[i]: input_values[i] for i in range(len(input_names))}
            yield {**vals, **inputs}

    @staticmethod
    def put_input_values_in_db(inputs, block_db):
        # Get either json dump or str of input values to put in database
        serializable_input_values = []
        for input in inputs:
            serialized = {}
            for input_name, input_val in input.items():
                try:
                    serialized.update({input_name: json.dumps(input_val)})
                except TypeError:
                    serialized.update({input_name: str(input_val)})
            serializable_input_values.append(serialized)

        block_db.input_values = serializable_input_values

    def check_inputs(self, map_inputs, values_from_upstream):
        inputs = map_inputs.copy()

        input_names = []
        sequences = []

        if not self.input_mapping:
            raise AttributeError(
                f"MapWorkflow {self.name} has multiple inputs. You must specify "
                "on which target to map with the map_on attribute of MapWorkflow"
            )

        for sequence_input_name, iterable_target in self.input_mapping.items():
            input_names.append(iterable_target)

            try:
                sequences.append(map_inputs[sequence_input_name])
            except KeyError:
                raise IOCheckerError(
                    f"{self.name} did not get input {sequence_input_name}"
                )

            del inputs[sequence_input_name]

        self.generated_inputs = [
            {
                **{input_name: None for input_name in input_names},
                **inputs,
            }
        ]

        self.block_db_mappings = [{}]

        backup_cache = self.cache
        self.cache = None
        self.run_mapped_workflow(0, None, IOChecker)
        self.cache = backup_cache

    def run_mapped_workflow(
        self,
        index,
        block_db,
        block_runner_class: type(BlockRunner) = BlockRunner,
    ):
        inputs_copy = self.generated_inputs[index].copy()
        # bind external dependencies to internal tasks

        self.setup_external_edges(inputs_copy)

        result = []

        block_runner = block_runner_class(
            self.block_db_mappings[index],
            parent_block_db=block_db,
            initial_inputs=inputs_copy,
        )

        try:
            block_runner.compute(self)

            for block in self.end_blocks():
                result.append(block_runner.results[block.id])

            if self.cache:
                self.inputs_value = inputs_copy
                self.cache.write(result)
                self.inputs_value = None

        except SigTerm:
            raise
        except Exception as e:
            if self.raise_exceptions:
                raise e
            logger.warning(
                f"Mapped workflow {index} raised an exception. Inputs : {inputs_copy}"
            )
            logger.warning(traceback.format_exc())
            result = e

        return result

    # TODO replace with user provided reduce
    def reduce(self, output):
        if self.no_outputs:
            return None
        elif self.flatten_output:
            output_dict = {output_name: [] for output_name in self.outputs}

            for workflow_results in output:
                if isinstance(workflow_results, Exception):
                    # if the workflow task raised an exception, a proper flattening is not possible
                    # therefore return the exception for each expected output key
                    for key in output_dict:
                        output_dict[key].append(workflow_results)

                    # and skip the flattening for this result
                    continue

                for block_result in workflow_results:
                    if isinstance(block_result, Exception):
                        if self.raise_exceptions:
                            raise block_result
                    else:
                        for key, value in block_result.items():
                            output_dict[key].append(value)

            return dict(output_dict)

        else:
            return {self.output_name: output}
