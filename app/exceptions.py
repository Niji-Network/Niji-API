class APIException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"


class APIKeyException(APIException):
    def __init__(self, message: str = "Invalid or missing API key") -> None:
        super().__init__(message)


class ImageNotFoundException(APIException):
    def __init__(self, message: str = "Image not found") -> None:
        super().__init__(message)


class RateLimitExceededException(APIException):
    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message)


class UserNotAuthorizedException(APIException):
    def __init__(self, message: str = "User does not have the required permissions") -> None:
        super().__init__(message)