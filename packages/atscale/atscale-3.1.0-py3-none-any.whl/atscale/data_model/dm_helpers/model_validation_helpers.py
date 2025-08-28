import logging
import json
from inspect import getfullargspec
from typing import Dict, List, Union, Tuple
from copy import deepcopy

from atscale.errors import atscale_errors
from atscale.base import private_enums, endpoints
from atscale.utils import validation_utils
from atscale.connection.connection import _Connection
from atscale.parsers import dictionary_parser

logger = logging.getLogger(__name__)


def _perspective_check(
    data_model: "DataModel",
    error_msg: str = None,
):
    """Checks if the data_model provided is a perspective and throws an error if so.

    Args:
        data_model (DataModel): The DataModel to check
        error_msg (str, optional): Custom error string. Defaults to None to throw write error.
    """
    inspection = getfullargspec(_perspective_check)
    validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

    if error_msg is None:
        error_msg = "Write operations are not supported for perspectives."

    if data_model.is_perspective():
        raise atscale_errors.WorkFlowError(error_msg)


def _validate_mdx_syntax(
    atconn: _Connection,
    expression: str,
    raises=True,
) -> str:
    """Passes an MDX expression to the engine for validation

    Args:
        atconn (_Connection): the connection to use for validation
        expression (str): the expression to validate
        raises (bool, optional): Determines behavior if error is found. If
            True it will raise error, else it will return error message. Defaults to True.

    Returns:
        str: Either the error or an empty string if no error found
    """
    url = endpoints._endpoint_mdx_syntax_validation(atconn)
    data = {"formula": expression}
    response = atconn._submit_request(
        request_type=private_enums.RequestType.POST, url=url, data=json.dumps(data)
    )
    resp = response.json()
    if not resp["isSuccess"]:
        if raises:
            raise atscale_errors.AtScaleServerError(resp["errorMsg"])
        else:
            return resp["errorMsg"]
    return ""


def _validate_warehouse_connection(
    data_model: "DataModel",
    dbconn: "SQLConnection",
) -> bool:
    connection = data_model.get_connected_warehouse()
    if dbconn._verify(connection):
        return True
    msg = "The SQLConnection connects to a database that is not referenced by the given data_model."
    raise ValueError(msg)


def _check_duplicate_features_get_data(feature_list: List[str]):
    """Logs appropriate info if duplicate features encountered in get_data

    Args:
        feature_list (List[str]): The list of features to check
    """

    dupe_count = len(feature_list) - len(set(feature_list))

    if dupe_count > 0:
        input_feature_list_len = len(feature_list)
        logger.warning(
            f"The feature_list passed contains {dupe_count} duplicates; the DataFrame returned "
            f"by get_data will contain {input_feature_list_len - dupe_count} features instead of {input_feature_list_len}."
        )


def _check_features_helper(
    features: Union[list, Dict, set],
    check_against: Union[list, Dict, set],
    errmsg: str = None,
    diff_in_msg: bool = True,
) -> bool:
    """Checks that the given feature(s) exist(s) within a specified list of features.

    Args:
        features (Union[list, Dict, set]): feature(s) to confirm exist in the provided list. If a dict is passed,
                                           the keys will be used.
        check_against (Union[list, Dict, set]): features of the data model to check against. If a dict is passed, the keys
                                             will be used.
        errmsg (str, optional): Error message to raise if feature not found. Defaults to None.
        diff_in_msg (bool, optional): Whether format(sorted(non_existent_features)) should be called on the given errmsg.
                                      Defaults to True.

    Returns:
        bool: True if no error found
    """
    set_dif = set(features) - set(check_against)
    if len(set_dif) > 0:
        if errmsg:
            errmsg = errmsg.format(sorted(list(set_dif))) if diff_in_msg else errmsg
            raise atscale_errors.ObjectNotFoundError(errmsg)
        else:
            raise atscale_errors.ObjectNotFoundError(
                private_enums.CheckFeaturesErrMsg.ALL.get_errmsg()
            )
    return True


def _check_features(
    features_check_tuples: List[Tuple[Union[list, Dict, set], private_enums.CheckFeaturesErrMsg]],
    feature_dict: Dict = None,
    hierarchy_dict: Dict = None,
    errmsg: str = None,
    diff_in_msg: bool = True,
) -> bool:
    """Checks that the given feature(s) exist(s) within a specified list of features.

    Args:
        features_check_tuples (List[Tuple[Union[list, Dict, set], private_enums.CheckFeaturesErrMsg]]): List of (features/hierarchies,
                                        type check) pair(s) to run. Options are limited to (features, ALL/NUMERIC/CATEGORICAL)
                                        or (hierarchies, HIERARCHY).
        feature_dict (Dict, optional): Features of the data model to check against. Defaults to None.
        hierarchy_dict (Dict, optional): Hierarchies of the data model to check against. Defaults to None.
        errmsg (str, optional): Error message to raise if feature not found. Defaults to None.
        diff_in_msg (bool, optional): Whether format(sorted(non_existent_features)) should be called on the given errmsg.
                                      Defaults to True.

    Returns:
        bool: True if no error found
    """
    for tuple in features_check_tuples:
        features, check = tuple

        if check == private_enums.CheckFeaturesErrMsg.HIERARCHY and hierarchy_dict is None:
            raise Exception("hierarchy_dict cannot be 'None' if checking hierarchies")
        elif check != private_enums.CheckFeaturesErrMsg.HIERARCHY and feature_dict is None:
            raise Exception("feature_dict cannot be 'None' if checking features")

        if check == private_enums.CheckFeaturesErrMsg.HIERARCHY:
            check_dicts = [deepcopy(hierarchy_dict)]
        elif check == private_enums.CheckFeaturesErrMsg.ALL:
            check_dicts = [deepcopy(feature_dict)]
        else:
            parsed_dict = dictionary_parser.filter_dict(
                to_filter=feature_dict,
                val_filters=[lambda i: i["feature_type"] == check.value[1]],
            )
            check_dicts = [deepcopy(feature_dict), parsed_dict]

        if errmsg:
            helper_errmsgs = [errmsg]
        elif len(check_dicts) > 1:
            helper_errmsgs = [
                private_enums.CheckFeaturesErrMsg.ALL.get_errmsg(),
                check.get_errmsg(),
            ]
        else:
            helper_errmsgs = [check.get_errmsg()]

        for i, dict in enumerate(check_dicts):
            _check_features_helper(
                features=features,
                check_against=dict,
                errmsg=helper_errmsgs[i],
                diff_in_msg=diff_in_msg,
            )

    return True
