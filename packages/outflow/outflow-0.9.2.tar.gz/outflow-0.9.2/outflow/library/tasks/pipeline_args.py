# -*- coding: utf-8 -*-
from typing import Union, Iterable

from outflow.core.pipeline import context
from outflow.core.target import Target
from outflow.core.tasks import Task


class PipelineArgs(Task):
    def __init__(self, only: Union[None, Iterable] = None, **kwargs):
        """Task used to extract the pipeline arguments and pass them to the next task

        Args:
            only (Union[None, Iterable], optional): If specified, create targets only for the pipeline arguments listed. Defaults to None.
        """
        self.only_kwargs = only
        super().__init__(**kwargs)

    def setup_targets(self):
        """Update target outputs using pipeline arguments

        Args:
            only (Union[None, Iterable], optional): If specified, create targets only for the pipeline arguments listed. Defaults to None.
        """
        self.outputs = {}

        keys = vars(context.args) if self.only_kwargs is None else self.only_kwargs

        for key in keys:
            self.outputs.update({key: Target(name=key)})

    def run(self):
        """Return the pipeline arguments as task outputs"""
        pipeline_args = {}

        # return value using the pipeline args
        for key in self.outputs:
            pipeline_args[key] = getattr(context.args, key)
        return pipeline_args

    def check_inputs(self, *args, **kwargs):
        pass
