from http import HTTPStatus

from fishjam._openapi_client.models import Error
from fishjam._openapi_client.types import Response


class HTTPError(Exception):
    """"""

    @staticmethod
    def from_response(response: Response[Error]):
        """@private"""

        if not response.parsed:
            raise RuntimeError("Got endpoint error reponse without parsed field")

        errors = response.parsed.errors

        match response.status_code:
            case HTTPStatus.BAD_REQUEST:
                return BadRequestError(errors)

            case HTTPStatus.UNAUTHORIZED:
                return UnauthorizedError(errors)

            case HTTPStatus.NOT_FOUND:
                return NotFoundError(errors)

            case HTTPStatus.SERVICE_UNAVAILABLE:
                return ServiceUnavailableError(errors)

            case _:
                return InternalServerError(errors)


class BadRequestError(HTTPError):
    def __init__(self, errors):
        """@private"""
        super().__init__(errors)


class UnauthorizedError(HTTPError):
    def __init__(self, errors):
        """@private"""
        super().__init__(errors)


class NotFoundError(HTTPError):
    def __init__(self, errors):
        """@private"""
        super().__init__(errors)


class ServiceUnavailableError(HTTPError):
    def __init__(self, errors):
        """@private"""
        super().__init__(errors)


class InternalServerError(HTTPError):
    def __init__(self, errors):
        """@private"""
        super().__init__(errors)


class MissingFishjamIdError(Exception):
    def __init__(self, message: str = "Missing Fishjam ID"):
        """@private"""
        super().__init__(message)
