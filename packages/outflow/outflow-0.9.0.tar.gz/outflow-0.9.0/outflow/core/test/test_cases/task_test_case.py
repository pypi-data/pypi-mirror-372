# -*- coding: utf-8 -*-
import pytest
from outflow.core.pipeline import context
from outflow.core.pipeline.context_manager import PipelineContextManager
from outflow.core.workflow import Workflow


class TaskTestCase:
    """
    The TaskTestCase class is designed to be overridden in derived classes to create unit tests for tasks.

    Example:
        class TestMyPluginTasks(TaskTestCase):
            def test_task1(self):
                # --- initialize the task ---
                from my_plugin import task1
                from outflow.core.pipeline import config

                self.task = task1()

                config["tasks"] = {
                    "my_task_name": {
                        "param_a": "aaaaaa",
                        "param_b": "bbbb",
                    }
                }

                # --- run the task ---

                result = self.run_task(target_a='my_data', target_b='my_data')

                # --- make assertions ---

                # test the result
                result == 'my_result'

                # (...)

            def test_task2(self):
                # --- initialize the task ---
                from my_plugin import task2

                self.task = task2()

                # (...)
    """

    @pytest.fixture(autouse=True)
    def with_pipeline_context_manager(self):
        with PipelineContextManager():
            context.db_untracked = True
            context.force_dry_run = True
            with Workflow():
                yield

    def setup_method(self):
        """
        Setup the pipeline before each test
        :return:
        """

        # reset the task
        self.task = None

    def teardown_method(self):
        pass

    def run_task(self, *args, **kwargs):
        if self.task is None:
            raise ValueError("The task has not been initialized")

        return self.task(*args, block_db=None, **kwargs)
