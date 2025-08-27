import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class HaizeAPIError(Exception):
    """Base exception for all Haize SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        self.headers = headers


class InternalServerError(HaizeAPIError):
    """Raised when the server encounters an internal error (500)."""

    def __init__(
        self,
        message: str = "Something went wrong. Please try again later.",
        response_body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            message, status_code=500, response_body=response_body, headers=headers
        )


class NotFoundError(HaizeAPIError):
    """Raised when a requested resource is not found (404)."""

    def __init__(
        self,
        message: str = "Resource not found",
        resource_name: Optional[str] = None,
        resource_id: Optional[str] = None,
        response_body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        if resource_name and resource_id:
            message = f"{resource_name} with id {resource_id} not found"
        super().__init__(
            message, status_code=404, response_body=response_body, headers=headers
        )
        self.resource_name = resource_name
        self.resource_id = resource_id


class BadRequestError(HaizeAPIError):
    """Raised when the request is malformed or invalid (400)."""

    def __init__(
        self,
        message: str = "Bad request",
        response_body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            message, status_code=400, response_body=response_body, headers=headers
        )


class UnprocessableRequestError(HaizeAPIError):
    """Raised when the request is well-formed but cannot be processed (422)."""

    def __init__(
        self,
        message: str = "Unprocessable request",
        response_body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            message, status_code=422, response_body=response_body, headers=headers
        )


class UnauthorizedError(HaizeAPIError):
    """Raised when authentication is required or has failed (401)."""

    def __init__(
        self,
        message: str = "Unauthorized",
        response_body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            message, status_code=401, response_body=response_body, headers=headers
        )


class ForbiddenError(HaizeAPIError):
    """Raised when the user doesn't have permission to access a resource (403)."""

    def __init__(
        self,
        message: str = "Forbidden",
        action: Optional[str] = None,
        resource_group: Optional[str] = None,
        resource_subgroup: Optional[str] = None,
        response_body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        if action and resource_group:
            resource_type = resource_group
            if resource_subgroup:
                resource_type += f".{resource_subgroup}"
            message = f"User does not have the {action} permission on resources of type {resource_type}"
        super().__init__(
            message, status_code=403, response_body=response_body, headers=headers
        )
        self.action = action
        self.resource_group = resource_group
        self.resource_subgroup = resource_subgroup


def parse_error_response(
    status_code: int,
    response_text: str,
    headers: Optional[Dict[str, str]] = None,
) -> HaizeAPIError:
    """Parse an error response from the API and return the appropriate exception.

    Args:
        status_code: HTTP status code
        response_text: Raw response text from the API
        headers: Response headers

    Returns:
        Appropriate HaizeAPIError subclass based on status code and response content
    """
    detail = response_text
    try:
        error_data = json.loads(response_text)
        if isinstance(error_data, dict):
            detail = error_data.get("detail", response_text)
    except (json.JSONDecodeError, ValueError):
        logger.debug("Failed to parse error response: %s", response_text)

    if status_code == 400:
        return BadRequestError(
            message=detail, response_body=response_text, headers=headers
        )
    elif status_code == 401:
        return UnauthorizedError(
            message=detail, response_body=response_text, headers=headers
        )
    elif status_code == 403:
        return ForbiddenError(
            message=detail, response_body=response_text, headers=headers
        )
    elif status_code == 404:
        return NotFoundError(
            message=detail, response_body=response_text, headers=headers
        )
    elif status_code == 422:
        return UnprocessableRequestError(
            message=detail, response_body=response_text, headers=headers
        )
    elif status_code >= 500:
        return InternalServerError(
            message=detail, response_body=response_text, headers=headers
        )
    else:
        return HaizeAPIError(
            message=detail,
            status_code=status_code,
            response_body=response_text,
            headers=headers,
        )
