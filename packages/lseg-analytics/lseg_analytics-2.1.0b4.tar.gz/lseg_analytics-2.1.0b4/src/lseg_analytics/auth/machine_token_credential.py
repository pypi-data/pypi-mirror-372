import time
from typing import Any, List, Optional

import requests
from corehttp.credentials import AccessToken, TokenCredential

from ..exceptions import _ERROR_MESSAGE, AuthenticationError
from ._logger import logger


class MachineTokenCredential(TokenCredential):
    def __init__(self, client_id: str, client_secret: str, auth_endpoint: str, scopes: List[str]):
        self.url = auth_endpoint
        self._access_token = None
        self.request_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            "scope": " ".join(scopes),
            "audience": "API2-PROD",
            "ttl": 86400,
        }

    def get_token(self, *scopes: str, claims: Optional[str] = None, **kwargs: Any) -> AccessToken:
        try:
            logger.info(f"Getting access token using client_credentials from {self.url}")

            data = {"scope": " ".join(["trapi.data.quantitative-analytics.read"]), **self.request_data}

            response = requests.post(self.url, data=data)

            if response.status_code != 200:
                logger.error(
                    f"Failed to get access token. Response code: {response.status_code}. Response: {response.text}"
                )
                raise AuthenticationError(_ERROR_MESSAGE.CREDENTIAL_UNAUTHORIZED.value)

            access_token = response.json().get("access_token")
            expires_in = response.json().get("expires_in")

            if not access_token:
                raise AuthenticationError(
                    f"Failed to get access token. Successful response, but no access token found. Response: {response.text}"
                )

            logger.info("Access token retrieved successfully")

            return AccessToken(token=access_token, expires_on=time.time() + expires_in)
        except AuthenticationError as auth_err:
            raise auth_err
        except Exception as e:
            logger.error(f"Failed to get access token. Error: {e}")
            raise AuthenticationError(_ERROR_MESSAGE.GET_TOKEN_FAILED.value)
