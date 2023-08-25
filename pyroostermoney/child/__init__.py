"""Defines some standard values for a Natwest Rooster Money child."""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
import logging
from datetime import datetime, date

from pyroostermoney.const import URLS, CHILD_MAX_TRANSACTION_COUNT, TRANSFER_BODY
from pyroostermoney.api import RoosterSession
from pyroostermoney.events import EventSource, EventType
from pyroostermoney.enum import Weekdays, PotLedgerTypes
from pyroostermoney.exceptions import ActionFailed
from .money_pot import Pot
from .card import Card
from .standing_order import StandingOrder
from .jobs import Job
from .transaction import Transaction

_LOGGER = logging.getLogger(__name__)

class ChildAccount:
    """The child account."""

    def __init__(self, user_id: int,
                 session: RoosterSession,
                 exclude_card_pin = False) -> None:
        self._exclude_card_pin = exclude_card_pin
        self._session = session
        self.user_id = user_id
        self.interest_rate = None
        self.available_pocket_money = None
        self.currency = None
        self.first_name = None
        self.surname = None
        self.gender = None
        self.allowance = None
        self.allowance_amount = None
        self.allowance_day = None
        self.allowance_last_paid = None
        self.uses_real_money = -1
        self.profile_image = ""
        self.pots: list[Pot] = []
        self.card: Card = None
        self.standing_orders: list[StandingOrder] = []
        self.jobs: list[Job] = []
        self.active_allowance_period_id: int = None
        self.transactions: list[Transaction] = []
        self.declined_transactions: list[Transaction] = []
        self.latest_transaction: Transaction = None

    def __eq__(self, obj):
        if not isinstance(obj, ChildAccount):
            return NotImplemented

        return (self.available_pocket_money == obj.available_pocket_money
        ) and (self.jobs == obj.jobs) and (self.pots == obj.pots) and (
            self.active_allowance_period_id == obj.active_allowance_period_id
        )

    @classmethod
    async def create(cls,
                     user_id: int,
                     session: RoosterSession,
                     exclude_card_pin = True) -> 'ChildAccount':
        """Inits and creates a child account object."""
        self = cls(user_id, session, exclude_card_pin)
        await self.update()
        return self

    async def update(self):
        """Updates the cached data for this child."""
        p_self = self
        _LOGGER.debug("Update ChildAccount")
        self._parse_response(await self._session.request_handler(
            url=URLS.get("get_child").format(user_id=self.user_id)))
        await self.get_pocket_money()
        await self.get_card_details()
        await self.get_standing_orders()
        await self.get_active_allowance_period()
        await self.get_current_jobs()
        await self.get_spend_history()
        if (p_self is not None and
            p_self.active_allowance_period_id != self.active_allowance_period_id or
            p_self.available_pocket_money != self.available_pocket_money):
            self._session.events.fire_event(EventSource.CHILD, EventType.UPDATED,
                                            {
                                                "user_id": self.user_id
                                            })

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
        self.uses_real_money = raw_response["realMoneyStatus"] == 1
        self.profile_image = raw_response["profileImageUrl"]
        self.allowance = not raw_response["locked"]
        self.allowance_amount = raw_response["pocketMoneyAmount"]
        self.allowance_day = Weekdays(raw_response["pocketMoneyDayRaw"]+1)
        self.allowance_last_paid = raw_response["pocketMoneyLastPaid"]

    async def get_active_allowance_period(self):
        """Returns the current active allowance period."""
        allowance_periods = await self._session.request_handler(
            url=URLS.get("get_child_allowance_periods").format(user_id=self.user_id))
        allowance_periods = allowance_periods["response"]
        active_periods = [p for p in allowance_periods
                          if datetime.strptime(p["startDate"], "%Y-%m-%d").date() <=
                          date.today() <=
                          datetime.strptime(p["endDate"], "%Y-%m-%d").date()]
        if len(active_periods) != 1:
            raise LookupError("No allowance period found")

        active_periods = active_periods[0]
        self.active_allowance_period_id = int(active_periods.get("allowancePeriodId"))

        return active_periods

    async def _update_spend_history(self, count=10):
        """Internal update handler for the spend history"""
        url = URLS.get("get_child_spend_history").format(
            user_id=self.user_id,
            count=count
        )
        response = await self._session.request_handler(url=url)
        self.transactions = Transaction.parse_response(response["response"])
        # declined transaction should be ignored as it did not complete
        # therefore it doesn't count towards the "spend history"
        self.declined_transactions = list(filter(lambda x: x.declined, self.transactions))
        self.transactions = list(filter(lambda x: (x.declined is not True), self.transactions))
        p_transaction = self.latest_transaction
        self.latest_transaction = self.transactions[len(self.transactions)-1]
        if (p_transaction is not None
            and self.latest_transaction.transaction_id != p_transaction.transaction_id):
            self._session.events.fire_event(EventSource.TRANSACTIONS, EventType.UPDATED, {
                "old_transaction_id": p_transaction.transaction_id,
                "new_transaction_id": self.latest_transaction.transaction_id,
                "declined": self.latest_transaction.declined,
                "declined_reason": self.latest_transaction.declined_reason
            })

    async def get_spend_history(self, count=10) -> list[Transaction]:
        """Gets the spend history"""
        await self._update_spend_history(count)
        required = count
        # increase count dynamically to ignore declines
        while len(self.transactions) < required:
            _LOGGER.debug("ChildAccount get_spend_history returned only %s events",
                          len(self.transactions))
            count += 1
            await self._update_spend_history(count)
            if count == CHILD_MAX_TRANSACTION_COUNT:
                break

        return self.transactions

    async def get_current_jobs(self) -> list[Job]:
        """Gets jobs for the current allowance period."""
        p_jobs = self.jobs
        self.jobs = await self.get_allowance_period_jobs(self.active_allowance_period_id)
        if (len(p_jobs) > 0 and
            self.jobs[len(self.jobs)-1].master_job_id != p_jobs[len(p_jobs)-1].master_job_id):
            self._session.events.fire_event(EventSource.JOBS, EventType.UPDATED, {
                "job_length": [len(self.jobs)]
            })
        return self.jobs

    async def get_allowance_period_jobs(self, allowance_period_id):
        """Gets jobs for a given allowance period"""
        url = URLS.get("get_child_allowance_period_jobs").format(
            user_id=self.user_id,
            allowance_period_id=allowance_period_id
        )
        response = await self._session.request_handler(url)

        return Job.convert_response(response, self._session)

    async def get_pocket_money(self):
        """Gets pocket money"""
        url = URLS.get("get_child_pocket_money").format(
            user_id=self.user_id
        )
        response = await self._session.request_handler(url)
        self.pots: list[Pot] = Pot.convert_response(response["response"], self._session, self)

        return self.pots

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

    async def get_card_details(self):
        """Returns the card details for the child."""
        if self.card is not None:
            await self.card.update_family_card_entry() # Only run the updater if already set
            return self.card

        card_details = await self._session.request_handler(
            URLS.get("get_child_card_details").format(
                user_id=self.user_id
            )
        )

        self.card = Card.parse_response(card_details["response"], self.user_id, self._session)
        if self._exclude_card_pin is True:
            return self.card

        await self.card.init_card_pin()
        return self.card

    async def get_standing_orders(self) -> list[StandingOrder]:
        """Returns a list of standing orders for the child."""
        standing_orders = await self._session.request_handler(
            URLS.get("get_child_standing_orders").format(
                user_id=self.user_id
            )
        )
        p_standing_orders = self.standing_orders
        self.standing_orders = StandingOrder.convert_response(standing_orders)
        if (len(p_standing_orders)>0 and
            p_standing_orders[len(p_standing_orders)-1].regular_id is not
            self.standing_orders[len(self.standing_orders)-1].regular_id):
            self._session.events.fire_event(EventSource.STANDING_ORDER, EventType.UPDATED, {
                "new_regular_id": self.standing_orders[len(self.standing_orders)-1].regular_id,
                "old_regular_id": p_standing_orders[len(p_standing_orders)-1].regular_id
            })

        return self.standing_orders

    async def create_standing_order(self, standing_order: StandingOrder):
        """Create a standing order."""
        output = await self._session.request_handler(
            URLS.get("create_child_standing_order").format(
                user_id=self.user_id
            ),
            standing_order.__dict__,
            method="POST"
        )

        await self.update()

        return bool(output.get("status") == 200)

    async def delete_standing_order(self, standing_order: StandingOrder):
        """Delete a standing order."""
        output = await self._session.request_handler(
            URLS.get("delete_child_standing_order").format(
                user_id=self.user_id,
                standing_order_id=standing_order.regular_id
            ),
            method="DELETE"
        )

        await self.update()

        return bool(output.get("status") == 200)

    async def update_allowance(self, paused: bool = False, amount: float = 0.0):
        """Updates the allowance for the child."""
        data = {
            "locked": paused,
            "pocketMoneyAmount": amount if amount != 0.0 else self.allowance_amount,
            "stripData": True,
            "userId": self.user_id
        }

        await self._session.request_handler(URLS.get("get_child").format(user_id=self.user_id),
                                            body=data,
                                            method="PUT")
        await self.update()

    async def pot_money_transfer(
            self,
            source: PotLedgerTypes,
            destination: PotLedgerTypes,
            amount: float,
            to_custom_pot_id: str | None = None,
            from_custom_pot_id: str | None = None):
        """Transfers money between two pots.
        Much like pot money management, the amount is in GBP, so passing 1.5 will move £1.50.
        """
        body = TRANSFER_BODY
        body["childUserId"] = self.user_id
        body["familyId"] = self._session.family_id
        body["destinationLedgerType"] = str(destination)
        body["sourceLedgerType"] = str(source)
        body["transferAmount"]["amount"] = int(amount*100)

        # handle custom pots
        if source == PotLedgerTypes.CUSTOM:
            if from_custom_pot_id is not None:
                body["fromCustomPotId"] = from_custom_pot_id
            else:
                raise ValueError("Missing argument for 'from_custom_pot_id")
        if destination == PotLedgerTypes.CUSTOM:
            if from_custom_pot_id is not None:
                body["toCustomPotId"] = to_custom_pot_id
            else:
                raise ValueError("Missing argument for 'to_custom_pot_id")

        response = await self._session.request_handler(
            URLS.get("pot_money_transfer").format(
                family_id=self._session.family_id,
                user_id=self.user_id
            )
        )
        if response["status"] == 200:
            await self.get_pocket_money() # Call this to update pots.
        else:
            raise ActionFailed("HTTP Response Error", response)
