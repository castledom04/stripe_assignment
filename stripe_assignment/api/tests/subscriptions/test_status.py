from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from expects import equal, expect
from rest_framework import status

from ...models import Account, Subscription, User
from ...models.constants import SubscriptionProduct, SubscriptionStatus
from ..base import BaseAPITestCase


class StatusTestCase(BaseAPITestCase):

    def setUp(self):
        self.url = reverse('subscriptions-status')
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
        response = self.get(url=self.url, user=None)

        expect(response.status_code).to(equal(status.HTTP_401_UNAUTHORIZED))

    def test_it_returns_not_found_if_no_subscription_exists(self):

        response = self.get(url=self.url, user=self.user)

        expect(response.status_code).to(equal(status.HTTP_404_NOT_FOUND))

    def test_it_returns_correct_payload_data(self):
        now = timezone.now()
        price_reference = SubscriptionProduct.price_by_product(
            SubscriptionProduct.BASIC_PRODUCT_NAME)
        subscription = Subscription.objects.create(
            created_at=now,
            status=SubscriptionStatus.PENDING,
            payment_gateway_status='super status',
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
            id_reference='subscription reference id',
            price_reference=price_reference,
            account=self.account
        )

        response = self.get(url=self.url, user=self.user)

        expect(response.status_code).to(equal(status.HTTP_200_OK))
        current_period_start = subscription.current_period_start.strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ')
        current_period_end = subscription.current_period_start + \
            timedelta(days=30)
        current_period_end = current_period_end.strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ')
        expect(response.json()).to(equal({
            'status': SubscriptionStatus.PENDING,
            'payment_gateway_status': 'super status',
            'current_period_start': current_period_start,
            'current_period_end': current_period_end,
            'id_reference': 'subscription reference id',
            'price_reference': price_reference,
            'purchase_date': subscription.created_at.strftime('%Y-%m-%d')
        }))
