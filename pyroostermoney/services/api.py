"""Rooster Money API services."""
import json
from types import SimpleNamespace
import requests
from pyroostermoney.const import COUNTRY, LANGUAGE, CURRENCY, TIMEZONE, TIMEZONE_ID, BASE_URL

HEADERS = {
    "content-type": "application/json",
    "accept": "application/json"
}

LOGIN_BODY={
    "countryOfResidence": COUNTRY,
    "cultureCode": LANGUAGE,
    "currency": CURRENCY,
    "dismissibleAlertSections": [],
    "firstName": None,
    "password": None,
    "relationshipToChild": None,
    "showCountryPopup": None,
    "surname": None,
    "timeZoneId": TIMEZONE_ID,
    "timezone": TIMEZONE,
    "username": None
}

CREATE_PAYMENT_BODY={
    "adyenAPIVersion": "v67",
    "amount": {
        "currency": CURRENCY,
        "value": 0
    },
    "browserInfo": {
        "acceptHeader": "application/json",
        "userAgent": "Mozilla/5.0 Rooster Money 10.3.0"
    },
    "channel": "Android",
    "countryCode": COUNTRY.upper(),
    "isPreAuth": False,
    "paymentMethod": {
        "encryptedCardNumber": "",
        "encryptedExpiryMonth": "",
        "encryptedExpiryYear": "",
        "encryptedSecurityCode": "",
        "holderName": "",
        "type": "scheme"
    },
    "returnUrl": "roostermoneyapp://",
    "shopperEmail": ""
}

class RequestsHandler():
    """Handles HTTP requests from other service modules."""

    def __init__(self, login) -> None:
        self.auth_token=login.access_token,
        self.refresh_token=login.refresh_token,
        self.expiry_time=login.expiry_time
        self.headers = HEADERS
        self.headers["Authorization"] = f"{login.token_type} {self.auth_token[0]}"
        self.s = requests.Session()
        self.s.headers=self.headers
        pass

    @staticmethod
    def _is_success(status_code: int) -> bool:
        return status_code >= 200 and status_code < 300

    @staticmethod
    def _ensure_success(successful: bool):
        if successful:
            pass
        else:
            raise ConnectionError("HTTP Error")

    @staticmethod
    def login(username, password) -> object:
        """Login request"""
        s = requests.Session()
        s.auth = (username, password)
        b = LOGIN_BODY
        b["password"] = password
        b["username"] = username

        r = s.post(
            url=f"{BASE_URL}v1/parent",
            headers=HEADERS,
            json=b
        )

        RequestsHandler._ensure_success(RequestsHandler._is_success(r.status_code))

        return json.loads(r.content, object_hook=lambda d: SimpleNamespace(**d))

    def account_info(self) -> object:
        """Returns account information (/parent)"""
        r = self.s.get(
            url=f"{BASE_URL}/parent"
        )

        RequestsHandler._ensure_success(RequestsHandler._is_success(r.status_code))

        return json.loads(r.content, object_hook=lambda d: SimpleNamespace(**d))

    def get_top_up_methods(self, currency = CURRENCY) -> object:
        """Gets available topup methods (/parent/acquirer/topup/methods)"""
        r = self.s.get(
            url=f"{BASE_URL}/parent/acquirer/topup/methods?currency={currency}"
        )

        RequestsHandler._ensure_success(RequestsHandler._is_success(r.status_code))

        return json.loads(r.content, object_hook=lambda d: SimpleNamespace(**d))

    def get_available_cards(self) -> object:
        """Gets available topup payment cards (/parent/acquirer/cards)"""
        r = self.s.get(
            url=f"{BASE_URL}/parent/acquirer/cards"
        )

        RequestsHandler._ensure_success(RequestsHandler._is_success(r.status_code))

        return json.loads(r.content, object_hook=lambda d: SimpleNamespace(**d))

    def get_family_account(self) -> object:
        """Gets family account details (/parent/family/account)"""
        r = self.s.get(
            url=f"{BASE_URL}/parent/family/account"
        )

        RequestsHandler._ensure_success(RequestsHandler._is_success(r.status_code))

        return json.loads(r.content, object_hook=lambda d: SimpleNamespace(**d))

    def get_child_pocket_money(self, userId):
        """Gets pocket money for a given child (/parent/child/{userId}/pocketmoney)"""
        r = self.s.get(
            url=f"{BASE_URL}/parent/child/{userId}/pocketmoney"
        )

        RequestsHandler._ensure_success(RequestsHandler._is_success(r.status_code))

        return json.loads(r.content, object_hook=lambda d: SimpleNamespace(**d))

    def get_child_allowance_periods(self, userId):
        """Gets allowance periods for a given child (/parent/child/{userId}/allowance-periods)"""
        r = self.s.get(
            url=f"{BASE_URL}/parent/child/{userId}/allowance-periods"
        )

        RequestsHandler._ensure_success(RequestsHandler._is_success(r.status_code))

        return json.loads(r.content, object_hook=lambda d: SimpleNamespace(**d))

    def get_child_allowance_period_jobs(self, userId, allowancePeriodId):
        """Gets jobs for a given allowance period for a given child (/parent/child/{userId}/allowance-periods/{allowancePeriodId})"""
        r = self.s.get(
            url=f"{BASE_URL}/parent/child/{userId}/allowance-periods/{allowancePeriodId}/jobs"
        )

        RequestsHandler._ensure_success(RequestsHandler._is_success(r.status_code))

        return json.loads(r.content, object_hook=lambda d: SimpleNamespace(**d))

    def get_master_job_list(self):
        """Gets master job list (/parent/master-jobs)"""
        r = self.s.get(
            url=f"{BASE_URL}/parent/master-jobs"
        )

        RequestsHandler._ensure_success(RequestsHandler._is_success(r.status_code))

        return json.loads(r.content, object_hook=lambda d: SimpleNamespace(**d))

    def get_child_spend_history(self, userId, count=10):
        """Gets the spend history for a given child (/parent/child/{userId}/spendHistory?count={count})"""
        r = self.s.get(
            url=f"{BASE_URL}/parent/child/{userId}/spendHistory?count={count}"
        )

        RequestsHandler._ensure_success(RequestsHandler._is_success(r.status_code))

        return json.loads(r.content, object_hook=lambda d: SimpleNamespace(**d))

    def create_payment(self, value: float, card_number, expiry_month, expiry_year, security_code, holder_name):
        """Creates a payment to allow topping up the family account."""
        b = CREATE_PAYMENT_BODY
        b["amount"]["value"] = value*100
        b["paymentMethod"]["encryptedCardNumber"] = card_number
        b["paymentMethod"]["encryptedExpiryMonth"] = expiry_month
        b["paymentMethod"]["encryptedExpiryYear"] = expiry_year
        b["paymentMethod"]["encryptedSecurityCode"] = security_code
        b["paymentMethod"]["holderName"] = holder_name
        b["shopperEmail"] = self.account_info().email
        r = self.s.post(
            url=f"{BASE_URL}/parent/acquirer/create-payment",
            json=b
        )

        RequestsHandler._ensure_success(RequestsHandler._is_success(r.status_code))

        return json.loads(r.content, object_hook=lambda d: SimpleNamespace(**d))
