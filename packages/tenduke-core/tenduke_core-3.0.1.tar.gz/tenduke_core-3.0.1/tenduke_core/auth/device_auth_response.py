"""Data returned in Device Authorization Response."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DeviceAuthorizationResponse:
    """
    Data from Device Authorization Response.

    Callers should use this data to initiate the user interaction phase
    of the Device Authorization Grant flow, before or simultaneously with
    starting polling for the token.

    See https://www.rfc-editor.org/rfc/rfc8628#section-3.2.

    Attributes:
        user_code: The end-user verification code.
        uri:
            The end-user verification URI on the authorization server. The URI should be short and
            easy to remember as end users will be asked to manually type it into their user agent.
        uri_complete:
            A verification URI that includes the "user_code" (or other information with the same
            function as the "user_code"), which is designed for non-textual transmission.
    """

    user_code: str
    uri: str
    uri_complete: Optional[str]
