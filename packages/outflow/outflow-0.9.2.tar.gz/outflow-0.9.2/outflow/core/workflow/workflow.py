# -*- coding: utf-8 -*-
import hashlib
import json
from pathlib import Path
from typing import List, Iterable, Union, Type, Callable, Optional, overload

import networkx

from outflow.core.block import Block
from outflow.core.logging import logger
from outflow.core.pipeline import context
from outflow.core.workflow import WorkflowManager
from outflow.core.workflow.workflow_cache import WorkflowCache


class Workflow(Block):
    block_type = "workflow"

    def __init__(
        self,
        *,
        cache: bool = False,
        CacheClass: Type[WorkflowCache] = WorkflowCache,
        cache_dir: Union[str, Path, None] = None,
        **kwargs,
    ):
        """
        A class to store a workflow of blocks
        """

        # reset targets in __init__ since the intended usage of this class is
        # to automatically get inputs and outputs from tasks, they are not
        # supposed to be set by users
        self._outputs = {}
        self._inputs = {}

        super().__init__(**kwargs)
        self.digraph = networkx.DiGraph()
        if cache:
            self.cache = CacheClass(workflow=self, cache_dir=cache_dir)
        else:
            self.cache = None

        self.external_edges = {}
        self.workflow_manager: WorkflowManager
        self.block_db_mappings: List[dict] = []

        self.inputs_value = None

    def _json_default(self, obj):
        # Checks if the object has special methods for json serialization
        try:
            if hasattr(obj, "_sa_class_manager") and hasattr(obj, "__table__"):
                # if obj is an sqlalchemy orm object
                return {
                    c.name: str(getattr(obj, c.name)) for c in obj.__table__.columns
                }
            elif hasattr(obj, "to_json"):
                return obj.to_json()
            elif hasattr(obj, "__getstate__"):
                return obj.__getstate__()
            else:
                return obj.__dict__
        except Exception:
            logger.error(f"Could not pickle object {obj}")
            raise

    def get_config_values(self) -> dict:
        # relevant issue https://gitlab.com/outflow-project/outflow/-/issues/60
        relevant_config_values = {}
        for task in self:
            if task.block_type == "task":
                if task.parameterized_kwargs:
                    relevant_config_values.update(task.parameterized_kwargs)

        return relevant_config_values

    @property
    def hash(self) -> str:
        if self.inputs_value is None:
            raise AttributeError(
                "self.inputs_value must be set before using WorkflowCache methods"
            )

        data = []

        for t in self:
            data.append(t.name)
            for p in t.upstream_blocks:
                data.append(p.name)
            for s in t.downstream_blocks:
                data.append(s.name)

        values_to_hash = {
            **self.inputs_value,
            **self.get_config_values(),
            "__workflow_name": self.name,
            "__digraph_data": data,
        }

        try:
            dumps = json.dumps(
                values_to_hash,
                default=self._json_default,
                sort_keys=True,
                ensure_ascii=False,
                indent=None,
                separators=(",", ":"),
            )
        except AttributeError:
            raise AttributeError(
                f"Workflows with activated cache must have json serializable inputs. Could not serialize {values_to_hash}"
            )

        return hashlib.sha256(dumps.encode("utf8")).hexdigest()

    def run(self, *args, block_db, **kwargs):
        """Run the workflow

        Args:
            block_db: the orm object of type Block that represent the current
                workflow.
            kwargs: inputs of the workflow

        """

        # Save the input values in self, useful for calls to self.hash
        self.inputs_value = kwargs

        result = {}
        do_run = False

        if self.cache and self.cache.exists():
            try:
                result = self.cache.read()  # try except here and skip if cannot read
            except Exception:
                logger.warning("Could not read artifact file")
                do_run = True
        else:
            do_run = True

        if do_run:
            # compute result
            from outflow.core.tasks import BlockRunner

            self.create_graph_in_db()

            task_manager = BlockRunner(
                self.block_db_mappings[-1],
                parent_block_db=block_db,
                initial_inputs=kwargs,
            )
            task_manager.compute(self)

            merged_results = {}

            for end_block in self.end_blocks():
                end_block_result = task_manager.results[end_block.id]
                if end_block_result is not None:
                    for key, val in end_block_result.items():
                        if key in merged_results:
                            raise KeyError(
                                f"Key {key} found in multiple end blocks. "
                                f"Output target names of workflow end blocks must be unique."
                            )
                        else:
                            merged_results.update({key: val})

            result = merged_results

            if self.cache:
                self.cache.write(result)

        self.inputs_value = None

        return result

    def add_child(self, block: Block):
        """Add given block to the workflow digraph"""
        self.digraph.add_node(block, db_refs=[])

    @property
    def upstream_blocks(self) -> List[Block]:
        """Return the list of upstream blocks"""
        return self.parent_workflow.get_upstream(self)

    @property
    def downstream_blocks(self) -> List[Block]:
        """Return the list of downstream blocks"""
        return self.parent_workflow.get_downstream(self)

    def create_graph_in_db(self, nb_copies: int = 1):
        """Create database objects for all blocks of this workflow and their edges.

        Args:
            nb_copies: number of copies of the workflow to put in database
        """
        for i in range(nb_copies):
            mapping = {}

            for block in self:
                mapping[block] = block.create_db_block()

            for block in self:
                for downstream in block.downstream_blocks:
                    Block.create_db_edge(
                        mapping[block],
                        mapping[downstream],
                    )

            self.block_db_mappings.append(mapping)

        context.session.commit()

    def __call__(self, **inputs):
        logger.debug(f"Running workflow {self.name}")
        self.block_db_mappings.clear()  # TODO test if this is the right thing to do
        return self.run(**inputs)

    def add_external_edge(self, upstream_block: Block, downstream_block: Block):
        """Adds the edge between the two given blocks to the external edges of this workflow"""
        self.external_edges.update({upstream_block: downstream_block})

        # Edit workflow inputs so that it expects the upstream blocks outputs
        self.inputs.update({item for item in upstream_block.outputs.items()})

    def setup_external_edges(self, inputs: dict):
        """Binds values from inputs_copy to internal tasks.

        When a workflow has external edges, the values expected by the internal
        task is given to the workflow block. Call this function at the start of
        the workflow execution to bind these values to the blocks that expect them.

        Args:
            inputs:

        """

        internal_tasks_inputs = {}
        for external_task, internal_task in self.external_edges.items():
            external_task_inputs = {}
            for output_name in external_task.outputs:
                external_task_inputs.update({output_name: inputs[output_name]})
                del inputs[output_name]

            internal_tasks_inputs.update({internal_task: external_task_inputs})

        for internal_task, external_inputs in internal_tasks_inputs.items():
            real_internal_task = [
                task for task in self if task.name == internal_task.name
            ][0]
            real_internal_task.bind(**external_inputs)

    def get_upstream(self, block: Block) -> List[Block]:
        """Return the list of upstream blocks of the given block in the current workflow"""
        return list(self.digraph.predecessors(block))

    def get_downstream(self, block: Block) -> List[Block]:
        """Return the list of downstream blocks of the given block in the current workflow"""
        return list(self.digraph.successors(block))

    def __iter__(self) -> Iterable[Block]:
        """Returns an iterable of all the blocks of the workflow sorted by the digraph"""
        for block in self.sorted_children():
            yield block

    def sorted_children(self) -> Iterable[Block]:
        """Returns an iterable of all the blocks of the workflow sorted by the digraph"""
        sorted_children = networkx.topological_sort(self.digraph)
        for block in sorted_children:
            yield block

    def start_blocks(self) -> List[Block]:
        """Returns the list of blocks without any upstream blocks"""
        start_blocks = []
        for node in self.digraph:
            if self.digraph.in_degree(node) == 0:
                start_blocks.append(node)

        return start_blocks

    def end_blocks(self) -> List[Block]:
        """Returns the list of blocks without any downstream blocks"""
        end_blocks = []
        for node in self.digraph:
            if self.digraph.out_degree(node) == 0:
                end_blocks.append(node)

        return end_blocks

    def start(self):
        """Sets up a context manager for this workflow"""
        self.workflow_manager = WorkflowManager(workflow=self).__enter__()
        return self

    def stop(self, *args):
        if not args:
            args = (None, None, None)
        self.workflow_manager.__exit__(*args)

        self.workflow_manager = None

        self.setup_targets()

    def __enter__(self):
        return self.start()

    def __exit__(self, *args):
        """Exits this workflow context manager"""
        if args:
            if args[0] is NotImplementedError:
                return False

        self.stop(*args)

    def setup_targets(self):
        """Method called at context manager exit

        Copies the outputs of the last tasks and the inputs of the first tasks
        Can be overridden in Workflow subclasses
        """

        for block in self.end_blocks():
            self.outputs.update(block.outputs)

        for block in self.start_blocks():
            self.inputs.update(block.inputs)

    def __getstate__(self):
        """Sets up the workflow for pickling

        Replaces orm objects of contained blocks in attribute block_db_mapping
        by their row id.
        """

        state = self.__dict__.copy()

        mappings_copy = []

        for mapping in self.block_db_mappings:
            new_mapping = {}
            for block, db_block in mapping.items():
                new_mapping[block] = db_block.id

            mappings_copy.append(new_mapping)

        state["block_db_mappings"] = mappings_copy

        return state

    def __setstate__(self, state):
        """Unpickle a workflow

        Replaces row ids by their orm object in attribute block_db_mapping.
        """

        vars(self).update(state)

        from outflow.management.models.block import (
            Block as BlockModel,
        )

        dbm: list = self.block_db_mappings

        for mapping in dbm:
            for block, db_block_id in mapping.items():
                mapping[block] = BlockModel.one(id=db_block_id)

    def check_inputs(self, block_inputs: dict, values_from_upstream: dict):
        from outflow.core.tasks.io_checker import IOChecker

        IOChecker({}, parent_block_db=None, initial_inputs=block_inputs).compute(self)

    @classmethod
    def as_workflow(
        cls: Type["Workflow"],
        run_func: Callable = None,
        name: Optional[str] = None,
        cache: bool = False,
        **kwargs,
    ) -> Callable:
        """
        Transform the decorated function into a workflow factory.

        The definition of the 'as_workflow' decorator is done outside of the class to ensure proper function typing with overloads
        """
        return as_workflow(run_func=run_func, cls=cls, name=name, cache=cache, **kwargs)


@overload
def as_workflow(
    run_func: Callable,
    cls: Type[Workflow] = Workflow,
    name: Optional[str] = None,
    cache: bool = False,
    **kwargs,
) -> Callable[..., Workflow]:
    pass


@overload
def as_workflow(
    cls: Type[Workflow] = Workflow,
    name: Optional[str] = None,
    cache: bool = False,
    **kwargs,
) -> Callable[..., Callable[..., Workflow]]:
    pass


def as_workflow(
    run_func: Callable = None,
    cls: Type[Workflow] = Workflow,
    name: Optional[str] = None,
    cache: bool = False,
    **kwargs,
):
    """
    Transform the decorated function into another function, a workflow factory

    """

    if run_func is None:

        def inner_function(_run_func):
            return as_workflow(_run_func, cls, cache=cache, name=name, **kwargs)

        return inner_function
    else:
        if name is None:
            name = run_func.__name__

        def proxy(*_args, **_kwargs):
            workflow = cls(name=name, cache=cache, **kwargs)
            workflow.start()
            run_func(*_args, **_kwargs)
            workflow.stop()
            return workflow

        return proxy
