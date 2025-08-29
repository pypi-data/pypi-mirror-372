# -*- coding: utf-8 -*-
"""
Lazy Config for Outflow.

Read values from the file specified by the OUTFLOW_CONFIG_PATH environment variable
"""

import json
import os
from copy import deepcopy
from pathlib import Path

import toml
import yaml
from outflow.core.generic.context_manager import ManagedClass
from outflow.core.logging import default_config as default_logger_config

# from yamlinclude import YamlIncludeConstructor
from yaml_include import Constructor

from .context_manager import PipelineContextManager

# YamlIncludeConstructor.add_to_loader_class(loader_class=yaml.SafeLoader)
yaml.add_constructor("!include", Constructor(), yaml.SafeLoader)

ENVIRONMENT_VARIABLE = "OUTFLOW_CONFIG_PATH"


class DictLikeMixin:
    """Define methods to use the config objects like dictionaries"""

    def __getitem__(self, key):
        """Override the [] to be able to use both 'config.key' and 'config["key"]'

        Args:
            key (string): The key used to retrieve the config value
        """
        return self.__getattribute__(key)

    def __setitem__(self, key, value):
        """Setter for keys USE WITH CAUTION AS IT MIGHT BREAK OUTFLOW"""
        self.__setattr__(key, value)

    def get(self, key, default=None):
        """Return the value for the specified key if key is in dict like object, if not, return the default value."""
        try:
            return self.__getitem__(key)
        except AttributeError:
            return default

    def __contains__(self, key):
        return hasattr(self, key)

    def update(self, values):
        for key, value in values.items():
            self[key] = value


class Config(ManagedClass, DictLikeMixin, context_manager=PipelineContextManager):
    @staticmethod
    def resolve_lazy_object():
        """
        Load the config file pointed to by the environment variable. This
        is used the first time config is needed.
        """
        from outflow.core.pipeline import settings

        # logger.debug("Resolving the LazyConfig object")

        config_filepath = os.environ.get(ENVIRONMENT_VARIABLE)
        if not config_filepath:
            if settings.ROOT_DIRECTORY is None:
                config_filepath = None
            else:
                # check for the default config file
                for ext in ["json", "yml", "yaml", "toml"]:
                    filepath = Path(settings.ROOT_DIRECTORY) / f"config.{ext}"
                    if filepath.exists():
                        config_filepath = filepath
                        break
        else:
            config_filepath = Path(config_filepath)

        return Config(config_filepath)

    def __init__(self, config_filepath_or_dict):
        self.name = "__pipeline_config__"
        self._CONFIG_FILEPATH = None

        if isinstance(config_filepath_or_dict, dict):
            self.init_from_dict(config_filepath_or_dict)
        else:
            self.init_from_file(config_filepath_or_dict)

    def resolve(self):
        """
        This method does nothing, it is useful to explicitly initialize the
        lazy object from the pipeline.
        """
        pass

    def init_from_dict(self, config_dict):
        for key in config_dict:
            config_value = config_dict[key]
            self.__setattr__(key, config_value)

    def init_from_file(self, config_filepath):
        # store the config filepath in case someone later cares
        self._CONFIG_FILEPATH = config_filepath

        if config_filepath and config_filepath.exists():
            with open(config_filepath, "r") as f:
                # read the file into memory as a string to avoid re-reading.
                config_file_content = f.read()
        else:
            config_file_content = "{}"

        load_functions = {
            "json": json.loads,
            "yaml": yaml.safe_load,
            "yml": yaml.safe_load,
            "toml": toml.loads,
        }

        default_config = {"logging": default_logger_config}
        custom_config = {}

        if config_filepath is not None:
            suffix = config_filepath.suffix[1:]  # remove dot

            if suffix not in load_functions:
                raise Exception(f"Unsupported config file {config_filepath}")

            custom_config = load_functions[suffix](config_file_content)

        config_dict = {
            **default_config,
            **custom_config,
            "logging": default_logger_config,
        }

        default_database_config = {"dialect": "sqlite", "path": "outflow.db"}

        config_dict.setdefault("databases", {})

        if "default" not in config_dict["databases"]:
            config_dict["databases"]["default"] = default_database_config

        for field in ["formatters", "loggers", "handlers"]:
            try:
                config_dict["logging"][field].update(custom_config["logging"][field])
            except KeyError:
                continue

        self.init_from_dict(config_dict)

    def __repr__(self):
        # skip private keys
        # dct = {
        #     key: value
        #     for key, value in self.__dict__.items()
        #     if not key.startswith("_")
        # }
        return (
            f'<{self.__class__.__name__} "{self._CONFIG_FILEPATH.as_posix() if self._CONFIG_FILEPATH else "Default"}"\n'
            # f"{pprint.pformat(dct)}>"
        )

    def to_serializable_dict(self):
        """
        This sanitize config object for json serialization, remove passwords
        from database config and remove non serializable attributes
        """
        c = deepcopy(self.__dict__)

        # cast from PosixPath to string
        c["_CONFIG_FILEPATH"] = str(c.get("_CONFIG_FILEPATH", None))

        return c

    @staticmethod
    def sanitize(config_dict):
        # remove database passwords
        for db_name, db in config_dict.get("databases", {}).items():
            if db["dialect"] == "postgresql":
                adm = db.get("admin", None)
                if adm:
                    config_dict["databases"][db_name]["admin"] = adm.replace(
                        adm.split(":")[1], "******"
                    )
                usr = db["user"]
                config_dict["databases"][db_name]["user"] = usr.replace(
                    usr.split(":")[1], "******"
                )

        sanitized_secrets = Config.recursively_remove_secrets(
            config_dict.get("secrets", {})
        )

        config_dict["secrets"] = sanitized_secrets

        return config_dict

    @staticmethod
    def recursively_remove_secrets(secrets_dict):
        if isinstance(secrets_dict, dict):
            return {
                key: Config.recursively_remove_secrets(val)
                for key, val in secrets_dict.items()
            }
        else:
            return "******"

    def __getstate__(self):
        return self.to_serializable_dict()

    def __setstate__(self, state):
        vars(self).update(state)
        self._CONFIG_FILEPATH = Path(self._CONFIG_FILEPATH)
