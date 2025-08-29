
class APIError(Exception):
    """Raise this, not request exceptions."""
    pass


class APIClientError(APIError):
    """
    Raise this to indicate any http error that falls within the
    4xx class of http status codes.
    """
    pass


class APIServerError(APIError):
    """
    Raise this to indicate a Server Error
    """
    pass


class RecordNotFoundError(APIClientError):
    """The record was not found."""
    pass


class SecurityPermissionsException(APIClientError):
    """The API credentials have insufficient security permissions."""
    pass
