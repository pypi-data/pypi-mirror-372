"""Utility functions for Kognic IO"""

import warnings
from collections.abc import Mapping
from datetime import datetime
from typing import Dict, List, Optional

import dateutil.parser


def ts_to_dt(date_string: str) -> datetime:
    """
    Parse string datetime into datetime
    """
    return dateutil.parser.parse(date_string)


def filter_none(js: dict) -> dict:
    if isinstance(js, Mapping):
        return {k: filter_none(v) for k, v in js.items() if v is not None}
    else:
        return js


def get_view_links(input_uuids: List[str]) -> Dict[str, str]:
    """
    For each given input uuid returns an URL where the input can be viewed in the web app.

    :param input_uuids: List with input uuids
    :return Dict: Dictionary mapping each uuid with a URL to view the input.
    """
    view_dict = dict()
    for input_uuid in input_uuids:
        view_dict[input_uuid] = f"https://app.kognic.com/view/input/{input_uuid}"

    return view_dict


def deprecated_parameter(from_name: str, to_name: str, end_version: Optional[str] = None):
    """
    Decorator to mark a parameter as deprecated and replaced by another. If the parameter is used, a deprecation warning
    is displayed. The parameter is then renamed to the new name.

    Example usage:

    def fun(foo: str): # Old version
        pass

    @deprecated_parameter("foo", "new_name")
    def fun(bar: str): # New version, where foo is renamed to bar
        pass

    The new function can now be called with either foo or bar as parameter name.
        fun("baz")
        fun(foo = "baz")
        fun(bar = "baz") # will emit a deprecation warning

    :param from_name: Name of the deprecated parameter
    :param to_name: Name of the new parameter
    :param end_version: Version where the parameter will be removed
    """

    version_part = f" in {end_version}" if end_version else "in the future"
    message = f"""The parameter "{from_name}" has been deprecated in favor of "{to_name}" and will be removed {version_part}"""

    def inner_decorator(f):
        def wrapped(*args, **kwargs):
            if from_name in kwargs:  # Display deprecation message if the deprecated parameter is used
                warnings.warn(message, DeprecationWarning, stacklevel=2)
                kwargs[to_name] = kwargs.pop(from_name)
            return f(*args, **kwargs)

        return wrapped

    return inner_decorator
