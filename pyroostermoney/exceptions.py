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

class NotEnoughFunds(Exception):
    """Not enough funds in x."""
    def __init__(self, fund_source) -> None:
        super().__init__(
            f"Not enough available funds in source {fund_source} to execute this operation.")

class ActionFailed(Exception):
    """A given action failed because on an unspecified error."""
    def __init__(self, *args: object) -> None:
        super().__init__("Action failed due to an unspecified error.", *args)
