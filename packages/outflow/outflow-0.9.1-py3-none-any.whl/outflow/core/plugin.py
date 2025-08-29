#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import inspect
import pathlib
import pkgutil
import sys

from outflow.core.logging import logger


class PluginError(Exception):
    """
    Errors related to plugin loading and definitions.
    """


class Plugin:
    """
    Class to manage plugins module of the pipeline.
    """

    @staticmethod
    def _check_and_load_module(*, plugin_name, plugin_path, module):
        """
        Check if a module inside the plugin is importable.
        """
        # name for loading
        name = ".".join([plugin_name, module])

        try:
            if module == "models":
                Plugin.import_models_submodules(plugin_name)
            else:
                # WIP fix database
                importlib.import_module(name)

            logger.debug(f"Module {name} successfully imported")
            return True
        except ImportError as ie:
            if (plugin_path / (module + ".py")).is_file() or (
                plugin_path / module / "__init__.py"
            ).is_file():
                raise
            logger.debug(
                f"Module {module} does not exist for plugin {plugin_name} in {plugin_path}: {ie}"
            )
            return False

    @staticmethod
    def load(plugin_name):
        """
        Check the plugin integrity and import the commands.
        """
        try:
            plugin_path = Plugin.get_path(plugin_name)
            logger.debug(f"Loading plugin '{plugin_name}' from '{plugin_path}' ...")
        except PluginError as e:
            raise PluginError(
                f"The '{plugin_name}' plugin could not be imported. "
                "Check the plugin list in the settings file. "
                "Maybe you forgot the namespace? "
                "Is the plugin properly installed?"
            ) from e
        logger.debug("checking commands, tasks and models...")
        plugin_content = ["models", "commands", "tasks"]
        content = list()
        for module in plugin_content:
            content.append(
                Plugin._check_and_load_module(
                    plugin_name=plugin_name, plugin_path=plugin_path, module=module
                )
            )
        if True not in content:
            raise PluginError(
                "An outflow plugin must contain at least one of "
                f"the following modules to be useful : {plugin_content}"
            )

    @staticmethod
    def get_path(plugin_name):
        try:
            return pathlib.Path(
                importlib.import_module(plugin_name).__file__
            ).parent.resolve()
        except ImportError as e:
            logger.print_exception(
                "Cannot find plugin {0}:".format(
                    plugin_name,
                )
            )
            raise PluginError(e)

    @staticmethod
    def import_models_submodules(plugin_name: str):
        """Import each models of the plugin

        Args:
            plugin_name (str): the plugin name
        """
        from outflow.core.db import Model
        from outflow.core.pipeline import context

        def is_model(obj):
            return inspect.isclass(obj) and issubclass(obj, Model) and obj is not Model

        models_dir_path = Plugin.get_path(plugin_name) / "models"

        models_module_name = plugin_name + ".models"

        importlib.import_module(models_module_name)

        model_classes = inspect.getmembers(sys.modules[models_module_name], is_model)

        for module_loader, name, is_pkg in pkgutil.iter_modules(
            [str(models_dir_path.resolve())]
        ):
            submodule_name = models_module_name + "." + name

            # ensure the module is imported
            importlib.import_module(submodule_name)

            # inspect the module to get all the model classes defined inside
            model_classes.extend(
                inspect.getmembers(sys.modules[submodule_name], is_model)
            )

        if context._models is None:
            context._models = []

        # return model classes in the pipeline context
        for name, model in set(model_classes):
            context._models.append(model)


def get_plugin_name():
    """
    Inspects frame stack to extract plugin_name.

    Returns:

    """
    frame = inspect.currentframe()
    plugin_name = None
    while frame is not None:
        frame = frame.f_back
        if frame:
            plugin_name = frame.f_locals.get("plugin_name", None)
            if plugin_name:
                break

    return plugin_name
