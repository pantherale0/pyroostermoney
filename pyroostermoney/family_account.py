# pylint: disable=fixme
"""Defines the class for the family account."""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments

import asyncio
import logging
from datetime import datetime

from .api import RoosterSession
from .const import URLS, DEFAULT_BANK_NAME, DEFAULT_BANK_TYPE, CREATE_PAYMENT_BODY, CURRENCY
from .events import EventType, EventSource

_LOGGER = logging.getLogger(__name__)

class FamilyAccount:
    """A family account."""

    def __init__(self,
                 raw_response: dict,
                 account_info: dict,
                 session: RoosterSession) -> None:
        self._session = session
        self._parse_response(raw_response, account_info)
        self._update_lock = asyncio.Lock()
        self.last_updated = datetime.now()

    def _parse_response(self, raw_response: dict, account_info: dict):
        """Parses the raw response."""
        _LOGGER.debug("Parsing new response")
        if "response" in raw_response:
            raw_response = raw_response["response"]

        self.account_number = raw_response["accountNumber"]
        self.sort_code = raw_response["sortCode"]
        self._precision = raw_response["suggestedMonthlyTransfer"]["precision"]
        amount = raw_response["suggestedMonthlyTransfer"]["amount"]
        self.suggested_monthly_transfer = amount / (1 * 10**self._precision)
        self.currency = raw_response["suggestedMonthlyTransfer"]["currency"]
        self.balance = account_info.get("familyLedgerBalance", None)
        self.family_id = account_info.get("familyId")
        if self.balance is not None:
            self.balance = float(self.balance)

    async def update(self):
        """Updates the FamilyAccount object data."""
        if self._update_lock.locked():
            return True

        async with self._update_lock:
            family_account = await self._session.request_handler(
                url=URLS.get("get_family_account"))
            account = await self._session.request_handler(
                url=URLS.get("get_account_info")
            )
            p_account = self.__dict__
            self._parse_response(raw_response=family_account, account_info=account)
            self.last_updated = datetime.now()
            if p_account is not self.__dict__:
                self._session.events.fire_event(EventSource.FAMILY_ACCOUNT, EventType.UPDATED,
                                                {
                                                    "user_id": self.account_number
                                                })

    @property
    def bank_transfer_details(self):
        """Gets the bank transfer details to top up the family account."""
        return {
            "account_number": self.account_number,
            "sort_code": self.sort_code,
            "type": DEFAULT_BANK_TYPE,
            "name": DEFAULT_BANK_NAME
        }

    async def create_payment(self,
                             value: float,
                             card_number,
                             expiry_month,
                             expiry_year,
                             security_code,
                             holder_name):
        """Creates a payment to allow topping up the family account."""
        request_body = CREATE_PAYMENT_BODY
        request_body["amount"]["value"] = value*100
        request_body["paymentMethod"]["encryptedCardNumber"] = card_number
        request_body["paymentMethod"]["encryptedExpiryMonth"] = expiry_month
        request_body["paymentMethod"]["encryptedExpiryYear"] = expiry_year
        request_body["paymentMethod"]["encryptedSecurityCode"] = security_code
        request_body["paymentMethod"]["holderName"] = holder_name
        ## TODO request_body["shopperEmail"] = self.account_info.email

        response = await self._session.request_handler(
            url=URLS.get("create_payment"),
            body=request_body,
            method="POST"
        )

        return response["response"]

    async def get_available_cards(self):
        """Gets available top up payment cards"""
        response = await self._session.request_handler(
            url=URLS.get("get_available_cards")
        )

        return response["response"]

    async def get_top_up_methods(self, currency=None):
        """Gets available top up methods for the family account."""
        if currency is None:
            currency=CURRENCY

        response = await self._session.request_handler(
            url=URLS.get("get_top_up_methods").format(
                currency=currency
            )
        )

        return response["response"]
