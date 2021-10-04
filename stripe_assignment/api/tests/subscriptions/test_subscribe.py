from django.urls import reverse
from django.utils import timezone
from doublex import Stub
from expects import be_above, be_false, be_true, equal, expect, have_len
from mock import patch
from rest_framework import status
from stripe.error import AuthenticationError, CardError, InvalidRequestError

from ...models import Account, Customer, PaymentMethod, Subscription, User
from ...models.constants import (PaymentMethodType, SubscriptionProduct,
                                 SubscriptionStatus)
from ..base import BaseAPITestCase


class SubscibeTestCase(BaseAPITestCase):

    def setUp(self):
        self.url = reverse('subscriptions-subscribe')
        self.account = Account.objects.create(name="User account")
        self.user = User.objects.create_user(
            username='goku',
            password='goku1234',
            first_name='Son',
            last_name='Goku',
            email='goku@dragonball.com',
            account=self.account
        )

    def test_it_returns_not_authorized_with_no_credentials(self):
        response = self.post(url=self.url, user=None, data={})

        expect(response.status_code).to(equal(status.HTTP_401_UNAUTHORIZED))

    def test_required_fields_when_creating_a_user(self):
        data = {}

        response = self.post(url=self.url, user=self.user, data=data)

        expect(response.status_code).to(equal(status.HTTP_400_BAD_REQUEST))
        expect(response.json()).to(equal({
            'subscription_product': ['This field is required.'],
            'card_number': ['This field is required.'],
            'card_expiration_month': ['This field is required.'],
            'card_expiration_year': ['This field is required.'],
            'card_cvc': ['This field is required.']
        }))

    def test_subscription_product_exist_validation(self):
        data = {
            'subscription_product': 'invented_product',
            'card_number': '4242424242424242',
            'card_expiration_month': 3,
            'card_expiration_year': 2100,
            'card_cvc': 123
        }

        response = self.post(url=self.url, user=self.user, data=data)

        expect(response.status_code).to(equal(status.HTTP_400_BAD_REQUEST))
        expect(response.json()).to(equal(
            {'subscription_product': ['Subscription product does not exist.']}
        ))

    def test_card_number_length_validation(self):
        data = {
            'subscription_product': SubscriptionProduct.BASIC_PRODUCT_NAME,
            'card_number': 123,
            'card_expiration_month': 3,
            'card_expiration_year': 2100,
            'card_cvc': 123
        }

        response = self.post(url=self.url, user=self.user, data=data)

        expect(response.status_code).to(equal(status.HTTP_400_BAD_REQUEST))
        expect(response.json()).to(equal(
            {'card_number': ['Ensure this field has at least 16 characters.']}
        ))

    def test_card_number_is_numeric_validation(self):
        data = {
            'subscription_product': SubscriptionProduct.BASIC_PRODUCT_NAME,
            'card_number': 'asdd123412341234',
            'card_expiration_month': 3,
            'card_expiration_year': 2100,
            'card_cvc': 123
        }

        response = self.post(url=self.url, user=self.user, data=data)

        expect(response.status_code).to(equal(status.HTTP_400_BAD_REQUEST))
        expect(response.json()).to(equal(
            {'card_number': ['Card number must be numeric.']}
        ))

    def test_card_expiration_validation(self):
        data = {
            'subscription_product': SubscriptionProduct.BASIC_PRODUCT_NAME,
            'card_number': '4242424242424242',
            'card_expiration_month': 3,
            'card_expiration_year': 2000,
            'card_cvc': 123
        }

        response = self.post(url=self.url, user=self.user, data=data)

        expect(response.status_code).to(equal(status.HTTP_400_BAD_REQUEST))
        expect(response.json()).to(equal({
            'card_expiration_month': ['Card expiration is past due.'],
            'card_expiration_year': ['Card expiration is past due.']
        }))

    @patch('stripe.Subscription.create')
    @patch('stripe.PaymentMethod.attach')
    @patch('stripe.PaymentMethod.create')
    @patch('stripe.Customer.modify')
    @patch('stripe.Customer.create')
    def test_it_creates_a_customer_if_does_not_exist(
        self,
        customer_create,
        customer_modify,
        payment_method_create,
        payment_method_attach,
        subscription_create
    ):
        data = {
            'subscription_product': SubscriptionProduct.BASIC_PRODUCT_NAME,
            'card_number': '4242424242424242',
            'card_expiration_month': 10,
            'card_expiration_year': 2100,
            'card_cvc': 767}
        with Stub() as StubCustomer:
            StubCustomer.id = "cus_whatever"
        customer_create.return_value = StubCustomer
        PaymentMethod.objects.create(
            is_active=True,
            id_reference='cus_whatever',
            type=PaymentMethodType.CARD,
            account=self.user.account)
        before_call_datetime = timezone.now()

        response = self.post(url=self.url, user=self.user, data=data)

        expect(response.status_code).to(equal(status.HTTP_200_OK))
        expect(customer_create.called).to(be_true)
        _, kwargs = customer_create.call_args
        expect(kwargs).to(equal({
            'name': self.user.name,
            'email': self.user.email,
            'metadata': {'user_id': f'{self.user.id}'}
        }))
        customer = self.user.get_customer()
        expect(customer.id_reference).to(equal('cus_whatever'))
        expect(customer.is_active).to(be_true)
        expect(customer.account).to(equal(self.user.account))
        expect(customer.created_at).to(be_above(before_call_datetime))

    @patch('stripe.Subscription.create')
    @patch('stripe.PaymentMethod.attach')
    @patch('stripe.PaymentMethod.create')
    @patch('stripe.Customer.modify')
    @patch('stripe.Customer.create')
    def test_it_does_not_create_a_customer_if_already_exist(
        self,
        customer_create,
        customer_modify,
        payment_method_create,
        payment_method_attach,
        subscription_create
    ):
        data = {
            'subscription_product': SubscriptionProduct.BASIC_PRODUCT_NAME,
            'card_number': '4242424242424242',
            'card_expiration_month': 10,
            'card_expiration_year': 2100,
            'card_cvc': 767}
        existing_customer = Customer.objects.create(
            is_active=True,
            id_reference='cus_whatever',
            account=self.user.account)
        PaymentMethod.objects.create(
            is_active=True,
            id_reference='cus_whatever',
            type=PaymentMethodType.CARD,
            account=self.user.account)

        response = self.post(url=self.url, user=self.user, data=data)

        expect(response.status_code).to(equal(status.HTTP_200_OK))
        expect(customer_create.called).to(be_false)
        expect(Customer.objects.filter(account=self.account)).to(have_len(1))
        expect(self.user.get_customer().id).to(equal(existing_customer.id))

    @patch('stripe.Subscription.create')
    @patch('stripe.PaymentMethod.attach')
    @patch('stripe.PaymentMethod.create')
    @patch('stripe.Customer.modify')
    def test_it_creates_a_payment_method_and_attaches_it_to_the_customer(
        self,
        customer_modify,
        payment_method_create,
        payment_method_attach,
        subscription_create
    ):
        data = {
            'subscription_product': SubscriptionProduct.BASIC_PRODUCT_NAME,
            'card_number': '4242424242424242',
            'card_expiration_month': 10,
            'card_expiration_year': 2100,
            'card_cvc': 767}
        Customer.objects.create(
            is_active=True,
            id_reference='cus_whatever',
            account=self.user.account)
        with Stub() as StubPaymentMethod:
            StubPaymentMethod.id = "pm_whatever"
        payment_method_create.return_value = StubPaymentMethod
        before_call_datetime = timezone.now()

        response = self.post(url=self.url, user=self.user, data=data)

        expect(response.status_code).to(equal(status.HTTP_200_OK))
        expect(payment_method_create.called).to(be_true)
        _, kwargs = payment_method_create.call_args
        expect(kwargs).to(equal({
            'type': 'card',
            'card': {
                "number": "4242424242424242",
                "exp_month": 10,
                "exp_year": 2100,
                "cvc": 767,
            },
        }))
        expect(payment_method_attach.called).to(be_true)
        _, kwargs = payment_method_attach.call_args
        expect(kwargs).to(equal({
            'sid': 'pm_whatever',
            'customer': 'cus_whatever',
        }))
        expect(customer_modify.called).to(be_true)
        _, kwargs = customer_modify.call_args
        expect(kwargs).to(equal({
            'sid': 'cus_whatever',
            'invoice_settings': {
                'default_payment_method': 'pm_whatever'
            }
        }))
        payment_method = self.user.get_payment_method()
        expect(payment_method.id_reference).to(equal('pm_whatever'))
        expect(payment_method.is_active).to(be_true)
        expect(payment_method.type).to(equal(PaymentMethodType.CARD))
        expect(payment_method.account).to(equal(self.user.account))
        expect(payment_method.created_at).to(be_above(before_call_datetime))

    @patch('stripe.Subscription.create')
    @patch('stripe.PaymentMethod.attach')
    @patch('stripe.PaymentMethod.create')
    @patch('stripe.Customer.modify')
    def test_it_does_not_creates_a_payment_method_if_already_exist(
        self,
        customer_modify,
        payment_method_create,
        payment_method_attach,
        subscription_create
    ):
        data = {
            'subscription_product': SubscriptionProduct.BASIC_PRODUCT_NAME,
            'card_number': '4242424242424242',
            'card_expiration_month': 10,
            'card_expiration_year': 2100,
            'card_cvc': 767}
        Customer.objects.create(
            is_active=True,
            id_reference='cus_whatever',
            account=self.user.account)
        existing_payment_method = PaymentMethod.objects.create(
            is_active=True,
            id_reference='cus_whatever',
            type=PaymentMethodType.CARD,
            account=self.user.account)

        response = self.post(url=self.url, user=self.user, data=data)

        expect(response.status_code).to(equal(status.HTTP_200_OK))
        expect(payment_method_create.called).to(be_false)
        expect(payment_method_attach.called).to(be_false)
        expect(customer_modify.called).to(be_false)
        expect(PaymentMethod.objects.filter(account=self.account)).to(have_len(1))
        expect(self.user.get_payment_method().id).to(equal(existing_payment_method.id))

    @patch('stripe.Subscription.create')
    @patch('stripe.PaymentMethod.attach')
    @patch('stripe.PaymentMethod.create')
    @patch('stripe.Customer.modify')
    def test_it_handles_payment_method_creation_error(
        self,
        customer_modify,
        payment_method_create,
        payment_method_attach,
        subscription_create
    ):
        data = {
            'subscription_product': SubscriptionProduct.BASIC_PRODUCT_NAME,
            'card_number': '4242424242424242',
            'card_expiration_month': 10,
            'card_expiration_year': 2100,
            'card_cvc': 767}
        Customer.objects.create(
            is_active=True,
            id_reference='cus_whatever',
            account=self.user.account)
        payment_method_create.side_effect = CardError(
            message="Card error",
            param="number",
            code="whatever"
        )

        response = self.post(url=self.url, user=self.user, data=data)

        expect(response.status_code).to(equal(status.HTTP_400_BAD_REQUEST))
        expect(response.json()).to(equal({'non_field_errors': ['Card error']}))
        expect(payment_method_create.called).to(be_true)
        expect(payment_method_attach.called).to(be_false)
        expect(customer_modify.called).to(be_false)
        expect(subscription_create.called).to(be_false)

    @patch('stripe.Subscription.create')
    def test_it_creates_a_temporal_subscription_to_avoid_creating_multiple_subscriptions(
        self,
        subscription_create
    ):
        data = {
            'subscription_product': SubscriptionProduct.BASIC_PRODUCT_NAME,
            'card_number': '4242424242424242',
            'card_expiration_month': 10,
            'card_expiration_year': 2100,
            'card_cvc': 767}
        Customer.objects.create(
            is_active=True,
            id_reference='cus_whatever',
            account=self.user.account)
        PaymentMethod.objects.create(
            is_active=True,
            id_reference='cus_whatever',
            type=PaymentMethodType.CARD,
            account=self.user.account)

        response = self.post(url=self.url, user=self.user, data=data)

        expect(response.status_code).to(equal(status.HTTP_200_OK))
        expect(subscription_create.called).to(be_true)
        _, kwargs = subscription_create.call_args
        expect(kwargs).to(equal({
            'customer': 'cus_whatever',
            'items': [{
                'price': SubscriptionProduct.BASIC_PRODUCT_PRICE_ID,
            }]
        }))
        subscription = self.user.get_subscription()
        expect(subscription.status).to(equal(SubscriptionStatus.PENDING))
        expect(subscription.price_reference).to(equal(
            SubscriptionProduct.price_by_product(SubscriptionProduct.BASIC_PRODUCT_NAME)))
        expect(subscription.account).to(equal(self.account))

    @patch('stripe.Subscription.create')
    def test_it_does_not_creates_a_subscription_if_already_exist_and_returns_a_409_error(
        self,
        subscription_create
    ):
        data = {
            'subscription_product': SubscriptionProduct.BASIC_PRODUCT_NAME,
            'card_number': '4242424242424242',
            'card_expiration_month': 10,
            'card_expiration_year': 2100,
            'card_cvc': 767}
        Customer.objects.create(
            is_active=True,
            id_reference='cus_whatever',
            account=self.user.account)
        PaymentMethod.objects.create(
            is_active=True,
            id_reference='cus_whatever',
            type=PaymentMethodType.CARD,
            account=self.user.account)
        subscription = Subscription.objects.create(
            status=SubscriptionStatus.PENDING,
            price_reference=SubscriptionProduct.price_by_product(
                SubscriptionProduct.BASIC_PRODUCT_NAME),
            account=self.account
        )

        response = self.post(url=self.url, user=self.user, data=data)

        expect(response.status_code).to(equal(status.HTTP_409_CONFLICT))
        expect(response.json()).to(equal({'non_field_errors': ['Already subscribed!']}))
        expect(subscription_create.called).to(be_false)
        expect(Subscription.objects.filter(account=self.account)).to(have_len(1))
        expect(self.user.get_subscription().id).to(equal(subscription.id))

    @patch('stripe.Subscription.create')
    def test_it_does_not_create_a_temporal_subscription_if_subscription_creation_fails(
        self,
        subscription_create
    ):
        data = {
            'subscription_product': SubscriptionProduct.BASIC_PRODUCT_NAME,
            'card_number': '4242424242424242',
            'card_expiration_month': 10,
            'card_expiration_year': 2100,
            'card_cvc': 767}
        Customer.objects.create(
            is_active=True,
            id_reference='cus_whatever',
            account=self.user.account)
        PaymentMethod.objects.create(
            is_active=True,
            id_reference='cus_whatever',
            type=PaymentMethodType.CARD,
            account=self.user.account)
        subscription_create.side_effect = InvalidRequestError(
            message="InvalidRequestError",
            param="number",
        )

        response = self.post(url=self.url, user=self.user, data=data)

        expect(response.status_code).to(equal(status.HTTP_400_BAD_REQUEST))
        expect(response.json()).to(equal({'non_field_errors': ['InvalidRequestError']}))
        expect(subscription_create.called).to(be_true)
        expect(self.user.get_subscription()).to(equal(None))

    @patch('stripe.Customer.create')
    def test_it_controls_payments_gateway_provider_errors(
        self,
        customer_create
    ):
        data = {
            'subscription_product': SubscriptionProduct.BASIC_PRODUCT_NAME,
            'card_number': '4242424242424242',
            'card_expiration_month': 10,
            'card_expiration_year': 2100,
            'card_cvc': 767}
        customer_create.side_effect = AuthenticationError(
            message="AuthenticationError",
        )

        response = self.post(url=self.url, user=self.user, data=data)

        expect(response.status_code).to(equal(status.HTTP_400_BAD_REQUEST))
        expect(response.json()).to(equal({'non_field_errors': ['AuthenticationError']}))
