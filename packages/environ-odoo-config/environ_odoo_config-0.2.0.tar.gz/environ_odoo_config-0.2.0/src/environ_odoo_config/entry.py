from __future__ import annotations

import contextlib
import logging
import os

from typing_extensions import Any, Dict, List, Mapping, Type, TypeVar

from environ_odoo_config.api import Env, OdooCliFlag, OdooConfig, dict_to_odoo_args
from environ_odoo_config.api_converter import DEFAULT, OdooConfigConverter
from environ_odoo_config.converters import load_converter
from environ_odoo_config.converters.extensions import load_converter_extensions
from environ_odoo_config.mappers import load_mappers, load_post_mappers

_logger = logging.getLogger(__name__)
CONVERTER_TYPE = TypeVar("CONVERTER_TYPE", bound=OdooConfigConverter)


class AllOdooConfigConverter:
    def __init__(self, extra_env: Env | Mapping[str, Any] = DEFAULT, *, use_environ: bool = True) -> None:
        self._converters = dict.fromkeys(load_converter())
        self._mappers = load_mappers()
        self._post_mappers = load_post_mappers()
        self._converters: Dict[Type[OdooConfigConverter], OdooConfigConverter] = {}
        env = Env()
        if use_environ:
            env = Env(os.environ)
        if isinstance(extra_env, Mapping):
            env.update(extra_env)
        self.env = env.apply_mapper()
        for converter in load_converter():
            self._converters[converter] = converter(self.env)

        for ext in load_converter_extensions():
            ext().apply(self.env, self)

    def to_dict(self) -> OdooCliFlag:
        store_values = OdooCliFlag()
        for converter in self._converters.values():
            with contextlib.suppress(NotImplementedError):
                store_values.update(converter.to_values())
        return store_values

    def to_odoo_args(self) -> List[str]:
        return dict_to_odoo_args(self.to_dict())

    def to_config(self, config: OdooConfig) -> None:
        for converter in self._converters.values():
            with contextlib.suppress(NotImplementedError):
                converter.write_to_config(config)

    def converters(self) -> Dict[Type[OdooConfigConverter], OdooConfigConverter]:
        return self._converters

    def __getitem__(self, item: Type[CONVERTER_TYPE]) -> CONVERTER_TYPE:
        return self._converters[item]


def env_to_dict(extra_env: Dict[str, str] = None) -> OdooCliFlag:
    """
    Convert [environnement variables][os.environ] to a dict, with odoo compatible args, by applying a mapper and
     converter.
    Args:
        extra_env: A dict to update environnement variables
    Returns:
        A dict with converted environnement variables
    """
    return AllOdooConfigConverter(extra_env, use_environ=True).to_dict()


def env_to_odoo_args(extra_env: Dict[str, str] = None) -> List[str]:
    """
    Entrypoint of this library
    Convert [environnement variable][os.environ] to a odoo args valid.
    See Also
         The env to args [converter][odoo_env_config.api.EnvConfigSection]
         The speccific cloud [env mapper][odoo_env_config.mappers]
    Examples
         >>> import odoo
         >>> odoo.tools.config.parse_args(env_to_odoo_args())
         >>> odoo.tools.config.save()
    Returns:
         A list with args created from Env
    """
    return AllOdooConfigConverter(extra_env, use_environ=True).to_odoo_args()


def env_to_config(config: OdooConfig, extra_env: Dict[str, str] = None) -> None:
    AllOdooConfigConverter(extra_env, use_environ=True).to_config(config)


def _reset_odoo_tools(odoo_module):
    odoo_module.tools.config.casts = {}
    odoo_module.tools.config.misc = {}
    odoo_module.tools.config.options = {}
    odoo_module.tools.config.config_file = None
    # Copy all optparse options (i.e. MyOption) into self.options.
    for group in odoo_module.tools.config.parser.option_groups:
        for option in group.option_list:
            if option.dest not in odoo_module.tools.config.options:
                odoo_module.tools.config.options[option.dest] = option.my_default
                odoo_module.tools.config.casts[option.dest] = option

    # generate default config
    odoo_module.tools.config._parse_config()


def direct_run_command(odoo_args: List[str], config_dest: str, other_env: Env = None):
    """
    Entrypoint of the command

    1. First we parse `args`
    2. Then we load `--profiles` if some are provided
    3. And finaly we execute [odoo_env_config][odoo_env_config.entry.env_to_odoo_args] and save it to the dest file

    Args:
        odoo_module: The Odoo module imported
        force_odoo_args: Other args to pass to odoo_module config
        config_dest: The dest file to store the config generated
        other_env: The environment where the config is extracted
    """
    import odoo as odoo_module

    with contextlib.suppress(Exception):
        odoo_module.netsvc.init_logger()

    _reset_odoo_tools(odoo_module)
    global_config = AllOdooConfigConverter(other_env, use_environ=True)
    odoo_module.tools.config.config_file = config_dest
    env_args = global_config.to_odoo_args()
    _logger.info("parse Odoo environ args: %s", env_args)
    odoo_module.tools.config._parse_config(env_args)
    _logger.info("parse Odoo manual args: %s", odoo_args)
    odoo_module.tools.config._parse_config(odoo_args)
    global_config.to_config(odoo_module.tools.config)
    odoo_module.tools.config.save()
