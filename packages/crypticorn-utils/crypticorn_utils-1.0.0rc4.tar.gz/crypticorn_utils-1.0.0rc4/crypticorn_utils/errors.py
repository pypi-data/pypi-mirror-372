"""Comprehensive error handling system defining various API error types, HTTP exceptions, and error content structures."""

from enum import StrEnum


class ErrorType(StrEnum):
    """Type of the API error."""

    USER_ERROR = "user error"
    """user error by people using our services"""
    EXCHANGE_ERROR = "exchange error"
    """re-tryable error by the exchange or network conditions"""
    SERVER_ERROR = "server error"
    """server error that needs a new version rollout for a fix"""
    NO_ERROR = "no error"
    """error that does not need to be handled or does not affect the program or is a placeholder."""


class ErrorLevel(StrEnum):
    """Level of the API error."""

    ERROR = "error"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
