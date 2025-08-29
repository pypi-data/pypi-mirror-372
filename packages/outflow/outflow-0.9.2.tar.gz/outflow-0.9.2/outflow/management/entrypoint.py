#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from outflow.core.pipeline import Pipeline


def entrypoint():
    with Pipeline(
        root_directory=None,
        settings_module="outflow.core.pipeline.default_settings",
        force_dry_run=True,
    ) as pipeline:
        return pipeline.run()
