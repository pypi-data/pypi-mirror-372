import sys
from pathlib import Path

from typing_extensions import Any

from environ_odoo_config.api_converter import (
    _DEFAULT,
    NOT_INI_CONFIG,
    EnumKey,
    EnvKey,
    RepeatableKey,
    SimpleCSVKey,
    SimpleKey,
)
from environ_odoo_config.converters import load_converter

if sys.version_info >= (3, 10):
    pass
else:
    pass
from string import Template

header_tmpl = Template("""= ${opt_group}

The converter `${class_name}` allow to ${class_doc} to valid odoo CLI.

include::partial$$${fname}.adoc[]

""")

field_tmpl = {
    SimpleKey: Template("""== ${init_dest}
${f_help}

TIP: $odoo_version

The environment variable `${env_key}` is used and expect a `${f_type}`.

${cli_used}
"""),
    RepeatableKey: Template("""== ${init_dest}
NOTE: ${f_help} with `${cli_used}`

The environment variable `${env_key}` is repeatable.
This mean a suffix can be added after an **single** `_`.
For example `${env_key}_value`, the suffix is `value` not `_value`

The behavior depends of the value.

* If the value is "True" then the suffix is used.
* If the value is "False" then value is discard
* If the value is not a boolean (int, float, string, csv) then the suffix is taken has value.

[,shell]
----
${env_key}="v1,v2" # <.>
${env_key}_0="v0,bar" # <.>
${env_key}_1="1" # <.>
${env_key}_FOO="True" # <.>
${env_key}_XX="bar" # <.>
----
<.> Classic csv value
<.> csv value : don't use the suffix
<.> Not a boolean value : use the value
<.> Boolean value: The suffix `FOO` is used
<.> Not a boolean value : use the value

The result (the order is not constant) will be ["v1", "v2", "v0", "foo", "bar"].

NOTE: Like csv value, all the value are deduplicated

"""),
    SimpleCSVKey: Template("""== ${init_dest}
NOTE: ${f_help} with `${cli_used}`

The environment variable `${env_key}` is used and expect a csv value.
For example `${env_key}="value1,value2"` or `${env_key}="value1"` are valid value.

The value are automaticaly deduplicated. +
`${env_key}="value1,value2"` and `${env_key}="value2,value1,value2"` are the same.

"""),
    EnumKey: Template("""== ${init_dest}
NOTE: ${f_help} with `${cli_used}`

The environment variable `${env_key}` is used and expect a `str`.
${cli_used}
${list_value}
"""),
}

special_tmpl = Template("""=== ${env_key}
NOTE: ${f_help}

The environment variable `${env_key}` is used and expect a `${f_type}`.
""")


def get_adoc(obj: Any) -> str:
    if hasattr(obj, "__adoc__"):
        return obj.__adoc__()
    return obj.__doc__


def convert_field(env_key: EnvKey[Any]):
    list_value = None
    if type(env_key) is EnumKey:
        list_value = "\n* ".join(["Possible value are:\n"] + list(env_key.py_type._value2member_map_.keys()))
    return field_tmpl[type(env_key)].substitute(
        init_dest=env_key.ini_dest,
        f_help=env_key.info.capitalize(),
        cli_used="\n* ".join(["Possible cli:\n"] + env_key.cli),
        env_key=env_key.key,
        f_type=env_key.py_type.__name__,
        list_value=list_value,
        odoo_version=get_adoc(env_key.odoo_version),
    )


converter_pages = Path(__file__).parent / Path("docs/modules/converters/pages")
partials_pages = Path(__file__).parent / Path("docs/modules/converters/partials")
for c in load_converter():
    parts = []
    doc_single_line = "convert environment variable related to " + c._opt_group.lower()
    fname = c.__module__.split(".")[-1]
    adoc_file: Path = converter_pages / (c.__module__.split(".")[-1] + ".adoc")
    if not adoc_file.exists():
        adoc_file.touch()
    if not (partials_pages / f"{fname}.adoc").exists():
        (partials_pages / f"{fname}.adoc").touch()
    parts = [
        header_tmpl.substitute(
            opt_group=c._opt_group, class_name=c.__qualname__, class_doc=doc_single_line, fname=fname
        )
    ]
    c._process_cls_fields()
    special_field = []
    for field_name, env_key in c._private_fields().items():
        if env_key.ini_dest == NOT_INI_CONFIG or env_key.cli_used() in (_DEFAULT, None):
            special_field.append((field_name, env_key))
            continue
        parts.append(convert_field(env_key))
        for other_version in env_key.other_version:
            parts.append(convert_field(other_version))
    parts.extend(["\n", "== Other keys", "\n"])
    for field_name, env_key in special_field:
        parts.append(
            special_tmpl.substitute(
                init_dest=env_key.ini_dest,
                f_help=env_key.info.capitalize(),
                cli_used="None",
                env_key=env_key.key,
                f_type=getattr(env_key.py_type, "__name__", "FFFFFFFFFFFFF"),
                odoo_version=get_adoc(env_key.odoo_version),
            )
        )
    with adoc_file.open(mode="w") as fopen:
        fopen.write("\n".join(parts))
