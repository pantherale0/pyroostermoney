"""Defines some standard values for a Natwest Rooster Money child."""
# pylint: disable=too-many-instance-attributes
import logging
from datetime import datetime, date

from pyroostermoney.const import URLS
from pyroostermoney.api import RoosterSession
from pyroostermoney.events import EventSource, EventType
from .money_pot import Pot
from .card import Card
from .standing_order import StandingOrder
from .jobs import Job
from .transaction import Transaction

_LOGGER = logging.getLogger(__name__)

class ChildAccount:
    """The child account."""

    def __init__(self, raw_response: dict, session: RoosterSession, exclude_card = False) -> None:
        self._parse_response(raw_response)
        self._session = session
        self.pots: list[Pot] = []
        self.card: Card = None
        self.standing_orders: list[StandingOrder] = []
        self.jobs: list[Job] = []
        self.active_allowance_period_id: int = None
        self.transactions: list[Transaction] = []
        self.latest_transaction: Transaction = None
        self._exclude_card = exclude_card

    def __del__(self):
        pass
        # if self._session.use_updater:
        #     self._updater.cancel()
        #     self._updater = None

    def __eq__(self, obj):
        if not isinstance(obj, ChildAccount):
            return NotImplemented

        return (self.available_pocket_money == obj.available_pocket_money
        ) and (self.jobs == obj.jobs) and (self.pots == obj.pots) and (
            self.active_allowance_period_id == obj.active_allowance_period_id
        )

    async def perform_init(self):
        """Performs init for some internal async props."""
        await self.get_pocket_money()
        if not self._exclude_card:
            await self.get_card_details()
            self._exclude_card=True
        await self.get_standing_orders()
        await self.get_active_allowance_period()
        await self.get_current_jobs()
        await self.get_spend_history()

    async def update(self):
        """Updates the cached data for this child."""
        p_self = self
        _LOGGER.debug("Update ChildAccount")
        response = await self._session.request_handler(
            url=URLS.get("get_child").format(user_id=self.user_id))
        self._parse_response(response)
        await self.perform_init()
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
        self.user_id = raw_response["userId"]
        self.profile_image = raw_response["profileImageUrl"]

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

    async def get_spend_history(self, count=10) -> list[Transaction]:
        """Gets the spend history"""
        url = URLS.get("get_child_spend_history").format(
            user_id=self.user_id,
            count=count
        )
        response = await self._session.request_handler(url=url)
        self.transactions = Transaction.parse_response(response["response"])
        p_transaction = self.latest_transaction
        self.latest_transaction = self.transactions[len(self.transactions)-1]
        if (p_transaction is not None
            and self.latest_transaction.transaction_id != p_transaction.transaction_id):
            self._session.events.fire_event(EventSource.TRANSACTIONS, EventType.UPDATED, {
                "old_transaction_id": p_transaction.transaction_id,
                "new_transaction_id": self.latest_transaction.transaction_id
            })
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
        self.pots: list[Pot] = Pot.convert_response(response["response"])

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
        card_details = await self._session.request_handler(
            URLS.get("get_child_card_details").format(
                user_id=self.user_id
            )
        )

        self.card = Card.parse_response(card_details["response"], self.user_id, self._session)
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

    # async def add_to_pot(self, value: float, target: Pot) -> Pot:
    #     """Add money to a pot."""

    # async def remove_from_pot(self, value: float, target: Pot) -> Pot:
    #     """Remove money from a pot"""

    # async def transfer_money(self, value: float, source: Pot, target: Pot) -> Pot:
    #     """Transfers money between two pots."""

    # async def create_pot(self, new_pot: Pot) -> Pot:
    #     """Create a new pot."""

    # async def delete_pot(self, pot: Pot) -> bool:
    #     """Delete a pot."""

    async def create_standing_order(self, standing_order: StandingOrder):
        """Create a standing order."""
        output = await self._session.request_handler(
            URLS.get("create_child_standing_order").format(
                user_id=self.user_id
            ),
            standing_order.__dict__,
            method="POST"
        )

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

        return bool(output.get("status") == 200)

    async def update_allowance(self, paused: bool = False, amount: float = 0.0):
        """Updates the allowance for the child."""
        data = {
            "locked": paused,
            "pocketMoneyAmount": amount,
            "stripData": True,
            "userId": self.user_id
        }

        await self._session.request_handler(URLS.get("get_child").format(user_id=self.user_id),
                                            body=data,
                                            method="PUT")
