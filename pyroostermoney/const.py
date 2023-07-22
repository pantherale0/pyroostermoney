# pylint: disable=line-too-long
"""Static Rooster Money variables"""

VERSION="0.2.3"
BASE_URL="https://api.rooster.money"
OAUTH_TOKEN_URL="https://auth.rooster.money/oidc/token"
LANGUAGE="en-GB"
COUNTRY="gb"
CURRENCY="GBP"
TIMEZONE_ID=60
TIMEZONE="GMT+01:00"
DEFAULT_PRECISION=2
DEFAULT_BANK_NAME="Rooster Money"
DEFAULT_BANK_TYPE="Business"
MOBILE_APP_VERSION="10.3.1"

SAVINGS_POT_ID="SAVE_POT"
SPEND_POT_ID="SPEND_POT"
GIVE_POT_ID="GIVE_POT"
GOAL_POT_ID="GOAL_POT"

URLS = {
    "login": "api/v1/parent",
    "get_account_info": "api/parent",
    "get_child": "api/parent/child/{user_id}",
    "get_child_allowance_periods": "api/parent/child/{user_id}/allowance-periods",
    "get_top_up_methods": "api/parent/acquirer/topup/methods?currency={currency}",
    "get_available_cards": "api/parent/acquirer/cards",
    "get_family_account": "api/parent/family/account",
    "get_child_pocket_money": "api/parent/child/{user_id}/pocketmoney",
    "get_child_allowance_period_jobs": "api/parent/child/{user_id}/allowance-periods/{allowance_period_id}/jobs",
    "get_master_jobs": "api/parent/master-jobs",
    "get_child_spend_history": "api/parent/child/{user_id}/spendHistory?count={count}",
    "create_payment": "api/parent/acquirer/create-payment",
    "get_child_card_details": "api/parent/child/{user_id}/card/details",
    "get_child_card_pin": "api/parent/child/{user_id}/cards/{card_id}/pin",
    "get_family_account_cards": "api/parent/family/cards",
    "get_child_standing_orders": "api/parent/child/{user_id}/standingorder",
    "create_child_standing_order": "api/parent/child/{user_id}/standingorder/",
    "delete_child_standing_order": "api/parent/child/{user_id}/standingorder/{delete_child_standing_order}",
    "get_master_job_list": "api/parent/master-jobs",
    "boost_pot": "api/v1/families/{family_id}/children/{user_id}/pots/{pot_id}/boost",
    "scheduled_job_action": "/api/parent/scheduled-jobs/{schedule_id}/{action}"
}

HEADERS = {
    "content-type": "application/json",
    "accept": "application/json",
    "user-agent": f"Mozilla/5.0 Rooster Money {MOBILE_APP_VERSION}"
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

BOOST_BODY = {
    "amount": {
        "amount": 0.0,
        "currency": CURRENCY,
        "precision": DEFAULT_PRECISION
    },
    "metaData": {
        "flowSource": "spend pot"
    },
    "reason": ""
}
