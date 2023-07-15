"""The RoosterMoney integration."""

import logging

from .const import URLS, CREATE_PAYMENT_BODY, CURRENCY, DEFAULT_BANK_NAME, DEFAULT_BANK_TYPE
from .child import ChildAccount
from .api import RoosterSession

_LOGGER = logging.getLogger(__name__)

class RoosterMoney(RoosterSession):
    """The RoosterMoney module."""

    def __init__(self, username: str, password: str) -> None:
        super().__init__(
            username=username,
            password=password
        )

    async def get_account_info(self) -> dict:
        """Returns the account info for the current user."""
        return await self.internal_request_handler(url=URLS.get("get_account_info"))

    async def get_child_account(self, user_id) -> ChildAccount:
        """Fetches and returns a given child account details."""
        response = await self.internal_request_handler(
            url=URLS.get("get_child").format(user_id=user_id))

        return ChildAccount(response, self)

    async def get_master_job_list(self):
        """Gets master job list (/parent/master-jobs)"""
        response = await self.internal_request_handler(
            url=URLS.get("get_master_job_list")
        )

        return response

    async def get_top_up_methods(self, currency=None):
        """Gets available top up methods for the family account."""
        if currency is None:
            currency=CURRENCY

        response = await self.internal_request_handler(
            url=URLS.get("get_top_up_methods").format(
                currency=currency
            )
        )

        return response["response"]

    async def get_available_cards(self):
        """Gets available top up payment cards"""
        response = await self.internal_request_handler(
            url=URLS.get("get_available_cards")
        )

        return response["response"]

    async def get_family_account(self):
        """Gets family account details (/parent/family/account)"""
        response = await self.internal_request_handler(
            url=URLS.get("get_family_account")
        )

        return response["response"]

    async def get_bank_transfer_account_details(self):
        """Returns bank account details to add money to the family account."""
        account = await self.get_family_account()
        return {
            "account_number": account["accountNumber"],
            "sort_code": account["sortCode"],
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

        response = await self.internal_request_handler(
            url=URLS.get("create_payment"),
            body=request_body,
            method="POST"
        )

        return response["response"]
