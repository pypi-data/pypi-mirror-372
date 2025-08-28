# -*- coding: utf-8 -*-
from typing import Any, NewType


class Skipped:
    pass


def outputs_type_factory(type_dict: dict):
    return type_dict


_outflow_map_iterator_prefix = "_OutflowMapIterator__"
_outflow_parameter_prefix = "_OutflowParameter__"


def IterateOn(iterable_target_name, input_type=Any, **kwargs):
    import warnings

    warnings.warn(
        "IterateOn is deprecated, use 'map_on' parameter of MapWorkflow instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    return NewType(
        _outflow_map_iterator_prefix + iterable_target_name,
        kwargs.get("type", input_type),
    )


IterateOn.prefix = _outflow_map_iterator_prefix


def Parameter(parameter_type=Any, **kwargs):
    return NewType(
        _outflow_parameter_prefix,
        kwargs.get("type", parameter_type),
    )


Parameter.prefix = _outflow_parameter_prefix
