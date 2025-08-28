"""
Python file containing all the function used by the cli.
`odoo_env_confi` expose a script command when installed.
>>> odoo - env2config - h

This command allow to run this libraray inside an odoo command (See `odoo.cli.Command`
"""

import argparse
import logging
import os

from . import entry


def init_logger():
    _logger_level = getattr(logging, os.environ.get("NDP_SERVER_LOG_LEVEL", "INFO"), logging.INFO)
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(logging.StreamHandler())


class SplitArgs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # start or ending comma removed to avoid empty value in list
        setattr(
            namespace,
            self.dest,
            getattr(namespace, self.dest, []) + list(filter(None, values.split(","))),
        )


def get_odoo_cmd_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--dest", dest="config_dest", help="Path to odoo configuration file", default="odoo-config.ini")
    return p


def env_to_config():
    # add_help=False otherwise conflict with -h parameter of parent parser
    parser = get_odoo_cmd_parser()
    ns, other = parser.parse_known_args()
    parser.exit(entry.direct_run_command(other, ns.config_dest))
