#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
import sys

from outflow.core.pipeline import Pipeline

if __name__ == "__main__":
    pipeline_root_directory = Pipeline.get_parent_directory_posix_path(__file__)
    # add plugins to the python path
    # note: for cython like plugins, the compilation step is required and
    # plugin installation via pip is strongly encouraged
    plugins_dir = pathlib.Path(__file__).parent / "plugins"
    for plugin_path in plugins_dir.glob("*"):
        sys.path.append(plugin_path.resolve().as_posix())

    with Pipeline(root_directory=pipeline_root_directory) as pipeline:
        exit(pipeline.run())
