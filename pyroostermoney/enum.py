"RoosterMoney enums."

from enum import Enum, IntEnum

class Weekdays(IntEnum):
    """Weekdays."""
    MONDAY=1
    TUESDAY=2
    WEDNESDAY=3
    THURSDAY=4
    FRIDAY=5
    SATURDAY=6
    SUNDAY=7

class JobScheduleTypes(Enum):
    """Job schedule types."""
    REPEATING = 2
    ANYTIME = 1
    UNKNOWN = -1

class JobTime(IntEnum):
    """Job times."""
    MORNING = 12
    AFTERNOON = 17
    EVENING = 22
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
