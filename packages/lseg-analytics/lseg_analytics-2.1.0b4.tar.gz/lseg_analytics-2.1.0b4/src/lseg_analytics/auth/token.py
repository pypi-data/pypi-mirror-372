from lseg_analytics._client.client import Client

__all__ = ["set_token"]


def set_token(token: str):
    """Set Authorization Bearer token"""

    Client()._config.headers_policy.add_header("Authorization", "Bearer " + token)
