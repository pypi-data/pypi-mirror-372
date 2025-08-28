import warnings
from collections import OrderedDict
from typing import Any, Collection, Dict, List, Optional, Set, Union

BOOL_ACCEPTED_VALUE: Set[str] = {str(1), str(0), str(True), str(False), "Yes", "No"}
BOOL_ACCEPTED_VALUE |= {a[0] for a in BOOL_ACCEPTED_VALUE}
BOOL_ACCEPTED_VALUE |= {a.lower() for a in BOOL_ACCEPTED_VALUE}
_FLOAT_PART = 2


def to_bool(anything: Union[Any, None]) -> bool:
    """
    Convert `anything` to a [bool][bool] according to [os.environ][os.environ] most found _True_ value.
    Args:
        anything: The value to convert
    Returns:
        `True` if `anything` in `True`, `"True"` `"1"`  otherwise `False`
    Notes:
        If the value is a string, then this is case **insensitive**
    Examples:
        >>> is_true("")
        False
        >>> is_true("True")
        True
        >>> is_true("TRUE")
        True
        >>> is_true("true")
        True
        >>> is_true("trUE")
        True
        >>> is_true("0")
        False
        >>> is_true("1")
        True
        >>> is_true([1, 2])
        False
        >>> is_true({"key": "value"})
        False
        >>> is_true((1, 2, 3))
        False

    """
    if not anything or not isinstance(anything, (str, bool, int, float)):
        return False
    return (
        bool(anything)
        and (str(anything).isdigit() and bool(int(anything)))
        or (str(anything).capitalize() == str(True))
        or False
    )


def is_boolean(anything: Union[Any, None]) -> bool:
    """
    Return `True` if the value is a boolean value.
    Args:
        anything: The value to test
    Returns:
        `True` if `anything` can be considered as a boolean value
    Notes:
        If the value is a string, then this is case **insensitive**
    Examples:
        >>> is_boolean("") or is_boolean(" ") or is_boolean(None)
        False
        >>> is_boolean("True") and is_boolean("true") and is_boolean("TrUe") and is_boolean("TRUE")
        True
        >>> is_boolean("False") and is_boolean("false") and is_boolean("FalSe") and is_boolean("FALSE")
        True
        >>> is_boolean("Yes") and is_boolean("Y") and is_boolean("y") and is_boolean("yes") and is_boolean("yES")
        True
        >>> is_boolean("No") and is_boolean("NO") and is_boolean("no") and is_boolean("n") and is_boolean("N")
        True
        >>> is_boolean("T") and is_boolean("t") and is_boolean("F") and is_boolean("F")
        True
        >>> is_boolean(1) and is_boolean(1) and is_boolean(0) and is_boolean("1") and is_boolean("0")
        True
        >>> is_boolean(2) or is_boolean(-1)
        False
        >>> is_boolean("Vrai") or is_boolean("Faux") or is_boolean("FauX") or is_boolean("VRai")
        False
        >>> is_boolean("V") or is_boolean("v")
        False
        >>> is_boolean(True) and is_boolean(False)
        True
    """
    return str(anything).lower() in BOOL_ACCEPTED_VALUE


def is_true(anything: Union[Any, None]) -> bool:
    """
    Deprecated, the name is confusing, with the new function `is_bool`
     Args:
        anything: The value to convert
    Returns:
        `True` if `anything` in `True`, `"True"` `"1"`  otherwise `False`
    Notes:
        If the value is a string, then this is case **insensitive**
        Any value that is not converted to True will be False
    """
    warnings.warn("Use to_bool instead", category=DeprecationWarning, stacklevel=2)
    return to_bool(anything)


def to_int(anything: Union[Any, None]) -> int:
    return int(to_float(anything))


