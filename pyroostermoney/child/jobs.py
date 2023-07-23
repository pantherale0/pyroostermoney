"""Job type."""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-locals
# pylint: disable=too-many-arguments
from datetime import datetime
from enum import Enum

from pyroostermoney.api import RoosterSession
from pyroostermoney.const import CURRENCY, URLS

class JobScheduleTypes(Enum):
    """Job schedule types."""
    REPEATING = 2
    ANYTIME = 1
    UNKNOWN = -1

class JobTime(Enum):
    """Job times."""
    MORNING = 12
    AFTERNOON = 17
    ANYTIME = 23

class JobState(Enum):
    """Job states."""
    NO_PREVIOUS_STATE = 0
    TODO = 1
    AWAITING_APPROVAL = 2
    APPROVED = 3
    PAUSED = 4
    OVERDUE = 5
    NOT_DONE = 6
    SKIPPED = 7

    def __str__(self) -> str:
        return str(self.name)

class JobActions(Enum):
    """All supported job actions."""
    APPROVE = 8

    def __str__(self) -> str:
        return str(self.name).lower()

class Job:
    """A job."""

    def __init__(self,
                 allowance_period_id,
                 currency,
                 description,
                 due_any_day,
                 due_date,
                 expiry_processed,
                 final_reward_amount,
                 image_url,
                 locked,
                 master_job_id,
                 reopened,
                 reward_amount,
                 scheduled_job_id,
                 state,
                 time_of_day,
                 title,
                 job_type,
                 schedule_type,
                 session,
                 user_id_list: list | None=None):
        self.allowance_period_id: int = allowance_period_id
        self.currency: str = currency
        self.description: str = description
        self.due_any_day: bool = due_any_day
        self.due_date: datetime = due_date
        self.expiry_processed: bool = expiry_processed
        self.final_reward_amount: float = final_reward_amount
        self.image_url: str = image_url
        self.locked: bool = locked
        self.master_job_id: int = master_job_id
        self.reopened: bool = reopened
        self.reward_amount: float = reward_amount
        self.scheduled_job_id: int = scheduled_job_id
        self.state: JobState = state
        self.time_of_day: JobTime = JobTime(time_of_day)
        self.schedule_type: JobScheduleTypes = (
            JobScheduleTypes(schedule_type) if schedule_type is not None
            else JobScheduleTypes.UNKNOWN)
        self.title: str = title
        self.type: int = job_type
        self._session: RoosterSession = session
        if user_id_list is not None:
            self.user_id_list = user_id_list

    @staticmethod
    def from_dict(obj: dict, session) -> 'Job':
        """Converts to a job from a dict."""
        if "scheduleInfo" in obj:
            # Move nested scheduleInfo into main
            for info in obj.get("scheduleInfo").keys():
                if info == "type":
                    info = "scheduleType"
                obj[info] = obj.get("scheduleInfo").get(info)
            obj["scheduleInfo"] = None
        if "dueDate" in obj:
            _due_date = datetime.strptime(obj.get("dueDate"), "%Y-%m-%d")
        else:
            _due_date = None
        return Job(
            allowance_period_id=int(obj.get("allowancePeriodId", -1)),
            currency=str(obj.get("currency", CURRENCY)),
            description=str(obj.get("description", "")),
            due_any_day=bool(obj.get("dueAnyDay", False)),
            due_date=_due_date,
            expiry_processed=bool(obj.get("expiryProcessed", False)),
            final_reward_amount=float(obj.get("finalRewardAmount", 0)),
            image_url=str(obj.get("imageUrl", "")),
            locked=bool(obj.get("locked", False)),
            master_job_id=int(obj.get("masterJobId", 0)),
            reopened=bool(obj.get("reopened", False)),
            reward_amount=float(obj.get("rewardAmount", 0)),
            scheduled_job_id=int(obj.get("scheduledJobId", 0)),
            state=JobState(obj.get("state", 0)),
            time_of_day=int(obj.get("timeOfDay", 0)),
            title=str(obj.get("title", "")),
            job_type=int(obj.get("type", 0)),
            session=session,
            user_id_list=obj.get("childUserIds", None),
            schedule_type=obj.get("scheduleType")
        )

    @staticmethod
    def convert_response(raw_response: dict, session: RoosterSession) -> list['Job']:
        """Converts a raw response."""
        if "response" in raw_response:
            raw_response=raw_response["response"]

        output: list[Job] = []

        for state in raw_response:
            for job in raw_response.get(state, []):
                output.append(Job.from_dict(job, session))
        return output

    async def job_action(self, action: JobActions, message: str = ""):
        """Performs the given action on a scheduled job."""
        if self.scheduled_job_id is None:
            raise NotImplementedError("This function is only available on scheduled jobs.")

        await self._session.request_handler(
            url=URLS.get("scheduled_job_action").format(
                schedule_id=self.scheduled_job_id,
                action=str(action)
            ),
            body={
                "message": message
            },
            method="POST"
        )
