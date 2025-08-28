import json
from typing import Dict, Callable
import requests
import pandas as pd

from atscale.errors import atscale_errors


def generate_headers(
    content_type: str = "json",
    token: str = None,
) -> Dict:
    """generate the headers needed to query the api

    Args:
        content_type (str, optional): the shorthand of the content type for headers acceptable options are ['json', 'xml', 'x-www-form-urlencoded']
        token (str, optional): the Bearer token if applicable

    Returns:
        Dict: the header dictionary
    """
    response_dict = {}

    if content_type == "json":
        response_dict["Content-type"] = "application/json"
    elif content_type == "x-www-form-urlencoded":
        response_dict["Content-type"] = "application/x-www-form-urlencoded"
    elif content_type == "xml":
        response_dict["Content-type"] = "application/xml"
    else:
        raise ValueError(f"Invalid content_type: `{content_type}`")

    if token:
        response_dict["Authorization"] = "Bearer " + token

    return response_dict


def check_response(
    response,
):
    """Checks the response code of the query response

    Args:
        response (requests.Response): the api query response

    Returns:
        requests.Response: returns the response if the reponse is ok
    """
    error_code_dict: Dict[int, Callable] = {
        400: lambda message: atscale_errors.ValidationError(message=message),
        401: lambda message: atscale_errors.AuthenticationError(message=message),
        403: lambda message: atscale_errors.InsufficientAccessError(message=message),
        404: lambda message: atscale_errors.InaccessibleAPIError(message=message),
        500: lambda message: atscale_errors.AtScaleServerError(message=message),
        503: lambda message: atscale_errors.DisabledDesignCenterError(message=message),
    }
    if response.ok:
        return response
    else:
        try:
            resp = json.loads(response.text)

            response_message = resp.get("message", resp.get("response", {}).get("message", ""))
            verbose_message = resp.get("error", resp.get("response", {}).get("error", ""))

            reason = resp.get("status", {}).get("message", "")
            if reason == response_message:
                if reason == verbose_message:
                    message = f"{reason}"
                else:
                    message = f"{reason}: {verbose_message}"
            elif response_message == verbose_message:
                message = f"{reason}: {verbose_message}"
            else:
                message = f"{reason}: {response_message}, {verbose_message}"
            if message == ": , ":
                message = response.text
        except json.JSONDecodeError as e:
            message = response.text
        if response.status_code in error_code_dict:
            raise error_code_dict[response.status_code](message)
        else:
            raise atscale_errors.AtScaleServerError(message)


def get_rest_request(
    url,
    data: str = "",
    headers: Dict = None,
    raises: bool = True,
    session: requests.Session = None,
):
    """Sends a get request to the given url with the given parameters and returns the response.
    Raises error if response status code is not 200 unless raises is set to False in which case the errored response
    will be returned

    Args:
        url (str): the url to submit a get request to
        data (str, optional): the data to include in the request. Defaults to ''.
        headers (Dict, optional): the headers to include in the request. Defaults to None.
        raises (bool, optional): decide if we should raise the default error or the AtScale error. Defaults to True.

    Returns:
        requests.Response: the query response
    """
    if session is None:
        response = requests.get(url, data=data, headers=headers, stream=False)
    else:
        response = session.get(url, data=data, headers=headers, stream=False)
        session.close()
    if raises:
        check_response(response)
    return response


def patch_rest_request(
    url,
    data: str = "",
    headers: Dict = None,
    raises: bool = True,
    session: requests.Session = None,
):
    """Sends a patch request to the given url with the given parameters and returns the response.
    Raises error if response status code is not 200 unless raises is set to False in which case the errored response
    will be returned

    Args:
        url (str): the url to submit a patch request to
        data (str, optional): the data to include in the request. Defaults to ''.
        headers (Dict, optional): the headers to include in the request. Defaults to None.
        raises (bool, optional): decide if we should raise the default error or the AtScale error. Defaults to True.

    Returns:
        requests.Response: the query response
    """
    if session is None:
        response = requests.patch(url, data=data, headers=headers, stream=False)
    else:
        response = session.patch(url, data=data, headers=headers, stream=False)
        session.close()
    if raises:
        check_response(response)
    return response


