"""Static Rooster Money variables"""

VERSION="0.1.0"
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
    "get_child": "api/parent/child/{user_id}"
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
