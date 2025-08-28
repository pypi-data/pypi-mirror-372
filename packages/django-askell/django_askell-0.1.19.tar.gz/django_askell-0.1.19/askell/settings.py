import os

from django.conf import settings

def get_setting(key, default_value=None):

    value = getattr(settings, key, None)

    if value:
        return value

    value = os.getenv(key)
    if value:
        return value

    return default_value

ASKELL_ACCOUNT_NAME = get_setting('ASKELL_ACCOUNT_NAME')
ASKELL_API_TOKEN = get_setting('ASKELL_API_TOKEN')
ASKELL_SECRET_KEY = get_setting('ASKELL_SECRET_KEY')
ASKELL_PUBLIC_KEY = get_setting('ASKELL_PUBLIC_KEY')
ASKELL_WEBHOOK_SECRET = get_setting('ASKELL_WEBHOOK_SECRET', '')
ASKELL_ENDPOINT = get_setting(
    'ASKELL_ENDPOINT', 'https://askell.is/api')

ASKELL_CUSTOMER_REFERENCE_USER_FIELD = get_setting(
    'ASKELL_CUSTOMER_REFERENCE_USER_FIELD', 'pk'
)

ASKELL_SUBSCRIPTION_REFERENCE_USER_FIELD = get_setting(
    'ASKELL_SUBSCRIPTION_REFERENCE_USER_FIELD', 'pk'
)