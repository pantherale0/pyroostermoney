"""Static Rooster Money variables"""

VERSION="0.1.3"
BASE_URL="https://api.rooster.money"
LANGUAGE="en-GB"
COUNTRY="gb"
CURRENCY="GBP"
TIMEZONE_ID=60
TIMEZONE="GMT+01:00"
DEFAULT_PRECISION=2
DEFAULT_BANK_NAME="Rooster Money"
DEFAULT_BANK_TYPE="Business"
MOBILE_APP_VERSION="10.3.1"

URLS = {
    "login": "api/v1/parent",
    "get_account_info": "api/parent",
    "get_child": "api/parent/child/{user_id}",
    "get_child_allowance_periods": "api/parent/child/{user_id}/allowance-periods",
    "get_top_up_methods": "api/parent/acquirer/topup/methods?currency={currency}",
    "get_available_cards": "api/parent/acquirer/cards",
    "get_family_account": "api/parent/family/account",
    "get_child_pocket_money": "api/parent/child/{user_id}/pocketmoney",
    "get_child_allowance_period_jobs": "api/parent/child/{user_id}/allowance-periods/{allowance_period_id}",
    "get_master_jobs": "api/parent/master-jobs",
    "get_child_spend_history": "api/parent/child/{user_id}/spendHistory?count={count}",
    "create_payment": "api/parent/acquirer/create-payment"
}

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
        "userAgent": f"Mozilla/5.0 Rooster Money {MOBILE_APP_VERSION}"
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
