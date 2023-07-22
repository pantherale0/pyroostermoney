# pylint: disable=too-many-arguments
"""Master jobs interface."""

from datetime import datetime

from .child import Job, ChildAccount
from .child.jobs import JobTime
from .const import URLS, DEFAULT_JOB_IMAGE_URL, CREATE_MASTER_JOB_BODY
from .api import RoosterSession
from .events import EventSource, EventType

class MasterJobs:
    """A collection of handlers for master jobs."""

    def __init__(self, session: RoosterSession) -> None:
        self._session = session
        self.jobs: list[Job] = []

    async def update(self):
        """Performs an async update"""
        await self.get_master_job_list()

    async def create_master_job(self,
                                children: list[ChildAccount],
                                description: str,
                                title: str,
                                image: str = DEFAULT_JOB_IMAGE_URL,
                                reward_amount: float = 1,
                                starting_date: datetime = datetime.now(),
                                anytime: bool = True,
                                after_last_done: bool = False,
                                job_time: JobTime = JobTime.MORNING):
        """Creates a master job"""
        data = CREATE_MASTER_JOB_BODY
        data["masterJob"]["createdByGuardianId"] = self._session.account_info.get("userId")
        data["masterJob"]["description"] = description
        data["masterJob"]["imageUrl"] = image
        data["masterJob"]["rewardAmount"] = reward_amount
        schedule_info = {
                    "afterLastDone": after_last_done,
                    "dueAnyDay": anytime,
                    "repeatEvery": 1,
                    "startingDate": {
                        "day": starting_date.date().day,
                        "month": starting_date.date().month,
                        "year": starting_date.date().year
                    },
                    "timeOfDay": int(job_time),
                    "type": 1
                }
        data["masterJob"]["scheduleInfo"] = schedule_info
        data["masterJob"]["title"] = title

        for child in children:
            data["childUserIds"].append(child.user_id)

        response = await self._session.request_handler(
            url=URLS.get("get_master_jobs"),
            body=data,
            method="POST"
        )

        if response["status"] != 200:
            raise SystemError(response["status"])

        await self.update()

        self._session.events.fire_event(EventSource.JOBS,
                                        EventType.CREATED,
                                        response.get("response"))

    async def get_master_job_list(self) -> list[Job]:
        """Gets master job list (/parent/master-jobs)"""
        response = await self._session.request_handler(
            url=URLS.get("get_master_job_list")
        )
        jobs = Job.convert_response(response.get("response"), self._session)
        for job in jobs:
            self.jobs.append(job)
        return self.jobs
