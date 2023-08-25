"""Defines a money pot."""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=too-few-public-methods
from datetime import datetime

from pyroostermoney.const import (
    SPEND_POT_ID,
    SAVINGS_POT_ID,
    GIVE_POT_ID,
    GOAL_POT_ID,
    BOOST_BODY,
    URLS)
from pyroostermoney.enum import (
    EventSource,
    EventType
)
from pyroostermoney.exceptions import NotEnoughFunds, ActionFailed
from pyroostermoney.api import RoosterSession

class Pot:
    """A money pot."""

    def __init__(self,
                 name: str,
                 ledger: dict | None,
                 pot_id: str,
                 image: str | None,
                 enabled: bool,
                 value: float,
                 target: float | None = None,
                 last_updated: datetime | None = None,
                 session: RoosterSession = None,
                 child = None) -> None:
        self.name = name
        self.ledger = ledger
        self.pot_id = pot_id
        self.image = image
        self.enabled = enabled
        self.value = value
        self.target = target
        self.last_updated = last_updated
        self._session = session
        self._user_id = child.user_id

    async def add_to_pot(self, value: float, reason: str = "") -> None:
        """Add money to the pot.
        Value is in GBP, so providing 1.5 will add £1.50 (or 150p)
        """
        if value > self._session.family_balance:
            raise NotEnoughFunds("family account")
        body = BOOST_BODY
        body["amount"]["amount"] = int(value*100)
        body["reason"] = reason
        response = await self._session.request_handler(
            URLS.get("boost_pot").format(
                user_id=self._user_id,
                pot_id=self.pot_id,
                family_id=self._session.family_id
            ),
            body=body,
            method="PUT"
        )
        if response["status"] == 200:
            self.value += value
            self._session.events.fire_event(EventSource.CHILD, EventType.UPDATED, {
                "pot": self.pot_id,
                "reason": reason
            })
        else:
            raise ActionFailed("HTTP Response Error", response)

    @staticmethod
    def convert_response(raw: dict, session: RoosterSession, child) -> list['Pot']:
        """Converts a raw response into a list of Pot"""
        output: list[Pot] = []

        # process the default pots first, starting with savings
        savings = Pot(name="Savings",
                    ledger=None,
                    pot_id=SAVINGS_POT_ID,
                    image=None,
                    enabled=raw["potSettings"]["savePot"]["display"],
                    value=raw["safeTotal"],
                    target=raw["saveGoalAmount"],
                    session=session,
                    child=child)
        output.append(savings)

        # goal pot
        goals = Pot(name="Goals",
                    ledger=None,
                    pot_id=GOAL_POT_ID,
                    image=None,
                    enabled=raw["potSettings"]["goalPot"]["display"],
                    value=raw["allocatedToGoals"],
                    session=session,
                    child=child)
        output.append(goals)

        # spend pot
        goals = Pot(name="Spending",
                    ledger=None,
                    pot_id=SPEND_POT_ID,
                    image=None,
                    enabled=raw["potSettings"]["spendPot"]["display"],
                    value=raw["walletTotal"],
                    session=session,
                    child=child)
        output.append(goals)

        # spend pot
        goals = Pot(name="Give",
                    ledger=None,
                    pot_id=GIVE_POT_ID,
                    image=None,
                    enabled=raw["potSettings"]["givePot"]["display"],
                    value=raw["giveAmount"],
                    session=session,
                    child=child)
        output.append(goals)

        # now process custom pots
        for pot in raw["customPots"]:
            custom_pot = Pot(
                name=pot["customLedgerMetadata"]["title"],
                pot_id=pot["customPotId"],
                ledger=pot["customLedgerMetadata"],
                image=pot["customLedgerMetadata"]["imageUrl"],
                enabled=True, # custom pots enabled by default
                value=pot["availableBalance"]["amount"],
                target=pot["customLedgerMetadata"]["upperLimit"]["amount"],
                last_updated=pot["updated"],
                session=session,
                child=child
            )
            output.append(custom_pot)

        return output
