# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from http import HTTPStatus


class ClientError(Exception):
    """Base class for exceptions in joblib."""

    def __init__(self, message, error=None, error_code=None):
        self.message = message
        self.error = error
        self.error_code = error_code

    def __str__(self):
        return str(self.message) + ("\nError code: " + str(self.error_code) if self.error_code else "") + ("\nError: " + str(self.error) if self.error is not None else "")


class BadRequestError(ClientError):
    """Exception raised for invalid input to joblib."""

    def __init__(self, message, error=None):
        super().__init__(message, error=error, error_code=HTTPStatus.BAD_REQUEST.value)


class ObjectNotFoundError(ClientError):
    """Exception raised when reuested object could not be found."""

    def __init__(self, message, error=None):
        super().__init__(message, error=error, error_code=HTTPStatus.NOT_FOUND.value)


class DependentServiceError(ClientError):
    """Exception raised when call to dependent services fail."""

    def __init__(self, message, response, error=None):
        self.response = response
        message = "{} ({} {})\nStatus code: {}, body: {}".format(message, response.request.method, response.request.url, response.status_code,
                                                                 response.text if response.apparent_encoding is not None else "[binary content, " + str(len(response.content)) + " bytes]")
        super().__init__(message, error=error, error_code=response.status_code)


class MissingValueError(ClientError, ValueError):
    def __init__(self, field, error=None):
        super().__init__("Value for {} is not provided.".format(
            field), error, error_code=HTTPStatus.BAD_REQUEST.value)


class InvalidInputError(ClientError, ValueError):
    def __init__(self, field, error=None):
        super().__init__("The value provided for {} is invalid.".format(
            field), error, error_code=HTTPStatus.BAD_REQUEST.value)


class UnexpectedTypeError(ClientError, ValueError):
    def __init__(self, field, expected_type, actual_type):
        super().__init__("Unexpected type of '{}' is specified, expected: {}, actual: '{}'.".format(
            field, expected_type, actual_type), error_code=HTTPStatus.BAD_REQUEST.value)


class UnsupportedOperationError(ClientError):
    """Exception raised for unsupported operation is requested."""

    def __init__(self, message=None, operation_name=None, error=None):
        if message is None:
            message = "The requested operation({}) is not supported.".format(
                operation_name)
        super().__init__(message, error=error, error_code=HTTPStatus.METHOD_NOT_ALLOWED.value)


class NotImplementedError(ClientError):
    """Exception raised for operation requested is not yet implemented."""

    def __init__(self, operation_name, error=None):
        super().__init__("The requested operation({}) is not yet implemented.".format(
            operation_name), error=error, error_code=HTTPStatus.NOT_IMPLEMENTED.value)


class MaxRetryError(ClientError):
    """Exception raised if requested operation did not succeed even after retries."""

    def __init__(self, operation_name, error=None):
        super().__init__("Max retries exceeded for the requested operation {}.".format(
            operation_name), error=error)


class ServiceUnavailableError(ClientError):
    """Exception raised when sufficient resources are not available to process the request."""

    def __init__(self, response=None, error=None, message=None):
        if not message:
            message = "Sufficient resources are not available to process the request ({} {}).".format(
                response.request.method, response.request.url)
        if response:
            error = response.text if response.apparent_encoding is not None else "[binary content, " + str(
                len(response.content)) + " bytes]"
        super().__init__(message, error=error, error_code=HTTPStatus.SERVICE_UNAVAILABLE.value)


class DatabaseError(ClientError):
    """Exception raised when interaction with database fails."""

    def __init__(self, message, error=None):
        super().__init__(message, error=error)


class AuthenticationError(ClientError):
    """Exception raised when user tried to access with invalid credentials."""

    def __init__(self, message, error=None):
        super().__init__(message, error=error)
