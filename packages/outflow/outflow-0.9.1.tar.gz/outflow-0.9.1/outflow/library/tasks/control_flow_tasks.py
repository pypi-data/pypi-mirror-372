# -*- coding: utf-8 -*-
from typing import Callable

from outflow.core.exceptions import IOCheckerError
from outflow.core.tasks import Task
from outflow.core.types import Skipped


class IdentityTask(Task):
    """Important : when implementing an IdentityTask, make sure the self.run()
    function ends with `return kwargs`
    TODO: Change the name of this task because it is not really an "identity" as we are allowed to mutate kwargs
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def setup_targets(self):
        pass

    def add_upstream(self, upstream_block: "Block"):
        super().add_upstream(upstream_block)
        self.copy_targets(upstream_block)

    def copy_targets(self, block: "Block"):
        self.inputs.update(block.outputs)
        self.outputs.update(block.outputs)

    # def __call__(self, *args, **kwargs):
    #     return super().__call__(*args, **kwargs)

    def run(self, **kwargs):
        return kwargs


class ConditionalTask(IdentityTask):
    def __init__(self, condition: Callable, *args, **kwargs):
        super().__init__(**kwargs)
        self._condition = condition

    def condition(self, **kwargs):
        return self._condition(**kwargs)


class ThenTask(ConditionalTask):
    def run(self, **kwargs):
        if not self.condition(**kwargs):
            for downstream_block in self.downstream_blocks:
                downstream_block.skip = True

        return super().run(**kwargs)


class ElseTask(ConditionalTask):
    def run(self, **kwargs):
        if self.condition(**kwargs):
            for downstream_block in self.downstream_blocks:
                downstream_block.skip = True

        return super().run(**kwargs)


class IfTask(IdentityTask):
    pass


def IfThenElse(condition: Callable, name: str = "ConditionalTask"):
    # subclass if/else task to avoid edge effects with targets and other class attributes
    if_task = type("If" + name, (IfTask,), {})()
    then_task = type("Then" + name, (ThenTask,), {})(condition)
    else_task = type("ElseNot" + name, (ElseTask,), {})(condition)
    if_task >> then_task
    then_task.inputs = if_task.inputs
    then_task.outputs = if_task.outputs
    if_task >> else_task
    else_task.inputs = if_task.inputs
    else_task.outputs = if_task.outputs

    return if_task, then_task, else_task


class MergeTask(IdentityTask):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.skip_if_upstream_skip = False

    def __call__(self, *args, **kwargs):
        if all(upstream.skip for upstream in self.upstream_blocks):
            self.skip = True

        return super().__call__(*args, **kwargs)

    def run(self, **kwargs):
        not_none_inputs = {
            key: val
            for key, val in kwargs.items()
            if val is not None and not isinstance(val, Skipped)
        }

        stripped_return_dict = {}

        # TODO: maybe check if all inputs start with the same name

        for output in self.outputs:
            for input_name, input_val in not_none_inputs.items():
                if input_name.endswith(output):
                    stripped_return_dict.update({output: input_val})

        return stripped_return_dict

    def check_inputs(self, task_inputs, values_from_upstream):
        # TODO test if still working

        inputs_ok = []
        for output in self.outputs:
            for input_name, input_val in task_inputs.items():
                if input_name.endswith(output):
                    inputs_ok.append(input_name)

        if len(inputs_ok) != len(task_inputs.items()):
            raise IOCheckerError(
                "Task {} did not get all expected inputs: expected {}, got {}".format(
                    self.name,
                    [k for k in self.inputs.keys()],
                    {{**values_from_upstream, **task_inputs.keys()}},
                )
            )
