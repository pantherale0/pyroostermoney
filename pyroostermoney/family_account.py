# pylint: disable=fixme
"""Defines the class for the family account."""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=no-else-raise
import logging
from datetime import date

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
        self.current_month_transactions = None
        self.latest_transaction = None

    def _parse_response(self, raw_response: dict, account_info: dict):
        """Parses the raw response."""
        _LOGGER.debug("Parsing new response")
        if "response" in raw_response:
            raw_response = raw_response["response"]

        if "response" in account_info:
            account_info = account_info["response"]

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

    def _parse_transaction_history(self, raw_response: dict) -> dict:
        """Parses a transaction history response."""
        transactions = []
        if "response" in raw_response:
            raw_response=raw_response["response"]

        for transaction in raw_response:
            parsed = {
                "amount": 0,
                "reason": transaction["reason"],
                "type": transaction["transactionType"]
            }
            if transaction["creditAmount"]["amount"] > 0:
                parsed["amount"] = transaction["creditAmount"]["amount"]/100
            else:
                parsed["amount"] = 0-(transaction["debitAmount"]["amount"]/100)
            transactions.append(parsed)
        return transactions

    async def get_transaction_history(self, search_date: date = None):
        """Gets the transaction history.
        If search_date is set to None this also acts an updater method."""
        if search_date is None:
            search_date = date.today()
        history = await self._session.request_handler(
            url=URLS.get("get_family_account_statement").format(
                month=search_date.month,
                year=search_date.year
            )
        )
        if search_date == date.today():
            self.current_month_transactions = self._parse_transaction_history(history)
            if len(self.current_month_transactions) > 0:
                self.latest_transaction = self.current_month_transactions[0]
            else:
                self.latest_transaction = None
            return self.current_month_transactions
        return self._parse_transaction_history(history)

    async def update(self):
        """Updates the FamilyAccount object data."""
        family_account = await self._session.request_handler(
            url=URLS.get("get_family_account"))
        account = await self._session.request_handler(
            url=URLS.get("get_account_info")
        )
        p_account = self.__dict__
        self._parse_response(raw_response=family_account, account_info=account)
        await self.get_transaction_history()
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
