from __future__ import annotations

import enum
import logging
import os
import typing
from collections import OrderedDict
from typing import Any, TypeVar

from typing_extensions import (
    Dict,
    List,
    Mapping,
    Protocol,
    Self,
    Tuple,
    Type,
    Union,
    cast,
)

from . import utils
from .mappers import apply_mapper

if typing.TYPE_CHECKING:
    from .api_converter import OdooConfigConverter

_logger = logging.getLogger(__name__)
SHORTCUT_CLI_LENGHT = 2  # Lenght of 1 dash and 1 lettre for cli. `-i` or `-d`


ET = TypeVar("ET", bound=enum.Enum)


@enum.unique
class OdooVersion(enum.IntEnum):
    NO_VERSION = 0  # Special value
    # V11 = 11
    V12 = 12
    V13 = 13
    V14 = 14
    V15 = 15
    V16 = 16
    V17 = 17
    V18 = 18

    def max(self) -> OdooVersionRange:
        return OdooVersionRange(vmin=OdooVersion.V12, vmax=self)

    def min(self) -> OdooVersionRange:
        return OdooVersionRange(vmin=self, vmax=OdooVersion.V18)


class OdooVersionRange:
    def __init__(self, *, vmin: OdooVersion = OdooVersion.V12, vmax: OdooVersion = OdooVersion.V18) -> None:
        self._min = vmin
        self._max = vmax

    def is_valid(self, version: OdooVersion) -> bool:
        return self._min <= version <= self._max

    def __adoc__(self) -> str:
        if self._min == self._max:
            return f"Only Odoo version {float(self._min.value)} is supported"
        return f"Supported Odoo version from {float(self._min.value)} until {float(self._max.value)}"


TYPE_CONVERTER = TypeVar("TYPE_CONVERTER", bound="OdooConfigConverter")


class Env(dict, Mapping[str, str]):
    def copy(self) -> Self:
        return Env(self)

    @property
    def odoo_version(self) -> int:
        """
        Returns:
            `env:ODOO_VERSION` as [int][int]
        """
        return self.odoo_version_type.value

    @property
    def odoo_version_type(self) -> OdooVersion:
        """
        Returns:
            `env:ODOO_VERSION` as OdooVersion
        """
        int_version = self.get_int("ODOO_VERSION")
        return OdooVersion(min(int_version, OdooVersion.V18.value))

    @property
    def main_instance(self) -> bool:
        """
        Returns:
            `True` if `instance_number` `==` `0`
        """
        return self.instance_number == 0

    @property
    def instance_number(self) -> int:
        """
        Returns:
            `env:INSTANCE_NUMBER`
        """
        return self.get_int("INSTANCE_NUMBER")

    @property
    def odoo_bin(self) -> str:
        """
        Returns:
            The `env:ODOO_BIN` or `/odoo/bin` path even if not exist
        """
        return self.get("ODOO_BIN", os.path.join("/odoo", "odoo-bin"))

    def mutate(self, *arg, **kwargs) -> Self:
        """
        Same as [dict.update][dict.update] but return `self`
        Returns:
            current self after the `update`
        """
        self.update(*arg, **kwargs)
        return self

    def get_bool(self, *keys: str, default: bool = False) -> bool:
        return utils.to_bool(self.gets(*keys, default=str(default)))

    def get_int(self, *keys: str, default: int = 0) -> int:
        return utils.to_int(self.gets(*keys, default=str(default)))

    def get_converter(self, converter: Type[TYPE_CONVERTER]) -> TYPE_CONVERTER:
        return converter(self)

    def apply_mapper(self) -> "Env":
        return apply_mapper(self)

    def get_enum(self, key: str, enum_type: Type[ET], *, default: ET) -> ET:
        value = self.get(key)
        if not value or value not in enum_type.__members__:
            return default
        return enum_type[value]

    def is_boolean(self, *keys: str) -> bool:
        return utils.is_boolean(self.gets(*keys))

    def get_list(self, key: str, separator=",", allow_duplicate: bool = False) -> List[str]:
        value = self.get(key)
        if self.is_boolean(key) and not self.get_bool(key):
            return []
        if not value:
            return []
        if allow_duplicate:
            return [u.strip() for u in value.strip().split(separator)]
        res = OrderedDict()
        for value in value.strip().split(separator):
            res[value.strip()] = None
        return list(res.keys())

    def gets(self, *keys: str, default: str = None, none_if_false: bool = True) -> Union[str, None]:
        """
        Returns:
            The first not false value found from keys (in keys orders) or the default
        """
        return utils.get_value(self, *keys, default=default, if_all_falsy_return_none=none_if_false)

    def get_start_with(self, prefix) -> List[Tuple[str, str]]:
        result = {}
        for key, value in self.items():
            if key.startswith(prefix):
                result[key[len(prefix) :]] = value
        return cast(List[Tuple[str, str]], list(result.items()))

    def __add__(self, other: Mapping[str, Any]) -> "Env":
        result = self.copy()
        result.update(other)
        return result


class OdooCliFlag(dict, Mapping[str, Any]):
    def set(self, key: str, value: Any, force_set: bool = False) -> Self:
        if value or force_set:
            self[key] = value
        return self

    def set_all(self, values: Dict[str, Any], force_set: bool = False) -> Self:
        for key, value in values.items():
            self.set(key, value, force_set)
        return self


def dict_to_odoo_args(values: Dict[str, Any]) -> List[str]:
    result = []
    clean_values = utils.DictUtil.clean_none_env_value(values)
    clean_values = utils.DictUtil.clean_dict(clean_values)
    for key, value in clean_values.items():
        if not value:
            continue
        key = utils.add_dash(key)
        if value == str(True):
            result.append(key)
        else:
            result.append(f"{key}={value}")
    return result


class OdooConfig(Protocol):
    options: Dict[str, Any]
    misc: Dict[str, Dict[str, Any]]

    def set_admin_password(self, value: str): ...

    def get(self, key, default=None): ...

    def pop(self, key, default=None): ...

    def get_misc(self, sect, key, default=None): ...

    def __setitem__(self, key, value): ...

    def __getitem__(self, key): ...


class OdooConfigConverterProtocole(Protocol):
    """
    Base class for section
    A section is a part of the CLI of Odoo
    It takes an env and return the odoo cli flags
    """

    def init(self, curr_env: Env) -> Self:
        return self

    def to_values(self) -> OdooCliFlag:
        raise NotImplementedError("Not implemented in this section {}".format(type(self).__name__))

    def write_to_config(self, config: OdooConfig):
        raise NotImplementedError()


odoo_log_levels = [
    "info",
    "debug_rpc",
    "warn",
    "test",
    "critical",
    "runbot",
    "debug_sql",
    "error",
    "debug",
    "debug_rpc_answer",
    "notset",
]
