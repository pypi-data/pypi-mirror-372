"""OAuth / Open ID Connect client."""

from dataclasses import dataclass

from tenduke_core.http.session_factory import SessionFactory

# conditional import for Python versions <= 3.10
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone

    UTC = timezone.utc

from datetime import datetime
from typing import Optional, TypeVar

import jwt
from jwt import PyJWKClient

from ..config import TendukeConfig
from ..exceptions.oauth import raise_error_from_error_response
from ..exceptions.validation import IdTokenMissingError, UserInfoUrlMissingError
from .auth_provider import IdTokenAuth
from .token_response import TokenResponse
from .user_info import UserInfo

T = TypeVar("T", bound="IdToken")


def _is_expired(id_token, leeway):
    if id_token is None:
        return None
    seconds_to_expiry = (id_token.expiry - datetime.now(UTC)).total_seconds()
    return seconds_to_expiry < leeway


@dataclass
class IdToken:
    """Holds details of id_token.

    Attributes:
        token: JWT content of id_token.
        expiry: Expiry datetime of the IdToken. 'exp' claim of JWT as a datetime.
    """

    token: str
    expiry: datetime

    @classmethod
    def from_token(
        cls: type[T],
        token: TokenResponse,
        jwks_client: Optional[PyJWKClient],
        client_id: Optional[str],
    ) -> Optional[T]:
        """Parse id_token and retrieve expiry datetime.

        Args:
            token: id_token JWT.
            jwks_client:
                jwt.PyJWKClient initialized with the jwks url of the idp the id_token is from.
            client_id: The client_id of the application the id_token was issued to.

        Returns:
            An IdToken object with expiry datetime set if there is a token, and it can be parsed;
            otherwise None.
        """
        if token.id_token is not None and jwks_client is not None:
            pub_key = jwks_client.get_signing_key_from_jwt(token.id_token)
            id_token_claims = jwt.decode(
                token.id_token,
                pub_key.key,
                algorithms=["RS256"],
                audience=client_id,
                options={"verify_exp": False},
            )
            expiry = datetime.fromtimestamp(id_token_claims["exp"], UTC)
            return cls(token.id_token, expiry)
        return None


class OAuthClient:
    """OAuth / Open ID Connect client."""

    def __init__(self, config: TendukeConfig, session_factory: SessionFactory):
        """
        Construct an instance of the OAuth Client.

        Args:
            config:
                Configuration parameters for interacting with the OAuth / Open ID Authorization
                Server.
            session_factory:
                Used to create requests Session configured with the settings from config and with
                the configured User-Agent header value.
        """
        self.config = config
        self._idp_jwks_client = None
        if config.idp_jwks_uri:
            self._idp_jwks_client = PyJWKClient(
                config.idp_jwks_uri, cache_keys=True, lifespan=345000
            )
        self._try_to_refresh = True
        self._token: Optional[TokenResponse] = None
        self._id_token: Optional[IdToken] = None
        self.session = session_factory.create()

    @property
    def token(self) -> Optional[TokenResponse]:
        """The current token response."""
        return self._token

    @token.setter
    def token(self, value: TokenResponse):
        if value.id_token is not None:
            self._id_token = IdToken.from_token(
                value, self._idp_jwks_client, self.config.idp_oauth_client_id
            )
        self._try_to_refresh = value.refresh_token is not None and value.id_token is not None
        self._token = value

    @property
    def id_token(self) -> Optional[str]:
        """The current identity token (if any)."""
        if not self._token:
            return None
        self._refresh_token()
        return self._id_token.token if self._id_token else None

    def get_user_info(self) -> UserInfo:
        """Retrieve the details of the user from the userinfo endpoint.

        Returns:
            The information for the authenticated user.

        Raises:
            ValueError: User info URL missing from configuration.
            OAuth2Error: The user info request was unsuccessful.
        """
        headers = {"Authorization": f"Bearer {self._token.access_token}"} if self._token else {}
        if not self.config.idp_userinfo_url:
            raise UserInfoUrlMissingError()

        response = self.session.get(self.config.idp_userinfo_url, headers=headers)
        if not response.ok:
            raise_error_from_error_response(response)

        info = UserInfo.from_api(response.json())
        return info

    def auth(self) -> IdTokenAuth:
        """Get an authorization implementation based on the current identity.

        Returns:
            An authorization provider hook that sets the authorization header of HTTP requests
            using the current id_token.
        """
        if not self.id_token:
            raise IdTokenMissingError()

        return IdTokenAuth(lambda: self.id_token or "")

    def _can_refresh(self):
        return (
            self._try_to_refresh
            and self._token is not None
            and self._token.refresh_token is not None
            and self.config.idp_oauth_token_url is not None
        )

    def _refresh_token(self):
        # if we know the expiry of the id_token, check it is still valid
        # if it is close to expiry and with have a token url, see if we can get a new one
        is_expired = _is_expired(self._id_token, self.config.token_refresh_leeway_seconds)
        can_refesh = self._can_refresh()

        # type checking disabled for members already checked for None in
        #  _is_expired and _can_refresh
        if is_expired and can_refesh:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self._token.refresh_token,  # pyright: ignore[reportOptionalMemberAccess]
                "client_id": self.config.idp_oauth_client_id,
            }
            if self.config.idp_oauth_client_secret:
                data["client_secret"] = self.config.idp_oauth_client_secret
            response = self.session.post(self.config.idp_oauth_token_url, data=data)  # pyright: ignore[reportArgumentType]
            if response.ok:
                token = TokenResponse.from_api(response.json())
                self.token = token
