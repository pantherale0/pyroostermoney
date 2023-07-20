"""A standing order."""
# pylint: disable=too-many-arguments

class StandingOrder:
    """A standing order."""

    def __init__(self,
                 amount: float,
                 day: str,
                 frequency: str,
                 regular_id: str,
                 active: bool,
                 tag: str,
                 title: str) -> None:
        self.amount = amount
        self.day = day
        self.frequency = frequency
        self.regular_id = regular_id
        self.active = active
        self.tag = tag
        self.title = title

    def __dict__(self) -> dict:
        return {
            "amount": str(self.amount),
            "day": self.day,
            "frequency": self.frequency,
            "tag": self.tag,
            "title": self.title
        }

    @staticmethod
    def convert_response(raw_response: str) -> list['StandingOrder']:
        """Parses a raw response of standing orders into a list of StandingOrder"""
        output: list[StandingOrder] = []
        if "response" in raw_response:
            raw_response = raw_response["response"]

        for regular in raw_response:
            standing_order = StandingOrder(
                amount=float(regular.get("amount")),
                day=regular.get("day"),
                frequency=regular.get("frequency"),
                regular_id=regular.get("id"),
                active= bool(regular.get("paused")) is not True,
                tag=regular.get("tag"),
                title=regular.get("title")
            )
            output.append(standing_order)

        return output
