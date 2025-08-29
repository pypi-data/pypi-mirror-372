import json
import os
from concurrent.futures import ThreadPoolExecutor

import requests
from corehttp.rest import HttpRequest
from corehttp.rest._rest_py3 import _HttpResponseBase as SansIOHttpResponse
from corehttp.runtime.policies import (
    BearerTokenCredentialPolicy,
    NetworkTraceLoggingPolicy,
    SansIOHTTPPolicy,
)

from lseg_analytics.auth.machine_token_credential import MachineTokenCredential
from lseg_analytics.auth.user_token_credential import UserTokenCredential
from lseg_analytics.exceptions import (
    _ERROR_MESSAGE,
    ProxyAuthFailureError,
    ProxyNotEnabledError,
    ProxyNotFoundError,
    ProxyStatusError,
)
from lseg_analytics_basic_client import AnalyticsAPIClient

from ._logger import logger
from .config import load_config

__all__ = [
    "Client",
]

HTTPRequestType = HttpRequest
HTTPResponseType = SansIOHttpResponse


class CustomSDKPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):
    """Custom Policy for decoding response of Rest Yield Book CSV related endpoints
    which don't have 'Content-Type' in the response."""

    def on_response(self, request, response):
        if "/results/bulk/csv" in response.http_response.url and response.http_response.status_code == 200:
            response.http_response._content_type = "text/csv"
        return super().on_response(request, response)


def _get_proxy_port_from_file():
    port_file = f'{os.path.expanduser("~")}{os.path.sep}.lseg{os.path.sep}VSCode{os.path.sep}.portInUse'
    logger.debug(f"Trying to read proxy port from file:{port_file}")
    if os.path.isfile(port_file):
        logger.info(f"Reading from file:{port_file}")
        with open(port_file) as f:
            port = f.read()
            if port.strip().strip("\n").lower() == "disabled":
                raise ProxyNotEnabledError(_ERROR_MESSAGE.PROXY_DISABLED.value)
            return int(port)
    else:
        raise Exception(f"Port file({port_file}) is not found")


def get_proxy_status_response(port):
    url = f"http://localhost:{port}/status"
    try:
        response = requests.get(url, timeout=1)  # timeout is 1 second
        return port, response
    except Exception as err:
        logger.warning(f"Get exception:{err} when requesting url :{url}")
        return port, None


def _check_proxy_status(ports_list):
    logger.debug(f"checking if localhost proxy is working with ports[{ports_list}]")
    with ThreadPoolExecutor(max_workers=10) as exe:
        responses = exe.map(get_proxy_status_response, ports_list)
        for port, response in responses:
            try:
                if response is not None:
                    if response.status_code == 200:
                        data = json.loads(response.text)
                        if "lsegProxyEnabled" in data:
                            if data["lsegProxyEnabled"]:
                                return f"http://localhost:{port}"
                            else:
                                raise ProxyNotEnabledError(_ERROR_MESSAGE.PROXY_DISABLED.value)
                        else:
                            logger.error(
                                f"Failed to get status from proxy. lsegProxyEnabled is not in payload, Port: {port} Detail:{data}"
                            )
                            raise ProxyStatusError(_ERROR_MESSAGE.INVALID_RESPONSE.value)
                    elif response.status_code == 401:
                        raise ProxyAuthFailureError(_ERROR_MESSAGE.PROXY_UNAUTHORIZED.value)
                    elif response.status_code == 403:
                        raise ProxyAuthFailureError(_ERROR_MESSAGE.PROXY_FORBIDDEN.value)
                    else:
                        logger.error(
                            f"Failed to get status from proxy. Incorrect status code {response.status_code} with port: {port}"
                        )
                        raise ProxyStatusError(_ERROR_MESSAGE.INVALID_RESPONSE.value)
            except (ProxyStatusError, ProxyNotEnabledError, ProxyAuthFailureError) as err:
                raise err
            except Exception as err:
                logger.error(
                    f"Failed to get status from proxy. Got exception when parsing response with port {port}: {err}"
                )
                raise ProxyStatusError(_ERROR_MESSAGE.INVALID_RESPONSE.value)
    raise ProxyNotFoundError(_ERROR_MESSAGE.NO_AVALIABLE_PORT.value)


