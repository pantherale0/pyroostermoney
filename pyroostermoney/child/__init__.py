"""Defines some standard values for a Natwest Rooster Money child."""

import asyncio
import datetime

from pyroostermoney.const import URLS
from pyroostermoney.api import RoosterSession

class ChildAccount:
    """The child account."""

    def __init__(self, raw_response: dict, session: RoosterSession) -> None:
        self._parse_response(raw_response)
        self._session = session

    async def update(self):
        """Updates the cached data for this child."""
        response = await self._session.internal_request_handler(
            url=URLS.get("get_child").format(user_id=self.user_id))
        self._parse_response(response)

    def _parse_response(self, raw_response:dict):
        """Parses the raw_response into this object"""
        if "response" in raw_response:
            raw_response = raw_response["response"]
        self.interest_rate = raw_response["interestRate"]
        self.available_pocket_money = raw_response["availablePocketMoney"]
        self.currency = raw_response["currency"]
        self.first_name = raw_response["firstName"]
        self.surname = raw_response["surname"]
        self.gender = "male" if raw_response["gender"] == 1 else "female"
        self.uses_real_money = True if raw_response["realMoneyStatus"] == 1 else False
        self.user_id = raw_response["userId"]

    async def get_active_allowance_period(self):
        """Returns the current active allowance period."""
        allowance_periods = await self._session.internal_request_handler(
            url=URLS.get("get_child_allowance_periods").format(user_id=self.user_id))
        allowance_periods = allowance_periods["response"]
        active_periods = [p for p in allowance_periods
                          if datetime.datetime.strptime(p["startDate"], "%Y-%m-%d").date() <=
                          datetime.date.today() <=
                          datetime.datetime.strptime(p["endDate"], "%Y-%m-%d").date()]
        if len(active_periods) != 1:
            raise LookupError("No allowance period found")
        return active_periods[0]

    async def get_spend_history(self, count=10):
        """Gets the spend history"""
        url = URLS.get("get_child_spend_history").format(
            user_id=self.user_id,
            count=count
        )
        response = await self._session.internal_request_handler(url=url)

        return response["response"]

    async def get_allowance_period_jobs(self, allowance_period_id):
        """Gets jobs for a given allowance period"""
        url = URLS.get("get_child_allowance_period_jobs").format(
            user_id=self.user_id,
            allowance_period_id=allowance_period_id
        )
        response = await self._session.internal_request_handler(url)

        return response["response"]

    async def get_pocket_money(self):
        """Gets pocket money"""
        url = URLS.get("get_child_pocket_money").format(
            user_id=self.user_id
        )
        response = await self._session.internal_request_handler(url)

        return response["response"]

    async def special_get_pocket_money(self):
        """Same as get_pocket_money yet parses the response and provides a basic dict."""
        pocket_money = await self.get_pocket_money()

        return {
            "total": pocket_money["walletTotal"],
            "available": pocket_money["availablePocketMoney"],
            "spend": pocket_money["pocketMoneyAmount"],
            "save": pocket_money["safeTotal"],
            "give": pocket_money["giveAmount"]
        }
