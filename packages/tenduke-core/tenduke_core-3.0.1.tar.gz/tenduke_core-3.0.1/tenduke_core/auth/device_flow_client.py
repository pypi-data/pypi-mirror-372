"""Helper to perform OAuth device flow."""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

from tenduke_core.http.session_factory import SessionFactory

from ..config import TendukeConfig
from ..exceptions.oauth import raise_error_from_error_response
from ..exceptions.validation import (
    DeviceCodeAuthorizationUrlMissingError,
    TokenUrlMissingError,
)
from .device_auth_response import DeviceAuthorizationResponse
from .oauth_client import OAuthClient
from .token_response import TokenResponse


def _device_authorization_request_parameters(client_id, client_secret, scopes):
    """Build parameters for authorization request."""
    params = {
        "client_id": client_id,
        "scope": scopes,
    }
    if client_secret:
        params["client_secret"] = client_secret
    return params


def _poll_params(client_id, device_code, client_secret: Optional[str] = None):
    """Build parameters for token request."""
    params = {
        "client_id": client_id,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": device_code,
    }
    if client_secret:
        params["client_secret"] = client_secret
    return params


class DeviceFlowClient(OAuthClient):
    """Helper class to perform OAuth device flow."""

    class VerificationUri:
        """Verification URI/URL handling.

        As some implementations of device flow use URI and some use URL in the parameter name,
        we need to check for both.
        The logic in making the requests is that we should use the '_complete' variant of the URI
        if it is present/populated and use the incomplete version if it is not.
        """

        def __init__(self):
            """Construct a VerificationUri instance."""
            self._verification_uri_complete = ""
            self._verification_url_complete = ""
            self._verification_uri = ""
            self._verification_url = ""

        def read_from_dict(self, data: dict[str, str]):
            """Read the verification uri details from a dictionary.

            RFC8628 specifies verification_uri. At least one identity provider in the
            wild sends verification_url.
            Outside of this class, we don't need to worry about verification_url, this
            class will read whichever is present.

            Args:
                data: The contents of the Device Authorization Response.
            """
            self._verification_uri = data.get("verification_uri", "")
            self._verification_url = data.get("verification_url", "")
            self._verification_uri_complete = data.get("verification_uri_complete", "")
            self._verification_url_complete = data.get("verification_url_complete", "")

        def uri(self) -> str:
            """Return the token poll uri."""
            return self._verification_uri or self._verification_url

        def uri_complete(self) -> str:
            """Return the token poll complete uri."""
            return (
                self._verification_uri_complete
                or self._verification_url_complete
                or self._verification_uri
                or self._verification_url
            )

    def __init__(self, config: TendukeConfig, session_factory: SessionFactory):
        """Construct an instance of the DeviceFlowClient.

        Args:
            config:
                Configuration parameters for interacting with the OAuth / Open ID Authorization
                Server.
            session_factory:
                Used to create requests Session configured with the settings from config and with
                the configured User-Agent header value.
        """
        self._device_code = None
        self._expires_at = None
        self._user_code: str = ""
        self._interval = 5
        self._verification_uri = self.VerificationUri()
        super().__init__(config, session_factory)

    def authorize(self) -> DeviceAuthorizationResponse:
        """Make the authorization request and return the details to display to the user.

        Returns:
            A DeviceAuthorizationResponse object containing the code and uri needed to fetch a
            token.

        Raises:
            ValueError: Required configuration item idp_oauth_device_code_url was missing.
            OAuth2Error: Device Authorization Request was unsuccessful.
        """
        params = _device_authorization_request_parameters(
            self.config.idp_oauth_client_id,
            self.config.idp_oauth_client_secret,
            self.config.idp_oauth_scope,
        )
        url = self.config.idp_oauth_device_code_url
        if not url:
            raise DeviceCodeAuthorizationUrlMissingError()

        response = self.session.post(url, params)
        if not response.ok:
            raise_error_from_error_response(response)
        response_json = response.json()
        self._parse_authorize_response(response_json)
        return DeviceAuthorizationResponse(
            self._user_code,
            self._verification_uri.uri(),
            self._verification_uri.uri_complete(),
        )

    def _parse_authorize_response(self, data):
        self._device_code = data.get("device_code")
        if "expires_in" in data:
            seconds = data["expires_in"]
            self._expires_at = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        self._user_code = data.get("user_code", "")
        self._interval = data.get("interval") or 5
        self._verification_uri.read_from_dict(data)

    async def poll_for_token_async(self):
        """Poll for an OAuth device flow token.

        The method waits for the specified interval between attempts.
        This method is asynchronous (non-blocking).

        Raises:
            OAuth2Error: Device Access Token Request was unsuccessful.
        """
        poll = True
        while poll:
            response = self._make_poll_request()
            if response.ok:
                poll = False
                token = TokenResponse.from_api(response.json())
                self.token = token
                return token

            poll = await self._handle_error_token_response_async(response)

    def poll_for_token(self):
        """Poll for an OAuth device flow token.

        The method waits for the specified interval between attempts.
        This method is synchronous (blocking).

        Raises:
            OAuth2Error: Device Access Token Request was unsuccessful.
        """
        return asyncio.run(self.poll_for_token_async())

    def _make_poll_request(self):
        params = _poll_params(
            self.config.idp_oauth_client_id,
            self._device_code,
            self.config.idp_oauth_client_secret,
        )
        url = self.config.idp_oauth_token_url
        if not url:
            raise TokenUrlMissingError()
        return self.session.post(url, data=params)

    async def _handle_error_token_response_async(self, response):
        json = response.json()
        error = json.get("error")
        error_code = json.get("error_code")

        continue_codes = ["authorization_pending", "slow_down"]
        if error in continue_codes or error_code in continue_codes:
            if "slow_down" in (error, error_code):
                self._interval += 5
            await asyncio.sleep(self._interval)
            # signal loop in caller to keep polling
            return True

        return raise_error_from_error_response(response)