def _get_proxy_info():
    try:
        # add the port from file at first, so we will check it firstly
        port = _get_proxy_port_from_file()
        proxy_url = _check_proxy_status([port])
        logger.info(f"Proxy is found with port configured, proxy url is:{proxy_url}")
        return proxy_url
    except (ProxyStatusError, ProxyNotEnabledError, ProxyAuthFailureError) as err:
        raise err
    except Exception as err:  # No break
        logger.warning(f"Failed to load proxy port from local file, error: {err}")

    # add default ports: 60100 to 60110 inclusive
    ports = range(60100, 60111)
    proxy_url = _check_proxy_status(list(ports))
    logger.info(f"proxy is found, proxy url is:{proxy_url}")
    return proxy_url


class Client:
    user_token_cred = None

    @classmethod
    def reload(cls):
        if cls.user_token_cred:
            cls.user_token_cred.cleanup()
        cls._instance = None

    def __new__(cls):
        if not getattr(cls, "_instance", None):
            cfg = load_config()
            authentication_policy = None
            if (
                cfg.machine_auth
                and cfg.machine_auth.client_id
                and cfg.machine_auth.token_endpoint
                and cfg.machine_auth.client_secret
            ):
                authentication_policy = BearerTokenCredentialPolicy(
                    credential=MachineTokenCredential(
                        client_id=cfg.machine_auth.client_id,
                        client_secret=cfg.machine_auth.client_secret,
                        auth_endpoint=cfg.machine_auth.token_endpoint,
                        scopes=cfg.machine_auth.scopes,
                    ),
                    scopes=cfg.machine_auth.scopes,
                )
            elif cfg.user_auth and cfg.user_auth.client_id and cfg.user_auth.authority and cfg.user_auth.redirect_uri:
                cls.user_token_cred = UserTokenCredential(
                    client_id=cfg.user_auth.client_id,
                    authority=cfg.user_auth.authority,
                    redirect_uri=cfg.user_auth.redirect_uri,
                    scopes=cfg.user_auth.scopes,
                )
                authentication_policy = BearerTokenCredentialPolicy(
                    credential=cls.user_token_cred,
                    scopes=cfg.user_auth.scopes,
                )
            else:
                proxy_disabled = os.getenv("LSEG_ANALYTICS_PROXY_DISABLED", "false").lower() in ("true", "1")
                if not proxy_disabled:
                    Client.retrieve_proxy_endpoint(cfg)

            from corehttp.runtime.policies import (
                ContentDecodePolicy,
                HeadersPolicy,
                NetworkTraceLoggingPolicy,
                ProxyPolicy,
                RetryPolicy,
                UserAgentPolicy,
            )

            logging_policy = NetworkTraceLoggingPolicy()
            logging_policy.enable_http_logger = True
            headers_policy = HeadersPolicy()
            if cfg.headers:
                for key, value in cfg.headers.items():
                    headers_policy.add_header(key, value)
            policies = [
                headers_policy,
                UserAgentPolicy(),
                ProxyPolicy(),
                ContentDecodePolicy(),
                RetryPolicy(),
                CustomSDKPolicy(),
                authentication_policy,
                logging_policy,
            ]
            cls._instance = AnalyticsAPIClient(endpoint=cfg.base_url, username=cfg.username, policies=policies)
            cls._instance._config.headers_policy = headers_policy
            cls._instance._config.authentication_policy = authentication_policy
            cls._instance._config.logging_policy = logging_policy
        return cls._instance

    @staticmethod
    def retrieve_proxy_endpoint(cfg):
        cfg.base_url = _get_proxy_info()
