class APIKeyException(Exception):
    def __init__(self, message: str = "Invalid or missing API key") -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"APIKeyException: {self.message}"


class ImageNotFoundException(Exception):
    def __init__(self, message: str = "Image not found") -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"ImageNotFoundException: {self.message}"


class RateLimitExceededException(Exception):
    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"RateLimitExceededException: {self.message}"


class UserNotAuthorizedException(Exception):
    def __init__(self, message: str = "User does not have the required permissions") -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"UserNotAuthorizedException: {self.message}"