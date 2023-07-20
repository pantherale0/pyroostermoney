"""Defines a money pot."""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=too-few-public-methods
from datetime import datetime

from pyroostermoney.const import SPEND_POT_ID, SAVINGS_POT_ID, GIVE_POT_ID, GOAL_POT_ID

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
                 last_updated: datetime | None = None) -> None:
        self.name = name
        self.ledger = ledger
        self.pot_id = pot_id
        self.image = image
        self.enabled = enabled
        self.value = value
        self.target = target
        self.last_updated = last_updated

    @staticmethod
    def convert_response(raw: dict) -> list['Pot']:
        """Converts a raw response into a list of Pot"""
        output: list[Pot] = []

        # process the default pots first, starting with savings
        savings = Pot(name="Savings",
                    ledger=None,
                    pot_id=SAVINGS_POT_ID,
                    image=None,
                    enabled=raw["potSettings"]["savePot"]["display"],
                    value=raw["safeTotal"],
                    target=raw["saveGoalAmount"])
        output.append(savings)

        # goal pot
        goals = Pot(name="Goals",
                    ledger=None,
                    pot_id=GOAL_POT_ID,
                    image=None,
                    enabled=raw["potSettings"]["goalPot"]["display"],
                    value=raw["allocatedToGoals"])
        output.append(goals)

        # spend pot
        goals = Pot(name="Spending",
                    ledger=None,
                    pot_id=SPEND_POT_ID,
                    image=None,
                    enabled=raw["potSettings"]["spendPot"]["display"],
                    value=raw["walletTotal"])
        output.append(goals)

        # spend pot
        goals = Pot(name="Give",
                    ledger=None,
                    pot_id=GIVE_POT_ID,
                    image=None,
                    enabled=raw["potSettings"]["givePot"]["display"],
                    value=raw["giveAmount"])
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
                last_updated=pot["updated"]
            )
            output.append(custom_pot)

        return output
