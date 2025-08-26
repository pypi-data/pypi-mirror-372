import logging

import odoo
import odoo.cli.command
from environ_odoo_config import cli, entry

_logger = logging.getLogger(__name__)

if odoo.release.version >= "16.0":  # Prior to 16.0, change tje cli name was buggy. Backport code
    from odoo.cli import Command as OdooCommand
else:

    class OdooCommand:
        name = None

        def __init_subclass__(cls):
            cls.name = cls.name or cls.__name__.lower()
            odoo.cli.command.commands[cls.name] = cls


def _exec(args):
    """
    Entrypoint of the command

    1. First we parse `args`
    2. Then we load `--profiles` if some are provided
    3. And finaly we execute [odoo_env_config][odoo_env_config.entry.env_to_odoo_args] and save it to the dest file

    Args:
        args: the args provided by Odoo
    """
    ns, sub_args = cli.get_odoo_cmd_parser().parse_known_args(args)
    # Removing blank sub_args
    # Is called with "$ENV_VAR" but ENV_VAR isn't set, then `sub_args` contains `['']
    # So we remove empty string from it
    sub_args = [s for s in sub_args if s.split()]
    entry.direct_run_command(sub_args, ns.config_dest)


class _GenerateConfig(OdooCommand):
    """
    Convert Environ variable to odoo config save it to `--dest` or `$ODOO_RC`
    """

    # The attribute EnvironConfigGenerate (exactly the same of the current class name) is for old odoo version
    name = "generate-config"

    def run(self, args):
        return _exec(args)


class _Env2Config(OdooCommand):
    """
    Deprecated alias of `generate-config`
    """

    # The attribute EnvironConfigGenerate (exactly the same of the current class name) is for old odoo version
    name = "envconfig"

    def run(self, args):
        return _exec(args)


class _OEnv2Config(OdooCommand):
    """
    Deprecated alias of `generate-config`
    """

    # The attribute EnvironConfigGenerate (exactly the same of the current class name) is for old odoo version
    name = "oenv2config"

    def run(self, args):
        return _exec(args)


class _ConfigShow(OdooCommand):
    """
    Display the config with pprint.pformat
    """

    name = "config_show"

    def run(self, args):
        from pprint import pformat

        _logger.error("Config :")
        odoo.tools.config.parse_config(args)
        _logger.info("Config %s\n", pformat(self.odoo_module.tools.config.options))
        _logger.info("Misc Config %s\n", pformat(self.odoo_module.tools.config.misc))
