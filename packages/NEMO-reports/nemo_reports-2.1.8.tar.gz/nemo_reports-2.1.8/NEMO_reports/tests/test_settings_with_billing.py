from .test_settings import *

INSTALLED_APPS += [
    "NEMO_billing",
    "NEMO_billing.rates",
    "NEMO_billing.invoices",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "./test_nemo_billing.db",
    }
}