def to_float(anything: Union[Any, None]) -> float:
    """
    Convert `anything` to a [int][int] according to [os.environ][os.environ] most found _int_ value.
    Args:
        anything: The value to convert
    Returns:
        the value as `int`, otherwise `0`
    Notes:
        If a float is given, then a hard convert to [int][int] is done. See Examples.
    Examples:
        >>> to_int("0") == 0
        True
        >>> to_int("0.0") == 0.0
        True
        >>> to_int("0.5") == 0.5
        True
        >>> to_int("0.5") == 0.5
        True
        >>> to_int(True) == 0
        True
        >>> to_int("True") == 0
        True
        >>> to_int([1, 2])
        0
        >>> to_int({"key": "value"})
        0
        >>> to_int((1, 2, 3))
        0
        >>> to_int(10)
        10
        >>> to_int("10")
        10

    """
    if anything is None:
        return 0.0
    # Keep isinstance(anything, bool) before isinstance(anything, int).
    # bool are int
    if isinstance(anything, bool):
        return 0.0
    if isinstance(anything, (int, float)):
        return float(anything)
    if isinstance(anything, str):
        try:
            return float(anything)
        except ValueError:
            return 0.0
    return 0.0


def is_number(anything: Union[Any, None]) -> bool:
    """
    Convert `anything` to a [int][int] according to [os.environ][os.environ] most found _int_ value.
    Args:
        anything: The value to convert
    Returns:
        the value as `int`, otherwise `0`
    Notes:
        If a float is given, then a hard convert to [int][int] is done. See Examples.
    Examples:
        >>> is_number("0")
        True
        >>> is_number(10)
        True
        >>> is_number("10")
        True
        >>> is_number("0.0")
        True
        >>> is_number("0.5")
        True
        >>> is_number("-0.5")
        True
        >>> is_number(-0.5)
        True
        >>> is_number(True)
        False
        >>> is_number("True")
        False
        >>> is_number([1, 2])
        False
        >>> is_number({"key": "value"})
        False
        >>> is_number((1, 2, 3))
        False
        >>> is_number(None)
        False

    """
    if not isinstance(anything, (str, int, float)) or not anything:
        return False
    if isinstance(anything, bool):
        return False
    try:
        float(anything)
        return True
    except ValueError:
        return False


SUPPORTED_TRUE_VALUE = [True, str(True), str(True).upper(), str(True).lower()]
SUPPORTED_FALSE_VALUE = [False, str(False), str(False).upper(), str(False).lower()]


def is_bool(anything: Union[Any, None]) -> bool:
    """
    Return True if anythong is a valid bool value, True or False, as string or not.
    int, float or any other type are not valid bool
    Args:
        anything: The value to check
    Returns:
        `True` if `anything` in SUPPORTED_[TRUE | FALSE]_VALUE
    Notes:
        If the value is a string, then this is case **insensitive**
    Examples:
        >>> is_bool("")
        False
        >>> is_bool("True")
        True
        >>> is_bool("TRUE")
        True
        >>> is_bool("true")
        True
        >>> is_bool("trUE")
        True
        >>> is_bool(True)
        True
        >>> is_bool("False")
        True
        >>> is_bool("FALSE")
        True
        >>> is_bool("false")
        True
        >>> is_bool("FALse")
        True
        >>> is_bool(False)
        True
        >>> is_bool("0")
        False
        >>> is_bool("1")
        False
        >>> is_bool([1, 2])
        False
        >>> is_bool({"key": "value"})
        False
        >>> is_bool((1, 2, 3))
        False

    """
    return str(anything).upper() in SUPPORTED_TRUE_VALUE + SUPPORTED_FALSE_VALUE


def negate_bool(value: Any) -> bool:
    return not to_bool(value)


def add_dash(value: str) -> str:
    """
    Return the value with 1 or 2 dash `-` as prefix
    If the value lenght is > 2 the 2 `-` is added as prefix else only one
    if the value is already prefixed, no dash added
    Args:
        value: The value, can contains `=`, in this case only the first part is take in the lenght of the option
    Returns:
        the value with dash
    Examples:
        >>> add_dash("my_option")
        '--my_option'
        >>> add_dash("k=value")
        '-k=value'
        >>> add_dash("key=value")
        '--key=value'
        >>> add_dash("--key=value")
        '--key=value'
        >>> add_dash("-o")
        '-o'
        >>> add_dash("i")
        '-i'
        >>> add_dash("-u=base")
        '-u=base'
        >>> add_dash(None)  # type check warning but ok
        ''
        >>> add_dash("")
        ''

    """
    if not value:
        return ""
    if not value.startswith("-"):
        dash = "-" * min(len(value.split("=", maxsplit=1)[0]), 2)
        return f"{dash}{value}"
    return value


