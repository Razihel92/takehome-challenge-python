from typing import Self

from fastapi import status


class AppError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message

    @classmethod
    def bad_request(cls, message: str) -> Self:
        return cls(status.HTTP_400_BAD_REQUEST, message)

    @classmethod
    def not_found(cls, message: str) -> Self:
        return cls(status.HTTP_404_NOT_FOUND, message)

    @classmethod
    def conflict(cls, message: str) -> Self:
        return cls(status.HTTP_409_CONFLICT, message)

    @classmethod
    def service_unavailable(cls, message: str) -> Self:
        return cls(status.HTTP_503_SERVICE_UNAVAILABLE, message)
