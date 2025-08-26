from __future__ import annotations

import abc
import os

import importlib_metadata as md
from typing_extensions import Any, List, Protocol, Type, TypeVar

from environ_odoo_config.api import Env

CONVERTER_TYPE = TypeVar("CONVERTER_TYPE", bound=Any)


class OdooConfigConverterExtension(abc.ABC):
    @abc.abstractmethod
    def apply(self, env: Env, full_config: ConfigConverterItems) -> None: ...


class ConfigConverterItems(Protocol):
    def __getitem__(self, item: Type[CONVERTER_TYPE]) -> CONVERTER_TYPE: ...


def load_converter_extensions() -> List[Type[OdooConfigConverterExtension]]:
    exclude_ = set(k.strip() for k in os.getenv("ODOO_ENV2CONFIG_EXCLUDE_CONVERTER_EXTENSIONS", "").split(",") if k)
    result: List[Type[OdooConfigConverterExtension]] = []
    for entry_point in md.entry_points().select(group="environ_odoo_config.entry_extensions"):
        # If no distro is specified, use first to come up.
        if entry_point.name in exclude_:
            continue
        result.append(entry_point.load())
    return result
