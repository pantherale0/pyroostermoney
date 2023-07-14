"""Python Rooster Money module."""

from .services.login import ParentLoginManager
from .services.session import SessionManager
from .const import DEFAULT_BANK_NAME, DEFAULT_BANK_TYPE

class RoosterMoney():

    def __init__(self) -> None:
        self.account = None
        self.session = None

    def login(self, username, password):
        """Starts a session to Rooster Money and logs into the API."""
        self.account = ParentLoginManager(username, password)
        self.session = SessionManager(self.account)

    def account_info(self):
        return self.session.requests.account_info()
    
    def request_update(self):
        self.session._update()

    def get_child(self, userId: int) -> object:
        return self.session.get_child(userId)
    
    def get_child_active_allowance_period(self, userId: int) -> object:
        return self.session.get_child_active_allowance_period(userId)
    
    def get_bank_transfer_account_details(self):
        acc = self.session.requests.get_family_account()
        return {
            "account_number": acc.accountNumber,
            "sort_code": acc.sortCode,
            "type": DEFAULT_BANK_TYPE,
            "name": DEFAULT_BANK_NAME
        }

    def get_child_pocket_money(self, userId: int):
        pocket_money = self.session.requests.get_child_pocket_money(userId)

        return {
            "total": pocket_money.walletTotal,
            "available": pocket_money.availablePocketMoney,
            "spend": pocket_money.pocketMoneyAmount,
            "save": pocket_money.safeTotal,
            "give": pocket_money.giveAmount
        }

    def topup_family_account(self, value):
        r = self.session.requests.create_payment(value, 1, 1, 1, 1, "test")
        return r
