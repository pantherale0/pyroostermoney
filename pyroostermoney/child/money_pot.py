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
    EventType,
    PotMoneyActions,
    PotLedgerTypes
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
                 child = None,
                 ledger_type: PotLedgerTypes | str | None = None) -> None:
        self.name = name
        self.ledger = ledger
        self.pot_id = pot_id
        self.image = image
        self.enabled = enabled
        self.value = value
        self.target = target/100 if target is not None else None
        self.last_updated = last_updated
        self._session = session
        self._user_id = child.user_id
        self.ledger_type = ledger_type

    async def add_to_pot(self, value: float, reason: str = "") -> None:
        """Add money to the pot.
        Value is in GBP, so providing 1.5 will add £1.50 (or 150p)
        """
        if value > self._session.family_balance:
            raise NotEnoughFunds("family account")
        await self._pot_money_action(PotMoneyActions.BOOST, value, reason)
        self.value += value

    async def remove_from_pot(self, value: float, reason: str = "") -> None:
        """Remove money from the pot.
        Value is in GBP, so providing 1.5 will remove £1.50 (or 150p)
        """
        if value > self.value:
            raise NotEnoughFunds(self.pot_id)
        await self._pot_money_action(PotMoneyActions.REMOVE, value, reason)
        self.value -= value

    async def _pot_money_action(self,
                                action: PotMoneyActions,
                                value: float,
                                reason: str = "") -> None:
        """Internal pot money action handler."""
        body = BOOST_BODY
        body["amount"]["amount"] = int(value*100)
        body["reason"] = reason
        response = await self._session.request_handler(
            URLS.get("pot_money_action").format(
                user_id=self._user_id,
                pot_id=self.pot_id,
                family_id=self._session.family_id,
                action=action
            ),
            body=body,
            method="PUT"
        )
        if response["status"] == 200:
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
                    ledger_type=PotLedgerTypes.SAVE,
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
                    ledger_type=PotLedgerTypes.GOAL,
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
                    ledger_type=PotLedgerTypes.SPEND,
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
                    ledger_type=PotLedgerTypes.GIVE,
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
                ledger_type=PotLedgerTypes.CUSTOM,
                last_updated=pot["updated"],
                session=session,
                child=child
            )
            output.append(custom_pot)

        return output
