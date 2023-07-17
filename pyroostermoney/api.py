"""Rooster Money requests and session handler."""

import json
import logging
import base64
import asyncio
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

async def _delete_request(url, body: dict, auth=None, headers=None):
    if headers is None:
        headers=HEADERS
    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{BASE_URL}/{url}",
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

    def __init__(self, username: str, password: str, update_interval: int=30, use_updater: bool=False) -> None:
        self._username = username
        self._password = password
        self._session = None
        self._headers = HEADERS
        self._logged_in = False
        self._logging_in = asyncio.Lock()
        self.update_interval = update_interval
        self.use_updater = use_updater

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
                                                                auth=auth,
                                                                headers=self._headers)

            if login_response["status"] == 401:
                raise InvalidAuthError(self._username, login_response["status"])

            login_response = login_response["response"]
            token = base64.b64encode(str(self._password[::-1]).encode('utf-8')).decode('utf-8')

            self._session = {
                "access_token": login_response["tokens"]["access_token"],
                "refresh_token": login_response["tokens"]["refresh_token"],
                "token_type": login_response["tokens"]["token_type"],
                "expiry_time": datetime.now() + timedelta(0,
                                                          login_response["tokens"]["expires_in"]),
                "security_code": token
            }

            token_type = login_response["tokens"]["token_type"]
            access_token = login_response["tokens"]["access_token"]

            self._headers["Authorization"] = f"{token_type} {access_token}"

            self._logged_in = True

        return True

    async def _internal_request_handler(self,
                                        url,
                                        body=None,
                                        headers=None,
                                        auth=None,
                                        method="GET",
                                        login_request=False,
                                        add_security_token=False):
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
        elif self._session["expiry_time"] < datetime.now() and login_request:
            _LOGGER.debug("Login request.")
            return await _post_request(url, body, auth, headers)

        # Check if auth has expired

        if self._session["expiry_time"] < datetime.now():
            raise AuthenticationExpired()

        if headers is None:
            headers = self._headers

        if add_security_token:
            headers["securitytoken"] = self._session["security_code"]

        if method == "GET":
            return await _fetch_request(url, headers=headers)
        elif method == "POST":
            return await _post_request(url, body=body, headers=headers)
        elif method == "DELETE":
            return await _delete_request(url, body=body, headers=headers)
        else:
            raise ValueError("Invalid type argument.")

    async def request_handler(self,
                                        url,
                                        body=None,
                                        headers=None,
                                        auth=None,
                                        method="GET",
                                        login_request=False,
                                        add_security_token=False):
        """Public calls for the private _internal_request_handler."""
        _LOGGER.debug(f"Sending {method} HTTP request to {url}")
        try:
            return await self._internal_request_handler(
                url=url,
                body=body,
                headers=headers,
                auth=auth,
                method=method,
                login_request=login_request,
                add_security_token=add_security_token
            )
        except AuthenticationExpired:
            await self.async_login()
            return await self._internal_request_handler(
                url=url,
                body=body,
                headers=headers,
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
