import json
import re
import urllib
from enum import Enum, unique
from io import IOBase
from typing import Any, Iterable, List, Optional, Union

from corehttp.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
)
from corehttp.rest import HttpRequest, HttpResponse
from corehttp.utils import case_insensitive_dict

from lseg_analytics._client.client import Client
from lseg_analytics.exceptions import check_exception_and_raise
from lseg_analytics_basic_client import models as _models
from lseg_analytics_basic_client._model_base import (
    SdkJSONEncoder,
    _failsafe_deserialize,
)
from lseg_analytics_basic_client._serialization import Serializer

from ._logger import logger

_SERIALIZER = Serializer()


@unique
class RequestMethod(str, Enum):
    """
    Possible values for the request methods:
       GET : GET request method.
       POST : POST request method.
       DELETE : DELETE request method.
       PUT : PUT request method.
    """

    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"

    def __str__(self) -> str:
        return str(self.value)


class APIRequest:
    """
    Defines the wrapper around the data delivery mechanism of the Analytics Data Platform.

    Parameters
    ----------
    url : str
        API endpoint URL.
    method : RequestMethod, optional
        HTTP request method.
    path_parameters : dict, optional
        Parameters that can be added to the endpoint URL.
    query_parameters : dict, optional
        HTTP request query parameters.
    header_parameters : dict, optional
        HTTP request header parameters.
    body_parameters : dict, optional
        HTTP request body parameters.


    Examples
    --------
    >>> from lseg_analytics.delivery import APIRequest
    >>> api_request = APIRequest(
    >>>        url='/financials/reference-data/calendars/v2/{calendarId}/$count-periods',
    >>>        method = RequestMethod.POST,
    >>>        path_parameters={"calendarId": "0c182661-9a84-49a0-a065-64a959555515"},
    >>>        body_parameters={"dayCountBasis": "Dcb_Actual_360", "endDate": "2023-12-31", "startDate": "2023-01-01"}
    >>>    )
    """

    def __init__(
        self,
        url: str,
        method: Union["RequestMethod", str, None] = RequestMethod.GET,
        path_parameters: Optional[dict] = None,
        query_parameters: Optional[dict] = None,
        header_parameters: Optional[dict] = None,
        body_parameters: Union[dict, List[dict], str, bytes, Iterable[bytes]] = None,
    ):
        self.url = url
        self.method = method
        self.path_parameters = path_parameters
        self.query_parameters = query_parameters
        self.body_parameters = body_parameters
        self.header_parameters = header_parameters

    def send(self) -> HttpResponse:
        """
        Send a request to the Analytics Data Platform API directly.

        Returns
        -------
        Response

        Examples
        --------
        >>> from lseg_analytics.delivery import APIRequest
        >>> api_request = APIRequest(
        >>>        url='/financials/reference-data/calendars/v2/{calendarId}/$count-periods',
        >>>        method = RequestMethod.POST,
        >>>        path_parameters={"calendarId": "0c182661-9a84-49a0-a065-64a959555515"},
        >>>        body_parameters={"dayCountBasis": "Dcb_Actual_360", "endDate": "2023-12-31", "startDate": "2023-01-01"}
        >>>    )
        >>> api_request.send()
        """
        try:
            # Validate URL and path parameters before constructing
            _validate_endpoint_request_url_parameters(self.url, self.path_parameters)

            # build the request
            _request = _build_request(
                self.url,
                self.method,
                self.path_parameters,
                self.query_parameters,
                self.body_parameters,
                self.header_parameters,
            )
            # contact request url
            path_format_arguments = {
                "endpoint": _SERIALIZER.url("self._config.endpoint", Client()._config.endpoint, "str", skip_quote=True),
            }
            _request.url = Client()._client.format_url(_request.url, **path_format_arguments)

            response = Client()._client.send_request(_request)

            if response.status_code not in [200, 201, 202, 204]:
                _handle_response(response)
            else:
                return response
        except Exception as err:
            # logger.error("Error get data, error:", err)
            check_exception_and_raise(err, logger)


def _validate_endpoint_request_url_parameters(url, path_parameters):
    if url == "":
        logger.error("Requested URL is missing, please provide valid URL")
        raise ValueError("Requested URL is missing, please provide valid URL")

    # Find all path parameters in the URL (anything enclosed in {})
    path_param_pattern = re.compile(r"{([^{}]+)}")
    required_params = path_param_pattern.findall(url)

    if required_params:
        if not path_parameters:
            logger.error(
                f"URL contains path parameters {required_params}, but no path_parameters dictionary was provided"
            )
            raise ValueError(
                f"URL contains path parameters {required_params}, but no path_parameters dictionary was provided"
            )

        # Check if all required parameters are provided
        missing_params = [param for param in required_params if param not in path_parameters]
        if missing_params:
            logger.error(f"The following path parameters are missing: {', '.join(missing_params)}")
            raise ValueError(f"The following path parameters are missing: {', '.join(missing_params)}")


def _build_request(url, method, path_parameters, query_parameters, body_parameters, header_parameters) -> HttpRequest:
    header_parameters = case_insensitive_dict(header_parameters or {})
    content_type = header_parameters.pop("Content-Type", "application/json")
    accept = header_parameters.pop("Accept", "application/json")
    # Construct headers
    if content_type is not None:
        header_parameters["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    header_parameters["Accept"] = _SERIALIZER.header("accept", accept, "str")

    # Construct URL
    if path_parameters:
        for key, value in path_parameters.items():
            value = _bool_or_none_to_str(value)
            value = urllib.parse.quote_plus(str(value))
            url = url.replace("{" + key + "}", value)

    _content = None
    if body_parameters:
        if isinstance(body_parameters, (IOBase, bytes)):
            _content = body_parameters
        else:
            _content = json.dumps(body_parameters, cls=SdkJSONEncoder, exclude_readonly=True)

    return HttpRequest(method=method, url=url, params=query_parameters, headers=header_parameters, content=_content)


def _bool_or_none_to_str(value: Any) -> Union[str, Any]:
    """
    Coerce a bool type or None type into a string value.

    Note that we prefer JSON-style 'true'/'false' for boolean values here.
    """
    if isinstance(value, bool):
        return str(value).lower()
    elif value is None:
        return ""

    return value


def _handle_response(response):
    error = None
    if response.status_code == 401:
        error = _failsafe_deserialize(_models.ServiceErrorResponse, response.json())
        raise ClientAuthenticationError(response=response, model=error)
    elif response.status_code == 404:
        error = _failsafe_deserialize(_models.ServiceErrorResponse, response.json())
        raise ResourceNotFoundError(response=response, model=error)
    elif response.status_code == 409:
        error = _failsafe_deserialize(_models.ServiceErrorResponse, response.json())
        raise ResourceExistsError(response=response, model=error)
    elif response.status_code in [400, 403, 405, 406, 408, 410, 412, 415, 423, 428, 429, 500, 501, 502, 503, 504]:
        error = _failsafe_deserialize(_models.ServiceErrorResponse, response.json())
    raise HttpResponseError(response=response, model=error)
