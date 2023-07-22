"""Rooster Money requests and session handler."""
# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes
import logging
import base64
import asyncio
from datetime import datetime, timedelta

import aiohttp

from .const import HEADERS, BASE_URL, LOGIN_BODY, URLS, OAUTH_TOKEN_URL
from .exceptions import InvalidAuthError, NotLoggedIn, AuthenticationExpired
from .events import Events

_LOGGER = logging.getLogger(__name__)

class RoosterSession:
    """The main Rooster Session."""

    def __init__(self,
                 username: str,
                 password: str,
                 update_interval: int=30,
                 use_updater: bool=False) -> None:
        self._username = username
        self._password = password
        self._session = None
        self._headers = HEADERS
        self._logged_in = False
        self._logging_in = asyncio.Lock()
        self.events = Events()
        self.update_interval = update_interval
        self.use_updater = use_updater

    async def _send_request(self,
                      url,
                      body: dict = None,
                      auth=None,
                      method="GET"):
        """Handles sending HTTP requests"""
        async with aiohttp.ClientSession() as session:
            async with session.request(method=method,
                                       url=f"{BASE_URL}/{url}",
                                       json=body,
                                       auth=auth,
                                       headers=self._headers) as response:
                output = {
                    "status": response.status,
                    "response": {}
                }
                if response.status == 401:
                    raise PermissionError("Unauthorized session")
                if response.status == 403:
                    raise PermissionError("Access denied.")
                if response.status == 204:
                    return output
                if response.status >= 200 and response.status < 204:
                    output["response"] = await response.json()
                    return output
                return output

    def _parse_login(self, login_response, token):
        """Parses a login response"""
        if "tokens" in login_response:
            login_response=login_response.get("tokens")
        if "error" in login_response:
            error = login_response.get("error")
            raise ConnectionError(error)
        token_type = login_response.get("token_type")
        access_token = login_response.get("access_token")

        self._headers["Authorization"] = f"{token_type} {access_token}"
        return {
                "access_token": access_token,
                "refresh_token": login_response.get("refresh_token"),
                "token_type": token_type,
                "expiry_time": datetime.now() + timedelta(0,
                                                          login_response.get("expires_in")),
                "security_code": token
            }

    async def async_login(self):
        """Logs into RoosterMoney and starts a new active session."""
        if self._logging_in.locked():
            _LOGGER.warning("Login already attempting. Only one execution allowed.")
            while self._logging_in.locked():
                await asyncio.sleep(1)
            return True

        async with self._logging_in:
            if self._session is not None:
                if self._session.get("expiry_time") > datetime.now():
                    _LOGGER.debug("Not logging in again, session already active.")
                    return True

            req_body = LOGIN_BODY
            req_body["username"] = self._username
            req_body["password"] = self._password
            auth = aiohttp.BasicAuth(self._username, self._password)

            if "Authorization" in self._headers:
                self._headers.pop("Authorization")

            login_response = await self.request_handler(url=URLS.get("login"),
                                                                body=req_body,
                                                                auth=auth)

            if login_response["status"] == 401:
                raise InvalidAuthError(self._username, login_response["status"])

            login_response = login_response["response"]
            token = base64.b64encode(str(self._password[::-1]).encode('utf-8')).decode('utf-8')

            self._session = self._parse_login(login_response, token)

            self._logged_in = True

        return True

    async def refresh_token(self):
        """Refresh the current access token when the session expires."""
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field("audience", "rooster-app")
            form.add_field("grant_type", "refresh_token")
            form.add_field("client_id", "rooster-app")
            form.add_field("refresh_token", self._session.get("refresh_token"))
            try:
                async with session.post(OAUTH_TOKEN_URL, data=form) as request:
                    data = await request.json()
                    self._session = self._parse_login(data, self._session.get("security_code"))
            except ConnectionError:
                await self.async_login()

    async def _internal_request_handler(self,
                                        url,
                                        body=None,
                                        auth=None,
                                        method="GET",
                                        login_request=False,
                                        add_security_token=False):
        """Handles all incoming requests to make sure that the session is active."""

        if self._session is None and self._logged_in:
            raise RuntimeError("Invalid state. Missing session data yet currently logged in?")
        if self._session is None and self._logged_in is False and auth is not None:
            _LOGGER.info("Not logged in, trying now.")
            return await self._send_request(url, body, auth, "POST")
        if self._session is None and self._logged_in is False and auth is None:
            raise NotLoggedIn()
        if self._session is not None and self._logged_in is False:
            raise RuntimeError("Invalid state. Session data available yet not logged in?")
        if self._session["expiry_time"] < datetime.now() and login_request:
            _LOGGER.debug("Login request.")
            return await self._send_request(url, body, auth, "POST")

        # Check if auth has expired
        # pylint: disable=no-else-raise
        # pylint: disable=no-else-return
        if self._session["expiry_time"] < datetime.now():
            raise AuthenticationExpired()

        if add_security_token:
            self._headers["securitytoken"] = self._session["security_code"]
        elif "securitytoken" in self._headers:
            self._headers.pop("securitytoken")

        return await self._send_request(url=url, body=body, auth=auth, method=method.upper())

    async def request_handler(self,
                                        url,
                                        body=None,
                                        auth=None,
                                        method="GET",
                                        login_request=False,
                                        add_security_token=False):
        """Public calls for the private _internal_request_handler."""
        _LOGGER.debug("Sending %s HTTP request to %s", method, url)
        try:
            return await self._internal_request_handler(
                url=url,
                body=body,
                auth=auth,
                method=method,
                login_request=login_request,
                add_security_token=add_security_token
            )
        except AuthenticationExpired:
            await self.refresh_token()
            return await self._internal_request_handler(
                url=url,
                body=body,
                auth=auth,
                method=method,
                login_request=login_request
            )
        except NotLoggedIn as exc:
            raise NotLoggedIn() from exc
        except aiohttp.ClientOSError as exc:
            # silent exc handler
            if exc.errno == 104: # connection reset by peer
                _LOGGER.debug("Connection reset by peer - retrying request.")
                asyncio.sleep(5)
                await self.request_handler(**locals())
            else:
                raise aiohttp.ClientOSError from exc
