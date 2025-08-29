# -*- coding: utf-8 -*-
from ..generic.serializable_proxy import SerializableProxy

config = SerializableProxy()
context = SerializableProxy()
settings = SerializableProxy()

from .lazy_config import Config  # noqa: E402
from .lazy_context import PipelineContext  # noqa: E402
from .lazy_settings import Settings  # noqa: E402

config.set_factory(Config.resolve_lazy_object)
context.set_factory(PipelineContext)
settings.set_factory(Settings.resolve_lazy_object)

from .pipeline import (  # noqa: F401, E402
    Pipeline,
    get_pipeline_states,
    set_pipeline_state,
)
