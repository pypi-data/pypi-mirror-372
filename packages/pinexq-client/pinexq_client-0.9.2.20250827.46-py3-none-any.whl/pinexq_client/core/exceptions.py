from httpx import Response, URL

from pinexq_client.core.model.error import ProblemDetails
from .model.sirenmodels import TEntity


class ClientException(Exception):
    """
    Base class for all exceptions that are thrown by the PinexQ client.
    """

    def __init__(self, message: str):
        self.message = message


class NotAvailableException(ClientException):
    """
    Exception that is thrown when an action or a link is not available.
    """


class ApiException(Exception):
    """
    Base class for all exceptions that are thrown by the PinexQ API.
    """
    status: int = None  # default status code, can be overridden in subclasses
    problem_details: ProblemDetails | None = None

    def __init__(self, message: str, problem_details: ProblemDetails | None = None):
        super().__init__(message)
        self.problem_details = problem_details

    def __str__(self) -> str:
        message = super().__str__()
        if self.problem_details:
            message += f"\n{self.problem_details}"
        return message


class TemporarilyNotAvailableException(ApiException):
    """
    Exception that is thrown when the API returns a 503 status code.

    """
    status: int = 503


class TooManyRequestsException(ApiException):
    """
    Exception that is thrown when the API returns a 429 status code.

    """
    status: int = 429


def raise_exception_on_error(message: str, response: TEntity | Response | ProblemDetails | URL | None):
    match response:
        case ProblemDetails() as problem_details:
            match problem_details.status:
                case 429:
                    raise TooManyRequestsException(message, problem_details)
                case 503:
                    raise TemporarilyNotAvailableException(message, problem_details)
                case _:
                    raise ApiException(message, problem_details)
        case Response() as http_response:
            match http_response.status_code:
                case 429:
                    raise TooManyRequestsException(message)
                case 503:
                    raise TemporarilyNotAvailableException(message)
                case _:
                    raise ApiException(message)
