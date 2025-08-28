class Error(Exception):
    pass


class SetupError(Error):
    """
    An error raised when something is missing or failing
    during set up. It includes an error message pointing
    to what is wrong.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"💥 {self.message}"
    

class AuthenticationError(Error):
    """
    An error raised when something went wrong during authentication.
    It includes an error message.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"💥 Authentication failed. {self.message}"


class ClientError(Error):
    """
    An error raised when a request to the API failed due to a client problem or bad request.
    It includes an HTTP status code and an error message.
    """

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"💥 {str(self.status_code)} {self.message}"


class ServerError(Error):
    """
    An error raised when a request to the API failed due to a server problem.
    It includes an HTTP status code and an error message.
    """

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"💥 {str(self.status_code)} {self.message}"
    

class RequestTimeoutError(Error):
    """
    Exception raised for request timeouts.
    """
    def __init__(self, message="Request timed out."):
        self.message = message

    def __str__(self):
        return f"💥 {self.message}"


class RequestFailedError(Error):
    """
    Exception raised for failed HTTP requests.
    """
    def __init__(self, message="Request failed to complete."):
        self.message = message

    def __str__(self):
        return f"💥 {self.message}"


class UnexpectedError(Error):
    """
    Exception raised for unexpected errors.
    """
    def __init__(self, message="An unexpected error has occurred."):
        self.message = message

    def __str__(self):
        return f"💥 {self.message}"