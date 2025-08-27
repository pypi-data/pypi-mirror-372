"""OAuth2 Errors."""

from typing import Optional

from requests import Response


class OAuth2Error(IOError):
    """Base exception for errors encountered during OAuth flows."""

    error: str = "unknown error"
    status_code: int = 400
    description: str = ""

    def __init__(
        self, error: Optional[str] = None, status_code: Optional[int] = None, description: str = ""
    ):
        """Construct an OAuth2Error instance.

        Args:
            error: error code.
            status_code: HTTP Status code of error response.
            description: Textual description of the error.
        """
        if status_code is not None:
            self.status_code = status_code
        self.error = error or "unknown error"
        self.description = description


class AccessDeniedError(OAuth2Error):
    """The resource owner or authorization server denied the request."""

    error = "access_denied"


class AuthenticationFailed(OAuth2Error):
    """No authorization response was received."""

    error = "Authentication failed"
    description = "Failed to retrieve token using PKCE flow."


class ExpiredTokenError(OAuth2Error):
    """
    Device flow device_code has expired.

    The "device_code" has expired, and the device authorization session has concluded.
    The client MAY commence a new device authorization request but SHOULD wait for user
    interaction before restarting to avoid unnecessary polling.
    """

    error = "expired_token"


class InvalidRequestError(OAuth2Error):
    """
    Request is invalid.

    The request is missing a required parameter, includes an invalid
    parameter value, includes a parameter more than once, or is
    otherwise malformed.
    """

    error = "invalid_request"


class InvalidClientError(OAuth2Error):
    """
    Client authentication failed.

    Client authentication failed (e.g. unknown client, no
    client authentication included, or unsupported
    authentication method). The authorization server MAY
    return an HTTP 401 (Unauthorized) status code to indicate
    which HTTP authentication schemes are supported.  If the
    client attempted to authenticate via the "Authorization"
    request header field, the authorization server MUST
    respond with an HTTP 401 (Unauthorized) status code and
    include the "WWW-Authenticate" response header field
    matching the authentication scheme used by the client.
    """

    error = "invalid_client"


class InvalidGrantError(OAuth2Error):
    """
    Authorization grant invalid.

    The provided authorization grant (e.g., authorization
    code, resource owner credentials) or refresh token is
    invalid, expired, revoked, does not match the redirection
    URI used in the authorization request, or was issued to
    another client.
    """

    error = "invalid_grant"


class UnauthorizedClientError(OAuth2Error):
    """The authenticated client is not authorized to use this authorization grant type."""

    error = "unauthorized_client"


class UnsupportedGrantTypeError(OAuth2Error):
    """The authorization grant type is not supported by the authorization server."""

    error = "unsupported_grant_type"


class UnsupportedResponseTypeError(OAuth2Error):
    """The requested response type is not supported by the endpoint."""

    error = "unsupported_response_type"


class InvalidScopeError(OAuth2Error):
    """The requested scope is invalid, unknown, or malformed."""

    error = "invalid_scope"


class ServerError(OAuth2Error):
    """Server error.

    The authorization server encountered an unexpected condition that prevented
    it from fulfilling the request.
    """

    error = "server_error"


class TemporarilyUnavailableError(OAuth2Error):
    """Temporarily unavailable.

    The authorization server is currently unable to handle the request due to a temporary
    overloading or maintenance of the server.
    """

    error = "temporarily_unavailable"


class InvalidTokenError(OAuth2Error):
    """The access token provided is expired, revoked, malformed, or invalid for other reasons."""

    error = "invalid_token"


class InsufficientScopeError(OAuth2Error):
    """The requested scope is invalid, unknown, or malformed."""

    error = "insufficient_scope"


_error_code_map = {
    "access_denied": AccessDeniedError,
    "expired_token": ExpiredTokenError,
    "insufficient_scope": InsufficientScopeError,
    "invalid_client": InvalidClientError,
    "invalid_grant": InvalidGrantError,
    "invalid_request": InvalidRequestError,
    "invalid_scope": InvalidScopeError,
    "invalid_token": InvalidTokenError,
    "server_error": ServerError,
    "temporarily_unavailable": TemporarilyUnavailableError,
    "unauthorized_client": UnauthorizedClientError,
    "unsupported_grant_type": UnsupportedGrantTypeError,
    "unsupported_response_type": UnsupportedResponseTypeError,
}


def raise_error_from_error_response(response: Response) -> OAuth2Error:
    """Raise an error matching the failed response to an OAuth request.

    Args:
        response: The response from the HTTP request to be mapped to an error.

    Returns:
        OAuth2Error matching the status_code of the response object.
    """
    json = response.json()
    error = json.get("error")
    error_code = json.get("error_code")
    error_description = json.get("error_description")

    if error in _error_code_map:
        raise _error_code_map[error](
            status_code=response.status_code, description=error_description
        )

    if error_code in _error_code_map:
        raise _error_code_map[error_code](
            status_code=response.status_code, description=error_description
        )

    error_to_report = error or error_code or "unkown error"
    description = error_description or "An unknown error has been encountered."
    raise OAuth2Error(
        error=error_to_report,
        status_code=response.status_code,
        description=description,
    )
