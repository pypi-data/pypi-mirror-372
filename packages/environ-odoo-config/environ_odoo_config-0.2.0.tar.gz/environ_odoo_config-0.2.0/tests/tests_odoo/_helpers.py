import configparser
import os
import unittest
import uuid
from os.path import join as pjoin
from typing import Any, Dict, List, Tuple

import dotenv
from src.environ_odoo_config import api, cli, entry


def _try_find_addons_info() -> Tuple[str, int]:
    """
    Try to find the odoo path to be able to run the test inside Odoo on local host or inside a odoo docker image

    In local machine :
    1. You need to run the test in the correct odoo virtualenv
    2. Install this library with `pip install -e .` in the correct odoo virtualenv
    3. Add ODOO_VERSION equal the version you are in

    Returns:
        The absolute path of odoo-bin, the odoo version
    Raises:
        FileNotFoundError if no odoo-bin is found

    """
    current_env = api.Env(os.environ)
    odoo_version: int = current_env.odoo_version
    odoo_path = current_env.odoo_bin
    if current_env.odoo_version:
        # If the odoo-bin file not exist, maybe we are in a dev computer.
        # So we try to find where the odoo-bin is installed
        if not os.path.exists(current_env.odoo_bin):
            _base_path = "~/workspace/python/odoo/"
            odoov_path = pjoin(
                os.path.expanduser(_base_path),
                f"v{odoo_version}",
                f"odoo{odoo_version}",
                "odoo-bin",
            )
            if os.path.exists(odoov_path):
                odoo_path = odoov_path
    if not os.path.exists(odoo_path):
        raise FileNotFoundError(odoo_path)
    return odoo_path, odoo_version


def create_config(
    env_files: List[str] = None, odoo_rc: str = None, extra_odoo_args: List[str] = None
) -> configparser.ConfigParser:
    """
    This function create a config file using the subprocess launching odoo of the version

    Args:
        env_files: The profile you want to add
        odoo_rc: To force where the odoo-rc is generated
        extra_odoo_args: Extra Odoo Args you want to add instead of Env var
    Returns:
        The odoo-rc generated if success
    Raises:
        ValueError: if the subprocess calling oenv2config failed
    """
    odoo_bin_path, odoo_version = _try_find_addons_info()
    rand = str(uuid.uuid4()).split("-")[0]
    odoo_rc = odoo_rc or f"/tmp/odoo_rc-{rand}.ini"
    print("rc file in ", odoo_rc)
    if os.path.exists(odoo_rc):
        os.remove(odoo_rc)  # Remove to sure no file exist
    other_envs = api.Env({})
    for env_file in env_files or []:
        efile = pjoin(os.path.dirname(__file__), "profiles", f"{env_file}.env")
        if os.path.exists(efile):
            other_envs.update(dotenv.dotenv_values(efile))
        efile_v = pjoin(
            os.path.dirname(__file__), "profiles", f"{env_file}-{odoo_version}.env"
        )
        if os.path.exists(efile_v):
            other_envs.update(dotenv.dotenv_values(efile_v))
    res_code = entry.direct_run_command(extra_odoo_args or [], odoo_rc, other_envs)
    if res_code:
        raise ValueError("Error on launch odoo env to config")
    parser = configparser.ConfigParser()
    parser.read(odoo_rc)
    return parser


def assertParser(
    case: unittest.TestCase,
    parser: configparser.ConfigParser,
    expected_values: Dict[str, Any],
    section="options",
):
    """
    Assert the parser comparing the expectedValue.
    Do some typing converstion based on the type of the value of the key in expected_values
    If the value in `expected_values` to compare to the same key in parser is:
    - bool, the `parser.getboolean` is used with `assertEqual`
    - int, the `parser.getint` is used with `assertEqual`
    - float, the function `parser.getfloat` is used with `assertEqual`
    - List, a split on `,` if applied and `assertListEqual`
    - other `assertEqual` without conversion

    Args:
        case: The test case
        parser: The parser to assert
        expected_values: The key, value to assert
        section: If you want to assert an another section
    """
    case.assertTrue(parser)
    case.assertTrue(expected_values)
    dict_compare = {}
    for key, value in expected_values.items():
        pvalue = parser.get(section, key)
        if isinstance(value, bool):
            try:
                pvalue = parser.getboolean(section, key)
            except ValueError:
                case.fail(
                    f"{section}.{key}, not an 'boolean' value, {parser.get(section, key)}"
                )
        elif isinstance(value, int):
            try:
                pvalue = parser.getint(section, key)
            except ValueError:
                case.fail(
                    f"{section}.{key}, not an 'int' value, '{parser.get(section, key)}'"
                )
        elif isinstance(value, float):
            try:
                pvalue = parser.getfloat(section, key)
            except ValueError:
                case.fail(
                    f"{section}.{key}, not an 'float' value, {parser.get(section, key)}"
                )

        elif isinstance(value, list):
            pvalue = parser.get(section, key).split(",")
        case.assertEqual(pvalue, value, f"{section}.{key}, not equal")
        dict_compare[key] = pvalue
    case.assertDictEqual(expected_values, dict_compare)
