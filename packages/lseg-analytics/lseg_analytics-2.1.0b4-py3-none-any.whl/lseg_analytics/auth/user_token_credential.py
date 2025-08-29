import threading
import time
import webbrowser
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pkce
import requests
from corehttp.credentials import AccessToken, TokenCredential
from requests_oauthlib import OAuth2Session

from ..exceptions import _ERROR_MESSAGE, AuthenticationError
from ._logger import logger
from .loopback_client import LoopbackClient

AUTH_GRANT_TYPE = "authorization_code"
REFRESH_TOKEN = "refresh_token"
RESPONSE_TYPE = "code"
RESPONSE_MODE = "query"
CODE_CHALLENGE_METHOD = "S256"


class UserTokenCredential(TokenCredential):
    def __init__(self, client_id: str, authority: str, redirect_uri: str, scopes: List[str]):
        """Initialize a UserTokenCredential.

        Args:
            client_id: The client ID of the application.
            authority: The authority URL.
            redirect_uri: The redirect URI.
            scopes: The requested scopes.
        """
        self.client_id = client_id
        self.authority = authority if authority.startswith("https") else f"https://{authority}"
        self.redirect_uri = redirect_uri
        self.scope = " ".join(scopes)
        self._token_cache: Dict[str, Any] = {}
        self._token_refresh_lock = threading.RLock()
        self._refresh_timer_task = None  # For the Timer-based scheduled refresh
        self._stop_timer_event = threading.Event()
        self._retry_count = 0
        self._max_retries = 3

    def _refresh_token(self):
        """Refresh the access token using the refresh token.
        Raises:
            AuthenticationError: If the token cannot be refreshed.
        """
        try:
            if "refresh_token" not in self._token_cache:
                logger.error("No refresh token available for token refresh")
                raise AuthenticationError("No refresh token available for token refresh")

            refresh_token = self._token_cache["refresh_token"]
            token_url = f"{self.authority}/as/token.oauth2"

            logger.info(f"Refreshing access token using refresh_token grant type")
            request_data = {
                "refresh_token": refresh_token,
                "grant_type": REFRESH_TOKEN,
                "client_id": self.client_id,
            }

            # Set request timeout based on token expiration
            # If we already have a token, check its expiration time
            timeout = 15  # Default timeout: 15 seconds
            if "expires_on" in self._token_cache:
                time_remaining = self._token_cache["expires_on"] - time.time()
                if time_remaining <= 60:  # 1 minute or less
                    timeout = 15  # Use a shorter timeout when token is about to expire
                else:
                    timeout = 60  # Use normal timeout for tokens with some time left

            response = requests.post(token_url, data=request_data, timeout=timeout)
            data = response.json()

            if "access_token" not in data:
                logger.error("Failed to refresh access token")
                raise AuthenticationError("Failed to refresh access token")

            # Update token cache with new tokens
            self._update_token_cache(data)

            logger.info("Access token refreshed successfully")

            access_token = data["access_token"]
            expires_in = data.get("expires_in", 0)

            # Schedule the next token refresh based on expiration time
            self._schedule_token_refresh(expires_in)

            return AccessToken(token=access_token, expires_on=time.time() + expires_in)
        except Exception as e:
            logger.error(f"Failed to refresh access token: {e}")
            raise AuthenticationError(f"Failed to refresh access token: {e}")

    def _update_token_cache(self, data: Dict[str, Any]) -> None:
        """Update the token cache with new token information.

        Args:
            data: The token response data.
        """
        self._token_cache.update(
            {
                "access_token": data.get("access_token"),
                "refresh_token": data.get("refresh_token"),
                "expires_on": time.time() + data.get("expires_in", 0),
            }
        )

    def _schedule_token_refresh(self, expires_in: int) -> None:
        """Schedule a token refresh based on expiration time.

        Args:
            expires_in: The token expiration time in seconds.
        """
        # Cancel any existing refresh timer
        if hasattr(self, "_refresh_timer_task"):
            if self._refresh_timer_task is not None:
                self._refresh_timer_task.cancel()

        if expires_in <= 300:  # 5 minutes or less
            refresh_delay = expires_in - 60  # Refresh with 1 minute remaining
            logger.info(f"Token expires in {expires_in}s (≤5 min). Scheduling refresh in {refresh_delay}s")
        else:
            refresh_delay = expires_in - 300  # Refresh with 5 minutes remaining
            logger.info(f"Token expires in {expires_in}s (>5 min). Scheduling refresh in {refresh_delay}s")

        # Calculate absolute refresh time
        refresh_time = time.time() + refresh_delay

        # Schedule the timer using Timer (which starts a thread only when needed)
        self._refresh_timer_task = threading.Timer(refresh_delay, self._execute_refresh)
        self._refresh_timer_task.daemon = True
        self._refresh_timer_task.name = f"TokenRefresh-{int(refresh_time)}"
        self._refresh_timer_task.start()
        logger.info(f'Scheduled token refresh at {datetime.fromtimestamp(refresh_time).strftime("%Y-%m-%d %H:%M:%S")}')

    def _execute_refresh(self) -> None:
        """Execute token refresh at the scheduled time"""
        # Check if we've been asked to stop refresh operations
        if self._stop_timer_event.is_set():
            logger.info("Skipping scheduled token refresh because stop event is set")
            return

        logger.info("Executing scheduled token refresh")
        try:
            with self._token_refresh_lock:
                self._refresh_token()
                self._retry_count = 0
        except Exception as e:
            self._retry_count += 1
            logger.error(f"Scheduled token refresh failed: {e}")

            # Implement retry logic - retry immediately up to max_retries
            if self._retry_count <= self._max_retries:
                logger.warning(
                    f"Will retry token refresh immediately (attempt {self._retry_count}/{self._max_retries})"
                )
                self._execute_refresh()  # Retry immediately
            else:
                logger.error(f"Token refresh failed after {self._max_retries} attempts")
                self._retry_count = 0

    # get the access token
    def get_token(self, *scopes: str, claims: Optional[str] = None, **kwargs: Any) -> AccessToken:
        """Get an access token.

        Args:
            *scopes: The requested scopes.
            claims: Optional claims.
            **kwargs: Additional keyword arguments.

        Returns:
            AccessToken: An access token.

        Raises:
            AuthenticationError: If the token cannot be retrieved or refreshed.
        """
        with self._token_refresh_lock:
            # Check if we have a cached token that's still valid
            if "access_token" in self._token_cache and time.time() < (self._token_cache["expires_on"] - 60):
                logger.info("Using cached access token")
                return AccessToken(token=self._token_cache["access_token"], expires_on=self._token_cache["expires_on"])
            # Try to refresh the token if we have a refresh token
            if "refresh_token" in self._token_cache:
                try:
                    logger.info("Token expired or near expiration, attempting refresh")
                    return self._refresh_token()
                except AuthenticationError:
                    logger.info("Token refresh failed, falling back to interactive authentication")
                    # Fall through to interactive authentication
            # Interactive authentication flow
            try:
                # create loopback listener
                logger.info("Create loopback listener")
                loopback_client = LoopbackClient.initialize(redirect_uri=self.redirect_uri)

                # update the local redirectUri with the loopback port added
                self.redirect_uri = loopback_client.redirect_uri

                # Get authorization request URL
                logger.info("Get authorization request URL")
                aaa = OAuth2Session(client_id=self.client_id, redirect_uri=self.redirect_uri, scope=self.scope)
                authorization_url, state = aaa.authorization_url(f"{self.authority}/as/authorization.oauth2")
                logger.info("Create PKCE code verifier and challenge")
                code_verifier, code_challenge = pkce.generate_pkce_pair()
                authorization_url += f"&code_challenge={code_challenge}&code_challenge_method={CODE_CHALLENGE_METHOD}"

                logger.info("Invoking authorization_code grant type")
                # open browser to authorization URL
                webbrowser.open_new(authorization_url)

                # listen for auth code
                auth_code = loopback_client.listen_for_auth_code()

                # handle auth code token exchange
                request_data = {
                    "grant_type": AUTH_GRANT_TYPE,
                    "client_id": self.client_id,
                    "redirect_uri": self.redirect_uri,
                    "code_verifier": code_verifier,
                    "code": auth_code,
                }

                token_url = f"{self.authority}/as/token.oauth2"
                logger.info(f"Getting access token using authorization_code grant type from {token_url}")

                response = requests.post(token_url, data=request_data)
                data = response.json()
                if "access_token" in data:
                    access_token = data["access_token"]
                else:
                    msg = "Access token could not be retrieved"
                    logger.fatal(msg)
                    raise AuthenticationError(msg)
                expires_in = data["expires_in"] if "expires_in" in data else 0
                logger.info("Access token retrieved successfully")

                # Update token cache with new tokens
                self._update_token_cache(data)

                # Schedule the next token refresh based on expiration time
                self._schedule_token_refresh(expires_in)

                return AccessToken(token=access_token, expires_on=time.time() + expires_in)
            except AuthenticationError as auth_err:
                raise auth_err
            except Exception as e:
                logger.error(f"Failed to get access token. Error: {e}")
                raise AuthenticationError(_ERROR_MESSAGE.GET_TOKEN_FAILED.value)

    def cleanup(self):
        """Clean up resources used by this credential.

        This method should be called when the credential is no longer needed
        to ensure the background refresh timer is properly stopped.
        """
        logger.info("Cleaning up UserTokenCredential resources")
        # Set the stop event to prevent any scheduled refreshes from executing
        self._stop_timer_event.set()

        # Cancel any scheduled refresh task
        if self._refresh_timer_task is not None:
            self._refresh_timer_task.cancel()
            self._refresh_timer_task = None
            logger.info("Cancelled scheduled token refresh")