def get_value(
    env_vars: Dict[str, str],
    *keys: str,
    default: str = None,
    if_all_falsy_return_none: bool = True,
) -> Optional[str]:
    """
    Allow to get the value from multiplke key inside a dict
    Usefull to search a value where the key can be multiple in [os.environ][os.environ]
    Args:
        env_vars: The dict to find in
        keys: all the values
        default: The default value if not any key found
        if_all_falsy_return_none: Force return `None` if the value is a `False` value

    Returns:
        if none_if_false==True : The first not falsy value found from keys (in keys orders) or None
        or default if keys do not exist
        if none_if_false==False : The first not falsy value found from keys (in keys orders) or
        the first falsy value found from keys or default if keys do not exist
    Examples:
        >>> get_value({"k1": "v1", "k2": "v2"}, "k1")
        'v1'
        >>> get_value({"k1": "v1", "k2": "v2"}, "k2")
        'v2'
        >>> get_value({"k1": "v1", "k2": "v2"}, "k2", "k1")
        'v2'
        >>> get_value({"k1": "v1", "k2": "v2"}, "k1", "k2")
        'v1'
        >>> get_value({"k1": "v1", "k2": "v2"}, "k3", "k2")
        'v2'
        >>> get_value(
        ...     {"k1": "v1", "k2": "v2"},
        ...     "k3",
        ... ) is None
        True
        >>> get_value({"k1": "v1", "k2": "v2"}, "k3", default="v3")
        'v3'
        >>> get_value({"k1": "", "k2": "v2"}, "k1", "k2", if_all_falsy_return_none=True)
        'v2'
        >>> get_value({"k1": "", "k2": "v2"}, "k1", if_all_falsy_return_none=False)
        ''
        >>> get_value({"k1": "", "k2": "v2"}, "k1", if_all_falsy_return_none=True) is None
        True
        >>> get_value({"k1": "", "k2": "v2"}, "k1", default="v1", if_all_falsy_return_none=False)
        ''
        >>> get_value({}, "k1", default="v1")
        'v1'
    """
    res = None
    last_falsy_value = default
    for key in keys:
        res = env_vars.get(key)
        if res:
            return res
        elif res is not None:
            last_falsy_value = res

    if if_all_falsy_return_none and (res is not None):
        return None

    return last_falsy_value


class DictUtil:
    """
    Utility class to manipulate [Dict][typing.Dict]
    """

    @staticmethod
    def clean_dict(values: Dict[str, Any]) -> Dict[str, str]:
        """
        Remove `False` value, `None` value
        Flat Dict value witha recursive call
        And convert List to `str` by comma joining value
        Args:
            values: A dict to clean and flat value

        Returns:
            A new dict without dirty value and None key value
        """
        new_values = OrderedDict()
        for key, value in values.items():
            if isinstance(value, dict):
                value = DictUtil.clean_dict(value)
            elif isinstance(value, (list, tuple, set)):
                value = ",".join([str(x) for x in value]) or ""
            if value is not False and value is not None and not isinstance(value, dict):
                new_values[key] = str(value)
        return new_values

    @staticmethod
    def clean_none_env_value(dict_value: Dict[str, Any]) -> Dict[str, Any]:
        """
        Like the name say, remove all the key with a `None` value
        Args:
            dict_value: A dict to clean

        Returns:
            A new Dict without the key where the value was `None`
        """
        result = OrderedDict()
        for key, value in dict_value.items():
            if value is not None:
                result[key] = value
        return result


def csv_list_value(value: str) -> List[str]:
    return [v.strip() for v in (value and value.split(",") or []) if v.strip()]


def csv_set_value(value: str) -> Set[str]:
    return {v.strip() for v in (value and value.split(",") or []) if v.strip()}


def no_change(v: Any) -> Any:
    return v


def if_not_none(value: Any) -> bool:
    return value is not None


def if_not_empty(value: Collection[Any]) -> bool:
    return bool(len(value))


def always_true(value: Any) -> bool:
    return True
