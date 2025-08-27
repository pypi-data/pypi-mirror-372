"""Configure requests session for use by a client."""

import functools
import sys
from typing import Optional

from requests import Session
from requests.auth import AuthBase

from ..config import TendukeConfig


class SessionFactory:
    """Creates and configures the HTTP session for OIDC and API requests."""

    def __init__(
        self,
        config: TendukeConfig,
        app_name: str,
        app_version: str,
        sdk_name: str,
        sdk_version: str,
    ):
        """Construct an instance of the SessionFactory."""
        self._config = config
        self._user_agent = f"{app_name}/{app_version} {sdk_name}/{sdk_version} Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    def create(
        self,
        auth: Optional[AuthBase] = None,
    ):
        """Create and configures session.

        Args:
            auth: Authorization hook.
            timeout: Connect and read timeout values.
            proxies: Proxy definitions.

        Returns:
            A session configured to use the parameters passed in for all requests made using the
            session.
        """
        session = Session()
        session.headers.update({"User-Agent": self._user_agent})

        timeout = (self._config.http_timeout_seconds, self._config.http_timeout_seconds)

        proxies = {}
        if self._config.https_proxy:
            proxies["https"] = self._config.https_proxy

        session.request = functools.partial(  # type: ignore[method-assign]
            session.request, timeout=timeout, proxies=proxies
        )
        session.auth = auth
        return session
