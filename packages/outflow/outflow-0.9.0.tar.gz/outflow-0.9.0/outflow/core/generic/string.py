# -*- coding: utf-8 -*-
import re

from .constants import NIST_STEPS, SI_STEPS


class MemoryValueException(Exception):
    pass


class MemoryUnitException(Exception):
    pass


def to_camel_case(snake_str):
    components = snake_str.split("_")
    # We capitalize the first letter of each component and join them together
    return "".join(s[:1].upper() + s[1:] for s in components)


def to_snake_case(camel_str):
    return_value = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", camel_str)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", return_value).lower()


def as_byte(str_value: str):
    memory_pattern = r"^(.*[0-9]\s*)([kMGTPEZY]i?)?B$"
    match = re.match(memory_pattern, str_value.strip())

    if match:
        value, unit = match.groups()
        unit = unit + "B" if unit else "B"
    else:
        raise MemoryValueException(
            f"Unexpected memory value '{str_value}'. Memory shall match the following pattern: '{memory_pattern}'"
        )

    steps = {**NIST_STEPS, **SI_STEPS}

    if unit not in steps:
        raise MemoryUnitException(
            f"Unexpected memory unit '{unit}'. Valid choices are: '{list(steps.keys())}'"
        )

    return float(value) * steps[unit]
