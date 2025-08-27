import logging
from enum import Enum, StrEnum
from typing import Any, Callable, Literal, Optional, Self, TypedDict, Union

from crypticorn_utils.errors import (
    ErrorLevel,
    ErrorType,
)
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import HTTPException as FastAPIHTTPException
from fastapi import Request, WebSocketException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

_logger = logging.getLogger("crypticorn")

class ExceptionDetail(BaseModel):
    """Exception details returned to the client."""

    message: Optional[str] = Field(None, description="An additional error message")
    code: str = Field(..., description="The unique error code")
    type: ErrorType = Field(..., description="The type of error")
    level: ErrorLevel = Field(..., description="The level of the error")
    status_code: int = Field(..., description="The HTTP status code")
    details: Any = Field(None, description="Additional details about the error")

exception_response = {
    "default": {"model": ExceptionDetail, "description": "Error response"}
}

_EXCEPTION_TYPES = Literal['http', 'websocket']

class ExceptionHandler:
    """This class is used to handle errors and exceptions. It is used to build exceptions and raise them.

    - Register the exception handlers to the FastAPI app.
    - Configure the instance with a callback to get the error object from the error identifier.
    - Build exceptions from error codes defined in the client code.

    Example for the client code implementation:

    ```python
    from crypticorn_utils import ExceptionHandler, BaseError

    class ErrorCodes(StrEnum):
        ...

    class Errors(BaseError):
        ...

    handler = ExceptionHandler(callback=Errors.from_identifier, type='http')
    ws_handler = ExceptionHandler(callback=Errors.from_identifier, type='websocket')

    handler.register_exception_handlers(app)

    @app.get("/")
    def get_root():
        raise handler.build_exception(ErrorCodes.UNKNOWN_ERROR)
    ```
    """

    def __init__(
        self,
        callback: Callable[[str], "BaseError"],
    ):
        """
        :param callback: The callback to use to get the error object from the error identifier.
        :param type: The type of exception to raise. Defaults to HTTP.
        """
        self.callback = callback

    def _http_exception(
        self, content: ExceptionDetail, headers: Optional[dict[str, str]] = None
    ) -> HTTPException:
        return HTTPException(
            detail=content.model_dump(mode="json"),
            headers=headers,
            status_code=content.status_code,
        )

    def _websocket_exception(self, content: ExceptionDetail) -> WebSocketException:
        return WebSocketException(
            reason=content.model_dump(mode="json"),
            code=content.status_code,
        )

    def build_exception(  # type: ignore[return]
        self,
        code: str,
        *, 
        message: Optional[str] = None,
        headers: Optional[dict[str, str]] = None,
        details: Any = None,
        type: _EXCEPTION_TYPES = 'http',
    ) -> Union[HTTPException, WebSocketException]:
        """Build an exception, without raising it.
        :param code: The error code to raise.
        :param message: The message to include in the error.
        :param headers: The headers to include in the error.
        :param details: The details to include in the error.
        :param type: The type of exception to raise. Defaults to HTTP.

        :return: The exception to raise, either an HTTPException or a WebSocketException.

        ```python
        @app.get("/")
        def get_root():
            raise handler.build_exception(ErrorCodes.UNKNOWN_ERROR)
        ```
        """
        error = self.callback(code)
        content = ExceptionDetail(
            message=message,
            code=error.identifier,
            type=error.type,
            level=error.level,
            status_code=error.http_code,
            details=details,
        )
        if type == 'http':
            return self._http_exception(content, headers)
        elif type == 'websocket':
            return self._websocket_exception(content)

    async def _general_handler(self, request: Request, exc: Exception) -> JSONResponse:
        """Default exception handler for all exceptions."""
        body = ExceptionDetail(
            message=str(exc),
            code="unknown_error",
            type=ErrorType.SERVER_ERROR,
            level=ErrorLevel.ERROR,
            status_code=500,
        )
        res = JSONResponse(
            status_code=body.status_code,
            content=body.model_dump(mode="json"),
            headers=None,
        )
        _logger.error(f"General error: {str(exc)}")
        return res

    async def _request_validation_handler(
        self, request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Exception handler for all request validation errors."""
        body = ExceptionDetail(
            message=str(exc),
            code="invalid_data_request",
            type=ErrorType.USER_ERROR,
            level=ErrorLevel.ERROR,
            status_code=400,
        )
        res = JSONResponse(
            status_code=body.status_code,
            content=body.model_dump(mode="json"),
            headers=None,
        )
        _logger.error(f"Request validation error: {str(exc)}")
        return res

    async def _response_validation_handler(
        self, request: Request, exc: ResponseValidationError
    ) -> JSONResponse:
        """Exception handler for all response validation errors."""
        body = ExceptionDetail(
            message=str(exc),
            code="invalid_data_response",
            type=ErrorType.USER_ERROR,
            level=ErrorLevel.ERROR,
            status_code=400,
        )
        res = JSONResponse(
            status_code=body.status_code,
            content=body.model_dump(mode="json"),
            headers=None,
        )
        _logger.error(f"Response validation error: {str(exc)}")
        return res

    async def _http_handler(self, request: Request, exc: HTTPException) -> JSONResponse:
        """Exception handler for HTTPExceptions. It unwraps the HTTPException and returns the detail in a flat JSON response."""
        res = JSONResponse(
            status_code=exc.status_code, content=exc.detail, headers=exc.headers
        )
        _logger.error(f"HTTP error: {str(exc)}")
        return res

    def register_exception_handlers(self, app: FastAPI):
        """Utility to register serveral exception handlers in one go. Catches Exception, HTTPException and Data Validation errors, logs them and responds with a unified json body.

        ```python
        handler.register_exception_handlers(app)
        ```
        """
        app.add_exception_handler(Exception, self._general_handler)
        app.add_exception_handler(FastAPIHTTPException, self._http_handler)
        app.add_exception_handler(
            RequestValidationError, self._request_validation_handler
        )
        app.add_exception_handler(
            ResponseValidationError, self._response_validation_handler
        )


class BaseError(Enum):
    """Base API error for the API."""

    @property
    def identifier(self) -> str:
        return self.value[0]

    @property
    def type(self) -> ErrorType:
        return self.value[1]

    @property
    def level(self) -> ErrorLevel:
        return self.value[2]

    @property
    def http_code(self) -> int:
        return self.value[3]

    @property
    def websocket_code(self) -> int:
        return self.value[4]

    @classmethod
    def from_identifier(cls, identifier: str) -> Self:
        return next(error for error in cls if error.identifier == identifier)


## Since enums don't support inheritance, you can copy these values to your own enum.

# class ErrorCodes(StrEnum):
#     UNKNOWN_ERROR = "unknown_error"
#     INVALID_DATA_REQUEST = "invalid_data_request"
#     INVALID_DATA_RESPONSE = "invalid_data_response"
#     OBJECT_ALREADY_EXISTS = "object_already_exists"
#     OBJECT_NOT_FOUND = "object_not_found"

# class Errors(BaseError):
    # UNKNOWN_ERROR = (
    #     ErrorCodes.UNKNOWN_ERROR,
    #     ErrorType.SERVER_ERROR,
    #     ErrorLevel.ERROR,
    #     status.HTTP_500_INTERNAL_SERVER_ERROR,
    #     status.WS_1011_INTERNAL_ERROR,
    # )
    # INVALID_DATA_REQUEST = (
    #     ErrorCodes.INVALID_DATA_REQUEST,
    #     ErrorType.USER_ERROR,
    #     ErrorLevel.ERROR,
    #     status.HTTP_422_UNPROCESSABLE_ENTITY,
    #     status.WS_1007_INVALID_FRAME_PAYLOAD_DATA,
    # )
    # INVALID_DATA_RESPONSE = (
    #     ErrorCodes.INVALID_DATA_RESPONSE,
    #     ErrorType.SERVER_ERROR,
    #     ErrorLevel.ERROR,
    #     status.HTTP_422_UNPROCESSABLE_ENTITY,
    #     status.WS_1007_INVALID_FRAME_PAYLOAD_DATA,
    # )
    # OBJECT_ALREADY_EXISTS = (
    #     ErrorCodes.OBJECT_ALREADY_EXISTS,
    #     ErrorType.USER_ERROR,
    #     ErrorLevel.ERROR,
    #     status.HTTP_409_CONFLICT,
    #     status.WS_1008_POLICY_VIOLATION,
    # )
    # OBJECT_NOT_FOUND = (
    #     ErrorCodes.OBJECT_NOT_FOUND,
    #     ErrorType.USER_ERROR,
    #     ErrorLevel.ERROR,
    #     status.HTTP_404_NOT_FOUND,
    #     status.WS_1008_POLICY_VIOLATION,
    # )
