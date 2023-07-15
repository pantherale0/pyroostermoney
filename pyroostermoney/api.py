"""Rooster Money requests and session handler."""

import json
import logging
from datetime import datetime, timedelta

import aiohttp

from .const import HEADERS, BASE_URL, LOGIN_BODY, URLS
from .exceptions import InvalidAuthError, NotLoggedIn, AuthenticationExpired

_LOGGER = logging.getLogger(__name__)

async def _fetch_request(url, headers=None):
    if headers is None:
        headers=HEADERS
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/{url}", headers=headers) as response:
            text = await response.text()
            return {
                "status": response.status,
                "response": json.loads(text)
            }

async def _post_request(url, body: dict, auth=None, headers=None):
    if headers is None:
        headers=HEADERS
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/{url}",
                                json=body,
                                headers=headers,
                                auth=auth) as response:
            text = await response.text()
            return {
                "status": response.status,
                "response": json.loads(text)
            }

class RoosterSession:
    """The main Rooster Session."""

    def __init__(self, username: str, password: str) -> None:
        self._username = username
        self._password = password
        self._session = None
        self._headers = HEADERS
        self._logged_in = False

    async def async_login(self):
        """Logs into RoosterMoney and starts a new active session."""
        req_body = LOGIN_BODY
        req_body["username"] = self._username
        req_body["password"] = self._password
        auth = aiohttp.BasicAuth(self._username, self._password)

        login_response = await self.internal_request_handler(url=URLS.get("login"),
                                                              body=req_body,
                                                              auth=auth,
                                                              headers=HEADERS)

        if login_response["status"] == 401:
            raise InvalidAuthError(self._username, login_response["status"])

        login_response = login_response["response"]

        self._session = {
            "access_token": login_response["tokens"]["access_token"],
            "refresh_token": login_response["tokens"]["refresh_token"],
            "token_type": login_response["tokens"]["token_type"],
            "expiry_time": datetime.now() + timedelta(0, login_response["tokens"]["expires_in"])
        }

        token_type = login_response["tokens"]["token_type"]
        access_token = login_response["tokens"]["access_token"]

        self._headers["Authorization"] = f"{token_type} {access_token}"

        self._logged_in = True

        return True

    async def internal_request_handler(self,
                                        url,
                                        body=None,
                                        headers=None,
                                        auth=None,
                                        method="GET"):
        """Handles all incoming requests to make sure that the session is active."""
        if self._session is None and self._logged_in:
            raise RuntimeError("Invalid state. Missing session data yet currently logged in?")
        elif self._session is None and self._logged_in is False and auth is not None:
            _LOGGER.info("Not logged in, trying now.")
            if headers is None:
                headers = self._headers
            return await _post_request(url, body, auth, headers)
        elif self._session is None and self._logged_in is False and auth is None:
            raise NotLoggedIn()
        elif self._session is not None and self._logged_in is False:
            raise RuntimeError("Invalid state. Session data available yet not logged in?")

        # Check if auth has expired

        if self._session["expiry_time"] < datetime.now():
            raise AuthenticationExpired()

        if headers is None:
            headers = self._headers

        if method == "GET":
            return await _fetch_request(url, headers=headers)
        elif method == "POST":
            return await _post_request(url, body=body, headers=headers)
        else:
            raise ValueError("Invalid type argument.")
