from decimal import Decimal

from django.conf import settings

# Are prices shown with tax included or not?
PLATA_PRICE_INCLUDES_TAX = getattr(settings, 'PLATA_PRICE_INCLUDES_TAX', True)

PLATA_ORDER_PROCESSORS = getattr(settings, 'PLATA_ORDER_PROCESSORS', [
    'plata.shop.processors.InitializeOrderProcessor',
    'plata.shop.processors.DiscountProcessor',
    'plata.shop.processors.TaxProcessor',
    'plata.shop.processors.ItemSummationProcessor',
    'plata.shop.processors.ZeroShippingProcessor',
    'plata.shop.processors.OrderSummationProcessor',
    ])

PLATA_PAYMENT_MODULES = getattr(settings, 'PLATA_PAYMENT_MODULES', [
    'plata.payment.modules.cod.PaymentProcessor',
    'plata.payment.modules.postfinance.PaymentProcessor',
    'plata.payment.modules.paypal.PaymentProcessor',
    ])

PLATA_PAYMENT_MODULE_NAMES = getattr(settings, 'PLATA_PAYMENT_MODULE_NAMES', {})

PLATA_SHIPPING_FIXEDAMOUNT = getattr(settings, 'PLATA_SHIPPING_FIXEDAMOUNT', {
    'cost': Decimal('8.00'),
    'tax': Decimal('7.6'),
    })
# Specify the minimum order amount (not considering discounts, not currency-aware) after which shipping is free.
PLATA_SHIPPING_ZERO_WAIVER_MINIMUM = getattr(settings, 'PLATA_SHIPPING_ZERO_WAIVER_MINIMUM', 100)
PLATA_REPORTING_STATIONERY = getattr(settings, 'PLATA_REPORTING_STATIONERY',
    'pdfdocument.elements.ExampleStationery')
PLATA_REPORTING_ADDRESSLINE = getattr(settings, 'PLATA_REPORTING_ADDRESSLINE', '')

PLATA_ALWAYS_BCC = getattr(settings, 'PLATA_ALWAYS_BCC',
    [email for name, email in settings.ADMINS])
PLATA_ORDER_BCC = getattr(settings, 'PLATA_ORDER_BCC',
    [email for name, email in settings.MANAGERS])
PLATA_EMAIL_SENDER_ADDRESS = getattr(settings, 'PLATA_EMAIL_SENDER_ADDRESS', '')
# TODO rework this into a more generic notification configuration
PLATA_SHIPPING_INFO = getattr(settings, 'PLATA_SHIPPING_INFO', PLATA_ORDER_BCC)

CURRENCIES = getattr(settings, 'CURRENCIES', ('CHF', 'EUR', 'USD'))

# Translations for the whole system including the backend
LANGUAGES = getattr(settings, 'LANGUAGES', (('en', 'English'), ('de', 'German')))
# Translations available to visitors of the store (i.e. the store front)
STORE_FRONT_LANGUAGES = getattr(settings, 'STORE_FRONT_LANGUAGES', (('en', 'English'), ('de', 'German')))

# For the personalized order history, we only display the last xy different ordered articles
PLATA_ORDER_HISTORY_MAX_PRODUCTS = getattr(settings, 'PLATA_ORDER_HISTORY_MAX_PRODUCTS', 10)

# Custom settings for the checkout process
PLATA_SIMPLE_CHECKOUT_ENABLED = getattr(settings, 'PLATA_SIMPLE_CHECKOUT_ENABLED', False)
PLATA_SIMPLEST_CHECKOUT_ENABLED = getattr(settings, 'PLATA_SIMPLEST_CHECKOUT_ENABLED', False)
PLATA_AUTH_REQUIRED_TO_ORDER = getattr(settings, 'PLATA_AUTH_REQUIRED_TO_ORDER', True)

PLATA_PRODUCT_THUMBNAIL_SIZE = getattr(settings, 'PLATA_PRODUCT_THUMBNAIL_SIZE', '95x114')
PLATA_PRODUCT_MINI_THUMBNAIL_SIZE = getattr(settings, 'PLATA_PRODUCT_MINI_THUMBNAIL_SIZE', '31x38')