def post_rest_request(
    url,
    data: str = "",
    headers: Dict = None,
    raises: bool = True,
    session: requests.Session = None,
):
    """Sends a post request to the given url with the given parameters and returns the response.
    Raises error if response status code is not 200 unless raises is set to False in which case the errored response
    will be returned

    Args:
        url (str): the url to submit a post request to
        data (str, optional): the data to include in the request. Defaults to ''.
        headers (Dict, optional): the headers to include in the request. Defaults to None.
        raises (bool, optional): decide if we should raise the default error or the AtScale error. Defaults to True.

    Returns:
        requests.Response: the query response
    """
    if session is None:
        response = requests.post(url, data=data, headers=headers, stream=False)
    else:
        response = session.post(url, data=data, headers=headers, stream=False)
        session.close()
    if raises:
        check_response(response)
    return response


def put_rest_request(
    url,
    data: str = "",
    headers: Dict = None,
    raises: bool = True,
    session: requests.Session = None,
):
    """Sends a put request to the given url with the given parameters and returns the response.
    Raises error if response status code is not 200 unless raises is set to False in which case the errored response
    will be returned

    Args:
        url (str): the url to submit a put request to
        data (str, optional): the data to include in the request. Defaults to ''.
        headers (Dict, optional): the headers to include in the request. Defaults to None.
        raises (bool, optional): decide if we should raise the default error or the AtScale error. Defaults to True.

    Returns:
        requests.Response: the query response
    """
    if session is None:
        response = requests.put(url, data=data, headers=headers, stream=False)
    else:
        response = session.put(url, data=data, headers=headers, stream=False)
        session.close()
    if raises:
        check_response(response)
    return response


def delete_rest_request(
    url,
    data: str = "",
    headers: Dict = None,
    raises: bool = True,
    session: requests.Session = None,
):
    """Sends a delete request to the given url with the given parameters and returns the response.
    Raises error if response status code is not 200 unless raises is set to False in which case the errored response
    will be returned

    Args:
        url (str): the url to submit a delete request to
        data (str, optional): the data to include in the request. Defaults to ''.
        headers (Dict, optional): the headers to include in the request. Defaults to None.
        raises (bool, optional): decide if we should raise the default error or the AtScale error. Defaults to True.

    Returns:
        requests.Response: the query response
    """
    if session is None:
        response = requests.delete(url, data=data, headers=headers, stream=False)
    else:
        response = session.delete(url, data=data, headers=headers, stream=False)
        session.close()
    if raises:
        check_response(response)
    return response


def parse_rest_query_response(
    response,
) -> pd.DataFrame:
    """Parses results from a rest api SQL query response into a Dataframe.

    Args:
       response (requests.Response): The response used to formulate the dataframe that the function returns.

    Returns:
        pandas.DataFrame: the parsed query response
    """
    data = json.loads(response.text)
    if data["metadata"]["succeeded"] == False:
        raise atscale_errors.AtScaleServerError(data["metadata"]["error-message"])
    column_types = {}
    for column in data["metadata"]["columns"]:
        column_types[column["name"]] = column["type"]
    df = pd.DataFrame(columns=[x["name"] for x in data["metadata"]["columns"]], data=data["data"])
    for column in df.columns:
        df[column] = pd.to_numeric(df[column].values, errors="ignore")
        if "date" in column_types[column].lower() or "time" in column_types[column].lower():
            try:
                first_value_index = df[column].first_valid_index()
                # leave as nan if all null
                if first_value_index is not None:
                    # If date parse fails, just pass and leave the column as is
                    # infer_datetime_format is needed prior to Pandas 2.0.0 we can remove this if that becomes our required version
                    if int(pd.__version__.split(".")[0]) == 1:
                        dates = pd.to_datetime(
                            df[column], errors="raise", infer_datetime_format=True
                        )
                    else:
                        dates = pd.to_datetime(df[column], errors="raise")
                    # If it succeeds and there is a ":" is is a datetime so we just set the column
                    if ":" in df[column][first_value_index]:
                        df[column] = dates
                    # If no ":" it should just be a date so drop the time that pandas adds during parse
                    else:
                        df[column] = dates.dt.date
            except:
                pass
    return df
