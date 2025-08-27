"""Token response data model.

Authorization grant access token responses from Open ID Connect / OAuth compliant
IDPs will contain some or all of the fields in this class.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

from ..base_model import Model


@dataclass
class TokenResponse(Model):
    """Token response data model.

    https://www.rfc-editor.org/rfc/rfc6749#section-4.2.2

    Attributes:
        access_token: The access token issued by the authorization server.
        token_type: The type of the token issued.
        expires_in: The lifetime in seconds of the access token.
        expires_at:
            The datetime when the token will expire Derived from expires_in and the current system
            time when the token was received.
        refresh_token: The refresh token, which can be used to obtain new access tokens.
        id_token: ID Token value associated with the authenticated session.
    """

    access_token: str
    token_type: str
    expires_in: int
    expires_at: datetime = field(init=False)
    refresh_token: Optional[str] = None
    # id_token is not mandatory in the RFC 6749 Access Token Response
    # but Open ID Connect id_token is required for ID Token auth
    id_token: Optional[str] = None

    def __post_init__(self):
        """Initialize expires_at based on expires_in and current time."""
        self.expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.expires_in)
