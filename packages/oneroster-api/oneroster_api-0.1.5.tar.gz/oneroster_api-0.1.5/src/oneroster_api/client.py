"""OneRoster Client instance."""

import json
import logging
import time
from base64 import b64encode
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

_base_url: str = None
_encoded_str: str = None
_token_path: Path = None


def set_credentials(
    base_url: str,
    client_id: str,
    client_secret: str,
    credential_path: Path = Path("oneroster_credentials.json"),
) -> None:
    """Setup credentials and needed info for token generation and requests."""
    global _base_url, _encoded_str, _token_path
    _base_url = base_url
    auth_str: str = f"{client_id}:{client_secret}"
    _encoded_str = b64encode(auth_str.encode()).decode()
    _token_path = credential_path


def get_request(endpoint: str, params: dict | None = None) -> requests.Response:
    """Get Request."""
    if _encoded_str is None or _base_url is None:
        error_msg: str = "Credentials not provided. Please run set_credentials() and provide base url, client id and secret."
        raise RuntimeError(
            error_msg,
        )
    token = get_valid_token()
    url = f"{_base_url}/api/oneroster/v1p1/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    resp = requests.get(url=url, headers=headers, params=params, timeout=30)
    return resp


def get_access_token() -> requests.Response:
    """Retrieves access token."""
    token_url = f"{_base_url}/oauth/token"
    headers = {
        "Authorization": f"Basic {_encoded_str}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data: dict = {
        "grant_type": "client_credentials",
    }
    resp = requests.post(
        url=token_url,
        headers=headers,
        data=data,
        timeout=30,
    )
    resp.raise_for_status()
    logger.info("Retrieved new OneRoster Token")
    return resp


def get_valid_token() -> str:
    """Checks if there is a json credentials."""
    if _token_path.exists():
        with _token_path.open("r") as file:
            token_data = json.load(file)
        if time.time() < token_data["expiration"]:
            logger.debug("OneRoster Access token on file still good.")
            return token_data["access_token"]
        logger.debug("OneRoster Access token on file is expired.")
    resp = get_access_token()
    token_data = {
        "access_token": resp.json()["access_token"],
        "expiration": time.time() + resp.json()["expires_in"],
    }
    with _token_path.open("w") as file:
        json.dump(token_data, file, indent=4)
    logger.debug("OneRoster Access token saved to file.")
    return token_data["access_token"]
