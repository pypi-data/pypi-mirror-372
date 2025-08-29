# -*- coding: utf-8 -*-
"""
Settings for Outflow.

Read values from the module specified by the OUTFLOW_SETTINGS_MODULE environment
variable, and then from default_settings; see the default_settings.py
for a list of all possible variables.
"""

import importlib
import typing

from outflow.core.generic.context_manager import ManagedClass

from .context_manager import PipelineContextManager

# from outflow.core.logging import logger


ENVIRONMENT_VARIABLE = "OUTFLOW_SETTINGS_MODULE"
DEFAULT_SETTINGS_MODULE = "outflow.core.pipeline.default_settings"


class Settings(ManagedClass, context_manager=PipelineContextManager):
    @staticmethod
    def resolve_lazy_object(
        settings_module: typing.Union[str, None] = DEFAULT_SETTINGS_MODULE,
    ):
        """
        Load the settings module pointed to by the environment variable. This
        is used the first time settings are needed, if the user hasn't
        configured settings manually.

        If settings_module is None, initialize an empty settings instance
        """
        return Settings(settings_module).manager.instances_by_name[
            "__pipeline_settings__"
        ]

    def __init__(self, settings_module: typing.Union[str, None]):
        """Initialize an object from the given module using only uppercase fields

        Args:
            settings_module (typing.Union[str, None]): If settings_module is None, initialize an empty settings instance
        """

        # set the name identifying the class instance in the pipeline context manager
        self.name = "__pipeline_settings__"

        if settings_module is None:
            return

        module_list = [DEFAULT_SETTINGS_MODULE]

        if settings_module != DEFAULT_SETTINGS_MODULE:
            module_list.append(settings_module)

        # update this dict using settings modules and starting with the default one
        for module in module_list:
            self.load_module(module)

    def resolve(self):
        """
        This method does nothing, it is useful to explicitly initialize the
        lazy object from the pipeline.
        """
        pass

    def load_module(self, settings_module: str):
        module = importlib.import_module(settings_module)
        # store the module in case someone later cares
        self.SETTINGS_MODULE = settings_module
        for setting in dir(module):
            # use only ALL_CAPS fields
            if setting.isupper():
                setting_value = getattr(module, setting)
                setattr(self, setting, setting_value)

    def __repr__(self):
        return f'<{self.__class__.__name__}> "id:{id(self)} - {self.SETTINGS_MODULE}"'

    def to_serializable_dict(self):
        """
        used for json serialization in database
        """
        c = self.__dict__.copy()

        # use class repr
        c["ROOT_COMMAND_CLASS"] = repr(c["ROOT_COMMAND_CLASS"])
        c["TEMP_DIR"] = c["TEMP_DIR"].as_posix()

        return c

    def __getstate__(self):
        """
        Used by slurm backend for pickle serialization on disk
        """
        return self.__dict__.copy()

    def __setstate__(self, state):
        vars(self).update(state)
