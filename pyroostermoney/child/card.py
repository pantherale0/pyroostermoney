"""Rooster Money card type."""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments

from pyroostermoney.api import RoosterSession
from pyroostermoney.const import URLS

class Card:
    """A card."""

    def __init__(self,
                 masked_card_number: str,
                 expiry_date: str,
                 name: str,
                 image: str,
                 title: str,
                 description: str,
                 category: str,
                 status: str,
                 user_id: str,
                 session: RoosterSession) -> None:
        self.masked_card_number = masked_card_number
        self.expiry_date = expiry_date
        self.name = name
        self.image = image
        self.title = title
        self.description = description
        self.category = category
        self.status = status
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

    @staticmethod
    def parse_response(raw: dict, user_id: str, session: RoosterSession) -> 'Card':
        """RESPONSE PARSER"""
        return Card(
            masked_card_number = raw["image"]["maskedPan"],
            expiry_date = raw["image"]["expDate"],
            name = raw["name"],
            image = raw["cardTemplate"]["imageUrl"],
            title = raw["cardTemplate"]["title"],
            description = raw["cardTemplate"]["description"],
            category = raw["cardTemplate"]["category"],
            status = raw["status"],
            session = session,
            user_id = user_id
        )
