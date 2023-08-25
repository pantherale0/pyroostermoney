"""The RoosterMoney integration."""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments

import logging

from .const import URLS
from .child import ChildAccount, Job
from .family_account import FamilyAccount
from .api import RoosterSession
from .events import EventSource, EventType
from .master_jobs import MasterJobs

_LOGGER = logging.getLogger(__name__)

class RoosterMoney(RoosterSession):
    """The RoosterMoney module."""

    def __init__(self,
                 remove_card_information = False) -> None:
        super().__init__()
        self.account_info = None
        self.children: list[ChildAccount] = []
        self.master_job_list: list[Job] = []
        self.master_jobs: MasterJobs = None
        self._discovered_children: list = []
        self.family_account: FamilyAccount = None
        self._remove_card_information = remove_card_information
        self._init = True

    @classmethod
    async def create(cls,
                 username: str,
                 password: str,
                 remove_card_information = False):
        """Starts a online session with Rooster Money"""
        self = cls(remove_card_information=remove_card_information)
        await self._session_start(username, password)
        await self.get_family_account()
        self.family_id = self.family_account.family_id
        self.family_balance = self.family_account.balance
        self.master_jobs = MasterJobs(self)
        await self.update()
        self._init = False
        return self

    async def update(self):
        """Perform an update of all root types"""
        self.events.fire_event(EventSource.INTERNAL,
                               EventType.UPDATED,
                               {"update_state": "started"})
        await self._update_children()
        await self.master_jobs.update()
        self.master_job_list = self.master_jobs.jobs
        await self.family_account.update()
        self.family_balance = self.family_account.balance
        if self._init is False:
            for child in self.children:
                await child.update()
        self.events.fire_event(EventSource.INTERNAL,
                               EventType.UPDATED,
                               {"update_state": "finished"})

    async def _update_children(self):
        """Updates the list of available children."""
        account_info = await self.get_account_info()
        children = account_info["children"]
        for child in children:
            if child.get("userId") not in self._discovered_children:
                child = await ChildAccount.create(child.get("userId"),
                                                self,
                                                self._remove_card_information)
                self._discovered_children.append(child.user_id)
                self.children.append(child)
                self.events.fire_event(EventSource.CHILD, EventType.CREATED, {
                    "user_id": child.user_id
                })
        _LOGGER.debug(self._discovered_children)
        self._cleanup()

    def get_children(self) -> list[ChildAccount]:
        """Returns a list of available children (compatibility only)"""
        return self.children

    def _cleanup(self) -> None:
        """Removes data that no longer exists from the updater."""
        for i in range(len(self.children)):
            child_id = self.children[i-1].user_id
            if child_id not in self._discovered_children:
                _LOGGER.debug("child %s no longer exists at source", child_id)
                self.children.pop(i-1)
                self.events.fire_event(EventSource.CHILD, EventType.DELETED, {
                    "user_id": child_id
                })

    async def get_account_info(self) -> dict:
        """Returns the account info for the current user."""
        self.account_info = await self.request_handler(url=URLS.get("get_account_info"))
        self.account_info = self.account_info["response"]
        return self.account_info

    def get_child_account(self, user_id) -> ChildAccount:
        """Fetches and returns a given child account details."""
        return [x for x in self.children if x.user_id == user_id][0]

    async def get_family_account(self) -> FamilyAccount:
        """Gets family account details (/parent/family/account)"""
        response = await self.request_handler(
            url=URLS.get("get_family_account")
        )
        account = await self.get_account_info()
        self.family_account =  FamilyAccount(response["response"], account, self)
        return self.family_account
