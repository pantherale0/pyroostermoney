"""The main child account class and further actions."""

class ChildAccount:
    """The child account."""

    def __init__(self, raw_response: dict) -> None:
        raw_response = raw_response["response"]
        self.interest_rate = raw_response["interestRate"]
        self.available_pocket_money = raw_response["availablePocketMoney"]
        self.currency = raw_response["currency"]
        self.first_name = raw_response["firstName"]
        self.surname = raw_response["surname"]
        self.gender = "male" if raw_response["gender"] == 1 else "female"
        self.uses_real_money = True if raw_response["realMoneyStatus"] == 1 else False
