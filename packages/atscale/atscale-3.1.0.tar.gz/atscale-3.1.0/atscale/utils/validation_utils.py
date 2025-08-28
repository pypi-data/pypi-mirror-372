from atscale.parsers import dictionary_parser
from atscale.base import private_enums
from atscale.errors import atscale_errors

from typing import Dict, List, Union, Tuple, get_origin
import logging
from pandas import DataFrame
from copy import deepcopy
from re import search

logger = logging.getLogger(__name__)


def validate_by_type_hints(
    inspection,
    func_params,
    accept_partial=False,
    raise_err=True,
):
    """Takes an inspection of a function (inspect.getfullargspec(<function without parenthesis>)) and the locals() dict
    and raises an error if any parameters as defined in the func_params dict don't match the type hint for the parameter
    with exception to the parameters default value."""
    text_rep = {
        Dict[str, str]: "Dict[str, str]",
        Dict[str, List[str]]: "Dict[str:List[str]]",
        Dict[str, Tuple[str, str]]: "Dict[str,Tuple[str, str]]",
        List[str]: "List[str]",
        List[Union[str, Tuple[str, str]]]: "List[Union[str, tuple]]",
    }
    if inspection.defaults is not None:
        defaults = {
            p: val
            for p, val in zip(inspection.args[-len(inspection.defaults) :], inspection.defaults)
        }
    else:
        defaults = {}

    bad_params = []
    missing_params = []

    for param in inspection.args:  # all but data_model
        if param not in inspection.annotations:
            continue

        if param in func_params:
            type_hint = inspection.annotations[
                param
            ]  # typing object like Dict[...] or an actual type like int
            if type(type_hint) != str:  # I.e., to avoid cases where the type hint is in string form
                origin = get_origin(type_hint)  # Dict[...] -> dict, int -> None
                if origin is None:  # builtin class like int
                    origin = type_hint  # <class: 'int'>, the actual type
                    type_hint = origin.__name__  # 'int', the name of the type
                elif hasattr(
                    origin, "_name"
                ):  # typing.get_origin(Union[...]) -> Union... union has _name
                    if param in defaults and func_params[param] == defaults[param]:
                        continue
                    elif type(func_params[param]) not in type_hint.__args__:
                        bad_params.append(
                            (param, text_rep.get(type_hint, str(type_hint).replace("typing.", "")))
                        )
                    continue

                    # continue  # ignore special form, for example Union

                if (
                    type(func_params[param]) == DataFrame
                ):  # Handling issue with truth values of DataFrames
                    if param in defaults and func_params[param].equals(defaults[param]):
                        continue  # always accept default value... None is used as a default for mutable types like {} or []
                elif param in defaults and func_params[param] == defaults[param]:
                    continue  # always accept default value... None is used as a default for mutable types like {} or []

                if type(func_params[param]) != origin and not isinstance(
                    func_params[param], origin
                ):
                    # If the parameter's type is not at least a subclass of the corresponding type hint (e.g., we don't
                    # want to error out if we pass a Snowflake connection to a parameter technically typed SQLConnection)
                    if origin == float and (
                        "int" in str(type(func_params[param])).lower()
                        or "float" in str(type(func_params[param])).lower()
                    ):  # Not taking issue with a user passing an int where the code expects a float
                        pass
                    elif origin == int and "int" in str(type(func_params[param])).lower():
                        # Not taking issue with a user passing an int where the code expects a float
                        pass
                    else:
                        bad_params.append(
                            (param, text_rep.get(type_hint, str(type_hint).replace("typing.", "")))
                        )
            else:
                if (
                    type(func_params[param]).__name__ != type_hint
                    and str(type(func_params[param])).split("'")[1] != type_hint
                ):
                    bad_params.append(
                        (param, text_rep.get(type_hint, str(type_hint).replace("typing.", "")))
                    )
        else:
            if not accept_partial:
                missing_params.append(param)

    if missing_params and raise_err:
        raise ValueError(f"Missing expected parameters {missing_params}")

    if bad_params and raise_err:
        bad_param_str = "Incorrect parameter types passed: "
        for param in bad_params:
            bad_param_str += f"the {param[0]} parameter must be of type {param[1]}\n\t"
        raise ValueError(bad_param_str)

    return (missing_params, bad_params)


def validate_role_play_format(
    role_play: str,
):
    """Validates that the given role play is of a valid format.

    Args:
        role_play (str): The role play string.

    Returns:
        None.
    """
    # role play expressions must contain {0}`

    if "{0}" not in role_play:
        raise ValueError(
            f'`role_play` value: `{role_play}` is invalid; it must contain the substring `"{{0}}"`'
        )
