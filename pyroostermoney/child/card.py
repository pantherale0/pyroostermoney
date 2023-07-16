"""Rooster Money card type."""

from pyroostermoney.api import RoosterSession
from pyroostermoney.const import URLS

class Card:
    """A card."""

    def __init__(self, raw: dict, user_id: str, session: RoosterSession) -> None:
        self.masked_card_number = raw["image"]["maskedPan"]
        self.expiry_date = raw["image"]["expDate"]
        self.name = raw["name"]
        self.image = raw["cardTemplate"]["imageUrl"]
        self.title = raw["cardTemplate"]["title"]
        self.description = raw["cardTemplate"]["description"]
        self.category = raw["cardTemplate"]["category"]
        self.status = raw["status"]
        self._session = session
        self.user_id = user_id
        self.pin = None

    async def init_card_pin(self) -> None:
        """initializes the card pin."""
        # first we need to get the family cards
        response = await self._session.request_handler(
            url=URLS.get("get_family_account_cards")
        )

        if response["status"] == 200:
            # get the card for the current user_id
            for card in response["response"]:
                if card["childId"] == self.user_id:
                    response = card
                    break

        # if status is still in response, we didn't get a card
        if "status" in response:
            raise ValueError(f"No card found for {self.user_id}")

        response = await self._session.request_handler(
            url=URLS.get("get_child_card_pin").format(
                user_id=self.user_id,
                card_id=response["cardId"]
            ),
            add_security_token=True
        )

        response: dict = response["response"]
        self.pin = response.get("pin", None)
