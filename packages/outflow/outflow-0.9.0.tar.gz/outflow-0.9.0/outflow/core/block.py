# -*- coding: utf-8 -*-
"""Module containing the base class for outflow tasks and workflows"""

from typing import Dict, Any, List
from uuid import uuid4

from outflow.core.generic.string import to_snake_case
from outflow.core.pipeline import context
from outflow.core.plugin import get_plugin_name
from outflow.core.target import Target, NoDefault
from outflow.core.logging import logger


class Block:
    """Abstract base class for outflow tasks and workflows

    Attributes:
        parent_workflow (Block): Reference to the parent block that wraps this block.
        uuid (str): A universally unique identifier for this block.
        status (str): Store the work cycle progress.
        inputs (Target): Inputs targets of this block.
        outputs (Target): Outputs targets of this block.
        skip (bool): Indicated if the blocks is skipped/will be skipped (it is the same thing for now)
        name (str): Name of this block
    """

    _inputs: Dict[str, Target] = {}
    _outputs: Dict[str, Target] = {}

    @property
    def block_type(self) -> str:
        raise NotImplementedError

    @classmethod
    def __init_subclass__(cls, **kwargs) -> None:
        # reset the targets definition attribute to avoid sharing targets definition with subclasses
        cls._outputs = {}
        cls._inputs = {}

        if not cls.__dict__.get("plugin_name", None):
            cls.plugin_name = get_plugin_name()

        cls.name = to_snake_case(cls.__name__)  # may be redefined in __init__

    def __init__(self, name: str = None, **bound_kwargs):
        if name is not None:
            self.name = name

        self.status = None
        self.skip = False
        self.skip_if_upstream_skip = False

        from outflow.core.workflow import WorkflowManager

        workflow_context = WorkflowManager().get_context()

        self.parent_workflow: "Workflow" = None

        if "workflow" in workflow_context:
            self.parent_workflow = workflow_context["workflow"]
            self.parent_workflow.add_child(self)

        # get class attributes to instance attributes so they get pickled
        self.inputs = self._inputs
        self.outputs = self._outputs

        self.bound_kwargs = {}

        self.bound_kwargs = bound_kwargs.copy()

    def __repr__(self):
        return f"{self.name}-{self.id}"

    def __str__(self) -> str:
        return self.name

    @property
    def id(self) -> int:
        """Used by BlockRunner to keep track of already ran blocks."""
        return id(self)

    def add_input(self, name: str, type=Any, default=NoDefault):
        """Add an input target"""
        self.inputs.update({name: Target(name, type, default)})

    def add_output(self, name: str, type=Any):
        """Add an output target"""
        self.outputs.update({name: Target(name, type)})

    def setup_targets(self):
        """
        Sets up the targets
        """
        raise NotImplementedError()

    def __lshift__(self, block: "Block") -> "Block":
        """
        Link two blocks right to left

        Example: self << block_or_list
        """
        self.add_upstream(block)
        return block

    def __rshift__(self, block: "Block") -> "Block":
        """
        Link two blocks left to right

        Example: self >> block_or_list
        """
        block.add_upstream(self)
        return block

    def __or__(self, other: "Block") -> "Block":
        return self >> other

    def run(self, *args, **kwargs):
        raise NotImplementedError()

    def add_downstream(self, downstream_block: "Block"):
        self._add_edge(self, downstream_block)

    def add_upstream(self, upstream_block: "Block"):
        self._add_edge(upstream_block, self)

    @property
    def upstream_blocks(self) -> List["Block"]:
        return self.parent_workflow.get_upstream(self)

    @property
    def downstream_blocks(self) -> List["Block"]:
        return self.parent_workflow.get_downstream(self)

    @staticmethod
    def _add_edge(
        upstream_block: "Block",
        downstream_block: "Block",
    ):
        if upstream_block.parent_workflow == downstream_block.parent_workflow:
            upstream_block.parent_workflow.digraph.add_edge(
                upstream_block, downstream_block
            )
        else:
            workflow = downstream_block.parent_workflow
            workflow.add_external_edge(upstream_block, downstream_block)
            upstream_block.add_downstream(workflow)

    def create_db_block(self):
        """Create a block in the database
        Should be manually committed
        """
        if context.db_untracked:
            from outflow.core.generic.null_object import NullObject

            return NullObject()
        else:
            from outflow.management.models.block import (
                Block as BlockModel,
            )

            json_inputs = {}
            json_outputs = {}

            for target in self.inputs.values():
                json_inputs.update(
                    {
                        target.name: {
                            "type": getattr(target.type, "__name__", None)
                            or repr(target.type),
                            "default": repr(target.default),
                        }
                    }
                )

            for target in self.outputs.values():
                json_outputs.update(
                    {
                        target.name: {
                            "type": getattr(target.type, "__name__", None)
                            or repr(target.type),
                        }
                    }
                )

            db_row = BlockModel(
                plugin=self.plugin_name,
                name=self.name,
                run=context.db_run,
                type=self.block_type,
                uuid=str(uuid4()),
                input_targets=json_inputs,
                output_targets=json_outputs,
                parent_id=None,
            )

            context.session.add(db_row)

            # if self.parent_workflow is not None:
            #     self.db_ref.children.append(db_row)

            return db_row

    @staticmethod
    def create_db_edge(
        upstream_db_block: "BlockModel", downstream_db_block: "BlockModel"
    ):
        """Create edge between blocks in database
        Should be manually committed
        """
        upstream_db_block.downstream_blocks.append(downstream_db_block)

    def check_inputs(self, block_inputs: dict, values_from_upstream: dict):
        # should raise outflow.core.exceptions.IOCheckerError if check fails
        logger.debug(f"check_inputs method not implement for block {self}")
        pass

    def bind(self, **kwargs):
        """Binds values that this task will get as inputs"""
        self.bound_kwargs.update(kwargs)

    def __call__(self, *args, **kwargs):
        raise NotImplementedError()
