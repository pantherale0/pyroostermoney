# pylint: disable=line-too-long
"""Static Rooster Money variables"""

VERSION="0.3.6"
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
DEFAULT_JOB_IMAGE_URL="https://images.roostermoney.com/static/default_job_icon.png"
MOBILE_APP_VERSION="10.4.1"

SAVINGS_POT_ID="SAVE_POT"
SPEND_POT_ID="SPEND_POT"
GIVE_POT_ID="GIVE_POT"
GOAL_POT_ID="GOAL_POT"

CHILD_MAX_TRANSACTION_COUNT=15 # maximum count for get_spend_history

URLS = {
    "login": "api/v1/parent", # POST
    "get_account_info": "api/parent", # GET
    "get_child": "api/parent/child/{user_id}", # GET
    "get_child_allowance_periods": "api/parent/child/{user_id}/allowance-periods", # GET
    "get_top_up_methods": "api/parent/acquirer/topup/methods?currency={currency}", # GET
    "get_available_cards": "api/parent/acquirer/cards", # GET
    "get_family_account": "api/parent/family/account", # GET
    "get_child_pocket_money": "api/parent/child/{user_id}/pocketmoney", # GET
    "get_child_allowance_period_jobs": "api/parent/child/{user_id}/allowance-periods/{allowance_period_id}/jobs", # GET
    "get_master_jobs": "api/parent/master-jobs", # GET
    "get_child_spend_history": "api/parent/child/{user_id}/spendHistory?count={count}", # GET
    "create_payment": "api/parent/acquirer/create-payment", # POST
    "get_child_card_details": "api/parent/child/{user_id}/card/details", # GET
    "get_child_card_pin": "api/parent/child/{user_id}/cards/{card_id}/pin", # GET
    "get_family_account_cards": "api/parent/family/cards", # GET
    "get_child_standing_orders": "api/parent/child/{user_id}/standingorder", # GET
    "create_child_standing_order": "api/parent/child/{user_id}/standingorder/", # POST
    "delete_child_standing_order": "api/parent/child/{user_id}/standingorder/{delete_child_standing_order}", # DELETE
    "get_master_job_list": "api/parent/master-jobs", # GET
    "pot_money_action": "api/v1/families/{family_id}/children/{user_id}/pots/{pot_id}/{action}", # PUT
    "scheduled_job_action": "/api/parent/scheduled-jobs/{schedule_id}/{action}", # POST
    "freeze_child_card": "/api/parent/child/{user_id}/cards/{card_id}/freeze", # POST
    "get_boost_reasons": "/api/parent/boost/reasons", # GET
    "pot_money_transfer": "/api/v1/families/{family_id}/children/{user_id}/potTransfer" # PUT
}

HEADERS = {
    "content-type": "application/json",
    "accept": "application/json",
    "user-agent": f"Mozilla/5.0 Rooster Money {MOBILE_APP_VERSION}",
    "version": MOBILE_APP_VERSION
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

TRANSFER_BODY = {
    "childUserId": 0,
    "destinationLedgerType": "",
    "familyId": 0,
    "sourceLedgerType": "",
    "transferAmount": {
        "amount": 0,
        "currency": CURRENCY,
        "precision": DEFAULT_PRECISION
    }
}

CREATE_MASTER_JOB_BODY = {
            "childUserIds": [],
            "masterJob": {
                "createdByGuardianId": 1,
                "currency": CURRENCY,
                "description": "",
                "familyId":1,
                "imageUrl": "",
                "rewardAmount": 0.0,
                "scheduleInfo": {
                    "afterLastDone": False,
                    "dueAnyDay": False,
                    "repeatEvery": 1,
                    "startingDate": {
                        "day": "",
                        "month": "",
                        "year": ""
                    },
                    "timeOfDay": 23,
                    "type": 1
                },
                "scheduleType": 1,
                "title": "",
                "type": 0
            }
        }
