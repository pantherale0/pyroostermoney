"""Defines exceptions."""

class InvalidAuthError(Exception):
    """An invalid auth error (HTTP 401)"""

    def __init__(self, username: str, status_code: int) -> None:
        self.username = username
        self.status_code = status_code

class NotLoggedIn(Exception):
    """Not logged in error."""

    def __init__(self) -> None:
        super().__init__("Not logged in, call 'async_login()' before executing commands.")

class AuthenticationExpired(Exception):
    """Auth expired error."""

    def __init__(self) -> None:
        super().__init__("Session has expired, call 'async_login()' again.")
