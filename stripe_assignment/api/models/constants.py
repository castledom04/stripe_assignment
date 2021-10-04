from django.conf import settings


class PaymentMethodType:
    CARD = 'card'
    BANK = 'bank'


class SubscriptionStatus:
    SUCCESSFUL = 'successful'
    FAILED = 'failed'
    PENDING = 'pending'


class SubscriptionProduct:
    BASIC_PRODUCT_NAME = 'basic_subscription'
    PRO_PRODUCT_NAME = 'pro_subscription'
    BASIC_PRODUCT_PRICE_ID = settings.STRIPE_BASIC_PRODUCT_PRICE_ID
    PRO_PRODUCT_PRICE_ID = settings.STRIPE_PRO_PRODUCT_PRICE_ID

    @staticmethod
    def get_products():
        return [
            SubscriptionProduct.BASIC_PRODUCT_NAME,
            SubscriptionProduct.PRO_PRODUCT_NAME]

    @staticmethod
    def price_by_product(product):
        if product == SubscriptionProduct.BASIC_PRODUCT_NAME:
            return SubscriptionProduct.BASIC_PRODUCT_PRICE_ID
        elif product == SubscriptionProduct.PRO_PRODUCT_NAME:
            return SubscriptionProduct.PRO_PRODUCT_PRICE_ID

        return None
