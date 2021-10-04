import stripe
from django.conf import settings

from ..exceptions import (PaymentsAlreadySubscribedError, PaymentsCardError,
                          PaymentsGatewayError)
from ..models import Customer, PaymentMethod, Subscription
from ..models.constants import (PaymentMethodType, SubscriptionProduct,
                                SubscriptionStatus)


class PaymentsGateway:

    def __init__(self):
        stripe.api_key = settings.STRIPE_API_SECRET

    def create_subscription(self, requester, data):
        try:
            customer = requester.get_customer()
            if customer:
                customer_reference = customer.id_reference
            else:
                customer_reference = self.__create_customer(requester)

            if not requester.get_payment_method():
                self.__create_payment_method(requester, customer_reference, data)

            self.__create_subscription(requester, customer_reference, data)

        except stripe.error.CardError as e:
            raise PaymentsCardError(message=e.user_message)

        except stripe.error.RateLimitError as e:
            self.__delete_temporal_subscription(requester)
            raise PaymentsGatewayError(message=f'{e}')

        except stripe.error.InvalidRequestError as e:
            self.__delete_temporal_subscription(requester)
            raise PaymentsGatewayError(message=f'{e}')

        except stripe.error.AuthenticationError as e:
            self.__delete_temporal_subscription(requester)
            raise PaymentsGatewayError(message=f'{e}')

        except stripe.error.APIConnectionError as e:
            self.__delete_temporal_subscription(requester)
            raise PaymentsGatewayError(message=f'{e}')

        except stripe.error.StripeError as e:
            self.__delete_temporal_subscription(requester)
            raise PaymentsGatewayError(message=f'{e}')

    def __create_customer(self, requester):
        customer = stripe.Customer.create(
            name=requester.name,
            email=requester.email,
            metadata={'user_id': f'{requester.id}'}
        )
        Customer.objects.create(
            is_active=True,
            id_reference=customer.id,
            account=requester.account)

        return customer.id

    def __create_payment_method(self, requester, customer_reference, data):
        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": data.get('card_number'),
                "exp_month": data.get('card_expiration_month'),
                "exp_year": data.get('card_expiration_year'),
                "cvc": data.get('card_cvc'),
            },
        )

        stripe.PaymentMethod.attach(
            sid=payment_method.id,
            customer=customer_reference
        )

        stripe.Customer.modify(
            sid=customer_reference,
            invoice_settings={
                'default_payment_method': payment_method.id
            }
        )

        PaymentMethod.objects.create(
            is_active=True,
            type=PaymentMethodType.CARD,
            id_reference=payment_method.id,
            account=requester.account)

    def __create_subscription(self, requester, customer_reference, data):
        if Subscription.objects.filter(account=requester.account).exists():
            raise PaymentsAlreadySubscribedError(message="Already subscribed!")

        Subscription.objects.create(
            status=SubscriptionStatus.PENDING,
            price_reference=SubscriptionProduct.price_by_product(data.get('subscription_product')),
            account=requester.account
        )

        return stripe.Subscription.create(
            customer=customer_reference,
            items=[{
                'price': SubscriptionProduct.price_by_product(data.get('subscription_product'))
            }],
        )

    def __delete_temporal_subscription(self, requester):
        subscription = Subscription.objects.filter(
            status=SubscriptionStatus.PENDING,
            account=requester.account)
        if subscription:
            subscription.delete()
