# -*- coding: utf-8 -*-
from contextlib import contextmanager

from .command_test_case import CommandTestCase


class DatabaseCommandTestCase(CommandTestCase):
    force_dry_run = False

    def run_command(self, *args, force_dry_run=False, **kwargs):
        return super().run_command(*args, force_dry_run=force_dry_run, **kwargs)

    @contextmanager
    def pipeline_db_session(
        self,
        *args,
        db_untracked=False,
        settings_module=None,
        force_dry_run=False,
        **kwargs,
    ):
        """Create a context in which the model metadata is loaded on enter and cleaned on exit

        Yields:
            sqlalchemy.orm.Session: A session used to communicate with the configured databases
        """
        from outflow.core.pipeline import Pipeline, context

        context.db_untracked = db_untracked
        context.force_dry_run = force_dry_run

        with Pipeline(
            *args,
            settings_module=settings_module,
            force_dry_run=force_dry_run,
            **kwargs,
        ):
            yield context.session
