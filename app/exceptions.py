class APIKeyException(Exception):
    """
    Exception raised when the API key is missing or invalid.

    Attributes:
        message (str): A description of the error.
    """
    def __init__(self, message: str = "Invalid or missing API key") -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"APIKeyException: {self.message}"


class ImageNotFoundException(Exception):
    """
    Exception raised when the requested image cannot be found.

    Attributes:
        message (str): A description of the error.
    """
    def __init__(self, message: str = "Image not found") -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"ImageNotFoundException: {self.message}"


class RateLimitExceededException(Exception):
    """
    Exception raised when the rate limit for requests is exceeded.

    Attributes:
        message (str): A description of the error.
    """
    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"RateLimitExceededException: {self.message}"