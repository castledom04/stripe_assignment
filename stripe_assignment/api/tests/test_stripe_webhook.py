from datetime import datetime

import pytz
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from expects import equal, expect
from rest_framework import status

from ..models import Account, Customer, Subscription, User
from ..models.constants import SubscriptionProduct, SubscriptionStatus
from .base import BaseAPITestCase


class StripeWebHookTestCase(BaseAPITestCase):

    def setUp(self):
        self.url = reverse('stripe-webhook')
        self.account = Account.objects.create(name="User account")
        self.user = User.objects.create_user(
            username='goku',
            password='goku1234',
            first_name='Son',
            last_name='Goku',
            email='goku@dragonball.com',
            account=self.account
        )

    @override_settings(STRIPE_WEBHOOK_SECRET='')
    def test_it_updates_subscription_data_from_a_created_event(self):
        stripe_data_mock = {
            'id': 'evt_1Jgi50KBAHswNGjYg6mOHDr0',
            'type': 'customer.subscription.created',
            'object': 'event',
            'api_version': '2020-08-27',
            'created': 1633318985,
            'data': {
                'object': {
                    'id': 'sub_1Jgi4xKBAHswNGjYuEORMJpB',
                    'created': 1633318983,
                    'current_period_end': 1635997383,
                    'current_period_start': 1633318983,
                    'customer': 'cus_KLOsroz46wGUr7',
                    'status': 'active',
                }
            }
        }
        Customer.objects.create(
            is_active=True,
            id_reference='cus_KLOsroz46wGUr7',
            account=self.user.account)
        Subscription.objects.create(
            status=SubscriptionStatus.PENDING,
            price_reference=SubscriptionProduct.price_by_product(
                SubscriptionProduct.BASIC_PRODUCT_NAME),
            account=self.account
        )

        response = self.post(url=self.url, user=None, data=stripe_data_mock)

        expect(response.status_code).to(equal(status.HTTP_200_OK))
        subscription = self.user.get_subscription()
        zone = pytz.timezone("UTC")
        current_period_start = zone.localize(datetime.fromtimestamp(1633318983))
        current_period_end = zone.localize(datetime.fromtimestamp(1635997383))
        expect(subscription.status).to(equal(SubscriptionStatus.SUCCESSFUL))
        expect(subscription.payment_gateway_status).to(equal('active'))
        expect(subscription.id_reference).to(equal('sub_1Jgi4xKBAHswNGjYuEORMJpB'))
        expect(subscription.current_period_start).to(equal(current_period_start))
        expect(subscription.current_period_end).to(equal(current_period_end))

    @override_settings(STRIPE_WEBHOOK_SECRET='')
    def test_it_correctly_changes_status_to_failed_if_subscription_is_not_ready_from_a_created_event(self):
        stripe_data_mock = {
            'id': 'evt_1Jgi50KBAHswNGjYg6mOHDr0',
            'type': 'customer.subscription.created',
            'object': 'event',
            'api_version': '2020-08-27',
            'created': 1633318985,
            'data': {
                'object': {
                    'id': 'sub_1Jgi4xKBAHswNGjYuEORMJpB',
                    'created': 1633318983,
                    'current_period_end': 1635997383,
                    'current_period_start': 1633318983,
                    'customer': 'cus_KLOsroz46wGUr7',
                    'status': 'incomplete',
                }
            }
        }
        Customer.objects.create(
            is_active=True,
            id_reference='cus_KLOsroz46wGUr7',
            account=self.user.account)
        Subscription.objects.create(
            status=SubscriptionStatus.PENDING,
            price_reference=SubscriptionProduct.price_by_product(
                SubscriptionProduct.BASIC_PRODUCT_NAME),
            account=self.account
        )

        response = self.post(url=self.url, user=None, data=stripe_data_mock)

        expect(response.status_code).to(equal(status.HTTP_200_OK))
        subscription = self.user.get_subscription()
        expect(subscription.id_reference).to(equal('sub_1Jgi4xKBAHswNGjYuEORMJpB'))
        expect(subscription.status).to(equal(SubscriptionStatus.FAILED))

    @override_settings(STRIPE_WEBHOOK_SECRET='')
    def test_it_updates_subscription_data_from_a_updated_event(self):
        stripe_data_mock = {
            'id': 'evt_1Jgi50KBAHswNGjYg6mOHDr0',
            'type': 'customer.subscription.updated',
            'object': 'event',
            'api_version': '2020-08-27',
            'created': 1633318985,
            'data': {
                'object': {
                    'id': 'sub_1Jgi4xKBAHswNGjYuEORMJpB',
                    'created': 1633318983,
                    'current_period_end': 1635997383,
                    'current_period_start': 1633318983,
                    'customer': 'cus_KLOsroz46wGUr7',
                    'status': 'active',
                }
            }
        }
        Customer.objects.create(
            is_active=True,
            id_reference='cus_KLOsroz46wGUr7',
            account=self.user.account)
        Subscription.objects.create(
            status=SubscriptionStatus.FAILED,
            price_reference=SubscriptionProduct.price_by_product(
                SubscriptionProduct.BASIC_PRODUCT_NAME),
            account=self.account,
            payment_gateway_status='whatever',
            id_reference='whatever',
            current_period_start=timezone.now(),
            current_period_end=timezone.now(),
        )

        response = self.post(url=self.url, user=None, data=stripe_data_mock)

        expect(response.status_code).to(equal(status.HTTP_200_OK))
        subscription = self.user.get_subscription()
        zone = pytz.timezone("UTC")
        current_period_start = zone.localize(datetime.fromtimestamp(1633318983))
        current_period_end = zone.localize(datetime.fromtimestamp(1635997383))
        expect(subscription.status).to(equal(SubscriptionStatus.SUCCESSFUL))
        expect(subscription.payment_gateway_status).to(equal('active'))
        expect(subscription.id_reference).to(equal('sub_1Jgi4xKBAHswNGjYuEORMJpB'))
        expect(subscription.current_period_start).to(equal(current_period_start))
        expect(subscription.current_period_end).to(equal(current_period_end))
