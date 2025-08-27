"""Error types associated with a repsonse from a 10Duke API."""

from typing import Optional, TypeVar

from requests import Response
from requests.exceptions import JSONDecodeError


class ApiError(IOError):
    """
    Base exception for exception relating to 10Duke API requests.

    May be raised directly if there was an ambiguous exception that occurred
    while handling your api request.
    """

    def __init__(
        self, uri: Optional[str] = None, response: Optional[Response] = None, *args, **kwargs
    ):
        """Construct an ApiError.

        Args:
            uri: The URI that was called that yielded the error response.
            response: HTTP response from API that is in error.
        """
        # for a number of problems, the issue can be diagnosed from the requested uri
        self.uri = uri
        # if we were passed a response argument, get any details from it
        # that might help work out what went wrong
        response = response
        self.status_code = None
        self.reason = None
        self.code = None
        self.error = None
        self.description = None
        if response is not None:
            self.status_code = response.status_code
            self.reason = response.reason
            self._process_response_body(response)

        super().__init__(*args, **kwargs)

    def _process_response_body(self, response):
        try:
            json = response.json()
        except JSONDecodeError:
            json = {}

        self.code = json.get("code") or self.status_code
        self.error = json.get("error") or self.reason
        self.description = json.get("description")

    def __str__(self):
        """Make a string representation of the error, including any details from the HTTP response body."""
        return f"{super().__str__()} [{self.uri}] - {self.code}: {self.error} : {self.description or ''}"


class NotFoundError(ApiError):
    """The API HTTP request returned NotFound."""


class BadRequestError(ApiError):
    """The API HTTP request returned BadRequest."""


class ConflictError(ApiError):
    """The API HTTP request returned Contention."""


class TooManyRequestsError(ApiError):
    """The API HTTP request returned Too Many Requests."""


T_co = TypeVar("T_co", bound="ApiError", covariant=True)

ERROR_MAP: dict[int, type] = {
    400: BadRequestError,
    404: NotFoundError,
    409: ConflictError,
    429: TooManyRequestsError,
}


def map_error(code: int) -> type:
    """Map HTTP Status Code to 10Duke API Error.

    Args:
        code: HTTP status_code

    Returns:
        ApiError matching the status_code or the base ApiError if the code is
        unexpected.
    """
    return ERROR_MAP.get(code, ApiError)
