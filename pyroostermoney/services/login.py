"""Login models."""
from datetime import datetime, timedelta
from .requests import RequestsHandler

class LoginResponse():
    def __init__(self, access_token, refresh_token, token_type, expiry_time) -> None:
        self.access_token=access_token
        self.refresh_token=refresh_token
        self.token_type=token_type
        self.expiry_time=expiry_time


class ParentLoginManager():

    def __init__(self, username: str, password: str) -> None:
        self.username=username
        self.password=password
        self.session = None
        pass

    def login(self) -> LoginResponse:
        s = RequestsHandler.login(self.username, self.password)
        self.session = LoginResponse(access_token=s.tokens.access_token,
                                     refresh_token=s.tokens.refresh_token,
                                     token_type=s.tokens.token_type,
                                     expiry_time=datetime.now() + timedelta(0, s.tokens.expires_in))
        return s
