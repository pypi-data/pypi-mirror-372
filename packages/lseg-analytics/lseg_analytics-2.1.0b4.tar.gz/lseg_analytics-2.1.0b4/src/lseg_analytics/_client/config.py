"""Library-wide configuration"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from dotenv import load_dotenv

PREFIX = "LSEG_ANALYTICS_"
AUTH_PREFIX = f"{PREFIX}AUTH_"
HEADERS_PREFIX = "HTTP_HEADER_"
DEFAULT_SPACE = "Anonymous"


@dataclass
class MachineAuthConfig:
    """Machine account configuration object"""

    client_id: str
    client_secret: str
    token_endpoint: str
    scopes: Optional[List[str]] = None


@dataclass
class UserAuthConfig:
    """User account configuration object"""

    client_id: str
    authority: str
    redirect_uri: str
    scopes: Optional[List[str]] = None


@dataclass
class Config:
    """Configuration object"""

    base_url: str
    username: Optional[str] = None
    headers: Optional[Dict] = None

    machine_auth: Optional[MachineAuthConfig] = None
    user_auth: Optional[UserAuthConfig] = None


def load_config() -> Config:
    """Create configuration object from the environment variables"""

    load_dotenv()

    headers = {
        key.split(HEADERS_PREFIX).pop().replace("_", "-"): value
        for key, value in os.environ.items()
        if key.startswith(HEADERS_PREFIX)
    }

    machine_auth = None
    user_auth = None
    if os.getenv(f"{AUTH_PREFIX}CLIENT_ID") and os.getenv(f"{AUTH_PREFIX}CLIENT_SECRET"):
        machine_auth = MachineAuthConfig(
            client_id=os.getenv(f"{AUTH_PREFIX}CLIENT_ID"),
            client_secret=os.getenv(f"{AUTH_PREFIX}CLIENT_SECRET"),
            token_endpoint=os.getenv(
                f"{AUTH_PREFIX}TOKEN_ENDPOINT", "https://login.ciam.refinitiv.com/as/token.oauth2"
            ),
            scopes=os.getenv(f"{AUTH_PREFIX}SCOPES", "trapi.data.quantitative-analytics.read").split(","),
        )

    elif os.getenv(f"{AUTH_PREFIX}USE_USER_ACCOUNT"):
        user_auth = UserAuthConfig(
            client_id=os.getenv(f"{AUTH_PREFIX}APP_ID", "6a863f12-2acd-4962-8edc-8504458f9524"),
            authority=os.getenv(f"{AUTH_PREFIX}AUTHORITY", "login.ciam.refinitiv.com"),
            redirect_uri=os.getenv(f"{AUTH_PREFIX}REDIRECT_URI", "http://localhost:3000"),
            scopes=os.getenv(f"{AUTH_PREFIX}SCOPES", "trapi.data.quantitative-analytics.read").split(","),
        )

    return Config(
        base_url=os.getenv(f"{PREFIX}BASE_URL", "https://api.analytics.lseg.com"),
        username=os.getenv(f"{PREFIX}USERNAME"),
        headers=headers,
        machine_auth=machine_auth,
        user_auth=user_auth,
    )
