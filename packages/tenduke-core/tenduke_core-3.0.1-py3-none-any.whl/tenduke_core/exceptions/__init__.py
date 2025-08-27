"""Exceptions raised from the library."""

from .api import (
    ApiError,
    BadRequestError,
    ConflictError,
    NotFoundError,
    TooManyRequestsError,
    map_error,
)

__all__ = [
    "ApiError",
    "BadRequestError",
    "ConflictError",
    "NotFoundError",
    "TooManyRequestsError",
    "map_error",
]
