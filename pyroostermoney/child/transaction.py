"""A transaction class"""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments

from datetime import datetime

from pyroostermoney.const import CURRENCY


class Transaction:
    """Defines a single transaction."""

    def __init__(self,
                 action_user: int,
                 amount: float,
                 new_balance: float,
                 description: str,
                 extended_description: str,
                 guardian_profile_image: str,
                 transaction_id: int,
                 message: str,
                 resource_image: str,
                 transaction_timestamp: datetime,
                 source: str,
                 transaction_type: str,
                 user_id: int,
                 currency: str = CURRENCY) -> None:
        self.action_user = action_user
        self.amount = amount
        self.new_balance = new_balance
        self.description = description
        self.extended_description = extended_description
        self.guardian_profile_image = guardian_profile_image
        self.transaction_id = transaction_id
        self.message = message
        self.resource_image = resource_image
        self.transaction_timestamp = transaction_timestamp
        self.source = source
        self.transaction_type = transaction_type
        self.user_id = user_id
        self.currency = currency

    @staticmethod
    def from_dict(obj: dict) -> 'Transaction':
        """Converts a JSON response to a Transaction type"""

        return Transaction(
            action_user=obj.get("actionUserId"),
            amount=obj.get("amount"),
            new_balance=obj.get("balance"),
            currency=obj.get("currency"),
            description=obj.get("description"),
            extended_description=obj.get("descriptionExtension"),
            guardian_profile_image=obj.get("guardianProfileImage"),
            transaction_id=obj.get("id"),
            message=obj.get("message"),
            resource_image=obj.get("resourceImageURL"),
            transaction_timestamp=obj.get("time"),
            source=obj.get("transactionSource"),
            transaction_type=obj.get("type"),
            user_id=obj.get("userId")
        )

    @staticmethod
    def parse_response(obj: list) -> list['Transaction']:
        """Parses the raw response"""
        output = []
        for action in obj:
            output.append(Transaction.from_dict(action))
        return output
