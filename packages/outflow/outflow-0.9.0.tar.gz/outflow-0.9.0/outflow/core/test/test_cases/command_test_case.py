# -*- coding: utf-8 -*-
import pathlib

import pytest
from outflow.core.commands import RootCommand
from outflow.core.pipeline import Pipeline, context, settings
from outflow.core.pipeline.context_manager import PipelineContextManager


class CommandTestCase:
    """
    The CommandTestCase class is designed to be overridden in derived classes to create unit tests for commands.

    Example:
        class TestMyPluginCommands(CommandTestCase):
            def test_sub_command1(self):

                # --- create some fake data ---

                value1 = 'value1'
                value2 = 'value2'

                # --- initialize the command ---

                self.root_command_class = MyRootCommand


                arg_list = ['my_sub_command',
                            '--my_option1', value1,
                            '--my_option2', value2]

                # --- run the command ---

                return_code, result = self.run_command(arg_list)

                # --- make assertions ---

                # test the result
                assert return_code == 0
                assert result == {}

                # (...)
    """

    PLUGINS = ["outflow.management"]
    force_dry_run = True

    def setup_method(self):
        """
        Setup the pipeline before each test
        :return:
        """
        # reset the command
        self.root_command_class = None

    @pytest.fixture(autouse=True)
    def setup_within_pipeline_context(self, with_pipeline_context_manager):
        settings.PLUGINS = self.PLUGINS
        settings.TEMP_DIR = pathlib.Path(__file__).parent.resolve() / ".outflow_tmp"

    @pytest.fixture(autouse=True)
    def with_pipeline_context_manager(self):
        with PipelineContextManager():
            context.force_dry_run = self.force_dry_run
            yield

    def teardown_method(self):
        pass

    def run_command(self, arg_list=[], force_dry_run=None, **kwargs):
        settings.ROOT_COMMAND_CLASS = (
            RootCommand if self.root_command_class is None else self.root_command_class
        )

        if force_dry_run is not None:
            self.force_dry_run = force_dry_run

        with Pipeline(
            root_directory=None,
            settings_module=None,
            argv=arg_list,
            force_dry_run=self.force_dry_run,
            **kwargs,
        ) as pipeline:
            return_code = pipeline.run()

        return return_code, pipeline.result
