from pathlib import Path
from typing import Set

from environ_odoo_config.api import OdooVersion, OdooVersionRange
from environ_odoo_config.api_converter import NOT_INI_CONFIG, OdooConfigConverter, OnlyCli, RepeatableKey, SimpleKey
from environ_odoo_config.utils import if_not_none


class ConfigConverterTest(OdooConfigConverter):
    """
    convert environment variable related the tests configuration
    """

    _opt_group = "Test Configuration"

    test_enable_filled: bool = SimpleKey("TEST_ENABLE", from_environ_value=if_not_none, ini_dest=NOT_INI_CONFIG)
    test_enable: bool = SimpleKey("TEST_ENABLE", cli="--test-enable", info="Enable unit tests.")
    test_file: Path = SimpleKey("TEST_FILE", cli="--test-file", info="Launch a python test file.")
    test_tags: Set[str] = RepeatableKey(
        "TEST_TAGS",
        cli="--test-tags",
        info="""Comma-separated list of specs to filter which tests to execute. Enable unit tests if set.
        A filter spec has the format: [-][tag][/module][:class][.method][[params]]
        The '-' specifies if we want to include or exclude tests matching this spec.
        The tag will match tags added on a class with a @tagged decorator
        (all Test classes have 'standard' and 'at_install' tags
        until explicitly removed, see the decorator documentation).
        '*' will match all tags.
        If tag is omitted on include mode, its value is 'standard'.
        If tag is omitted on exclude mode, its value is '*'.
        The module, class, and method will respectively match the module name, test class name and test method name.
        Example: --test-tags :TestClass.test_func,/test_module,external
        It is also possible to provide parameters to a test method that supports them
        Example: --test-tags /web.test_js[mail]
        If negated, a test-tag with parameter will negate the parameter when passing it to the test
        Filtering and executing the tests happens twice: right
        after each module installation/update and at the end
        of the modules loading. At each stage tests are filtered
        by --test-tags specs and additionally by dynamic specs
        'at_install' and 'post_install' correspondingly.""",
        odoo_version=OdooVersionRange(vmin=OdooVersion.V12),
    )
    screencasts: Path = OnlyCli(
        "--screencasts", info="Screencasts will go in DIR/{db_name}/screencasts.", odoo_version=OdooVersion.V13.min()
    )
    screenshots: Path = OnlyCli(
        "--screenshots", info="Screenshot will go in DIR/{db_name}/screencasts.", odoo_version=OdooVersion.V13.min()
    )
