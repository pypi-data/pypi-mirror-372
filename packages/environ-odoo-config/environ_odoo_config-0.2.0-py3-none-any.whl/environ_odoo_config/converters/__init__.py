from __future__ import annotations

import contextlib
import os

import importlib_metadata as md
from typing_extensions import List, Type

from ..api import Env, OdooCliFlag
from ..api_converter import OdooConfigConverter


def load_converter() -> List[Type[OdooConfigConverter]]:
    exclude_ = set(k.strip() for k in os.getenv("ODOO_ENV2CONFIG_EXCLUDE_PARSER", "").split(",") if k)
    result: List[Type[OdooConfigConverter]] = []
    for entry_point in md.entry_points().select(group="environ_odoo_config.converter"):
        # If no distro is specified, use first to come up.
        if entry_point.name in exclude_:
            continue
        result.append(entry_point.load())
    return result


def apply_converter(env: Env) -> OdooCliFlag:
    """
    Apply the CONVERTER to extract the value of `env` and return all the Odoo args founded
    Args:
        env: The env to convert to OdooCliFlag

    Returns:
        All the args found by the CONVERTER
    """
    store_values = OdooCliFlag()
    for converter in load_converter():
        with contextlib.suppress(NotImplementedError):
            store_values.update(converter(env).to_values())
    return store_values
