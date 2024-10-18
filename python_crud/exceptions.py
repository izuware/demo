# exceptions 
#

class Error:
    """ Exceptions """

    class NotFound(Exception):
        """Raised when a requested resource is not found."""

    class MethodNotAllowed(Exception):
        """Raised when a request method is not allowed."""

    class BadRequest(Exception):
        """Raised when the request is malformed."""

    class InternalServerError(Exception):
        """Raised when there is an internal server error."""

    class NotAllowed(Exception):
        """Raised when authorization need"""

    class Conflict(Exception):
        """Raised when conflilct occurs"""
