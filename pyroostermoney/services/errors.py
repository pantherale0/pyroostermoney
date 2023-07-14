"""Defines errors."""

class InvalidAuthError(Exception):
    """An invalid auth error (HTTP 401)"""

    def __init__(self, username: str, status_code: int) -> None:
        self.username = username
        self.status_code = status_code
