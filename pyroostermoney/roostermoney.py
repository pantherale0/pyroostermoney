"""The RoosterMoney integration."""

import logging, asyncio
from datetime import datetime, timedelta

from .const import URLS
from .child import ChildAccount, Job
from .family_account import FamilyAccount
from .api import RoosterSession

_LOGGER = logging.getLogger(__name__)

class RoosterMoney(RoosterSession):
    """The RoosterMoney module."""

    def __init__(self, username: str, password: str, update_interval: int=30, use_updater: bool=False) -> None:
        super().__init__(
            username=username,
            password=password,
            use_updater=use_updater,
            update_interval=update_interval
        )
        self.account_info = None
        self.children: list[ChildAccount] = []
        self.master_job_list: list[Job] = []
        self._discovered_children: list = []
        self.family_account: FamilyAccount = None
        self._update_lock = asyncio.Lock()
        self._updater = None

    def __del__(self):
        if self.use_updater:
            self._updater.cancel()
            self._updater = None

    async def async_login(self):
        await super().async_login()
        await self.update()
        await self.get_family_account()
        if self.use_updater:
            _LOGGER.debug("Using built-in updater for RoosterMoney")
            self._updater = asyncio.create_task(self._update_scheduler())

    async def _update_scheduler(self):
        """Automatic updater"""
        while True:
            next_time = datetime.now() + timedelta(seconds=self.update_interval)
            while datetime.now() < next_time:
                await asyncio.sleep(1)
            _LOGGER.info("Updating data")
            await self.update()

    async def update(self):
        """Perform an update of all root types"""
        if self._update_lock.locked():
            return True

        async with self._update_lock:
            await self.get_children()
            await self.get_master_job_list()

    async def get_children(self) -> list[ChildAccount]:
        """Returns a list of available children."""
        account_info = await self.get_account_info()
        children = account_info["children"]
        for child in children:
            if child.get("userId") not in self._discovered_children:
                child = ChildAccount(child, self)
                await child.perform_init() # calling this will init some extra props.
                self._discovered_children.append(child.user_id)
                self.children.append(child)
        _LOGGER.debug(self._discovered_children)
        return self.children

    async def get_account_info(self) -> dict:
        """Returns the account info for the current user."""
        self.account_info = await self.request_handler(url=URLS.get("get_account_info"))
        self.account_info = self.account_info["response"]
        return self.account_info

    def get_child_account(self, user_id) -> ChildAccount:
        """Fetches and returns a given child account details."""
        return [x for x in self.children if x.user_id == user_id][0]

    async def get_master_job_list(self) -> list[Job]:
        """Gets master job list (/parent/master-jobs)"""
        response = await self.request_handler(
            url=URLS.get("get_master_job_list")
        )
        jobs = Job.convert_response(response.get("response"), self)
        for job in jobs:
            self.master_job_list.append(job)
        return self.master_job_list

    async def get_family_account(self) -> FamilyAccount:
        """Gets family account details (/parent/family/account)"""
        response = await self.request_handler(
            url=URLS.get("get_family_account")
        )
        account = await self.get_account_info()
        self.family_account =  FamilyAccount(response["response"], account, self)
        return self.family_account
