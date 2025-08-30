"""Custom wrapper around requests"""

from __future__ import annotations

import requests

from allianceauth.services.hooks import get_extension_logger

from eveprices import __url__, __version__, app_name

logger = get_extension_logger(__name__)


def get(url: str, *, headers: dict[str, str] | None = None) -> requests.Response:
    """
    Wrapper around `requests.get`
    """

    if not headers:
        headers = {}
    headers["User-Agent"] = get_user_agent()

    r = requests.get(
        url,
        headers=headers,
        timeout=5,
    )

    logger.debug("%d %s", r.status_code, r.text)

    if r.status_code >= 400:
        logger.error("Error raised when querying data from Janice %s", r.text)
        raise RequestError from r.raise_for_status()

    return r


def post(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    data: str | None = None,
) -> requests.Response:
    """
    Wrapper around `requests.post`
    """

    if not headers:
        headers = {}
    headers["User-Agent"] = get_user_agent()

    r = requests.post(url, headers=headers, data=data, timeout=1)

    logger.debug("%d %s", r.status_code, r.text)

    if r.status_code >= 400:
        logger.error("Error raised when querying data from Janice %s", r.text)
        raise RequestError from r.raise_for_status()

    return r


class RequestError(Exception):
    """Exception raised when the provider returned an error code"""


def get_user_agent() -> str:
    """
    Returns a header to be used in every request for identification
    """
    return f"{app_name}/{__version__} (dev discord contact: avatarofkhain; +{__url__})"
