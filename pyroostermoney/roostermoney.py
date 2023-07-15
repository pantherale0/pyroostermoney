"""The RoosterMoney integration."""

import logging

from .const import URLS
from .child import ChildAccount
from .family_account import FamilyAccount
from .api import RoosterSession

_LOGGER = logging.getLogger(__name__)

class RoosterMoney(RoosterSession):
    """The RoosterMoney module."""

    def __init__(self, username: str, password: str) -> None:
        super().__init__(
            username=username,
            password=password
        )

    async def get_children(self) -> list[ChildAccount]:
        """Returns a list of available children."""
        account_info = await self.get_account_info()
        children = account_info["response"]["children"]
        output = []
        for child in children:
            output.append(ChildAccount(child, self))
        return output

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

    async def get_family_account(self) -> FamilyAccount:
        """Gets family account details (/parent/family/account)"""
        response = await self.internal_request_handler(
            url=URLS.get("get_family_account")
        )

        return FamilyAccount(response["response"], self)
