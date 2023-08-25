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

class EventType(Enum):
    """Valid event types"""
    ALL = 0
    UPDATED = 1
    CREATED = 2
    DELETED = 4
    AUTH = 8
    EVENT_SUBSCRIBE = 16
    EVENT_UNSUBSCRIBE = 32

    def __str__(self) -> str:
        return self.name

class EventSource(Enum):
    """Valid event sources"""
    ALL = 0
    CHILD = 1
    FAMILY_ACCOUNT = 2
    JOBS = 4
    TRANSACTIONS = 8
    STANDING_ORDER = 16
    CARD = 32
    INTERNAL = 64

    def __str__(self) -> str:
        return self.name

class PotMoneyActions(Enum):
    """List of valid money management actions for pots."""
    REMOVE = 0
    BOOST = 1

    def __str__(self) -> str:
        return self.name.lower()

class PotLedgerTypes(Enum):
    """List of valid pot ledger types for money transfer."""
    SAVE = 0
    SPEND = 1
    GIVE = 2
    GOAL = 4
    CUSTOM = 8

    def __str__(self) -> str:
        return self.name.lower()
