"""Rooster Money card type."""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments

from pyroostermoney.api import RoosterSession
from pyroostermoney.const import URLS
from pyroostermoney.events import EventSource, EventType

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
        self._card_options = {}
        self._session = session
        self.masked_card_number = masked_card_number
        self.expiry_date = expiry_date
        self.name = name
        self.image = image
        self.title = title
        self.description = description
        self.category = category
        self.status = status
        self.user_id = user_id
        self.pin = None
        self.card_id = None
        self.contactless_limit = None
        self.contactless_count = None
        self.spend_limit = None
        self.total_spend = None

    async def init_card_pin(self) -> None:
        """initializes the card pin."""
        # first we need to get the family cards
        await self.update_family_card_entry()
        # if status is still in response, we didn't get a card
        if "status" in self._card_options:
            raise ValueError(f"No card found for {self.user_id}")

        response = await self._session.request_handler(
            url=URLS.get("get_child_card_pin").format(
                user_id=self.user_id,
                card_id=self.card_id
            ),
            add_security_token=True
        )

        response: dict = response["response"]
        self.pin = response.get("pin", None)

    async def update_family_card_entry(self):
        """Requests an update for the internal card entry"""
        response = await self._session.request_handler(
            url=URLS.get("get_family_account_cards")
        )

        if response["status"] == 200:
            # get the card for the current user_id
            for card in response["response"]:
                if card["childId"] == self.user_id:
                    response = card
                    break

        self._card_options = response
        self.card_id = response.get("cardId", None)
        self.contactless_limit = response.get("sca", {}).get("countLimit", 5)
        previous_count = self.contactless_count
        self.contactless_count = response.get("sca", {}).get("count", 0)
        self.spend_limit = response.get("sca", {}).get("spendLimit", {}).get("amount", 135)/100
        self.total_spend = response.get("sca", {}).get("totalSpend", {}).get("amount", 135)/100
        # raise an event if the contactless limit is reached
        if (self.contactless_count is self.contactless_limit) and (
            self.contactless_count is not previous_count):

            self._session.events.fire_event(EventSource.CARD, EventType.UPDATED, {
                "card_id": self.card_id,
                "card_event": "CONTACTLESS_LIMIT"
            })

    async def set_card_status(self, active: bool=True):
        """Freezes/Unfreezes the current card."""
        body = {
            "cardStatus": "active" if active else "lost",
            "reason": "Unfreeze card" if active else "Freeze card"
        }

        await self._session.request_handler(
            url=URLS.get("freeze_child_card").format(
                user_id=self.user_id,
                card_id=self.card_id
            ),
            body=body,
            method="POST")
        await self.update_family_card_entry()

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
